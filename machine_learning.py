#!/usr/bin/env python
from __future__ import division
import pandas
from sklearn.ensemble import RandomForestClassifier
import random
from sklearn import tree
from sklearn import cross_validation
import numpy
from sklearn.grid_search import GridSearchCV, RandomizedSearchCV
from time import time
from operator import itemgetter
from scipy.stats import randint as sp_randint
import numpy as np
import math

def or_equal(m, field, other_field):
    return m[field] if not math.isnan(m[field]) else m[other_field]


#df = pandas.read_csv('data/matches-ranked.csv',delimiter=";")
df = pandas.read_csv('data/matches-spark3.csv',delimiter=";")
df = df.convert_objects(convert_numeric=True)
#df['rival_ranking'] = df.apply(lambda x:or_equal(x,'rival_ranking','team_ranking'), axis=1)
#df['team_ranking'] = df.apply(lambda x:or_equal(x,'team_ranking','rival_ranking'), axis=1)
#df['ranking_diff'] = df['team_ranking'] - df['rival_ranking']
df.fillna(None, inplace=True)

    
# Utility function to report best scores
def report(grid_scores, n_top=3):
    top_scores = sorted(grid_scores, key=itemgetter(1), reverse=True)[:n_top]
    for i, score in enumerate(top_scores):
        print("Model with rank: {0}".format(i + 1))
        print("Mean validation score: {0:.3f} (std: {1:.3f})".format(
              score.mean_validation_score,
              np.std(score.cv_validation_scores)))
        print("Parameters: {0}".format(score.parameters))
        print("")


# specify parameters and distributions to sample from
param_dist = {"max_depth": [3, 8, 15, 20, None],
              "max_features": sp_randint(1, 20),
              "min_samples_split": sp_randint(1, 30),
              "min_samples_leaf": sp_randint(1, 30),
              "bootstrap": [True, False],
              "criterion": ["gini", "entropy"]}

def see_prediction_precision(result_column):
    clf = RandomForestClassifier(n_estimators=10)
    exclude = ["diff","team_score","rival_score","htf","hta", 'team_ranking', 'rival_ranking']
    consider_columns = [k for (k,v) in df.dtypes.to_dict().items() if k <> result_column and not (k in exclude) and v.type in [numpy.int64, numpy.float64, numpy.bool_]]
    print "Using columns: {0}".format(consider_columns)
    target = df[result_column]
    data = df[consider_columns]
    # run randomized search
    n_iter_search = 40
    random_search = RandomizedSearchCV(clf, param_distributions=param_dist, n_iter=n_iter_search)
    
    start = time()
    random_search.fit(data, target)
    print("RandomizedSearchCV took %.2f seconds for %d candidates"
          " parameter settings." % ((time() - start), n_iter_search))
    report(random_search.grid_scores_)

    #scores = cross_validation.cross_val_score(clf, data, target, cv=5)
    #print scores
    #KF = cross_validation.KFold(len(data), n_folds=5)
    #for train, test in KF:
    #   clf.fit(data.as_matrix()[train], target.as_matrix()[train])
    #   print "Percentage:"
    #   print clf.score(data.as_matrix()[test], target.as_matrix()[test])


#print "Prediction b_match_diff"
#see_prediction_precision('b_match_diff')
print "Prediction result"
see_prediction_precision('result')
