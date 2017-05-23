#!/bin/sh

set -e -x

# Shouldn't need to do this!? Go doesn't appear to be respecting the vendor/ path
# in the main source (although that may be due to how the code is getting loaded
# into the image)
echo "Moving vendor/ to gopath"
mv gopath/github.com/ONSdigital/sdx-spike/cf-deploy/vendor/* ${GOPATH}/src/

# We're one level down in /ci when we're running this script, so we need to
# jump back to run the tests.
cd ..
go test ./...
