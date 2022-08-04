from utils import save_tc
import os, sys

WORKDIR = '/home/maze/workspace'
OUTDIR = '/home/maze/workspace/syncdir'

def main(dest_dir):
    # Create destination directory
    os.system('mkdir -p %s' % dest_dir)

    time_file = os.path.join(WORKDIR, '.start')
    start_time = os.path.getmtime(time_file)

    # Collect testcases from AFL-master
    counter_tc = 1
    tc_dir = os.path.join(OUTDIR, 'afl-master', 'queue')
    for name in os.listdir(tc_dir):
        if name.startswith('id:') and 'orig:seed' not in name:
            tc_path = os.path.join(tc_dir, name)
            save_tc(dest_dir, tc_path, start_time, str(counter_tc) + '_tc')
            counter_tc = counter_tc + 1

    # Collect crashes from AFL-master
    counter_cr = 1
    crash_dir = os.path.join(OUTDIR, 'afl-master', 'crashes')
    for name in os.listdir(crash_dir):
        if name.startswith('id:'):
            crash_path = os.path.join(crash_dir, name)
            save_tc(dest_dir, crash_path, start_time, str(counter_cr) + '_crash')
            counter_cr = counter_cr + 1

    # Collect testcases from AFL-slave
    tc_dir = os.path.join(OUTDIR, 'afl-slave', 'queue')
    for name in os.listdir(tc_dir):
        if name.startswith('id:') and 'orig:seed' not in name:
            tc_path = os.path.join(tc_dir, name)
            save_tc(dest_dir, tc_path, start_time, str(counter_tc) + '_tc')
            counter_tc = counter_tc + 1

    # Collect crashes from AFL-slave
    crash_dir = os.path.join(OUTDIR, 'afl-slave', 'crashes')
    for name in os.listdir(crash_dir):
        if name.startswith('id:'):
            crash_path = os.path.join(crash_dir, name)
            save_tc(dest_dir, crash_path, start_time, str(counter_cr) + '_crash')
            counter_cr = counter_cr + 1

    # Collect testcases from Eclipser
    tc_dir = os.path.join(OUTDIR, 'eclipser-output', 'queue')
    for name in os.listdir(tc_dir):
        if name.startswith('id:'):
            tc_path = os.path.join(tc_dir, name)
            save_tc(dest_dir, tc_path, start_time, str(counter_tc) + '_tc')
            counter_tc = counter_tc + 1

    # Collect crashes from Eclipser
    crash_dir = os.path.join(OUTDIR, 'eclipser-output', 'crashes')
    for name in os.listdir(crash_dir):
        if name.startswith('id:'):
            crash_path = os.path.join(crash_dir, name)
            save_tc(dest_dir, crash_path, start_time, str(counter_cr) + '_crash')
            counter_cr = counter_cr +1

    os.system('touch /home/maze/outputs/.done')

if __name__ == '__main__':
    dest_dir = sys.argv[1]
    main(dest_dir)
