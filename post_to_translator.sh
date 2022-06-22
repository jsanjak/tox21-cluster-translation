#!/bin/bash

cd json

curl -X POST -H "Content-Type: application/json" -d "@indirect-one-hop-connection.json" https://ars.transltr.io/ars/api/submit

cd ..