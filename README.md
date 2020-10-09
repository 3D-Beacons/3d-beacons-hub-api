# 3D Beacons Hub API
3D Beacons Hub API is a programmatic way to obtain information of available experimental and theoretical models for a protein of interest.

## Getting Started
These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites
Below are the list of softwares/tools for the utilities to properly run in the environment.

Python 3.7+

**Note**

Because [Python 2.7 supports ended January 1](https://pythonclock.org/), 2020, new projects should consider supporting Python 3 only, which is simpler than trying to support both. As a result, support for Python 2.7 in this project has been dropped.

### Setup the environment
Setup a Python virtual environment and install required packages.
```
$ python3 -m venv venv
$ source venv/bin/activate
```

Once activated, it is good practice to update core packaging tools (pip, setuptools, and wheel) to the latest versions.

```
(venv) $ python -m pip install --upgrade pip setuptools wheel
```

Now install the project dependencies.

```
(venv) $ pip install -r dev-requirements.txt
(venv) $ pip install -r requirements.txt
```

### Provide registry data
This API works on a registry which includes the details of data services and the respective providers which is configured in `app/config/data.json`.

### Run the instance
To run the API locally, run below commands.

```
source venv/bin/activate
(venv) $ uvicorn app.app:app --reload
```
This spawns a local uvicorn server and hosts the API on it.

Use [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) to access swagger documentation. Alternatively use [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc) to use ReDoc version of the documentation.

Alternatively, the API can be run from the Dockerfile. To do so, follow below steps.

```
# build the docker image
docker build -t 3dbeacons-hub-api .

# run the application
docker run -p 8000:8000 3dbeacons-hub-api
```

## Testing

Automated testing is performed using [tox](https://tox.readthedocs.io/en/latest/index.html). tox will automatically create virtual environments based on tox.ini for unit testing and PEP8 style guide checking.

```
# Run all environments.
#   To only run a single environment, specify it like: -e pep8
(venv) $ tox
```

### Unit testing

This project uses [pytest](https://pytest.org/) for unit testing. Code coverage is provided by [pytest-cov](https://pytest-cov.readthedocs.io/en/latest/) plugin.

When running a unit test tox environment (e.g. ```tox```, ```tox -e py37```, etc.), a data file (e.g. ```.coverage.py37```) containing the coverage data is generated. This file is not readable on its own, but when the coverage tox environment is run (e.g. ```tox``` or ```tox -e -coverage```), coverage from all unit test environments is combined into a single data file and an HTML report is generated in the htmlcov folder showing each source file and which lines were executed during unit testing. Open ```htmlcov/index.html``` in a web browser to view the report. Code coverage reports help identify areas of the project that are currently not tested.

Code coverage is configured in ```pyproject.toml```.

To pass arguments to pytest through tox:

```
(venv) $ tox -e py37 -- -k main
```

### Code style checking
This project uses [PEP8](https://www.python.org/dev/peps/pep-0008/) for style guide and uses [flake8](http://flake8.pycqa.org/) for code compliance. flake8 is configured in ```[flake8]``` section of ```tox.ini```.

### Automated code formatting
Code is automatically formatted using [black](https://github.com/psf/black). Imports are automatically sorted and grouped using [isort](https://github.com/timothycrosley/isort/).

They are configured in ```pyproject.toml```. Please note to prefix ```tool.``` for all these configurations in ```pyproject.toml```.

Format the code using:
```
(venv) $ tox -e fmt
```

Verify if the code is properly formatted (in a CI job):

```
(venv) $ tox -e fmt-check
```

### Type checking
Type checking is performed by [mypy](https://mypy.readthedocs.io/en/stable/index.html#). Use ```tox -e mypy```. This is configured in ```mypy.ini```.
