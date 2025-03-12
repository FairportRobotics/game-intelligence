# pip install trueskill
import trueskill
import itertools
import math

def win_probability(team1, team2, BETA):
    delta_mu = sum(r.mu for r in team1) - sum(r.mu for r in team2)
    sum_sigma = sum(r.sigma ** 2 for r in itertools.chain(team1, team2))
    size = len(team1) + len(team2)
    denom = math.sqrt(size * (BETA * BETA) + sum_sigma)
    ts = trueskill.global_env()
    return ts.cdf(delta_mu / denom)

env = trueskill.TrueSkill()

'''
red1 = trueskill.Rating()
red2 = trueskill.Rating()
red3 = trueskill.Rating()
blue1 = trueskill.Rating()
blue2 = trueskill.Rating()
blue3 = trueskill.Rating()
red_alliance = [red1, red2, red3]
blue_alliance = [blue1, blue2, blue3]

print('{:.1%} chance to draw'.format(trueskill.quality([red_alliance, blue_alliance])))
'''
red1 = env.create_rating()
red2 = env.create_rating()
red3 = env.create_rating()
blue1 = env.create_rating()
blue2 = env.create_rating()
blue3 = env.create_rating()

print("Initial ratings")
print(red1.mu, red1.sigma)
print(blue1.mu, blue1.sigma)

red_alliance = [red1, red2, red3]
blue_alliance = [blue1, blue2, blue3]
print('{:.1%} chance to win'.format(win_probability(red_alliance, blue_alliance, env.beta)))

rating_groups = [(red1, red2, red3), (blue1, blue2, blue3)]
(red1, red2, red3), (blue1, blue2, blue3) = env.rate(rating_groups, ranks=[0, 1])

print("Updated ratings")
print(red1.mu, red1.sigma)
print(blue1.mu, blue1.sigma)  


red_alliance = [red1, red2, red3]
blue_alliance = [blue1, blue2, blue3]
print('{:.1%} chance to win'.format(win_probability(red_alliance, blue_alliance, env.beta)))
#'''