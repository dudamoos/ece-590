default: all

CFLAGS := -I./include -g --std=gnu99
CXXFLAGS := -I./include -g --std=gnu++0x
CC := gcc
CXX := g++

LIBS := -lach

all: hand-wave

hand-wave: build/main.o
	gcc -o $@ $< $(LIBS)

clean:
	rm -f hand-wave
	rm -f build/*.o

build/%.o: src/%.c
	$(CC) $(CFLAGS) -o $@ -c $<
