#!/usr/bin/env bash

poetry run isort crew3
poetry run black crew3
poetry run flake8 crew3
