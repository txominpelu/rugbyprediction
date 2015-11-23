#!/usr/bin/env python
# coding: utf-8

from __future__ import division
import pandas as pd
import requests
import difflib
import time
import functools
import math
from repoze.lru import lru_cache
from pyrsistent import freeze, thaw




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


INITIAL_DATE='2013-10-06'

def get_initial_ranking():
    df = pd.DataFrame.from_dict(date_ranking(INITIAL_DATE)['entries'])
    df['team'] = df['team'].map(lambda x: x['name'])
    return df
 
def add_team_id(teams_df, initial_ranking_df):
    initial_ranking_df['team_name'] = initial_ranking_df['team'].map(lambda x: closest_match(x, teams_df['team_name']))
    return pd.merge(initial_ranking_df, teams_df, on = "team_name")
    

def exchange(home_ranking, away_ranking, diff):
    gap = (home_ranking + 3) - away_ranking
    if diff > 0:
        return max(min(1 - (gap / 10), 2), 0)
    elif diff == 0:
        return max(- min((gap / 10), 1), -1)
    else:
        return max(min(-1 - (gap / 10), 0), -2)

def next_ranking_home(home_ranking, away_ranking, diff):
    """ Gets the next ranking for the home team after the current match

    >>> next_ranking_home(76.92,76.36,2) 
    77.564
    >>> next_ranking_home(76.92,76.36,16) 
    77.886
    >>> next_ranking_home(76.92,76.36,0) 
    76.564
    >>> next_ranking_home(76.92,76.36,-2) 
    75.564
    >>> next_ranking_home(76.92,76.36,-16) 
    74.886
    """
    factor = 1 if math.fabs(float(diff)) < 15 else 1.5
    return round(home_ranking + (factor * exchange(home_ranking, away_ranking, diff)), 3)
    
def next_ranking_away(home_ranking, away_ranking, diff):
    """ Gets the next ranking for the home team after the current match

    >>> next_ranking_away(76.92,76.36,-15) 
    78.394
    >>> next_ranking_away(76.92,76.36,-2) 
    77.716
    >>> next_ranking_away(76.92,76.36,0) 
    76.716
    >>> next_ranking_away(76.92,76.36,2) 
    75.716
    >>> next_ranking_away(76.92,76.36,15) 
    75.394
    """
    factor = 1 if abs(diff) < 15 else 1.5
    return  round(away_ranking - (factor * exchange(home_ranking, away_ranking, diff)), 3)
        
def step(context, m):
    """ Updates the new ranking after the match for both teams
    
    >>> context = freeze({'rankings': { 1: 76.92, 2: 76.36 } , 'matches': []})
    >>> match = {'home_id': 1, 'away_id': 2, 'diff': 2, 'league':1 , 'gameId': 2}
    >>> thaw(step(context, match)) == {'rankings': {1: 77.564, 2: 75.716}, 'matches': [{'league': 1, 'gameId':2, 'home_ranking': 76.92, 'away_ranking': 76.36}]}
    True
    >>> match = {'home_id': 1, 'away_id': 2, 'diff': -2, 'league':1 , 'gameId': 2}
    >>> thaw(step(context, match)) == {'rankings': {1: 75.564, 2: 77.716}, 'matches': [{'league': 1, 'gameId':2, 'away_ranking': 76.36, 'home_ranking': 76.92}]}
    True
    """
    m['home_ranking'] = context['rankings'][m['home_id']]
    m['away_ranking'] = context['rankings'][m['away_id']]
    next_team = next_ranking_home(m['home_ranking'], m['away_ranking'], m['diff'])
    next_rival = next_ranking_away(m['home_ranking'], m['away_ranking'], m['diff'])
    match = dict([(i, m[i]) for i in ['league', 'gameId', 'home_ranking', 'away_ranking']])
    context = context.transform(('rankings',m['home_id']), next_team) \
                     .transform(('rankings',m['away_id']), next_rival) \
                     .set('matches', context['matches'].append(freeze(match)))
    return context
   
    
def match_rankings(unique_matches_list, teams_initial_rankings):
    r = reduce(step, unique_matches_list, freeze({'rankings':teams_initial_rankings, 'matches': []}))
    return thaw(r['matches'])

if __name__ == '__main__':
    matches_df = pd.read_csv("data/matches-spark3.csv",delimiter=";").convert_objects(convert_numeric=True)
    teams_df = pd.concat([matches_df.rename(columns={'home_id': 'team_id'})[['team_id']], matches_df.rename(columns={'away_id': 'team_id'})[['team_id']]]).drop_duplicates()
    teams_df['ranking'] = 30
    rankings = teams_df.groupby('team_id')['ranking'].first().to_dict()
    #initial_ranking_df = get_initial_ranking()
    #merged = add_team_id(teams_df, initial_ranking_df)

    unique_matches_list = matches_df.groupby(['gameId','league']).first().reset_index().sort('date_t').to_dict('records')
    match_rankings_df = pd.DataFrame(match_rankings(unique_matches_list, rankings))
    pd.merge(matches_df, match_rankings_df, on=["gameId","league"]).to_csv('data/matches-with-ranking.csv',sep=';')
    #ranked = df[df['date_t'] >= '2003-10-06']
    #ranked['team_ranking'] = ranked.apply(lambda row: get_ranking(merged, row['team_id'], row['date']), axis=1) 
    #ranked['rival_ranking'] = ranked.apply(lambda row: get_ranking(merged, row['rival_id'], row['date']), axis=1) 
    #print ranked
    #ranked.to_csv("data/matches-ranked.csv", sep=";")

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
