#!/usr/bin/env python

import os
import re
import requests
import pandas as pd
from glob import glob
from io import BytesIO
from zipfile import ZipFile

# Pull legacy (2011-2018) data from OpenStates bulk downloads
print('Downloading data from OpenStates...')

if not os.path.exists('data/legacy'):
	os.mkdir('data/legacy')

	request = requests.get('https://data.openstates.org/legacy/csv/tn.zip')

	file = ZipFile(BytesIO(request.content))
	file.extractall('data/legacy')

# legacy := 107th-110th legislative sessions (2011-18)
legacy = pd.read_csv('data/legacy/tn_bills.csv') \
	.query('type == "bill"') \
	.reset_index(drop=True)

# Remove the 'Amends TCA Title x, Chapter y' from bill titles
legacy['title'] = legacy['title'].str.replace(' - $', '')
legacy['title'] = legacy['title'].str.replace(' - Amends.+$', '')

# Convert subjects to list
legacy['subjects'] = legacy['subjects'].str.split('|')
legacy['subjects'].fillna('', inplace=True)

# Add bill sponsors
sponsors = pd.read_csv('data/legacy/tn_bill_sponsors.csv') \
	.groupby(['session', 'bill_id'])['name'] \
	.agg(lambda x: list(x)) \
	.reset_index() \
	.rename(columns={'name': 'sponsors'})

# Look for bills meeting outcomes of interest
print('Extracting bill outcomes...')

actions = pd.read_csv('data/legacy/tn_bill_actions.csv') \
	.dropna(subset=['action'])


def search_actions(strings):
	"""
	Search actions meeting one of a list of patterns. Strings passed as a list
	are concatenated and used as a regex.

	Returns a DataFrame with bills passing stage specified by string.
	"""
	pattern = '|'.join(strings)

	b = actions[actions.action.str.contains(pattern)] \
		.loc[:, ['session', 'bill_id']] \
		.drop_duplicates()

	return b


# Passing all committees
patterns = [
	'H. Placed on Regular Calendar', 'H. Placed on Consent Calendar',
	'Placed on Senate Consent Calendar', 'Placed on Senate Regular Calendar'
]

committee = search_actions(patterns).assign(committee=True)

# Considered Uncontroversial
patterns = ['H. Placed on Consent Calendar', 'Placed on Senate Consent Calendar']

uncontroversial = search_actions(patterns).assign(uncontroversial=True)

# Voted-down := Failed house or senate vote at least once
patterns = ['Failed to pass H.', 'Failed to pass Senate']

voted_down = search_actions(patterns).assign(voted_down=True)

# Passed
patterns = ['Signed by Governor', 'Returned by Governor without signature']

passed = search_actions(patterns).assign(passed=True)

# Unanimous := Pass by all-0 vote on first attempt in both houses
actions['nays'] = pd.to_numeric(actions['action'].str.extract('Nays ([0-9]+)', expand=False))
actions['unanimous'] = pd.Series(actions['nays'] == 0)

patterns = ['Failed to pass H.', 'Failed to pass Senate', 'Passed H.', 'Passed Senate', 'Passed S.']

unanimous = actions[actions['action'].str.contains('|'.join(patterns))] \
	.groupby(['session', 'bill_id']) \
	.agg({'unanimous': 'min'}) \
	.reset_index(drop=False)

# Vetoed or Governor did not sign
patterns = ['Vetoed by Governor.', 'Returned by Governor without signature']

did_not_sign = search_actions(patterns).assign(did_not_sign=True)

# TODO: Pull text from scratch
# Full Text
print('Downloading and extracting bill text...')

path = glob('data/text/*/*.txt')

text = []

for file in path:
	with open(file, encoding="Latin_1") as f:
		text.append({
			'session': re.search('[0-9]{3}th', file).group(0),
			'bill_id': re.search('[H|S]B[0-9]{4}', file).group(0),
			'text': f.read()
		})

text = pd.DataFrame(text)

# Boilerplate Regex patterns
patterns = [
	'- ?[0-9]+ ?-',
	'[H|S]B[0-9]{4}',
	'[0-9]{6,8}',
	'\\([0-9]+\\)',
	'\\([A-Za-z]\\)',
	'SECTION [0-9]+\\.',
	'BE IT ENACTED BY THE GENERAL ASSEMBLY OF THE STATE OF TENNESSEE:',
	'SENATE BILL [0-9]{1,4} By ([A-Za-z]+) ?[A-Z]?',
	'HOUSE BILL [0-9]{1,4} By ([A-Za-z]+) ?[A-Z]?',
	'\\<BillNo\\>',
	'\\<Sponsor\\>'
]

# Some cleaning to remove boilerplate and line breaks
text['text'] = text['text'] \
	.str.replace('|'.join(patterns), '') \
	.str.replace('\\s{1,}', ' ') \
	.str.strip() \
	.str.replace('^AN ACT', 'An act') \
	.str.replace(' This act shall take effect .+, the public welfare requiring it\\.', '')

text['session'] = text['session'].str.replace('th', '').astype(int)

# Change bill ids represented as HB0001 to HB 1 to match OpenStates format
text['bill_id'] = \
	text['bill_id'].str.extract('([H|S]B)', expand=False) + ' ' + \
	text['bill_id'].str.extract('([0-9]{4})', expand=False).astype(int).astype(str)

# Combine features and export as json
print('Writing output...')

legacy[['session', 'bill_id', 'title', 'subjects']] \
	.merge(text, how='left', on=['session', 'bill_id'], validate='1:1') \
	.merge(sponsors, how='left', on=['session', 'bill_id'], validate='1:1') \
	.merge(committee, how='left', on=['session', 'bill_id'], validate='1:1') \
	.merge(uncontroversial, how='left', on=['session', 'bill_id'], validate='1:1') \
	.merge(voted_down, how='left', on=['session', 'bill_id'], validate='1:1') \
	.merge(passed, how='left', on=['session', 'bill_id'], validate='1:1') \
	.merge(unanimous, how='left', on=['session', 'bill_id'], validate='1:1') \
	.merge(did_not_sign, how='left', on=['session', 'bill_id'], validate='1:1') \
	.sort_values(['session', 'bill_id']) \
	.to_json('data/legacy.json', orient='records')

print('Done!')
