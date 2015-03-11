#!/bin/sh


virtualenv venv
source venv/bin/activate

while read line; do
    pip install $line
done < requirements.txt


