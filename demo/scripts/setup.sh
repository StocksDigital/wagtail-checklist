#!/bin/bash
virtualenv -p python3 env
. env/bin/activate
pip3 install -r requirements.txt
pushd demo
./manage.py migrate
cat ../scripts/data.py | ./manage.py shell
./manage.py loaddata images-fixtures.json
popd
