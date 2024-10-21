#!/bin/bash

for file in converted/*.png; do
    outfile="gray/$(basename "$file" ".png").gray" 
    magick $file -depth 8 -type Grayscale -compress none -colorspace Gray -strip $outfile 
    cwsq 0.75 wsq $outfile -raw_in 640,480,8,500
    mindtct "gray/$(basename "$outfile" ".gray").wsq"  "minutiaeWsq/$(basename "$outfile" ".gray")"
done
