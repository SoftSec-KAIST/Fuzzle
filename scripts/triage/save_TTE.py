import sys, os
import csv

def search_crash(file_path, target_hash):
    crash_dict = dict()
    timestamp = ""
    with open(file_path) as f:
        triage = f.readlines()
    for i in range(int(len(triage)/2)):
        crash_dict[triage[i*2].strip("\n")] = triage[i*2+1].strip("\n")
    for key in crash_dict:
        if target_hash in crash_dict[key]:
            key = key.split("/")
            timestamp = key[len(key)-1].split("_")[0]
            break
    return str(timestamp)

def main(file_list, file_dir, hash_file, out_path):
    with open(file_list, 'r') as files:
        name_list = []
        for file in files:
            name_list.append(file)
    with open(hash_file, 'r') as hashes:
        hash_list = []
        for hash in hashes:
            hash_list.append(hash)

    columns =  ["Tool", "Epoch"]
    for hash in hash_list:
        columns.append(hash.split(',')[0])
    f = open(out_path, 'w')
    writer = csv.writer(f)
    writer.writerow(columns)

    for name in name_list:
        row = []
        row.append(name.split("-")[0])
        row.append(int(name.split("-")[1]))
        for hash in hash_list:
            time = search_crash(os.path.join(file_dir, name.strip('\n')), hash.split(',')[1].strip('\n'))
            row.append(time)
        writer.writerow(row)
    f.close()

if __name__ == '__main__':
    file_list = sys.argv[1]
    file_dir = sys.argv[2]
    hash_file = sys.argv[3]
    out_path = sys.argv[4]
    main(file_list, file_dir, hash_file, out_path)
