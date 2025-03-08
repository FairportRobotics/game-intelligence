import pandas as pd
import trueskill
from glob import glob


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

all_data = []
for file_path in ['the-blue-alliance-api-data/2000.csv']:#glob('the-blue-alliance-api-data/*.csv'):
    print(file_path)
    # Read in the data
    df = pd.read_csv(file_path)
    df['event_start_date'] = pd.to_datetime(df['event_start_date'])
    # Get the unique event start dates and sort them
    dates_df = pd.DataFrame({'event_start_date' : df['event_start_date'].drop_duplicates()})
    dates_df.sort_values('event_start_date', inplace=True)
    dates_df.reset_index(drop=True, inplace=True)
    dates_df['date_sort'] = dates_df.index
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


env = trueskill.TrueSkill()
default = trueskill.Rating()
current_ratings = {}


row = all_data[0]
#r = current_ratings.get(578, {'mu': default.mu, 'sigma': default.sigma})

red_alliance_members = [col for col in row.keys() if 'red' in col and col != 'red_score']
blue_alliance_members = [col for col in row.keys() if 'blue' in col and col != 'blue_score']
for member in red_alliance_members:
    team_id = row[member]
    current_ratings[team_id] = current_ratings.get(team_id, {'mu': default.mu, 'sigma': default.sigma})
    #current_ratings[member] = env.create_rating()
print(current_ratings)
'''
for row in all_data:
    print(row)
#'''