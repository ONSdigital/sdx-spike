#!/bin/sh

set -e -x

cd sdx-pony/cf-deploy
  # go test ./...
  go version
  env
  go test ./...
cd -