import pandas as pd
import trueskill
from glob import glob
import sqlite3
from tqdm import tqdm
import itertools
import math

db = sqlite3.connect('the-blue-alliance.db')
cursor = db.cursor()
cursor.execute('DROP TABLE IF EXISTS match')
cursor.execute('CREATE TABLE match (id INTEGER PRIMARY KEY, year INTEGER, event_key TEXT, match_key TEXT, event_start_date TEXT, event_end_date TEXT, winning_alliance TEXT, red1 TEXT, red2 TEXT, red3 TEXT, red4 TEXT, blue1 TEXT, blue2 TEXT, blue3 TEXT, blue4 TEXT, red_score INTEGER, blue_score INTEGER)')
cursor.execute('DROP TABLE IF EXISTS trueskill')
cursor.execute('CREATE TABLE trueskill (id INTEGER PRIMARY KEY AUTOINCREMENT, team_id INTEGER, mu REAL, sigma REAL, match_id INTEGER)')
cursor.execute('DROP TABLE IF EXISTS crystal_ball')
cursor.execute('CREATE TABLE crystal_ball (id INTEGER PRIMARY KEY AUTOINCREMENT, winning_alliance TEXT, red1_mu REAL, red1_sigma REAL, red2_mu REAL, red2_sigma REAL, red3_mu REAL, red3_sigma REAL, red4_mu REAL, red4_sigma REAL, blue1_mu REAL, blue1_sigma REAL, blue2_mu REAL, blue2_sigma REAL, blue3_mu REAL, blue3_sigma REAL, blue4_mu REAL, blue4_sigma REAL)')
cursor.execute('DROP TABLE IF EXISTS predictions')
cursor.execute('CREATE TABLE predictions (id INTEGER PRIMARY KEY AUTOINCREMENT, match_id INTEGER, wining_alliance TEXT, pred_winining_alliance TEXT, p_red_win REAL, p_blue_win REAL, p_tie REAL)')
db.commit()

def get_match_type_sort(row):
    event_key = row['event_key'] + '_'
    match_key = row['match_key']
    match_key = match_key.replace(event_key, '')
    if 'qm' in match_key:
        return 1
    elif 'qf' in match_key:
        return 2
    elif 'sf' in match_key: 
        return 3
    elif 'f' in match_key:
        return 4
    else:
        return -1
    
def get_match_number_sort(row):
    event_key = row['event_key'] + '_'
    match_key = row['match_key']
    match_key = match_key.replace(event_key, '')
    return int(match_key.split('m')[-1])

def get_payoff_sort(row):
    event_key = row['event_key'] + '_'
    match_key = row['match_key']
    match_key = match_key.replace(event_key, '')
    match_key = match_key.split('m')[0]
    if not 'f' in match_key:
        return 0
    return int(match_key.split('f')[-1])

def win_probability(team1, team2, BETA):
    delta_mu = sum(r.mu for r in team1) - sum(r.mu for r in team2)
    sum_sigma = sum(r.sigma ** 2 for r in itertools.chain(team1, team2))
    size = len(team1) + len(team2)
    denom = math.sqrt(size * (BETA * BETA) + sum_sigma)
    ts = trueskill.global_env()
    return ts.cdf(delta_mu / denom)

def predict_winner(team1, team2, BETA):
    p = win_probability(team1, team2, BETA)
    if p == 0.5:
        result = 'tie'
    elif p > 0.5:
        result = 'red'
    else:
        result = 'blue'
    return result, p


all_data = []
for file_path in glob('the-blue-alliance-api-data/*.csv'):#['the-blue-alliance-api-data/2000.csv']:
    print(file_path)
    # Read in the data
    df = pd.read_csv(file_path)
    # Get the unique event start dates and sort them
    dates_df = pd.DataFrame({'event_start_date' : df['event_start_date'].drop_duplicates()})
    dates_df['event_start_date_dt'] = pd.to_datetime(dates_df['event_start_date'])
    dates_df.sort_values('event_start_date_dt', inplace=True)
    dates_df.reset_index(drop=True, inplace=True)
    dates_df['date_sort'] = dates_df.index
    dates_df.drop('event_start_date_dt', axis=1, inplace=True)  
    # Get the unique event keys and sort them alphabetically
    events_df = pd.DataFrame({'event_key' : df['event_key'].drop_duplicates()})
    events_df.sort_values('event_key', inplace=True)
    events_df.reset_index(drop=True, inplace=True)
    events_df['event_sort'] = events_df.index
    # Join in the event date and key sort columns
    df = df.join(dates_df.set_index('event_start_date'), on='event_start_date')
    df = df.join(events_df.set_index('event_key'), on='event_key')
    # Get the match type sort, payoff sort, and match number sort
    df['match_type_sort'] = df.apply(get_match_type_sort, axis=1)
    df['payoff_sort'] = df.apply(get_payoff_sort, axis=1)
    df['match_number_sort'] = df.apply(get_match_number_sort, axis=1)
    # Sort the data frame by the start date, event, then matches in order from qualification to finals
    df.sort_values(['date_sort', 'event_sort', 'match_type_sort',  'payoff_sort', 'match_number_sort'], inplace=True)
    # Create a sort column to keep track of the order
    df.reset_index(drop=True, inplace=True)
    # Create an id with the year and the sort index with leading zeros
    max_index = max(df.index)
    n = len(str(max_index))
    df['sort'] = df.index
    df['sort'] = df['sort'].astype(str)
    df['sort'] = df['sort'].str.zfill(n)
    df['id'] = df['year'].astype(str) + df['sort']
    df['id'] = df['id'].astype(int)
    # Drop all the sort columns because we don't need them anymore
    df.drop(columns=['date_sort', 'event_sort', 'match_type_sort', 'payoff_sort', 'match_number_sort', 'sort'], inplace=True)
    # Append the data to the all_data list
    list_of_dicts = df.to_dict(orient='records')
    all_data.extend(list_of_dicts)
    #print(df.head())
    #'''

'''
df = pd.DataFrame(all_data)
# Move column 'id' to the first position
column_to_move = df.pop('id')
df.insert(0, 'id', column_to_move)
# Alphabetize the red and blue columns
red_or_blue = [col for col in df.columns if 'red' in col or 'blue' in col]
red_or_blue.sort()
# Get the columns that are not red or blue
not_red_or_blue = [col for col in df.columns if col not in red_or_blue]
# Combine it all back together
all_cols = not_red_or_blue + red_or_blue
df = df[all_cols]

df.to_excel('the-blue-alliance-api-data/all_data.xlsx', index=False)
#'''

# These are the garbage team ids we don't want to include in the trueskill calculations
junk = [f'frc{x}' for x in range(9900, 10000)]
junk.append('frc0')

env = trueskill.TrueSkill()
default = trueskill.Rating()
current_ratings = {}

i = 0
for row in tqdm(all_data, desc="Processing matches"):
    #row = all_data[0]

    if row['red_score'] > -1 and row['blue_score'] > -1:
        red_alliance_members = [col for col in row.keys() if 'red' in col and col != 'red_score']
        blue_alliance_members = [col for col in row.keys() if 'blue' in col and col != 'blue_score']
        red_alliance_ratings = []
        blue_alliance_ratings = []

        red_alliance_keys = []
        blue_alliance_keys = []
        crystal_ball_data = {
            'winning_alliance': row['winning_alliance'],
            'red1_mu': None,
            'red1_sigma': None,
            'red2_mu': None,
            'red2_sigma': None,
            'red3_mu': None,
            'red3_sigma': None,
            'red4_mu': None,
            'red4_sigma': None,
            'blue1_mu': None,
            'blue1_sigma': None,
            'blue2_mu': None,
            'blue2_sigma': None,
            'blue3_mu': None,
            'blue3_sigma': None,
            'blue4_mu': None,
            'blue4_sigma': None
        }

        j = 0
        for member in red_alliance_members:
            team_id = row[member] #int(str(row[member]).replace('frc', ''))
            if team_id not in junk and team_id != 'frc':
                j += 1
                red_alliance_keys.append(team_id)
                current_ratings[team_id] = current_ratings.get(team_id, {'mu': default.mu, 'sigma': default.sigma})
                crystal_ball_data[f'red{j}_mu'] = current_ratings[team_id]['mu']
                crystal_ball_data[f'red{j}_sigma'] = current_ratings[team_id]['sigma']
                red_alliance_ratings.append(env.create_rating(mu=current_ratings[team_id]['mu'], sigma=current_ratings[team_id]['sigma']))
        j = 0
        for member in blue_alliance_members:
            team_id = row[member] #int(str(row[member]).replace('frc', ''))
            if team_id not in junk and team_id != 'frc':
                j += 1
                crystal_ball_data[f'blue{j}_mu'] = current_ratings.get(team_id, {'mu': default.mu, 'sigma': default.sigma})['mu']
                crystal_ball_data[f'blue{j}_sigma'] = current_ratings.get(team_id, {'mu': default.mu, 'sigma': default.sigma})['sigma']
                blue_alliance_keys.append(team_id)
                current_ratings[team_id] = current_ratings.get(team_id, {'mu': default.mu, 'sigma': default.sigma})
                crystal_ball_data[f'blue{j}_mu'] = current_ratings[team_id]['mu']
                crystal_ball_data[f'blue{j}_sigma'] = current_ratings[team_id]['sigma']
                blue_alliance_ratings.append(env.create_rating(mu=current_ratings[team_id]['mu'], sigma=current_ratings[team_id]['sigma']))

        if len(red_alliance_keys) > 0 and len(blue_alliance_keys) > 0:
            if row['winning_alliance'] == 'red':
                ranks = [0,1]
            elif row['winning_alliance'] == 'blue':
                ranks = [1,0]
            else:
                ranks = [0,0]
                crystal_ball_data['winning_alliance'] = 'tie'

            # Saving the ratings before the match along with the winner in crystal_ball table
            cursor.execute('''INSERT INTO crystal_ball (winning_alliance, red1_mu, red1_sigma, red2_mu, red2_sigma, red3_mu, red3_sigma, red4_mu, red4_sigma, blue1_mu, blue1_sigma, blue2_mu, blue2_sigma, blue3_mu, blue3_sigma, blue4_mu, blue4_sigma) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (crystal_ball_data['winning_alliance'], crystal_ball_data['red1_mu'], crystal_ball_data['red1_sigma'], crystal_ball_data['red2_mu'], crystal_ball_data['red2_sigma'], crystal_ball_data['red3_mu'], crystal_ball_data['red3_sigma'], crystal_ball_data['red4_mu'], crystal_ball_data['red4_sigma'], crystal_ball_data['blue1_mu'], crystal_ball_data['blue1_sigma'], crystal_ball_data['blue2_mu'], crystal_ball_data['blue2_sigma'], crystal_ball_data['blue3_mu'], crystal_ball_data['blue3_sigma'], crystal_ball_data['blue4_mu'], crystal_ball_data['blue4_sigma']))
            yhat_winner, p_win = predict_winner(red_alliance_ratings, blue_alliance_ratings, env.beta)  
            cursor.execute('''INSERT INTO predictions (wining_alliance, pred_winining_alliance, p_red_win, match_id) VALUES (?, ?, ?, ?)''', (crystal_ball_data['winning_alliance'], yhat_winner, p_win, row['id']))          
                
            red_alliance_ratings, blue_alliance_ratings = env.rate([tuple(red_alliance_ratings), tuple(blue_alliance_ratings)], ranks=ranks)
            red_alliance_ratings = dict(zip(red_alliance_keys, red_alliance_ratings))
            blue_alliance_ratings = dict(zip(blue_alliance_keys, blue_alliance_ratings))

            for team_id, rating in red_alliance_ratings.items():
                current_ratings[team_id] = {'mu': rating.mu, 'sigma': rating.sigma}
                cursor.execute('INSERT INTO trueskill (team_id, mu, sigma, match_id) VALUES (?, ?, ?, ?)', (team_id, rating.mu, rating.sigma, row['id']))

            for team_id, rating in blue_alliance_ratings.items():
                current_ratings[team_id] = {'mu': rating.mu, 'sigma': rating.sigma}
                cursor.execute('INSERT INTO trueskill (team_id, mu, sigma, match_id) VALUES (?, ?, ?, ?)', (team_id, rating.mu, rating.sigma, row['id']))


            columns = ', '.join(row.keys())
            placeholders = ':'+', :'.join(row.keys())
            query = 'INSERT INTO match (%s) VALUES (%s)' % (columns, placeholders)
            cursor.execute(query, row)

            if i % 100 == 1:
                db.commit()
            i += 1

#print(current_ratings)

print(i)

cursor.execute('DROP VIEW IF EXISTS latest_ratings')

cursor.execute('''
CREATE VIEW latest_ratings AS
SELECT t1.* 
FROM (SELECT MAX(match_id) AS match_id, team_id FROM trueskill GROUP BY team_id)t2
INNER JOIN trueskill t1 
ON t1.match_id = t2.match_id and t1.team_id = t2.team_id
ORDER BY team_id
''')

db.commit()