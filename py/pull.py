#!/usr/bin/env python

import os
import requests
from zipfile import ZipFile
from io import BytesIO

# Pull legacy (2011-2018) data from OpenStates bulk downloads
if not os.path.exists("data/"):
	os.mkdir('data/')

	request = requests.get('https://data.openstates.org/legacy/csv/tn.zip')

	file = ZipFile(BytesIO(request.content))
	file.extractall('data/')
