#!/bin/sh


virtualenv venv
. venv/bin/activate

while read line; do
    pip install $line
done < requirements.txt


