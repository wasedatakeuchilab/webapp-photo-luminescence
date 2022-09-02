# Web Application for Photo Luminescence Measurement <!-- omit in toc -->

<p align="center">
<a href="https://github.com/wasedatakeuchilab/webapp_photo_luminescence/actions?query=workflow%3ATest" target="_blank">
    <img src="https://github.com/wasedatakeuchilab/webapp_photo_luminescence/workflows/Test/badge.svg" alt="Test">
</a>
<a href="https://codecov.io/gh/wasedatakeuchilab/webapp_photo_luminescence" target="_blank">
    <img src="https://img.shields.io/codecov/c/github/wasedatakeuchilab/webapp_photo_luminescence?color=%2334D058" alt="Coverage">
</a>
</p>

This repository provides a web application for PL mesurements, with intuisive UI and high level operation to data.

- [Installation](#installation)
- [Run app](#run-app)
- [Docker image](#docker-image)
- [Setup dev environment](#setup-dev-environment)
  - [Install Poetry and dependencies](#install-poetry-and-dependencies)
  - [Install pre-commit](#install-pre-commit)
  - [Run tests](#run-tests)
- [License](#license)

## Installation

Python 3.10 or above is required.

```sh
$ pip install git+https://github.com/wasedatakeuchilab/webapp_photo_luminescence
```

## Run app

The [WSGI](https://wsgi.readthedocs.io/en/latest/) is `webapp_photo_luminescence:server`.

```sh
$ uvicorn webapp_photo_luminescence:server
```

## Docker image

You can also run the app as a Docker container.

```sh
$ docker pull wasedatakeuchilab/webapp-photo-luminescence  # Pull a image
$ docker build -t app .  # Build a image
```

## Setup dev environment

### Install Poetry and dependencies

The dependencies are managed with [Poetry](https://python-poetry.org/docs/) in this project.

```sh
$ pip install poetry~=1.2.0
$ poetry config virtualenvs.create false # Recommended if you work in a container
$ poetry shell  # No need if you run the previous line
$ poetry self install  # Install addons
$ poetry install # Install dependencies
```

### Install pre-commit

[pre-commit](https://pre-commit.com/) enables to execute linting and type-checking before committing.

```sh
$ pre-commit install
```

### Run tests

Run unit tests using [pytest](https://docs.pytest.org/en/7.1.x/contents.html).

```sh
$ pytest
```

## License

[MIT License](./LICENSE)
