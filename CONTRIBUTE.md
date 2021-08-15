# How to contribute

##### How to run the project locally

The project is using pipenv, to install the dependencies you can use:

```bash
python -m pip install --upgrade pip
python -m pip install --upgrade pipenv
```

To install the project in a virtual environment and all its dependencies you can use:

```bash
pipenv install --dev
```

In order to test that everything works you can use:

```
pipenv run auto-tag --help
```
You should see the help message for the CLI tool.


In order to run the CI checks you can look at [this pipeline](./.github/workflows/python-ci.yml) but the main checks can be run with:

```
pipenv run pylint --rcfile=.pylintrc auto_tag # to run PyLint
pipenv run mypy auto_tag                      # to run the type checking
pipenv run pytest --cov=auto_tag              # to run the tests
```

In CI we are running again multiple python version so in the end this is the most reliable way to see all the resets.


#### How to open a PR or an Issue

For both Pull Requests and Issue's we have templates that should guide you though the decimation process.
Pull Requests will usually be reviews only if the CI is passing but Issues will be addresses on a best effort basis.
