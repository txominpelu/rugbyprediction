#!/usr/bin/env python
from __future__ import division
import pandas
from sklearn.ensemble import RandomForestClassifier
import random
from sklearn import tree
from sklearn import cross_validation

df = pandas.read_csv('data/ground_matches.csv')
df['team_last10_avg_diff'].fillna(0, inplace=True)
df['rival_last10_avg_diff'].fillna(0, inplace=True)
df['team_last10_avg_same_match_diff'].fillna(0, inplace=True)
df['team_last10_avg_reverse_match_diff'].fillna(0, inplace=True)

def sample(percent):
    rows = random.sample(df.index, percent)
    df_30 = df.ix[rows]
    df_70 = df.drop(rows)
    return (df_30, df_70)

def draw_decission_tree():
    clf2 = tree.DecisionTreeClassifier()
    tree.export_graphviz(clf2, out_file='tree.dot')


df_30, df_70 = sample(30)

def see_prediction_precision(result_column):
    clf = RandomForestClassifier(n_estimators=10)
    consider_columns = ['team_last10_avg_diff','rival_last10_avg_diff','home_match','team_last10_avg_same_match_diff', 'team_last10_avg_reverse_match_diff'] 
    #consider_columns = ['team_last10_avg_diff','rival_last10_avg_diff','home_match'] 
    target = df[result_column]
    data = df[consider_columns]
    for i in range(0,4):
        X_train, X_test, y_train, y_test = cross_validation.train_test_split(data, target, test_size=0.4, random_state=0)
        clf = clf.fit(X_train, y_train)
        print "Percentage:"
        print clf.score(X_test, y_test)

	#print "Failed at:"
	#print "Tested for:"
	#prediction = clf.predict(X_test)
	#X_test['result'] = y_test
	#X_test['prediction'] = prediction
	#print X_test

print "Prediction b_match_diff"
see_prediction_precision('b_match_diff')
print "Prediction result"
see_prediction_precision('result')
