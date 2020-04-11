#!/bin/bash
for i in {1..100} 
do
	./snek_AI14
 	sleep 1
	if [ $(( i % 20 )) == 0 ]
	then
				spd-say "$i"
	fi	
done
spd-say "Done!"
