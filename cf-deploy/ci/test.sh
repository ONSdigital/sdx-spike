#!/bin/sh

set -e -x

echo "Copying vendor/ to gopath"
ls
cp -r vendor/ ${GOPATH}/src/

cd ..
go version
env
go test ./...
