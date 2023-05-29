#!/bin/bash

if [ -z "$CONFIGURATION_PATH" ]
then
    python3 main.py "$@"
else
    python3 main.py --configuration_path $CONFIGURATION_PATH "$@"
fi

