FROM maze-base

# Install dependencies
RUN apt-get install -yy \
      wget apt-transport-https git unzip \
      build-essential libtool libtool-bin gdb \
      automake autoconf bison flex python python3 sudo vim

# Copied from OSS-FUZZ
ENV OUT=/out
ENV SRC=/src
ENV WORK=/work
ENV PATH="$PATH:/out"
RUN mkdir -p $OUT $SRC $WORK
ENV CMAKE_VERSION 3.21.1
RUN wget https://github.com/Kitware/CMake/releases/download/v$CMAKE_VERSION/cmake-$CMAKE_VERSION-Linux-x86_64.sh && \
    chmod +x cmake-$CMAKE_VERSION-Linux-x86_64.sh && \
    ./cmake-$CMAKE_VERSION-Linux-x86_64.sh --skip-license --prefix="/usr/local" && \
    rm cmake-$CMAKE_VERSION-Linux-x86_64.sh && \
    rm -rf /usr/local/doc/cmake /usr/local/bin/cmake-gui
COPY checkout_build_install_llvm.sh /root/
RUN /root/checkout_build_install_llvm.sh
RUN rm /root/checkout_build_install_llvm.sh

# Install packages needed for fuzzers
RUN apt-get update && \
    apt-get install -yy \
      # Several packages get uninstalled after LLVM setup.
      git build-essential bc \
      # For libming
      libfreetype6 libfreetype6-dev \
      # For libxml
      python-dev \
      # For libjpeg
      nasm \
      # For lrzip
      libbz2-dev liblzo2-dev \
      # For 32bit binaries
      gcc-multilib \
      # For DAFL
      libgmp-dev libmpfr-dev pkg-config software-properties-common

# Add Scripts
WORKDIR /home/maze
RUN mkdir -p /home/maze/seed \
    mkdir -p /home/maze/script \
    mkdir -p /home/maze/workspace/src \
    mkdir -p /home/maze/workspace/dafl-input
RUN echo '' > /home/maze/seed/empty
COPY clang-compile.mk /home/maze/script/clang-compile.mk
COPY dafl-compile.mk /home/maze/script/dafl-compile.mk
COPY dafl-compile-noasan.mk /home/maze/script/dafl-compile-noasan.mk
COPY setup_smake.sh /home/maze/script/setup_smake.sh
ADD run_dafl.sh /home/maze/tools/run_dafl.sh
ADD get_tcs.py /home/maze/tools/get_tcs.py
ADD convert_to_cov_code.py /home/maze/tools/convert_to_cov_code.py
ADD get_coverage.sh /home/maze/tools/get_coverage.sh

# Setup smake.
WORKDIR /home/maze/script
RUN ./setup_smake.sh

# Setup Sparrow
RUN echo "deb http://apt.llvm.org/bionic/ llvm-toolchain-bionic-12 main" >> /etc/apt/sources.list && \
    wget -qO - https://apt.llvm.org/llvm-snapshot.gpg.key | apt-key add -
RUN echo "deb http://ppa.launchpad.net/ubuntu-toolchain-r/test/ubuntu bionic main" >> /etc/apt/sources.list && \
    apt-key adv --recv-keys --keyserver keyserver.ubuntu.com 1E9377A2BA9EF27F
RUN add-apt-repository ppa:avsm/ppa
RUN apt-get update
RUN apt-get install -y \
    libclang-cpp12-dev libclang-12-dev llvm-12-dev \
    libclang-dev llvm-dev ncurses-dev
RUN apt install opam -y
COPY setup_Sparrow.sh /home/maze/script/setup_Sparrow.sh
RUN /home/maze/script/setup_Sparrow.sh

# Setup DAFL.
RUN mkdir -p /home/maze/fuzzer
WORKDIR /home/maze/fuzzer
COPY setup_DAFL.sh /home/maze/fuzzer/setup_DAFL.sh
RUN ./setup_DAFL.sh

# Reset the working directory to top-level directory.
ENV AFL_I_DONT_CARE_ABOUT_MISSING_CRASHES=1
ENV AFL_SKIP_CPUFREQ=1
WORKDIR /home/maze
