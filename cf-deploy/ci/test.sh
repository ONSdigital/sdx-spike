#!/bin/sh

set -e -x

cd sdx-pony/cf-deploy
  # go test ./...
  go version
  ls vendor/
  go test ./...
cd -