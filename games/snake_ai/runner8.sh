#!/bin/bash
for i in {1..50} 
do
	./snek_AI25
 	sleep 1
	if [ $(( i % 20 )) == 0 ]
	then
				spd-say "$i"
	fi	
done
spd-say "Done!"


