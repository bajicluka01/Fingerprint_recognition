#!/bin/bash

for file in db/*.tif; do
    magick $file "converted/$(basename "$file" ".tif").png";    
done
