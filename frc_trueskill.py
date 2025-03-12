import trueskill
import csv
import glob

env = trueskill.TrueSkill()

default_rating = trueskill.Rating()
trueskill_data = {}

for file in glob.glob('frc-api-data/2006.csv'):
    with open(file, 'r') as f:
        for row in csv.DictReader(f):
            print(row) 
            '''
            if row[0] not in trueskill_data:
                trueskill_data[row[0]] = env.create_rating()
            if row[1] not in trueskill_data:
                trueskill_data[row[1]] = env.create_rating()
            rating_groups = [(trueskill_data[row[0]],), (trueskill_data[row[1]],)]
            if row[2] == '1':
                (trueskill_data[row[0]],), (trueskill_data[row[1]],) = env.rate(rating_groups)
            else:
                (trueskill_data[row[1]],), (trueskill_data[row[0]],) = env.rate(rating_groups)
            '''