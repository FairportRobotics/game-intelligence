"""metrics/ - Calculate ratings and averages, then SAVE them in `team_metrics`.

Pages only READ saved metrics. All the math happens here, in batch jobs, so pages
stay fast. Run everything with:  python -m metrics.run_all
"""
