#!/bin/bash

pip3 install -r requirements.txt
gunicorn -w 8 -b 0.0.0.0:8080 server:app
