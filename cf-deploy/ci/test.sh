#!/bin/sh

set -e -x

cd ..
  # go test ./...
  go version
  env
  go test ./...
cd -