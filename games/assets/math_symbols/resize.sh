for fname in $(ls)
do
	convert -resize 80% $fname $fname
done
