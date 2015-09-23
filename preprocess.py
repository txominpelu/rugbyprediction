import pandas
from datetime import datetime
from city2country import *

keys = ['date','ground']
data_folder = 'data'

def parse_date(d):
    return datetime.strptime(d, '%d %b %Y')

def remove_v(s):
    return s.replace("v ","")
    
def initial_dataset():
    df = pandas.read_csv('{0}/matches.csv'.format(data_folder))
    df['match_diff'] = df['team_score'] - df['rival_score']
    df['date'] = df['date'].apply(parse_date)
    df['rival_name'] = df['rival_name'].apply(remove_v)
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



def last10_average(df,row):
    last10 = df[df['team_id'] == row['team_id']][df['date'] < row['date']].sort('date',ascending=False).head(10)
    return last10['match_diff'].mean()

def last10_rival_average(df,row):
    last10_rival = df[df['team_id'] == row['rival_id']][df['date'] < row['date']].sort('date',ascending=False).head(10)
    return last10_rival['match_diff'].mean()

def add_average_last10(df):
    df_last10 = pandas.DataFrame.from_records([{"index": index, "average" : last10_average(df,row), "average_rival": last10_rival_average(df,row)} for index, row in df.iterrows()], index="index")
    df['team_last10_avg_diff'] = df_last10['average'] 
    df['rival_last10_avg_diff'] = df_last10['average_rival'] 
    return df

def step1():
    df = initial_dataset()
    df = joined_dataset(df)
    df = add_average_last10(df)
    df.to_csv("{0}/proc_matches.csv".format(data_folder))

def step2():
    df = pandas.read_csv("{0}/proc_matches.csv".format(data_folder))
    df = df[0:100]
    df['ground_country'] = df[['rival_name','team_name','ground']].apply(which_country, axis=1)
    df['home_match'] = df['ground_country'] == df['team_name']
    df.to_csv("{0}/ground_matches.csv".format(data_folder))

#step1()
step2()

