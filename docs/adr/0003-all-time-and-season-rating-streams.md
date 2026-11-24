# All-time and season rating streams

Maintain separate continuous all-time and season-reset TrueSkill and Elo ratings: all-time TrueSkill drives the primary match prediction, while season TrueSkill provides a comparison. This preserves the requested long-term history while keeping current-season performance visible despite the tradeoff that all-time ratings span different FRC games.
