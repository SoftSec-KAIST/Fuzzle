FROM maze-base

# Install dependencies
RUN apt -y install make build-essential

# Install AFL++
RUN git clone https://github.com/aflgo/aflgo.git /home/maze/tools/afl
ADD aflgo.patch /home/maze/tools/aflgo.patch
WORKDIR /home/maze/tools/afl
# Check out to 6e87b69ab2c31177d66e1c3d0b674393cfdceec7
RUN git checkout 6e87b69ab2c31177d66e1c3d0b674393cfdceec7
# TODO: patch AFLGo
RUN patch -p1 < ../aflgo.patch
RUN /home/maze/tools/afl/scripts/build/aflgo-build.sh

USER maze

ENV AFL_SKIP_CPUFREQ=1
ENV AFL_NO_AFFINITY=1
ENV AFL_I_DONT_CARE_ABOUT_MISSING_CRASHES=1

# Add scripts
ADD run_aflgo.sh /home/maze/tools/run_aflgo.sh
ADD get_tcs.py /home/maze/tools/get_tcs.py
ADD convert_to_cov_code.py /home/maze/tools/convert_to_cov_code.py
ADD get_coverage.sh /home/maze/tools/get_coverage.sh

WORKDIR /home/maze/workspace
