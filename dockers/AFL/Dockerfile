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
WORKDIR /home/maze/tools/AFL/qemu_mode
RUN /home/maze/tools/AFL/qemu_mode/build_qemu_support.sh
WORKDIR /home/maze/tools/AFL
RUN make install

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
