#!/bin/bash

# Arg1: Target Source code
# Arg2: Target Binary
# Arg3: Timeout (in minutes)

sudo chown -R maze:maze /home/maze/maze

WORKDIR=/home/maze/workspace

INDIR=$WORKDIR/inputs

# TIMEOUT in seconds
TIMEOUT=$((60*$3))

# Create dummy file to indicate running start
touch $WORKDIR/.start

mkdir -p $INDIR
echo 'A' > $INDIR/seed

MASTERBOX=$WORKDIR/afl-master-box
SLAVEBOX=$WORKDIR/afl-slave-box
ECLIPSERBOX=$WORKDIR/eclipser-box
SYNCDIR=$WORKDIR/syncdir

mkdir -p $MASTERBOX
mkdir -p $SLAVEBOX
mkdir -p $ECLIPSERBOX
mkdir -p $SYNCDIR

echo "Start master AFL"
CMD="timeout $3m /home/maze/tools/AFL/afl-fuzz -i $INDIR -o $SYNCDIR -M afl-master -Q -- $2 > $MASTERBOX/master-log.txt"
echo "#!/bin/bash" > $MASTERBOX/run_master.sh
echo $CMD >> $MASTERBOX/run_master.sh
chmod 755 $MASTERBOX/run_master.sh
$MASTERBOX/run_master.sh &
echo "Launched master AFL"

echo "Start slave AFL"
CMD="timeout $3m /home/maze/tools/AFL/afl-fuzz -i $INDIR -o $SYNCDIR -S afl-slave -Q -- $2 > $SLAVEBOX/slave-log.txt"
echo "#!/bin/bash" > $SLAVEBOX/run_slave.sh
echo $CMD >> $SLAVEBOX/run_slave.sh
chmod 755 $SLAVEBOX/run_slave.sh
$SLAVEBOX/run_slave.sh &
echo "Launched slave AFL"

dotnet /home/maze/tools/Eclipser/build/Eclipser.dll -p $2 -t $TIMEOUT -v 1 -s $SYNCDIR -o $SYNCDIR/eclipser-output
