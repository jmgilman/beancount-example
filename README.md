# beancount-example

<p align="center">
    <a href="https://github.com/jmgilman/beancount-example/actions/workflows/ci.yml">
        <img src="https://github.com/jmgilman/beancount-example/actions/workflows/ci.yml/badge.svg"/>
    </a>
</p>

> A small container which generates example beancount ledger files and makes them
available over HTTP. Primarily used in test environments which test against
beancount data.

## Usage

Run the container:

```shell
docker run -p 8001:8001 ghcr.io/jmgilman/example-beancount
```

The generated beancount data can be accessed at the root path:

```shell
curl http://localhost:8001/
```

## Configuration

The following environment variables can be set for controlling generation:

Name  |  Default | Description                                                        |
----- | -------- | ------------------------------------------------------------------ |
START | None     | The date at which to begin generating random entries               |
END   | None     | The date at which to stop generating random entries                |
BIRTH | None     | The fictional birth of the ledger owner (controls account opening) |

Note that unset values are randomly generated. Data is persistent across
requests and is only generated when the container is started.
