import sys, os
import csv

def get_TTE(file_path, target):
    crash_dict = dict()
    timestamp = ""
    with open(file_path) as f:
        backtrace = f.readlines()
    for i in range(int(len(backtrace)/4)):
        crash_dict[backtrace[i*4].strip("\n")] = backtrace[i*4+3].strip("\n")
    for key in crash_dict:
        if target + " " in crash_dict[key]:
            key = key.split("/")
            timestamp = key[len(key)-1].split("_")[0]
            break
    return str(timestamp)

def main(file_dir, target_file, out_path):
    file_list = os.listdir(file_dir)

    with open(target_file, 'r') as targets:
        target_list = []
        for target in targets:
            target_list.append(target)

    columns =  ["Tool", "Epoch"]
    for target in target_list:
        columns.append(target.strip('\n'))
    f = open(out_path, 'w')
    writer = csv.writer(f)
    writer.writerow(columns)

    for name in file_list:
        row = []
        row.append(name.split("-")[0])
        row.append(int(name.split("-")[1]))
        for target in target_list:
            time = get_TTE(os.path.join(file_dir, name), target.strip('\n'))
            row.append(time)
        writer.writerow(row)
    f.close()

if __name__ == '__main__':
    file_dir = sys.argv[1]
    target_file = sys.argv[2]
    out_path = sys.argv[3]
    main(file_dir, target_file, out_path)
