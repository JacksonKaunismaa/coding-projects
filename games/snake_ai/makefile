snek_AI: main.o snek_api.o
	gcc -o snek_AI main.o snek_api.o

test: test.o snek_api.o
	gcc -o test test.o snek_api.o

test.o: test.c snek_api.h ai_consts.h
	gcc -O3 -g -c test.c

main.o: main.c snek_api.h ai_consts.h
	gcc -O3 -g -c main.c

snek_api.o: snek_api.c snek_api.h ai_consts.h
	gcc -O3 -c -g snek_api.c

libsnek_py.so: snek_api.c snek_api.h 
	gcc -fPIC -shared -o ./py/libsnek_py.so snek_api.c
	
clean:
	rm *.o
