# Phase-specific team ratings

Create independent TrueSkill and Elo tracks for Autonomous, Teleop excluding End Game, and End Game, each with all-time and season scopes. Each rating estimates a team's phase skill from its alliance's phase result, not from individually attributed points; only disjoint, phase-attributable points determine the result (higher wins, equal scores draw, no margin), and unavailable scores skip that phase update. Normalize season-specific TBA fields, exclude unassigned foul/adjustment points and ranking-point bonuses, and apply the existing result precedence (FIRST, then TBA, then manual provisional) with provenance; recompute affected histories in match order when higher-priority data arrives.

## Consequences

- Include official qualification and playoff matches, but not practice or offseason matches. All-time streams continue across FRC seasons; season streams reset each season.
- Elo starts at 1500 with K=32. Compute alliance expectation from the mean member ratings and apply the same adjustment to each member.
- Share the TrueSkill initial scale across phases. Retain phase-specific performance and draw parameters only when time-ordered out-of-sample log loss beats shared defaults with sufficient data.
- Compare ratings only within the same phase, and keep phase ratings out of match predictions initially.
