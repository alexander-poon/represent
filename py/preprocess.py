#!/usr/bin/env python

"""
Common pre-processing for bill titles and text:

1) Tokenize
2) Lemmatize
3) Remove Punctuation and Stopwords
4) Entity Recognition (TODO)

The result is a list of lists, where each sublist represents word tokens for
each bill.

This can then be turned into a Bag of Words/TF-IDF/Vector representation and
passed to a topic model, predictive model, etc.
"""

import pandas as pd
import spacy

# TODO: Ensure dependencies are run before loading
legacy = pd.read_json('data/legacy.json')
current = pd.read_json('data/current.json')

bills = pd.concat([legacy, current], ignore_index=True, sort=False)

# Use spaCy annotator
nlp = spacy.load('en_core_web_sm')

# TODO: Label entities, then apply a custom spaCy model to extract entities from corpus
# https://spacy.io/api/annotation#named-entities
# ents = []
#
# for doc in nlp.pipe(bills['title'] + bills['text'], batch_size=50):
# 	ents.append([
# 		e.text.lower() for e in doc.ents
# 		if e.text.isalpha() and e.label_ in ['PERSON', 'NORP', 'FAC', 'ORG', 'GPE', 'LOC', 'EVENT']
# 	])

stop = list(nlp.Defaults.stop_words) + [
	'introduced', 'enacts', 'enacted', 'requires',
	'tennessee', 'code', 'annotated', 'act', 'relative', 'whereas',
	'chapter', 'part', 'section', 'subsection', 'subdivision', 'entirety', 'title',
	'amend', 'amends', 'amended', 'deleting', 'substituting', 'instead', 'following',
	'adding', 'new', 'appropriately', 'designated', 'language', 'purpose',
	'take', 'effect', 'upon', 'becoming', 'law', 'welfare', 'require',
	'shall', 'means', 'construe'
]

tokens = []

# Keep tokens conditional on part of speech
# https://spacy.io/api/annotation#pos-tagging
# Drop stopwords and tokens with non-word characters
for doc in nlp.pipe(bills['title'] + bills['text'], batch_size=50):

	sublist = []

	for token in doc:
		if token.is_alpha and token.pos_ in ['NOUN', 'VERB', 'PROPN'] and token.lower_ not in stop:
			sublist.append(token.lemma_)

	tokens.append(sublist)

pd.Series(tokens).to_json('data/tokens.json')
