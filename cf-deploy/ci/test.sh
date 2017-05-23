#!/bin/sh

set -e -x

pushd cf-deploy
  go test ./...
popd