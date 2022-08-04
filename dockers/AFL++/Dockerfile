FROM maze-base

# Install dependencies 
RUN apt -y install --no-install-suggests --no-install-recommends \
    automake \
    ninja-build \
    bison flex \
    build-essential \
    python3 python3-dev python3-setuptools \
    libtool libtool-bin \
    libglib2.0-dev \
    jupp nano bash-completion less \
    apt-utils apt-transport-https ca-certificates gnupg dialog \
    libpixman-1-dev \
    gnuplot-nox \
    && rm -rf /var/lib/apt/lists/*
RUN echo "deb http://apt.llvm.org/bionic/ llvm-toolchain-bionic-12 main" >> /etc/apt/sources.list && \
    wget -qO - https://apt.llvm.org/llvm-snapshot.gpg.key | apt-key add -
RUN echo "deb http://ppa.launchpad.net/ubuntu-toolchain-r/test/ubuntu bionic main" >> /etc/apt/sources.list && \
    apt-key adv --recv-keys --keyserver keyserver.ubuntu.com 1E9377A2BA9EF27F
RUN apt-get update && apt-get full-upgrade -y && \
    apt-get -y install --no-install-suggests --no-install-recommends \
    gcc-10 g++-10 gcc-10-plugin-dev gcc-10-multilib gcc-multilib gdb lcov \
    clang-12 clang-tools-12 libc++1-12 libc++-12-dev \
    libc++abi1-12 libc++abi-12-dev libclang1-12 libclang-12-dev \
    libclang-common-12-dev libclang-cpp12 libclang-cpp12-dev liblld-12 \
    liblld-12-dev liblldb-12 liblldb-12-dev libllvm12 libomp-12-dev \
    libomp5-12 lld-12 lldb-12 llvm-12 llvm-12-dev llvm-12-runtime llvm-12-tools \
    && rm -rf /var/lib/apt/lists/*
RUN update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-10 0
RUN update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-10 0

# Install AFL++
RUN git clone --depth=1 https://github.com/vanhauser-thc/afl-cov /home/maze/tools/afl-cov
RUN git clone https://github.com/AFLplusplus/AFLplusplus.git /home/maze/tools/AFLplusplus
ENV LLVM_CONFIG=llvm-config-12
WORKDIR /home/maze/tools/afl-cov
RUN make install
WORKDIR /home/maze/tools/AFLplusplus
# Check out to 3.13c
RUN git checkout 3.13c
# TODO: patch AFL++
RUN export CC=gcc-10 && export CXX=g++-10 && make clean && \
    make distrib && make install && make clean

USER maze
ENV AFL_SKIP_CPUFREQ=1
ENV AFL_NO_AFFINITY=1
ENV AFL_I_DONT_CARE_ABOUT_MISSING_CRASHES=1

# Add scripts
ADD run_afl++.sh /home/maze/tools/run_afl++.sh
ADD get_tcs.py /home/maze/tools/get_tcs.py
ADD convert_to_cov_code.py /home/maze/tools/convert_to_cov_code.py
ADD get_coverage.sh /home/maze/tools/get_coverage.sh

WORKDIR /home/maze/workspace
