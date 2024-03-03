FROM maze-base

# Install dependencies
RUN apt -y install make build-essential libtool libtool-bin python automake bison libglib2.0-dev

# Install AFL
RUN git clone https://github.com/google/AFL.git /home/maze/tools/AFL
ADD afl.patch /home/maze/tools/afl.patch
WORKDIR /home/maze/tools/AFL
# Check out to v2.57b
RUN git checkout v2.57b
# Patch AFL
RUN patch -p1 < ../afl.patch
RUN make
RUN make install

# Install AFL QEMU mode
#WORKDIR /home/maze/tools/AFL/qemu_mode
#RUN /home/maze/tools/AFL/qemu_mode/build_qemu_support.sh
#WORKDIR /home/maze/tools/AFL
#RUN make install

# Install llvm mode
RUN echo "deb http://apt.llvm.org/bionic/ llvm-toolchain-bionic-12 main" >> /etc/apt/sources.list && \
    wget -qO - https://apt.llvm.org/llvm-snapshot.gpg.key | apt-key add -
RUN echo "deb http://ppa.launchpad.net/ubuntu-toolchain-r/test/ubuntu bionic main" >> /etc/apt/sources.list && \
    apt-key adv --recv-keys --keyserver keyserver.ubuntu.com 1E9377A2BA9EF27F
RUN apt-get update && apt-get full-upgrade -y && \
    apt-get -y install --no-install-suggests --no-install-recommends \
    clang-12 llvm-12 llvm-12-dev llvm-12-runtime llvm-12-tools \
    && rm -rf /var/lib/apt/lists/*
RUN update-alternatives --install /usr/bin/llvm-config llvm-config /usr/bin/llvm-config-12 0
RUN update-alternatives --install /usr/bin/clang clang /usr/bin/clang-12 0
RUN update-alternatives --install /usr/bin/clang++ clang++ /usr/bin/clang++-12 0

WORKDIR /home/maze/tools/AFL/llvm_mode
RUN export CC=clang-12 && export CXX=clang++-12
RUN make

USER maze

ENV AFL_SKIP_CPUFREQ=1
ENV AFL_NO_AFFINITY=1
ENV AFL_I_DONT_CARE_ABOUT_MISSING_CRASHES=1

# Add scripts
ADD run_afl.sh /home/maze/tools/run_afl.sh
ADD get_tcs.py /home/maze/tools/get_tcs.py
ADD convert_to_cov_code.py /home/maze/tools/convert_to_cov_code.py
ADD get_coverage.sh /home/maze/tools/get_coverage.sh

WORKDIR /home/maze/workspace
