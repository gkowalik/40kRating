"""
@author: GKowalik
"""

import pandas as pd
import numpy as np
import math


#parameters
BOUNTY_WEIGHT = 1
DIFF_WEIGHT = 1




#data import
df_games=pd.read_excel('data\kozlow_test.xlsx')

#df_games['Player1']=df_games['Player1'].str.slice(stop=12)
#df_games['Player2']=df_games['Player2'].str.slice(stop=12)
df_games[['Result']]=df_games[['Result']].fillna(value='10-10')


df_games['P1_Score']=df_games['Result'].str.split(r"-", expand=True)[0].str.extract('(\d+)', expand=False).astype(int)
df_games['P2_Score']=df_games['Result'].str.split(r"-", expand=True)[1].str.extract('(\d+)', expand=False).astype(int)

df_games=df_games.drop(columns=['Table','Result'])

df_games_mirror= df_games.copy()
df_games_mirror['Player1']=df_games['Player2']
df_games_mirror['Player2']=df_games['Player1']

df_games_mirror['P1_Score']=df_games['P2_Score']
df_games_mirror['P2_Score']=df_games['P1_Score']

df_games=df_games.append(df_games_mirror)





results=df_games[['Player1','P1_Score']].groupby(['Player1']).sum()
results=results.sort_values(by=['P1_Score'],ascending=False)
results['Rank_org']=results.rank(ascending=False)
results['Score_std']=(results['P1_Score']-results['P1_Score'].min())/ results['P1_Score'].std()




df_games=df_games.join(results['Score_std'], on='Player1')
df_games=df_games.join(results['Score_std'], on='Player2', rsuffix='_op')


df_games['Expected Score'] = df_games['Score_std'] / (df_games['Score_std'] + df_games['Score_std_op'])*20

df_games['Score diff weighted'] = np.sign(df_games['P1_Score']  - df_games['Expected Score']) * (abs(df_games['P1_Score']  - df_games['Expected Score']) ** DIFF_WEIGHT)  

df_games['Bounty_score'] = (df_games['Score diff weighted'] * df_games['Score_std_op'] ) ** BOUNTY_WEIGHT


df_games.to_excel("outputs/games.xlsx")
  
  
results=results.join(df_games.groupby(['Player1']).sum()['Bounty_score'])
results['Final Score']=results['P1_Score']+results['Bounty_score']

results=results.sort_values(by=['Final Score'],ascending=False)
results['Rank_new']=results['Final Score'].rank(ascending=False)
results['Rank_diff']=results['Rank_org']-results['Rank_new']
#Rating calculation - by points (TODO: By rank)

results.rename(columns={"P1_score": "Raw Score"})


results.to_excel("outputs/ranking.xlsx")

print(results)  








