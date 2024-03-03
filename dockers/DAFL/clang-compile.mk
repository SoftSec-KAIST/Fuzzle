CC = clang
CFLAGS = -g -fno-omit-frame-pointer -Wno-error
CMAKE_EXPORT_COMPILE_COMMANDS=1

file: file.c
	$(CC) $(CFLAGS) -o file file.c

clean:
	rm -f file