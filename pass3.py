#################################### IPL - Blog 2 ##########################################


import pandas as pd
from __future__ import division

## 70% win rate if team scores more than 175 runs ## 

df = pd.read_csv('deliveries.csv')
full = df[['match_id', 'batting_team', 'bowling_team', 'total_runs']]
matches = pd.read_csv('matches.csv')
m = matches[['id', 'season']]
m.columns = ['match_id', 'season']
dt = matches[['id', 'winner']]
sim = full.merge(m, on = ['match_id'], how = 'left')
x = sim[['batting_team', 'match_id', 'total_runs']].groupby(['batting_team', 'match_id']).agg('sum')
x = x.reset_index()
dt.columns = ['match_id', 'winner']
x = x.merge(dt, on = ['match_id'], how = 'left')
y = x[x.total_runs > 175]
tot = y.shape[0]
wins = y[y.batting_team == y.winner].shape[0]
print wins / tot * 100 ## 69.92