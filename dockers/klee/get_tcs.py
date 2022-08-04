import os, sys
import subprocess

WORKDIR = '/home/maze/workspace'
OUTDIR = '/home/maze/workspace/outputs'

def save_tc(dest_dir, tc_path, start_time, sig):
    creation_time = os.path.getctime(tc_path)
    elapsed_time = creation_time - start_time
    if sig == '':
        sig = 'tc'
    name = '%011.5f_%s' % (elapsed_time, sig)
    file_path = os.path.join(dest_dir, name)
    os.system('cp %s %s' % (tc_path, file_path))

def main(dest_dir):
    # Create destination directory
    os.system('mkdir -p %s' % dest_dir)

    time_file = os.path.join(WORKDIR, '.start')
    start_time = os.path.getmtime(time_file)

    # Collect testcases
    counter_tc = 1
    for name in os.listdir(OUTDIR):
        if name.endswith('.ktest'):
            tc_path = os.path.join(OUTDIR, name)

            if name.replace('.ktest', '.abort.err') in os.listdir(OUTDIR):
                save_tc(dest_dir, tc_path, start_time, str(counter_tc) + '_crash.ktest')
            else:
                save_tc(dest_dir, tc_path, start_time, str(counter_tc) + '_tc.ktest')
            counter_tc = counter_tc + 1

    os.system('touch /home/maze/outputs/.done')

if __name__ == '__main__':
    dest_dir = sys.argv[1]
    main(dest_dir)
