#!/bin/bash

for file in converted/*.png; do
    mindtct $file "minutiae/$(basename "$file" ".png")";    
done
