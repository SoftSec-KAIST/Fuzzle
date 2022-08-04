FROM maze-base

# Install dependencies
RUN apt update -y && \
	apt-get build-dep -y qemu-user && \ 
	apt install -y \
	llvm-8 clang-8 nano \
	qemu-user git libglib2.0-dev libfdt-dev \
	libpixman-1-dev zlib1g-dev libcapstone-dev \
	strace cmake python3 libprotobuf10 \
	libibverbs-dev libjpeg62-dev \
	libpng16-16 libjbig-dev \
	build-essential libtool-bin python3-dev \
	automake flex bison libglib2.0-dev \
	libpixman-1-dev clang \
	python3-setuptools llvm wget \
	llvm-dev g++ g++-multilib python \
	python-pip lsb-release gcc-4.8 g++-4.8 \
	llvm-3.9 cmake libc6 libstdc++6 \
	linux-libc-dev gcc-multilib \
	apt-transport-https libtool \
        libtool-bin wget \
        automake autoconf \
        bison git gdb dumb-init valgrind ninja-build \
	time xxd python3-pip && \
	apt clean && \
	rm -rf /var/lib/apt/lists/*

USER maze

RUN pip install --user virtualenv
RUN python3 -m pip install --user pytest

# Install fuzzolic
RUN git clone https://github.com/season-lab/fuzzolic.git /home/maze/tools/fuzzolic
WORKDIR /home/maze/tools/fuzzolic
# Check out to 6aa53031ec81566b9e037b6a5a803520c24da80b
RUN git checkout 6aa53031ec81566b9e037b6a5a803520c24da80b
RUN git submodule update --init --recursive
# Build QEMU tracer
RUN cd tracer && ./configure --prefix=`pwd`/../build --target-list=x86_64-linux-user && make -j `nproc` 
# Build custom Z3
RUN cd solver/fuzzy-sat/fuzzolic-z3 && mkdir build && cd build && cmake .. -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=`pwd`/dist && make -j `nproc` && make install
# Set environment vars for Z3
ENV C_INCLUDE_PATH=/home/maze/tools/fuzzolic/solver/fuzzy-sat/fuzzolic-z3/build/dist/include
ENV LIBRARY_PATH=/home/maze/tools/fuzzolic/solver/fuzzy-sat/fuzzolic-z3/build/dist/lib
ENV LD_LIBRARY_PATH=/home/maze/tools/fuzzolic/solver/fuzzy-sat/fuzzolic-z3/build/dist/lib
ENV BASH_ENV=/home/maze/.bashrc
RUN echo "export C_INCLUDE_PATH=/home/maze/tools/fuzzolic/solver/fuzzy-sat/fuzzolic-z3/build/dist/include" >> $BASH_ENV
RUN echo "export LIBRARY_PATH=/home/maze/tools/fuzzolic/solver/fuzzy-sat/fuzzolic-z3/build/dist/lib" >> $BASH_ENV
RUN echo "export LD_LIBRARY_PATH=/home/maze/tools/fuzzolic/solver/fuzzy-sat/fuzzolic-z3/build/dist/lib" >> $BASH_ENV
# Create fuzzy-sat-CLI folder
RUN cd solver/fuzzy-sat && \
	git rev-parse HEAD > /tmp/revision && \
	git checkout master && \
	git submodule update && \
	cd ../.. && \
	cp -r solver/fuzzy-sat solver/fuzzy-sat-cli && \
	rm solver/fuzzy-sat-cli/.git && \
	cd solver/fuzzy-sat && \
	git checkout `cat /tmp/revision` && \
	git submodule update
# Build fuzzy-sat-CLI
RUN cd solver/fuzzy-sat-cli && make -j `nproc`
# Build fuzzy-sat
RUN cd solver/fuzzy-sat && make -j `nproc`
# Build solver frontend
RUN cd solver && cmake . && make -j `nproc`
# Build AFL++
# TODO: patch AFL++
RUN cd utils && git clone https://github.com/AFLplusplus/AFLplusplus.git && \
	cd AFLplusplus && git checkout 2dac4e7 && \
	git apply ../afl-showmap.c.patch && \
	make -j `nproc` all && cd qemu_mode && ./build_qemu_support.sh
ENV AFL_PATH=/home/maze/tools/fuzzolic/utils/AFLplusplus
RUN echo "export AFL_PATH=/home/maze/tools/fuzzolic/utils/AFLplusplus" >> $BASH_ENV
ENV AFL_SKIP_CPUFREQ=1
ENV AFL_NO_AFFINITY=1
ENV AFL_I_DONT_CARE_ABOUT_MISSING_CRASHES=1
# Build fuzzolic tests
RUN cd tests && make

# Add scripts
ADD run_fuzzolic.sh /home/maze/tools/run_fuzzolic.sh
ADD get_tcs.py /home/maze/tools/get_tcs.py
ADD convert_to_cov_code.py /home/maze/tools/convert_to_cov_code.py
ADD get_coverage.sh /home/maze/tools/get_coverage.sh

WORKDIR /home/maze/workspace
