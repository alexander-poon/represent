# represent 

Applying Natural Language Processing to extract interesting features from legislation.
Data from [OpenStates](https://openstates.org).

Features will be used in the [Swipe for Rights](https://github.com/coreyar/swipe-for-rights-api)
app, which will:

* Allow users to express support/opposition to legislation  
* Help users understand the content of legislation  
* Provide actionable ways that users can respond to legislation  

## Components

* Topic modeling with bill text
* Predictive modeling for bill outcomes

## Requirements

* An OpenStates API key from https://openstates.org/api/register/, saved as
environment variable `OPENSTATES_API_KEY`
* [pdftools](https://www.xpdfreader.com/download.html) to extract bill text

## Setup

Create a conda environment and install required packages:

`$ conda env create -f environment.yml`

Activate the environment:

`$ conda activate represent`

This should be sufficient to run the scripts in `py/` and notebooks in `notebooks/`.

Deactivate the conda environment:

`$ conda deactivate`

Remove the conda environment:

`$ conda env remove --name represent`
