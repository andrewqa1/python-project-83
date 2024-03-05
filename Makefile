#!/usr/bin/env python3

install:
	poetry install

dev:
	poetry run flask --app analyzer/app:app run

start:
	poetry run gunicorn -w 5 -b 0.0.0.0:8001 analyzer/app:app