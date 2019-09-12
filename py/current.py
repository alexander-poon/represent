#!/usr/bin/env python

import os
import re
import requests
import pandas as pd
from glob import glob
from pyopenstates import search_bills

# current := 111st- legislative sessions (2019-)
print('Downloading data from OpenStates...')

current = pd.DataFrame(search_bills(state='tn', search_window='session:111')) \
	.query('bill_id.str.contains("SB|HB")', engine='python') \
	.reset_index(drop=True)

current['session'] = current['session'].astype(int)

# Remove the 'Amends TCA Title x, Chapter y' from bill titles
current['title'] = current['title'].str.replace(' - $', '')
current['title'] = current['title'].str.replace(' - Amends.+$', '')

# Sponsors for each bill is a list of dictionaries
sponsors = [[sponsor.get('name') for sponsor in d] for d in current['sponsors']]

current['sponsors'] = sponsors

# Look for bills meeting outcomes of interest
print('Extracting bill outcomes...')

actions = pd.DataFrame()

for index, row in current.iterrows():
	actions = pd.concat([
		actions,
		pd.DataFrame(row['actions']).assign(bill_id=row['bill_id'], session=row['session'])
	])


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

# Full Text
print('Downloading and extracting bill text...')

if not os.path.exists('data/text/111th'):
	os.mkdir('data/text/111th')

# versions is a series of dicts with a link to pdf of bill text
urls = [v.get('url') for d in current['versions'] for v in d]

for url in urls:
	bill = re.search('[H|S]B[0-9]{4}', url).group(0)

	# Download pdf
	if not os.path.exists(f'data/text/111th/{bill}.txt'):
		response = requests.get(url)

		with open(f'data/text/111th/{bill}.pdf', 'wb') as f:
			f.write(response.content)

		# Convert to txt
		os.system(f'pdftotext data/text/111th/{bill}.pdf')

# Read text
path = glob('data/text/111th/*.txt')

text = []

for file in path:
	with open(file, encoding="Latin_1") as f:
		text.append({
			'session': re.search('[0-9]{3}th', file).group(0),
			'bill_id': re.search('[H|S]B[0-9]{4}', file).group(0),
			'text': f.read()
		})

text = pd.DataFrame(text)

# Regex patterns
patterns = [
	'-[0-9]+-',
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

current[['session', 'bill_id', 'title', 'subjects', 'sponsors']] \
	.drop_duplicates(['session', 'bill_id', 'title']) \
	.merge(text, how='left', on=['session', 'bill_id'], validate='1:1') \
	.merge(committee, how='left', on=['session', 'bill_id'], validate='1:1') \
	.merge(uncontroversial, how='left', on=['session', 'bill_id'], validate='1:1') \
	.merge(voted_down, how='left', on=['session', 'bill_id'], validate='1:1') \
	.merge(passed, how='left', on=['session', 'bill_id'], validate='1:1') \
	.merge(unanimous, how='left', on=['session', 'bill_id'], validate='1:1') \
	.merge(did_not_sign, how='left', on=['session', 'bill_id'], validate='1:1') \
	.sort_values(['session', 'bill_id']) \
	.to_json('data/current.json', orient='records')

print('Done!')
