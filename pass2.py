#################################### World T20 - Blog 1 ##########################################

## Important files generated - year_allteams.pickle, innings_allteams.pickle, wt20.csv

import pandas as pd
import pickle


##########################################################################################
################################# Feature Extraction #####################################

## codes represent the code of each team on the crickbuzz website

tofind_codes = [40, 25, 17, 29, 26, 15, 30, 27, 9]
last_codes = [12, 19, 33, 37, 20]
all_codes = list(range(1, 9)) + tofind_codes + last_codes


#################### Run Only Once - Use Pickle Files Then - Start ######################

teams = []
part1 = 'http://stats.espncricinfo.com/ci/engine/team/'
part2 = '.html?class=3;filter=advanced;orderby=start;template=results;type=team;view=year'
for i in all_codes:
	part = part1 + str(i) + part2
	t = pd.read_html(part)
	t = t[3]
	teams.append(t)

with open('year_allteams.pickle', 'wb') as handle:
	pickle.dump(teams, handle, protocol=pickle.HIGHEST_PROTOCOL)

team_inn = []
part1 = 'http://stats.espncricinfo.com/ci/engine/team/'
part2 = '.html?class=3;filter=advanced;orderby=start;template=results;type=team;view=innings'
for i in all_codes:
	part = part1 + str(i) + part2
	t = pd.read_html(part)
	t = t[3]
	team_inn.append(t)

with open('innings_allteams.pickle', 'wb') as handle:
	pickle.dump(team_inn, handle, protocol=pickle.HIGHEST_PROTOCOL)

allteams = set()
for i in range(len(team_inn)):
	allteams = allteams | set(team_inn[i]['Opposition'].tolist())
al = [i[2:] for i in allteams]

## Testing if all teams have been covered ## 
# allteams = set(al) 
# allteams - (top8 | others | last) ## set() - empty set no more teams

###################### Run Only Once - Use Pickle Files Then - End ######################

############### Finding matches played, won, lost for each team each year ###############

with open('year_allteams.pickle', 'rb') as handle:
	teams = pickle.load(handle)

with open('innings_allteams.pickle', 'rb') as handle:
	team_inn = pickle.load(handle)

all_teams = ['England', 'Australia', 'South Africa', 'West Indies', 'New Zealand' ,'India' ,'Pakistan', 'Sri Lanka'] + ['Afghanistan', 'Bangladesh', 'Canada', 'Ireland', 'Kenya', 'Netherlands', 'Scotland', 'U.A.E.', 'Zimbabwe'] + ['Bermuda', 'Hong Kong', 'Nepal', 'Oman', 'P.N.G.']

team_codes = {i:(all_codes[i], all_teams[i]) for i in range(len(all_teams))}

wt20 = pd.DataFrame(columns = ['team', 'season', 'total_matches', 'number_of_wins', 'number_of_losses'])

for i in range(len(teams)):
	d = teams[i]
	t =  pd.DataFrame(columns = ['team', 'season', 'total_matches', 'number_of_wins', 'number_of_losses'])
	t['team'] = [team_codes[i][1]] * d.shape[0]
	t['season'] = d['Year']
	t['total_matches'] = d['Mat'] - d['Tied'] - d['NR']
	t['number_of_wins'] = d['Won']
	t['number_of_losses'] = d['Lost']
	wt20 = wt20.append(t, ignore_index = True)

w = wt20[[1, 2, 3, 4]].astype(int)
w['team'] = wt20['team']
wt20 = w[['team', 'season', 'total_matches', 'number_of_wins', 'number_of_losses']]

################### Finding runs score, given for each team each year ###################

score_tables = []

for i in range(len(team_inn)):
    d = team_inn[i][['Score', 'Result', 'Opposition', 'Start Date', 'Unnamed: 10']]
    d = d[(d['Result'] == 'won') | (d['Result'] == 'lost')]
    newScore = []
    wickets = []
    for j in d['Score'].tolist():
        if j[0].isdigit():
            if '/' in j:
                newScore.append(int(j.split('/')[0]))
                wickets.append(int(j.split('/')[1]))
            else:
                newScore.append(int(j))
                wickets.append(10)
    d['Score'] = newScore
    
    d.loc[d.Result == 'won', 'Result'] = 1
    d.loc[d.Result == 'lost', 'Result'] = 0
    
    dt = d['Start Date'].apply(lambda x: pd.Series(x.split(' ')))
    d['Start Date'] = dt[2]
    
    op_team = []
    for j in d['Opposition'].tolist():
        op_team.append(j[j.index(' ') + 1 : len(j)])
        
    d['Opposition'] = op_team
    
    
    for j in range(len(all_teams)):
        d.loc[d.Opposition == all_teams[j],'Opposition'] = j
    
    d.columns = ['Score', 'Result', 'Opposition', 'Start Date', 'MatchID']
    
    score_tables.append(d)

for i in score_tables:
    op = i['Opposition']
    mid = i['MatchID']
    opp_runs = []
    for j, k in zip(op, mid):
        x = score_tables[j]
        runs = x[x['MatchID'] == k]['Score'].tolist()[0]
        opp_runs.append(runs)
    i['oppoScore'] = opp_runs

for i in range(len(score_tables)):
    score_tables[i]['Team'] = [i] * len(score_tables[i]['Score'].tolist())

scores = pd.DataFrame(columns = ['Score', 'Result', 'Opposition', 'Start Date', 'MatchID','oppoScore', 'Team'])

for i in score_tables:
    scores = scores.append(i, ignore_index = True)

sc = scores[[0, 5, 6]].astype(int)
sc['Result'] = scores['Result']
sc['Opposition'] = scores['Opposition']
sc['Start Date'] = scores['Start Date']
sc['MatchID'] = scores['MatchID']
scores = sc[['Team', 'Score', 'Opposition','oppoScore', 'Start Date', 'Result', 'MatchID']]

for i in range(len(all_teams)):
    scores.loc[scores['Team'] == i, 'Team'] = all_teams[i]

scores.to_csv('summary.csv', index = False)

#######################################
## Scores had 164 entries, wt20 165, finding that extra entry
scr = pd.read_csv('summary.csv')
scr['Start Date'] = scr['Start Date'].astype('str')
scr['Start Date'] = scr['Start Date'].astype('int')
x = zip(wt20['team'], wt20['season'])
y = zip(scores['Team'], scr['Start Date'])
set(x) - set(y) ## {('West Indies', 2006)}
## As West Indies played 1 match in 2006 and the match was a tie, so total_matches has '0'
#######################################


wt20 = wt20[wt20.total_matches != 0]

runs_scored = scores[['Team', 'Start Date', 'Score']].groupby(['Team', 'Start Date']).agg('sum')
runs_scored = runs_scored.reset_index()

runs_given = scores[['Team', 'Start Date', 'oppoScore']].groupby(['Team', 'Start Date']).agg('sum')
runs_given = runs_given.reset_index()

wt20 = wt20.sort(['team', 'season'], ascending = [True, True])


runs_scored.to_csv('runs_scored.csv', index = False)
runs_given.to_csv('runs_given.csv', index = False)
wt20.to_csv('wt20.csv', index = False)

## Now, manually copying the runs scored, and runs given from the files to the wt20 file

##########################################################################################
###################### Determining the power with smallest error #########################

import math
data = pd.read_csv('wt20.csv')
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

sorted(d.iteritems(), key = lambda (k, v) : (v, k))[0] ## (8.0, 0.16796628889838588)

##########################################################################################