import pandas

df = pandas.read_csv('matches.csv')
df_joined = df.merge(df, on=['date','ground'], how='inner')
