#!/bin/bash

FOLDER_PATH=$1

if [ -z "$FOLDER_PATH" ]; then
  echo "Input project folder please!"
  return 1
fi

if [ ! -d "$FOLDER_PATH" ]; then
  echo "Folder not exist: $FOLDER_PATH"
  return 1
fi

echo "Installing dependencies..."
pip install -r "$FOLDER_PATH/requirements.txt"

echo "Granting execute permission for ./scripts"
find "$FOLDER_PATH/scripts" -type f -exec chmod +x {} \;

export PROJECT_DIR="$FOLDER_PATH"

echo "Setup completed successfully."
