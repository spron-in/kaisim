#!/bin/bash

source /home/www/kaisim/.venv/bin/activate

exec /home/www/kaisim/.venv/bin/gunicorn --bind 127.0.0.1:5001 --workers 3 --threads 4 app:app
