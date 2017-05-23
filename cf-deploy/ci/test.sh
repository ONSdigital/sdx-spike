#!/bin/sh

set -e -x

cd ..
export GOPATH=$PWD/

go version
env
go test ./...
