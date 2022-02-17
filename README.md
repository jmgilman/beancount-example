# beancount-example

<p align="center">
    <a href="https://github.com/jmgilman/beancount-example/actions/workflows/ci.yml">
        <img src="https://github.com/jmgilman/beancount-example/actions/workflows/ci.yml/badge.svg"/>
    </a>
    <a href="https://hub.docker.com/repository/docker/jmgilman/beancount-example">
        <img src="https://img.shields.io/docker/image-size/jmgilman/beancount-example?sort=date"/>
    </a>
</p>

> A small container which generates example beancount ledger files and makes them
available over HTTP. Primarily used in test environments which test against
beancount data.

## Usage

Run the container:

```shell
docker run -p 8001:8001 jmgilman/example-beancount # or ghcr.io/jmgilman/example-beancount
```

The generated beancount data can be accessed at the root path:

```shell
curl http://localhost:8001/
```

By default, the example data is only generated once and then reused across
requests. This is helpful in test scenarios where you need the backing data to
remain unchanged.

To override this behavior and force the data to be regenerated, simply provide
the following query parameter with the request:

```shell
curl http://localhost:8001/?reset
```

This can be called any number of times with the backing data being regenerated
each time the query parameter is appended.

## Configuration

The following optional environment variables can be set for controlling
generation:

Name  |  Default | Description                                                        |
----- | -------- | ------------------------------------------------------------------ |
START | None     | The date at which to begin generating random entries               |
END   | None     | The date at which to stop generating random entries                |
BIRTH | None     | The fictional birth of the ledger owner (controls account opening) |

Note that unset values are randomly generated.
