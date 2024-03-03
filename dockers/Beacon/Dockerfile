FROM maze-base

# Install packages needed for Beacon fuzzers
RUN apt-get update && \
    apt-get install -yy \
      make python3 \
      # Several packages get uninstalled after LLVM setup.
      git build-essential bc \
      # For Beacon
      libncurses5 \
      # For libming
      libfreetype6 libfreetype6-dev

# Setup Beacon
WORKDIR /home/maze/tools
COPY Beacon-binaries/ /home/maze/tools/beacon
COPY ./setup_beacon.sh /home/maze/tools/setup_beacon.sh
RUN ./setup_beacon.sh

USER maze

ENV AFL_SKIP_CPUFREQ=1
ENV AFL_NO_AFFINITY=1
ENV AFL_I_DONT_CARE_ABOUT_MISSING_CRASHES=1

# Add scripts
ADD run_beacon.sh /home/maze/tools/run_beacon.sh
ADD get_tcs.py /home/maze/tools/get_tcs.py
ADD convert_to_cov_code.py /home/maze/tools/convert_to_cov_code.py
ADD get_coverage.sh /home/maze/tools/get_coverage.sh

WORKDIR /home/maze/workspace
