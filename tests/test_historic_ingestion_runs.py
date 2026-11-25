from pathlib import Path

from backend.historic_ingestion import (
    IngestionSummary,
    NormalizedHistoricBatch,
    ingest_historic_event,
)
from backend.historic_ingestion_runs import (
    EventSource,
    SourceResult,
    TransientSourceError,
    run_historic_ingestion,
)


class FakeSourceAdapter:
    def __init__(self, batches: dict[str, NormalizedHistoricBatch]) -> None:
        self.batches = batches
        self.calls = 0

    def fetch_event(self, event_key: str, source: str) -> SourceResult:
        self.calls += 1
        return SourceResult(batch=self.batches[event_key])


def event_batch(event_key: str) -> NormalizedHistoricBatch:
    return {
        "season": {"year": 2024},
        "event": {"key": event_key, "name": "Finger Lakes Regional"},
        "teams": [
            {"number": 578, "name": "Fairport Robotics"},
            {"number": 100, "name": "The Wildhats"},
        ],
        "matches": [
            {
                "key": f"{event_key}_qm1",
                "type": "qualification",
                "number": 1,
                "red": [578],
                "blue": [100],
            }
        ],
        "source": "tba",
    }


def test_run_ingests_selected_event_and_reports_canonical_counts(
    tmp_path: Path,
) -> None:
    batch = event_batch("2024nyro")
    summary = run_historic_ingestion(
        run_id="run-1",
        event_sources=[EventSource("2024nyro", "tba")],
        source_adapter=FakeSourceAdapter({"2024nyro": batch}),
        ingest_event=ingest_historic_event,
        canonical_database_path=tmp_path / "canonical.sqlite3",
        checkpoint_database_path=tmp_path / "checkpoints.sqlite3",
    )

    assert summary.created == 5
    assert summary.updated == 0
    assert summary.unchanged == 0
    assert summary.skipped == 0
    assert summary.failed == 0
    assert summary.replaced == 0
    assert summary.completed_events == ("2024nyro",)
    assert summary.human_summary == "Completed: 2024nyro. Skipped: none. Failed: none."
    assert isinstance(summary.ingestion_summary, IngestionSummary)


def test_resuming_a_completed_run_does_not_repeat_source_or_canonical_work(
    tmp_path: Path,
) -> None:
    adapter = FakeSourceAdapter({"2024nyro": event_batch("2024nyro")})
    arguments = {
        "run_id": "run-1",
        "event_sources": [EventSource("2024nyro", "tba")],
        "source_adapter": adapter,
        "ingest_event": ingest_historic_event,
        "canonical_database_path": tmp_path / "canonical.sqlite3",
        "checkpoint_database_path": tmp_path / "checkpoints.sqlite3",
    }

    first = run_historic_ingestion(**arguments)
    resumed = run_historic_ingestion(**arguments)

    assert adapter.calls == 1
    assert first.created == resumed.created == 5
    assert resumed.completed_events == ("2024nyro",)


def test_resuming_a_partial_run_only_retries_the_failed_event(tmp_path: Path) -> None:
    class PartialSourceAdapter(FakeSourceAdapter):
        def __init__(self) -> None:
            super().__init__(
                {
                    "2024nyro": event_batch("2024nyro"),
                    "2024miket": event_batch("2024miket"),
                }
            )
            self.event_calls: dict[str, int] = {}

        def fetch_event(self, event_key: str, source: str) -> SourceResult:
            self.calls += 1
            self.event_calls[event_key] = self.event_calls.get(event_key, 0) + 1
            if event_key == "2024nyro" and self.event_calls[event_key] == 1:
                raise TransientSourceError("temporarily unavailable")
            return SourceResult(batch=self.batches[event_key])

    adapter = PartialSourceAdapter()
    arguments = {
        "run_id": "run-1",
        "event_sources": [
            EventSource("2024nyro", "tba"),
            EventSource("2024miket", "tba"),
        ],
        "source_adapter": adapter,
        "ingest_event": ingest_historic_event,
        "canonical_database_path": tmp_path / "canonical.sqlite3",
        "checkpoint_database_path": tmp_path / "checkpoints.sqlite3",
        "max_attempts": 1,
    }

    first = run_historic_ingestion(**arguments)
    resumed = run_historic_ingestion(**arguments)

    assert first.failed_events == ("2024nyro",)
    assert first.completed_events == ("2024miket",)
    assert resumed.failed_events == ()
    assert resumed.completed_events == ("2024nyro", "2024miket")
    assert adapter.event_calls == {"2024nyro": 2, "2024miket": 1}


def test_unchanged_source_response_does_not_call_canonical_ingestor(
    tmp_path: Path,
) -> None:
    class UnchangedSourceAdapter:
        def fetch_event(self, event_key: str, source: str) -> SourceResult:
            return SourceResult(unchanged=True)

    ingested_batches: list[NormalizedHistoricBatch] = []

    def record_ingestion(
        normalized_batch: NormalizedHistoricBatch, *, database_path: str | Path
    ) -> IngestionSummary:
        ingested_batches.append(normalized_batch)
        return IngestionSummary(created=0, unchanged=0)

    summary = run_historic_ingestion(
        run_id="run-1",
        event_sources=[EventSource("2024nyro", "tba")],
        source_adapter=UnchangedSourceAdapter(),
        ingest_event=record_ingestion,
        canonical_database_path=tmp_path / "canonical.sqlite3",
        checkpoint_database_path=tmp_path / "checkpoints.sqlite3",
    )

    assert summary.unchanged == 1
    assert summary.skipped_events == ("2024nyro",)
    assert ingested_batches == []


def test_transient_source_failure_is_retried_within_the_attempt_limit(
    tmp_path: Path,
) -> None:
    class FlakySourceAdapter(FakeSourceAdapter):
        def fetch_event(self, event_key: str, source: str) -> SourceResult:
            self.calls += 1
            if self.calls < 3:
                raise TransientSourceError("private token value")
            return SourceResult(batch=self.batches[event_key])

    adapter = FlakySourceAdapter({"2024nyro": event_batch("2024nyro")})
    summary = run_historic_ingestion(
        run_id="run-1",
        event_sources=[EventSource("2024nyro", "tba")],
        source_adapter=adapter,
        ingest_event=ingest_historic_event,
        canonical_database_path=tmp_path / "canonical.sqlite3",
        checkpoint_database_path=tmp_path / "checkpoints.sqlite3",
        max_attempts=3,
    )

    assert adapter.calls == 3
    assert summary.created == 5
    assert summary.failed == 0
    assert summary.completed_events == ("2024nyro",)


def test_exhausted_transient_failures_are_reported_without_exception_secrets(
    tmp_path: Path,
) -> None:
    class UnavailableSourceAdapter:
        def __init__(self) -> None:
            self.calls = 0

        def fetch_event(self, event_key: str, source: str) -> SourceResult:
            self.calls += 1
            raise TransientSourceError("api-key=private-token")

    adapter = UnavailableSourceAdapter()
    summary = run_historic_ingestion(
        run_id="run-1",
        event_sources=[EventSource("2024nyro", "tba")],
        source_adapter=adapter,
        ingest_event=ingest_historic_event,
        canonical_database_path=tmp_path / "canonical.sqlite3",
        checkpoint_database_path=tmp_path / "checkpoints.sqlite3",
        max_attempts=2,
    )

    assert adapter.calls == 2
    assert summary.failed == 1
    assert summary.failed_events == ("2024nyro",)
    assert summary.failure_details[0].attempts == 2
    assert "transient source failure" in summary.failure_details[0].reason.lower()
    assert "retry" in summary.failure_details[0].reason.lower()
    assert "private-token" not in repr(summary)
