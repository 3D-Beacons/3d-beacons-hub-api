# 3D Beacons Hub API
# Welcome to the 3D Beacons Hub API

[![codecov](https://img.shields.io/codecov/c/github/3D-Beacons/3d-beacons-hub-api?style=for-the-badge)](https://codecov.io/gh/3D-Beacons/3d-beacons-hub-api)
[![build](https://img.shields.io/github/workflow/status/3D-Beacons/3d-beacons-hub-api/Hub%20API%20CI?style=for-the-badge)](https://github.com/3D-Beacons/3d-beacons-hub-api/actions?query=workflow%3A%22Hub+API+CI%22)
[![license](https://img.shields.io/github/license/3D-Beacons/3d-beacons-hub-api?style=for-the-badge)](https://raw.githubusercontent.com/3D-Beacons/3d-beacons-hub-api/master/LICENSE)

3D Beacons Hub API is a programmatic way to obtain information of available experimental and theoretical models for a protein of interest.

## Publication
**3D-Beacons: Decreasing the gap between protein sequences and structures through a federated network of protein structure data resources**<br> 
[Mihaly Varadi](https://github.com/mvaradi), [Sreenath Nair](https://github.com/sreenathnair), [Ian Sillitoe](https://github.com/orgs/3D-Beacons/people/sillitoe), [Gerardo Tauriello](https://github.com/orgs/3D-Beacons/people/gtauriello), Stephen Anyango, [Stefan Bienert](https://github.com/orgs/3D-Beacons/people/bienchen), Clemente Borges, Mandar Deshpande, Tim Green, Demis Hassabis, Andras Hatos, Tamas Hegedus, Maarten L Hekkelman, Robbie Joosten, John Jumper, Agata Laydon, Dmitry Molodenskiy, Damiano Piovesan, Edoardo Salladini, Steven L. Salzberg, Markus J Sommer, Martin Steinegger, Erzsebet Suhajda, Dmitri Svergun, Luiggi Tenorio-Ku, Silvio Tosatto, Kathryn Tunyasuvunakool, [Andrew Mark Waterhouse](https://github.com/orgs/3D-Beacons/people/awaterho), Augustin Žídek, Torsten Schwede, Christine Orengo, Sameer Velankar<br>
3 August 2022; BioRxiv https://doi.org/10.1101/2022.08.01.501973

## Background
3D-Beacons is an open collaboration between providers of macromolecular structure models. The goal of this collaboration is to provide model coordinates and meta-information from all the contributing data resources in a standardized data format and on a unified platform.

![Image](https://raw.githubusercontent.com/3D-Beacons/3d-beacons-documentation/main/assets/3d-beacons-summary.png)

**Schematical overview of the 3D-Beacons infrastructure**

3D-Beacons consists of a Registry, a Hub and Beacons who host Clients. The Registry is used by the Hub to look up which API endpoints are supported by the various Beacons. The Beacons provide data according to the 3D-Beacons data specifications ([documentation at GitHub](https://github.com/3D-Beacons/3d-beacons-specifications/blob/production/oas3.yaml)). The Hub collates the data from the Beacons and expose it via Hub API endpoints.

### Current 3D-Beacons
- [AlphaFill](https://alphafill.eu/)
- [AlphaFold DB](https://www.alphafold.ebi.ac.uk/)
- [Genome3D](http://www.genome3d.net/)
- [HegeLab](http://www.hegelab.org/)
- [isoform.io](https://isoform.io/)
- [ModelArchive](https://modelarchive.org/)
- [PDBe](https://www.ebi.ac.uk/pdbe/)
- [PED](https://proteinensemble.org/)
- [SASBDB](https://www.sasbdb.org/)
- [SWISS-MODEL Repository](https://swissmodel.expasy.org/)

## About the 3D-Beacons Hub API
The 3D-Beacons Hub API is an integrator that makes API requests to Beacon APIs and collates, ranks and exposes data. The Hub API is using the [3D-Beacons Registry](https://github.com/3D-Beacons/3d-beacons-registry) to look up which Beacons support what API endpoint.


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
This API works on a registry which includes the details of data services and the respective providers which is configured in `app/config/data.json`. It can be overriden to be picked from a URL. For doing so,
set the environmental variable `REGISTRY_DATA_JSON` as the URL.

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

### Unit Testing

Unit testing is performed with [pytest](https://pytest.org/).

pytest will automatically discover and run tests by recursively searching for folders and `.py` files prefixed with `test` for any functions prefixed by `test`.


Code coverage is provided by the [pytest-cov](https://pytest-cov.readthedocs.io/en/latest/) plugin.

Code coverage is configured in `pyproject.toml`.

### Workflow automation using pre-commit hooks ###

Code formatting and PEP8 compliance are automated using [pre-commit](https://pre-commit.com/) hooks. This is configured in `.pre-commit-config.yaml` which will run these hooks before `commit` ting anything to the repository.

Please note that this is already installed via dev-requirements.txt.

## Contributors
- Sreenath Nair - _Initial work_ - [sreenathnair](https://github.com/sreenathnair)
- Mihaly Varadi - _Initial work_ - [mvaradi](https://github.com/mvaradi)

See also the list of [contributors](https://github.com/3D-Beacons/3d-beacons-hub-api/contributors) who participated in this project.

### How to contribute
This repository is open to contributions. Please fork the repository and send pull requests.
