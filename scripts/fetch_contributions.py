"""Fetch GitHub public/authorized contribution calendar through the official GraphQL API.

Usage:
  GH_TOKEN=... python scripts/fetch_contributions.py

Never put a token in the repository. The token's access to nonpublic counts and
GitHub's user privacy settings determine what is available. No repository names
or private code are requested/stored. The existing JSON file is not overwritten
on network errors.
"""
from __future__ import annotations
import datetime as dt
import json
import os
from pathlib import Path
import urllib.error
import urllib.request

ROOT=Path(__file__).resolve().parents[1]
QUERY='''query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount } }
      }
    }
  }
}'''


def fetch(login:str,token:str):
    body=json.dumps({'query':QUERY,'variables':{'login':login}}).encode('utf-8')
    req=urllib.request.Request('https://api.github.com/graphql',data=body,headers={
        'Authorization':'Bearer '+token,
        'Accept':'application/vnd.github+json',
        'Content-Type':'application/json',
        'User-Agent':'github-profile-v2-generator'
    },method='POST')
    with urllib.request.urlopen(req,timeout=30) as resp:
        result=json.load(resp)
    if result.get('errors'):
        raise RuntimeError('GitHub GraphQL returned an error: '+json.dumps(result['errors'])[:350])
    calendar=result['data']['user']['contributionsCollection']['contributionCalendar']
    items=[]
    for week in calendar['weeks']:
        for d in week['contributionDays']:
            items.append({'date':d['date'],'count':d['contributionCount']})
    if not items:
        raise RuntimeError('Empty contribution calendar; refusing to overwrite last data')
    return {
        'status':'ok',
        'source':'GitHub GraphQL contributionsCollection.contributionCalendar',
        'username':login,
        'fetched_at_utc':dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds'),
        'total_contributions':calendar['totalContributions'],
        'days':items
    }


def main():
    token=os.environ.get('GH_TOKEN') or os.environ.get('GITHUB_TOKEN')
    if not token:
        raise SystemExit('GH_TOKEN or GITHUB_TOKEN required. No changes made.')
    profile=json.loads((ROOT/'content/profile.json').read_text(encoding='utf-8'))
    data=fetch(profile['github_username'],token)
    dest=ROOT/'data/contributions.json'
    dest.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('Fetched',len(data['days']),'days for',data['username'])


if __name__=='__main__':
    main()
