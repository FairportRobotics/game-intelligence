import sqlite3


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


conn = sqlite3.connect("trueskill.db")
conn.row_factory = dict_factory
cursor = conn.cursor()

sql = """
CREATE VIEW IF NOT EXISTS last_qm_trueskill AS
SELECT a.id, a.team, a.event_key, b.mu, b.sigma
FROM
(
SELECT MAX(t.id) as id, t.team, m.event_key
FROM trueskill_values t
INNER JOIN tba_matches m
ON t.key = m.key
WHERE m.comp_level = "qm"
GROUP BY t.team, m.event_key
) a
INNER JOIN trueskill_values b
ON a.id = b.id
ORDER BY a.team, a.id
"""

cursor.execute(sql)

sql = """
CREATE VIEW IF NOT EXISTS qf_roles AS
SELECT *
FROM (
    SELECT 
    DISTINCT event_key, blue_team_1 AS team , "Captain" AS level
    FROM tba_matches
    WHERE comp_level = "qf"

    UNION

    SELECT 
    DISTINCT event_key, red_team_1 AS team,  "Captain" AS level
    FROM tba_matches
    WHERE comp_level = "qf"

    UNION

    SELECT 
    DISTINCT event_key, blue_team_2 AS team , "Support" AS level
    FROM tba_matches
    WHERE comp_level = "qf"

    UNION

    SELECT 
    DISTINCT event_key, red_team_2 AS team,  "Support" AS level
    FROM tba_matches
    WHERE comp_level = "qf"

    UNION

    SELECT 
    DISTINCT event_key, blue_team_3 AS team , "Support" AS level
    FROM tba_matches
    WHERE comp_level = "qf"

    UNION

    SELECT 
    DISTINCT event_key, red_team_3 AS team,  "Support" AS level
    FROM tba_matches
    WHERE comp_level = "qf"

    UNION

    SELECT 
    DISTINCT event_key, blue_team_4 AS team , "Support" AS level
    FROM tba_matches
    WHERE comp_level = "qf"

    UNION

    SELECT 
    DISTINCT event_key, red_team_4 AS team,  "Support" AS level
    FROM tba_matches
    WHERE comp_level = "qf"
)
WHERE team IS NOT NULL
ORDER BY event_key, level, team
"""

cursor.execute(sql)
conn.commit()

sql = """
SELECT level, AVG(MU) AS mu, AVG(sigma) AS sigma
FROM (
SELECT mu, sigma, 
CASE WHEN level IS NULL 
THEN "Other" 
ELSE level
END AS level
FROM(
SELECT a.*, b.level 
FROM last_qm_trueskill a
LEFT JOIN qf_roles b
ON a.team = b.team AND a.event_key = b.event_key
) 
) 
GROUP BY level
"""

sql = """
SELECT level, mu, sigma, 
CASE WHEN level IS NULL 
THEN "Other" 
ELSE level
END AS level
FROM(
SELECT a.*, b.level 
FROM last_qm_trueskill a
LEFT JOIN qf_roles b
ON a.team = b.team AND a.event_key = b.event_key
) 
"""

results = cursor.execute(sql).fetchall()
# for result in results:
#    print(result)

import csv

# Open the CSV file in write mode
with open("full_data.csv", "w", newline="") as csvfile:
    # Create a DictWriter object
    writer = csv.DictWriter(csvfile, fieldnames=["level", "mu", "sigma"])

    # Write the header row
    writer.writeheader()

    # Write all the dictionary rows
    writer.writerows(results)
