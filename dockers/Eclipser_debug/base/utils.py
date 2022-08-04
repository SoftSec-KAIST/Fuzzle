import os

def save_tc(dest_dir, tc_path, start_time, sig):
    creation_time = os.path.getctime(tc_path)
    elapsed_time = creation_time - start_time
    if sig == '':
        sig = 'tc'
    name = '%011.5f_%s' % (elapsed_time, sig)
    file_path = os.path.join(dest_dir, name)
    os.system('cp %s %s' % (tc_path, file_path))
