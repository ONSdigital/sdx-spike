#!/bin/sh

set -e -x

echo "Copying vendor/ to gopath"

cp -r gopath/github.com/ONSdigital/sdx-spike/cf-deploy/vendor/ ${GOPATH}/src/

ls /go/src/

cd ..
go version
env
go test ./...
