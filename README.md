## Civic Engagement with Data Science

Search and recommendation and predictive models for state legislation. Inspired
by a discussion at a [Code for Nashville](https://github.com/code-for-nashville)
brigade meeting. Data from [OpenStates](https://openstates.org).

Using the OpenStates API requires an API key from
https://openstates.org/api/register/.

**Setup (conda)**

Create a conda environment and install required packages:

`$ conda env create -f environment.yml`

Activate the environment:

`$ conda activate legisPy`

Pull data from OpenStates bulk downloads:

`$ python py/pull.py`

This should be sufficient to run the scripts in `py/` and notebooks in
`notebooks/`.

To deactivate the conda environment:

`$ conda deactivate`

To remove the conda environment:

`$ conda env remove --name legisPy`

**Setup (virtualenv w/ python >= 3.6)**

Create a virtual environment in `~/.virtualenvs`:

`$ virtualenv ~/.virtualenvs/legisPy`

Activate the virtualenv:

`$ source ~/.virtualenvs/legisPy/bin/activate`

Install required packages:

`$ pip install -r requirements.txt`

Pull data from OpenStates bulk downloads:

`$ python py/pull.py`

This should be sufficient to run the scripts in `py/` and notebooks in
`notebooks/`.

Deactivate the virtualenv:

`$ deactivate`

Delete the virtualenv:

`$ rm -r ~/.virtualenvs/legisPy`
