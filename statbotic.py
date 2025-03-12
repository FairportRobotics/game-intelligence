import statbotics
import pandas as pd
sb = statbotics.Statbotics()
data = []


teams = ['578', '3003', '27']

for team in teams:
    data.append(sb.get_team(int(team)))

df = pd.DataFrame(data)
df.to_csv('statbotics.csv', index=False)

df
