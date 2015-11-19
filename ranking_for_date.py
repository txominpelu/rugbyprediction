#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import requests
import difflib
import time
import functools
from repoze.lru import lru_cache



df = pd.read_csv("data/matches-spark3.csv",delimiter=";")

def ranked_matches(df, team_id):
    return df[df['team_id'] == team_id].sort(['date_t'])[df['date_t'] >= '2003-10-06'].T.values

def teams(date):
    r = requests.get("http://cmsapi.pulselive.com/rugby/rankings/mru?date={date}&client=pulse".format(date=date)).json()
    time.sleep(0.01)
    return [f['team'] for f in  r['entries']]

@lru_cache(maxsize=1024)
def date_ranking(date):
    try:
        r = requests.get("http://cmsapi.pulselive.com/rugby/rankings/mru?date={date}&client=pulse".format(date=date)).json()
        return r
    except:
        return []
	
def ranking_on_date(team_id, date):
    print "Ranking for {0} on {1}".format(team_id, date)
    r = date_ranking(date)
    return [f for f in r['entries'] if f['team']['id'] == team_id]

    

def closest_match(x, elem): 
    closest = difflib.get_close_matches(x, elem)
    return closest[0] if len(closest) > 0 else None

def get_ranking(merged, id, date):
    t = merged[merged['team_id'] == id].to_dict()
    if len(t['id'].values()) > 0:
	r = ranking_on_date( t['id'].values()[0], date)
	if len(r) > 0:
            return r[0]['previousPts']
        return None
    else:
	return None
    
if __name__ == '__main__':
    df1 = df[['team_id', 'team_name']].drop_duplicates()
    df2 = pd.DataFrame.from_dict(teams('2015-11-18'))
    df2['team_name'] = df2['name'].map(lambda x: closest_match(x, df1['team_name']))
    merged = pd.merge(df1, df2)
    merged.to_csv("data/teams.csv")
    ranked = df[df['date_t'] >= '2003-10-06']
    ranked['team_ranking'] = ranked.apply(lambda row: get_ranking(merged, row['team_id'], row['date']), axis=1) 
    ranked['rival_ranking'] = ranked.apply(lambda row: get_ranking(merged, row['rival_id'], row['date']), axis=1) 
    print ranked
    ranked.to_csv("data/matches-ranked.csv", sep=";")
