## Motivation

Civic Engagement with Data Science. Inspired by a discussion at a [Code for Nashville](https://github.com/code-for-nashville) brigade meeting. Data from [OpenStates](https://openstates.org).

High level goals:

1. Identify legislation a person might pay attention to given location, interests
2. Summary of a legislator's body of work

## Usage

- Get a API key from [OpenStates]: with https://openstates.org/api/register/
- Put your api key in an environment variable with:

```bash
export OPENSTATESAPIKEY=<your_key>
```

Using and environment variable prevents it from accidentally getting saved and published in the code.

Next, pull data with
```bash
python ./py/pull.py
```

Now, you can open a notebook and the data will be stored in the data directory.
