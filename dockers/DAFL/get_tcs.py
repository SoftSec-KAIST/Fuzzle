from utils import save_tc
import os, sys

WORKDIR = '/home/maze/workspace'
OUTDIR = '/home/maze/workspace/outputs'

def main(dest_dir):
    # Create destination directory
    os.system('mkdir -p %s' % dest_dir)

    time_file = os.path.join(WORKDIR, '.start')
    start_time = os.path.getmtime(time_file)

    # Collect testcases
    counter_tc = 1
    tc_dir = os.path.join(OUTDIR, 'queue')
    for name in os.listdir(tc_dir):
        if name.startswith('id:') and 'orig:seed' not in name:
            tc_path = os.path.join(tc_dir, name)
            save_tc(dest_dir, tc_path, start_time, str(counter_tc) + '_tc')
            counter_tc = counter_tc + 1

    # Collect crashes
    counter_cr = 1
    crash_dir = os.path.join(OUTDIR, 'crashes')
    for name in os.listdir(crash_dir):
        if name.startswith('id:'):
            crash_path = os.path.join(crash_dir, name)
            save_tc(dest_dir, crash_path, start_time, str(counter_cr) + '_crash')
            counter_cr = counter_cr + 1

    os.system('touch /home/maze/outputs/.done')

if __name__ == '__main__':
    dest_dir = sys.argv[1]
    main(dest_dir)
