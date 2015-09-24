# %load machine_learning.py
import pandas
from sklearn.ensemble import RandomForestClassifier
import random

df = pandas.read_csv('data/ground_matches.csv')
df['team_last10_avg_diff'].fillna(0, inplace=True)
df['rival_last10_avg_diff'].fillna(0, inplace=True)
rows = random.sample(df.index, 30)

df_30 = df.ix[rows]
df_70 = df.drop(rows)

clf = RandomForestClassifier(n_estimators=10)
consider_columns = ['team_last10_avg_diff','rival_last10_avg_diff','home_match']
df_70_nt = df_70[consider_columns]
df_30_nt = df_30[consider_columns]

df_70_t = df_70['result']
clf = clf.fit(df_70_nt, df_70_t)

def draw_decission_tree():
    from sklearn import tree
    tree.export_graphviz(clf,
    clf2 = tree.DecisionTreeClassifier()
    tree.export_graphviz(clf,
    ...     out_file='tree.dot')
    clf2 = clf2.fit(df_70_nt, df_70_t)
    tree.export_graphviz(clf2,
    ...     out_file='tree.dot')
    predictions = clf.predict(df_30_nt)

results = [i for i in df_30['result']]
from __future__ import division
len ([(a,b) for (a,b) in zip(results, predictions) if a == b]) / len(predictions)
