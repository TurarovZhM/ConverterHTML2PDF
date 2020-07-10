#!/bin/bash
echo "Checking spelling for html files ..."
HTML_FOLDER=$(pwd)
SPELLCHECK_FOLDER=$(echo "$(pwd)/spellcheck")
python src/spellcheck/spellcheck-html-files.py -i $HTML_FOLDER -o $SPELLCHECK_FOLDER
