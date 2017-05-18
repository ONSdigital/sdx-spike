collector service
=================

The collector service sits as the gatekeeper into the SDX survey processing
pipeline, accepting surveys from eQ.

Getting Started
---------------

A simple `docker-compose.yml` is provided with an example rabbit server

```shell
$ docker-compose up
```

Then just start up the consumer

```shell
$ go run collecter.go
```

You can then publish messages to the queue via the rabbit management interface
that will be running at (http://localhost:15672) (user: `rabbit`, pass: `rabbit`)
