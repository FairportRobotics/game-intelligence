# This script aggregates all the match data from 
# https://github.com/the-blue-alliance/the-blue-alliance-data.
# The files are in CSV format.  The match data follows this pattern:
# <event_key>_<match_key>, <red1>, <red2>, <red3>, <blue1>, <blue2>, <blue3>, <red_score>, <blue_score>
# The matches in 2002 only had 2 teams per alliance until the playoffs.
# Special handeling of this data is needed.

# This script assumes the data from the repository has been copied into this directory
import os
import pandas as pd

start_year = 2002
end_year = 2019

the_data = []

for year in range(start_year, end_year + 1):
    print(year)
    for temp in os.walk(f"the-blue-alliance-data/events/{year}/"):
        dir = temp[0]
        for match_file in [x for x in temp[2] if "matches" in x]:
            with open(f"{dir}/{match_file}") as file:
                for line in file:
                    line = line.strip().split(",")
                    if len(line) == 7:
                        # This is a 2002 match with only two competitors
                        keys = ["event_key_match_key", "red1", "red2", "blue1", "blue2", "red_score", "blue_score"]
                    else:
                        keys = ["event_key_match_key", "red1", "red2", "red3", "blue1", "blue2", "blue3", "red_score", "blue_score"]
                    data = dict(zip(keys, line))
                    '''
                    data["year"] = year
              
                    # What alliance won?
                    if "blue_score" in data.keys() and "red_score" in data.keys():
                        if int(data["red_score"]) > int(data["blue_score"]):
                            winner = "red"
                        elif int(data["red_score"]) < int(data["blue_score"]):
                            winner = "blue"
                        else:
                            winner = "tie"
                    else:
                        winner = "error"
                    data["winner"] = winner
                    '''
                    
                    the_data.append(data)

df = pd.DataFrame(the_data)
df.to_csv("the-blue-alliance-data.csv", index=False)
