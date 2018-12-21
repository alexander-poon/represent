## Motivation

Civic Engagement with Data Science. Inspired by a discussion at a [Code for Nashville](https://github.com/code-for-nashville) brigade meeting. Data from [OpenStates](https://openstates.org).

High level goals:

1. Identify legislation a person might pay attention to given location, interests
2. Summary of a legislator's body of work

## Usage
One way to make sure you have all the dependencies is to use [Pipenv],
which reads `Pipfile` and checks `Pipfile.lock` at the top of this repo.

If you haven't installed [Pipenv], then use their [instructions].

Then run:
```bash
pipenv install
pipenv shell
jupyter notebook
```
This will install your dependencies, start a virtual environment and a notebook.
Anything you run in the [Pipenv] shell (virtual environment) including jupyter
will have access to all your dependencies.

---

[Pipenv]: https://pipenv.readthedocs.io/
[instructions]: https://pipenv.readthedocs.io/en/latest/#install-pipenv-today
