import sys
import csv
from collections import defaultdict
import statistics

def get_average_TTE(data, CVE):
    TTE_sum = 0.0
    bug_count = 0
    for row in data:
        if row[CVE] != None and row[CVE] != '':
            TTE_sum += float(row[CVE])
            bug_count += 1
    if bug_count == 0:
        return '-'
    else:
        average_TTE = (TTE_sum / bug_count)/3600
        return '%02.2f' % average_TTE

def get_median_TTE(data, CVE):
    TTE_list = list()
    for row in data:
        if row[CVE] != None and row[CVE] != '':
            TTE_list.append(float(row[CVE]))
    if len(TTE_list) < 1:
        return '-'
    else:
        median_TTE = (statistics.median(TTE_list))/3600
        return '%02.2f' % median_TTE

def get_count(data, CVE):
    count = 0
    for row in data:
        if row[CVE] != None and row[CVE] != '':
            count = count + 1
    return count

def parse_csv(file_path):
    with open(file_path, 'r') as f:
        csv_reader = csv.DictReader(f)
        tools = defaultdict(list)
        for row in csv_reader:
            tools[row['Tool']].append(row)

        # print column headers
        header = "\nTarget\t\t"
        header_line = "########"*(len(tools) + 1)*2
        for tool in tools:
            header += tool + "\t\t"
        print(header)
        print(header_line)

        # print each row
        line = "--------"*(len(tools) + 1)*2
        CVE_list = list()
        for key in tools['aflgo'][0]:
            if key != 'Tool' and key != 'Epoch':
                CVE_list.append(key)
        for CVE in CVE_list:
            row = CVE + "\t"
            for tool in tools:
                TTE = get_median_TTE(tools[tool], CVE)
                count = get_count(tools[tool], CVE)
                row += TTE + " (" + str(count) + ")" + "\t\t"
            print(row)
            print(line)

def main(file_path):
    parse_csv(file_path)

if __name__ == '__main__':
    file_path = sys.argv[1]
    main(file_path)
