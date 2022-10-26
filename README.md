# Web Application for TRPL measurement <!-- omit in toc -->

<p align="center">
<a href="https://github.com/wasedatakeuchilab/dawa-trpl/actions?query=workflow%3ATest" target="_blank">
    <img src="https://github.com/wasedatakeuchilab/dawa-trpl/workflows/Test/badge.svg" alt="Test">
</a>
<a href="https://codecov.io/gh/wasedatakeuchilab/dawa-trpl" target="_blank">
    <img src="https://img.shields.io/codecov/c/github/wasedatakeuchilab/dawa-trpl?color=%2334D058" alt="Coverage">
</a>
</p>

This repository provides a web application for PL mesurements, with intuisive UI and high level operations to data.

- [Installation](#installation)
- [Run app](#run-app)
- [Docker image](#docker-image)
- [Setup dev environment](#setup-dev-environment)
  - [Install dependencies](#install-dependencies)
  - [Install pre-commit](#install-pre-commit)
  - [Run tests](#run-tests)
- [License](#license)

## Installation

Python 3.10 or above is required.

```sh
pip install git+https://github.com/wasedatakeuchilab/dawa-trpl
```

## Run app

The [WSGI](https://wsgi.readthedocs.io/en/latest/) is `dawa_trpl:server`.

```sh
uvicorn dawa_trpl:server
```

## Docker image

You can also run the app as [a Docker container](https://hub.docker.com/repository/docker/wasedatakeuchilab/dawa-trpl).

```sh
docker run -it -p 8080:80 ghcr.io/wasedatakeuchilab/dawa-trpl
```

## Setup dev environment

### Install dependencies

```sh
pip install -e .[dev,test]
```

### Install pre-commit

[pre-commit](https://pre-commit.com/) enables to execute linting and type-checking before committing.

```sh
pre-commit install
```

### Run tests

Run unit tests using [pytest](https://docs.pytest.org/en/7.1.x/contents.html).

```sh
pytest
```

## License

[MIT License](./LICENSE)

Copyright (c) 2022 Shuhei Nitta
