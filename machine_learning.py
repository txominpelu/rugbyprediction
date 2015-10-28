#!/usr/bin/env python
from __future__ import division
import pandas
from sklearn.ensemble import RandomForestClassifier
import random
from sklearn import tree
from sklearn import cross_validation
import numpy

df = pandas.read_csv('data/matches-spark3.csv',delimiter=";")
df = df.convert_objects(convert_numeric=True)
df.fillna(0, inplace=True)

def see_prediction_precision(result_column):
    clf = RandomForestClassifier(n_estimators=10)
    exclude = ["diff","team_score","rival_score"]
    consider_columns = [k for (k,v) in df.dtypes.to_dict().items() if k <> result_column and not (k in exclude) and v.type in [numpy.int64, numpy.float64, numpy.bool_]]
    print "Using columns: {0}".format(consider_columns)
    target = df[result_column]
    data = df[consider_columns]
    for i in range(0,4):
        X_train, X_test, y_train, y_test = cross_validation.train_test_split(data, target, test_size=0.4, random_state=0)
        clf = clf.fit(X_train, y_train)
        print "Percentage:"
        print clf.score(X_test, y_test)


#print "Prediction b_match_diff"
#see_prediction_precision('b_match_diff')
print "Prediction result"
see_prediction_precision('result')
