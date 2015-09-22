import pandas
from datetime import datetime
import matplotlib.pyplot as plt

keys = ['date','ground']

def parse_date(d):
    return datetime.strptime(d, '%d %b %Y')
    
def initial_dataset():
    df = pandas.read_csv('matches.csv')
    df['match_diff'] = df['team_score'] - df['rival_score']
    df['date'] = df['date'].apply(parse_date)
    return df

def joined_dataset(df):
    fields = [f for f in df.columns.get_values() if f not in keys]
    x_fields = [f + "_x" for f in fields]
    y_fields = ["rival_name_y", "team_id_y"]
    select_fields = x_fields + y_fields + keys
    df_joined = df.merge(df, on=keys, how='inner')
    df_fields = df_joined[df_joined.rival_name_y != df_joined.rival_name_x][select_fields]
    to_rename = [(f, f.replace("_x","")) for f in x_fields] + [("rival_name_y", "team_name"), ("team_id_y", "rival_id")]
    df_renamed = df_fields.rename(columns=dict(to_rename))
    return df_renamed


df = initial_dataset()
df = joined_dataset(df)

def last10_average(row):
    last10 = df[df['team_id'] == row['team_id']][df['date'] < row['date']].sort('date',ascending=False).head(10)
    return last10['match_diff'].mean()

def last10_rival_average(row):
    last10_rival = df[df['team_id'] == row['rival_id']][df['date'] < row['date']].sort('date',ascending=False).head(10)
    return last10_rival['match_diff'].mean()

df_last10 = pandas.DataFrame.from_records([{"index": index, "average" : last10_average(row), "average_rival": last10_rival_average(row)} for index, row in df.iterrows()], index="index")
df['last10_avg_diff'] = df_last10['average'] - df_last10['average_rival']


groupedby_result = df.groupby(['result'])['last10_avg_diff']
print groupedby_result.describe()
groupedby_result.plot(kind='hist',bins=30, stacked=True,alpha=0.5, orientation='horizontal')
plt.show()

#df_grouped = df_renamed.sort('date').groupby(['team_id'])
#df_grouped_list = df_grouped['team_id']
#df_grouped['last_10'] = df_grouped.head(10).groupby('team_id')['match_diff'].mean()

