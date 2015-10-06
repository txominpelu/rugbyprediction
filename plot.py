
import pandas
from matplotlib import pyplot

df = pandas.read_csv('data/ground_matches.csv')
df['team_last10_avg_diff'].fillna(0,inplace=True)
df['team_last10_avg_diff'].astype(int)
pyplot.xcorr(df['match_diff'], df['team_last10_avg_diff'], maxlags=99)
pyplot.show()
