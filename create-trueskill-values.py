import sqlite3
import trueskill
from tqdm import tqdm
import pandas as pd

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

conn = sqlite3.connect("trueskill.db")
conn.row_factory = dict_factory
cursor = conn.cursor()

cursor.execute('DROP TABLE IF EXISTS "trueskill_values"')
cursor.execute('CREATE TABLE "trueskill_values" (id INTEGER PRIMARY KEY, "key" TEXT, "year" INTEGER, "team" TEXT, "mu" REAL, "sigma" REAL )')
conn.commit()

mu = 100
sigma = mu / 3
#sigma = 15
beta = sigma / 2
tau = sigma / 100

ratings = {}

# Get the draw probability
cursor.execute("SELECT COUNT(*) AS draw FROM tba_matches WHERE blue_score = red_score")
draw_count = cursor.fetchone()["draw"]
cursor.execute("SELECT COUNT(*) AS total FROM tba_matches")
total_count = cursor.fetchone()["total"]
draw_probability = draw_count / total_count
#print(draw_probability)

env = trueskill.TrueSkill(mu=mu, sigma=sigma, beta=beta, tau=tau, draw_probability=draw_probability)

sql = """
SELECT e.year, e.week, e.id AS e_id, m.* 
FROM 
tba_matches m
INNER JOIN tba_events e
WHERE 
e.key = m.event_key
ORDER BY e.id, m.id
"""

red_possiblity = ("red_team_1", "red_team_2", "red_team_3", "red_team_4")
blue_possiblity = ("blue_team_1", "blue_team_2", "blue_team_3", "blue_team_4")

cursor.execute(sql)
rows = cursor.fetchall()
for row in tqdm(rows, desc="Processing matches"):
    #print(row)
    red_teams = [row[pos] for pos in red_possiblity if row[pos] is not None]
    blue_teams = [row[pos] for pos in blue_possiblity if row[pos] is not None]

    if len(red_teams) > 0 and len(blue_teams) > 0:
        red_ratings = [ratings.get(team, env.create_rating()) for team in red_teams]
        blue_ratings = [ratings.get(team, env.create_rating()) for team in blue_teams]

        red_alliance = dict(zip(red_teams, red_ratings))
        blue_alliance = dict(zip(blue_teams, blue_ratings))
        match_alliances = [red_alliance, blue_alliance]

        if row["red_score"] < row["blue_score"]:
            ranks = [1, 0]
        elif row["red_score"] > row["blue_score"]:
            ranks = [0, 1]
        else:
            ranks = [0, 0]

        posterior_ratings = {}
        for rating in env.rate(match_alliances, ranks=ranks):
            posterior_ratings.update(rating)

        #print(posterior_ratings)

        data_to_insert = []
        for team, rating in posterior_ratings.items():
            data_to_insert.append({"key": row["key"], "year": row["year"], "team": team, "mu": rating.mu, "sigma": rating.sigma})
            ratings[team] = rating

        #print(data_to_insert)
        df = pd.DataFrame(data_to_insert)
        df.to_sql("trueskill_values", conn, if_exists="append", index=False)
