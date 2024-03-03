CC="/home/maze/fuzzer/DAFL/afl-clang-fast"
CXX="/home/maze/fuzzer/DAFL/afl-clang-fast++"
CFLAGS = -g -fno-omit-frame-pointer -Wno-error
CMAKE_EXPORT_COMPILE_COMMANDS=1

file_dafl: file.c
	$(CC) $(CFLAGS) -o file_dafl file.c

clean:
	rm -f file_dafl
