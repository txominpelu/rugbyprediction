# coding: utf-8
import pandas as pd
import numpy as np

import argparse

def columns(home):
  team_columns = ['id','name','logo']
  df2 = df.drop_duplicates(subset=['{0}_id'.format(home)])[['{0}_{1}'.format(home,i) for i in team_columns]]
  return df2.rename(columns=dict([("{0}_{1}".format(home,c),c) for c in team_columns]))

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument("matchesfile", help="file with a list of matches that we well use to extract the existent teams")
  parser.add_argument("outputfile", help="file where the result will be saved")
  args = parser.parse_args()
  df = pd.read_csv(args.matchesfile,",")
  away_teams = columns('away')
  home_teams = columns('home')
  all_teams = pd.concat([away_teams,home_teams]).drop_duplicates(subset=['id'])
  all_teams.to_csv(args.outputfile,index=False)
