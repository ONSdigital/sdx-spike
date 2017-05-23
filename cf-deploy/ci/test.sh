#!/bin/sh

set -e -x

export GOPATH=$PWD

go version
env
go test ./...
