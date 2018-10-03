#!/usr/bin/env python

from pyopenstates import *
from ratelimiter import RateLimiter
import pandas as pd

set_api_key('') # Get key here: https://openstates.org/api/register/

bills_request = search_bills(state='tn', fields=['session', 'id', 'bill_id', 'title', 'sponsors', 'type', 'subjects'])

# Keep only bills (dropping resolutions)
bills = pd.DataFrame(bills_request).query('bill_id.str.contains("SB|HB")', engine='python')

# Some columns are lists: extract or concatenate when list has multiple entries
bills['type'] = bills['type'].apply(lambda x: ''.join(x))
bills['subjects'] = bills['subjects'].apply(lambda x: '; '.join(x))

# Sponsors is a list of dictonaries with some missingness
sponsors = []

for i in range(len(bills)):
    try:
        sponsors.append('; '.join([d.get('name') for d in bills['sponsors'][i]]))
    except KeyError:
        sponsors.append('')
        
bills['sponsors'] = sponsors

bills.reset_index(inplace=True, drop=True)

bills[['bill_id', 'id', 'session', 'subjects', 'title', 'sponsors']].to_csv('../data/bills.csv', index=False)

# Avoid hitting API limits
rate_limiter = RateLimiter(max_calls=10, period=1)

actions = pd.DataFrame()

for s, bill in zip(bills['session'], bills['bill_id']):
    try:
        with rate_limiter:
            actions = pd.concat(
                [actions,
                 pd.DataFrame(get_bill(state='tn', term=s, bill_id=bill).get('actions'))
                    .assign(bill_id=bill, session=s)]
            )
    except:
        print(str(s) + ' ' + bill)
        continue

# Type column is a list: extract or concatenate when list has multiple entries
actions['type'] = actions['type'].apply(lambda x: '; '.join(x))
actions.reset_index(inplace=True, drop=True)

# Missing some vote tallies; will add these from action
actions['ayes'] = pd.to_numeric(actions['action'].str.extract('Ayes ([0-9]+)', expand=False))
actions['nays'] = pd.to_numeric(actions['action'].str.extract('Nays ([0-9]+)', expand=False))

actions[['action', 'actor', 'session', 'bill_id', 'type', 'ayes', 'nays']].to_csv('../data/actions.csv', index=False)
