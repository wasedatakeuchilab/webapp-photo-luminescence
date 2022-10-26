# Web application for TRPL measurement <!-- omit in toc -->

<p align="center">
<a href="https://github.com/wasedatakeuchilab/dawa-trpl/actions?query=workflow%3ATest" target="_blank">
    <img src="https://github.com/wasedatakeuchilab/dawa-trpl/workflows/Test/badge.svg" alt="Test">
</a>
<a href="https://codecov.io/gh/wasedatakeuchilab/dawa-trpl" target="_blank">
    <img src="https://img.shields.io/codecov/c/github/wasedatakeuchilab/dawa-trpl?color=%2334D058" alt="Coverage">
</a>
</p>

This repository provides a web application for TRPL mesurements, with intuisive UI and high level operations to data.

- [Installation](#installation)
- [Run app](#run-app)
- [Docker image](#docker-image)
- [License](#license)

## Installation

Python 3.10 or above is required.

```sh
pip install git+https://github.com/wasedatakeuchilab/dawa-trpl
```

## Run app

The [ASGI](https://asgi.readthedocs.io/en/latest/) is `dawa_trpl:server`.

```sh
uvicorn dawa_trpl:server
```

## Docker image

You can also run the app as [a Docker container](https://github.com/wasedatakeuchilab/dawa-trpl/pkgs/container/dawa-trpl).

```sh
docker run -it -p 8080:80 ghcr.io/wasedatakeuchilab/dawa-trpl
```

## License

[MIT License](./LICENSE)

Copyright (c) 2022 Shuhei Nitta
