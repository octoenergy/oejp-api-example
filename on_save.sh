#!/usr/bin/env bash

# This is a helper script that can be used as a File Watcher in PyCharm for automatically
# running black and isort after saving a file.

$HOME/.virtualenvs/oejp-api-example/bin/black $1
$HOME/.virtualenvs/oejp-api-example/bin/isort $1
