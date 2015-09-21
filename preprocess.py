import pandas

keys = ['date','ground']
df = pandas.read_csv('matches.csv')
df['match_diff'] = df['team_score'] - df['rival_score']
fields = [f for f in df.columns.get_values() if f not in keys]
x_fields = [f + "_x" for f in fields]
y_fields = ["rival_name_y", "team_id_y"]
select_fields = x_fields + y_fields + keys
df_joined = df.merge(df, on=keys, how='inner')
df_fields = df_joined[df_joined.rival_name_y != df_joined.rival_name_x][select_fields]
to_rename = [(f, f.replace("_x","")) for f in x_fields] + [("rival_name_y", "team_name"), ("team_id_y", "rival_id")]
df_renamed = df_fields.rename(columns=dict(to_rename))
df_grouped = df_renamed.sort('date').groupby(['team_id'])
df_renamed['last_10'] = df_grouped.head(10).groupby('team_id')['match_diff'].mean()
