for fname in $(ls)
do
	convert -resize 60% $fname $fname
done
