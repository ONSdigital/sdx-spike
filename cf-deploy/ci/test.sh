#!/bin/sh

set -e -x

cd sdx-pony/cf-deploy
  go test ./...
cd -