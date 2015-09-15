default: all

CFLAGS := -I./include -g --std=gnu99
CXXFLAGS := -I./include -g --std=gnu++0x
CC := gcc
CXX := g++

LIBS := -lach -lm

all: main

main: build/main.o
	gcc -o $@ $< $(LIBS)

clean:
	rm -f main
	rm -f build/*.o

build/%.o: src/%.c
	$(CC) $(CFLAGS) -o $@ -c $<
