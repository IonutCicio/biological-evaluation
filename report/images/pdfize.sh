#!/bin/bash

for filename in *.svg; do
    echo $(basename -s .svg $filename).pdf
    inkscape --export-filename=$(basename -s .svg $filename).pdf $filename

done


