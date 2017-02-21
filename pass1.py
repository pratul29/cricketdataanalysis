######################################### IPL - Blog 1############################################

## files generated - basic.csv


import pandas as pd
import math

##########################################################################################
################################# Feature Extraction #####################################

d = pd.read_csv('deliveries.csv')
full = d[['match_id', 'batting_team', 'bowling_team', 'total_runs']]
matches = pd.read_csv('matches.csv')
m = matches[['id', 'season']]
m.columns = ['match_id', 'season']
sim = full.merge(m, on = ['match_id'], how = 'left')
x = sim[['batting_team', 'season', 'total_runs']].groupby(['batting_team', 'season']).agg('sum')
x = x.reset_index()
x.columns = ['team', 'season', 'total_runs_scored']
y = sim[['bowling_team', 'season', 'total_runs']].groupby(['bowling_team', 'season']).agg('sum')
y = y.reset_index()
y.columns = ['team', 'season', 'total_runs_given']
data = x
data['total_runs_given'] = y['total_runs_given']
ma = matches[['season', 'winner', 'team1', 'team2']]
won = ma[['season', 'winner', 'team1']].groupby(['winner', 'season']).agg('count')
won = won.reset_index()
won.columns = ['team', 'season', 'number_of_wins']
data['number_of_wins'] = won['number_of_wins']
team1 = ma[['season', 'team1', 'team2']].groupby(['season', 'team1']).agg('count')
team1 = team1.reset_index()
team2 = ma[['season', 'team1', 'team2']].groupby(['season', 'team2']).agg('count')
team2 = team2.reset_index()
team1.columns = ['season', 'team', 'team1']
team2.columns = ['season', 'team', 'team2']
team = team1
team['team2'] = team2['team2']
team['total_matches'] = team['team1'] + team['team2']
data['total_matches'] = team['total_matches']
data = data[['team', 'season', 'total_runs_scored', 'total_runs_given', 'total_matches','number_of_wins']]
data['number_of_losses'] = data['total_matches'] - data['number_of_wins']

data.to_csv('basic.csv', index = False)

'''
Extracted Features - team, season, total_runs_scored, total_runs_given, total_matches, number_of_wins, number_of_losses
'''

##########################################################################################
###################### Determining the power with smallest error #########################

data = pd.read_csv('basic.csv')
data['actual_win_percentage'] = data['number_of_wins'] / data['total_matches']
data['scoring_ratio'] = data['total_runs_scored'] / data['total_runs_given'] 
scoring_ratio = data['scoring_ratio'].tolist() 
actual_win = data['actual_win_percentage']

i = 0.5
d = {}
while i < 20.5:
	temp = []
	for j in scoring_ratio:
		a = math.pow(j, i)
		wp = a / (a + 1)
		temp.append(wp)
	vals = [math.fabs(temp[k] - actual_win[k]) for k in range(len(temp))]
	val = sum(vals) / len(vals)
	d[i] = val
	i = i + 0.5

sorted(d.iteritems(), key = lambda (k, v) : (v, k))[0] ## (8.0, 0.1193371548592167)

##########################################################################################