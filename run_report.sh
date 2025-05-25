#!/bin/bash

# Exit immediately if any command fails
set -e

# Render the Quarto notebook
quarto render ./height_weight_tracker.ipynb --execute --output-dir ./docs

echo "✅ Report rendered successfully."

ARG=${1:-y}

# Step 2: Commit and push if argument is 'y' 
if [[ "$ARG" == "y" ]]; then
  git add docs/
  git commit -m "update report"
  git push
  echo "✅ Changes committed and pushed."
else
  echo "ℹ️ Skipped Git commit/push."
fi