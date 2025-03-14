import sqlite3
import trueskill
import itertools
import math

db = sqlite3.connect('the-blue-alliance.db')
cursor = db.cursor()

def get_latest_ratings(team_id):
    cursor.execute(f'SELECT * FROM latest_ratings WHERE team_id = "frc{team_id}"')
    try:
        id, team_id, mu, sigma, event_id = cursor.fetchall()[0]
        return mu, sigma
    except:
        return 25, 25/3

def win_probability(team1, team2, BETA):
    delta_mu = sum(r.mu for r in team1) - sum(r.mu for r in team2)
    sum_sigma = sum(r.sigma ** 2 for r in itertools.chain(team1, team2))
    size = len(team1) + len(team2)
    denom = math.sqrt(size * (BETA * BETA) + sum_sigma)
    ts = trueskill.global_env()
    return ts.cdf(delta_mu / denom)

env = trueskill.TrueSkill()

id = input("Red 1 id: ")
mu, sigma = get_latest_ratings(id)
print(mu, sigma)
red1 = trueskill.Rating(mu=mu, sigma=sigma)

id = input("Red 2 id: ")
mu, sigma = get_latest_ratings(id)
print(mu, sigma)
red2 = trueskill.Rating(mu=mu, sigma=sigma)

id = input("Red 3 id: ")
mu, sigma = get_latest_ratings(id)
print(mu, sigma)
red3 = trueskill.Rating(mu=mu, sigma=sigma)

id = input("Blue 1 id: ")
mu, sigma = get_latest_ratings(id)
print(mu, sigma)
blue1 = trueskill.Rating(mu=mu, sigma=sigma)

id = input("Blue 2 id: ")
mu, sigma = get_latest_ratings(id)
print(mu, sigma)
blue2 = trueskill.Rating(mu=mu, sigma=sigma)

id = input("Blue 3 id: ")
mu, sigma = get_latest_ratings(id)
print(mu, sigma)
blue3 = trueskill.Rating(mu=mu, sigma=sigma)

red_alliance = [red1, red2, red3]
blue_alliance = [blue1, blue2, blue3]

print('{:.1%} chance red to win'.format(win_probability(red_alliance, blue_alliance, env.beta)))