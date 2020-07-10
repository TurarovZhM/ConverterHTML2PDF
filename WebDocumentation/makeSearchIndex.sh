#!/bin/bash
echo "Creating search index ..."
HTML_FOLDER=$(pwd)
SEARCH_FOLDER=$(echo "$(pwd)/search")
python src/search/read-html-files.py -i $HTML_FOLDER -o $SEARCH_FOLDER
