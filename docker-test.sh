#!/bin/bash
docker stop metroterm
docker rm metroterm
docker image rm --force metroterm
docker build -t metroterm .
echo run
mkdir -p out
docker run --name metroterm -v $(pwd)/out:/srv/metroterm/out metroterm
ls -al out
