import sys
import csv
from collections import defaultdict

def get_files(file_list):
    with open(file_list, 'r') as f:
        filenames = []
        for file in f:
            filenames.append(file.strip('\n'))
        return filenames

def write_row_headers(writer):
    headers = ["Algorithm", "Size", "Seed", "Cycle Proportion",
     "Generator", "Tool", "Epoch", "Number of Hours",
     "Lines executed", "Branches executed", "Taken at least once",
     "Calls executed", "Time taken to first crash"]
    writer.writerow(headers)

def write_rows(writer, filenames):
    for file_path in filenames:
        with open(file_path) as f:
            row = []
            numb = 0
            for line in f:
                if numb == 0:
                    maze = file_path.split('/')[-1].strip('.txt\n').split('_')
                    for idx in range(len(maze)):
                        if idx < 2:
                            row.append(maze[idx])
                        elif idx == 2 or idx == 8:
                            row.append(int(maze[idx]))
                        elif idx == 4:
                            row.append(int(maze[idx].strip('percent')))
                        elif idx == 5 or idx == 7:
                            row.append(maze[idx])
                        elif idx == 9:
                            row.append(int(maze[idx].strip('hr')))
                    if len(maze) < 10:
                        row.append(0)
                if numb > 0 and numb < 5:
                    coverage = line.split(':')[1].split('%')[0]
                    row.append(float(coverage))
                elif numb == 7:
                    time_taken = line.strip('/home/maze/outputs/').split('_')[0]
                    row.append(float(time_taken))
                numb = numb + 1
        writer.writerow(row)

# group by parameter
def group_param(data, param):
    grouped = defaultdict(list)
    if param == "Algorithm":
        for row in data:
            grouped[row['Algorithm']].append(row)
    elif param == "Size":
        for row in data:
            grouped[row['Size']].append(row)
    elif param == "Cycle":
        for row in data:
                grouped[row['Cycle Proportion']].append(row)
    elif param == "Generator":
        for row in data:
                grouped[row['Generator']].append(row)
    else:
        print("Unsupported parameter")
        exit(1)
    return grouped

# get average branch coverage
def get_coverage(data):
    coverage_sum = 0.0
    for row in data:
        coverage_sum += float(row['Taken at least once'])
    average_cov = coverage_sum / len(data)
    return '%02.1f' % average_cov

# get bug finding success rate
def get_rate(data):
    total_bugs = 0
    for row in data:
        if row['Time taken to first crash'] != None and row['Time taken to first crash'] != '':
            total_bugs += 1
    average_percent = (total_bugs / len(data))*100
    return '%01.0f' % average_percent

# get average TTE
def get_TTE(data):
    TTE_sum = 0.0
    bug_count = 0
    for row in data:
        if row['Time taken to first crash'] != None and row['Time taken to first crash'] != '':
            TTE_sum += float(row['Time taken to first crash'])
            bug_count += 1
    if bug_count == 0:
        return '-'
    else:
        average_TTE = (TTE_sum / bug_count)/3600
        return '%02.2f' % average_TTE

def print_results_fuzzer(data, tool, param):
    print("##############################################")
    print("Fuzzer:\t\t" + tool)
    print("Varying:\t" + param)
    tool_data = group_param(data, param)
    for v in tool_data:
        print("----------------------------------------------")
        print(param + ":\t" + v)
        print("Coverage (%):\t" + get_coverage(tool_data[v]))
        print("Bugs (%):\t" + get_rate(tool_data[v]))
        print("TTE (h):\t" + get_TTE(tool_data[v]))

def sort_values(values):
    values_int = set()
    values_str = list()
    for v in values:
        values_int.add(int(v))
    values_int = sorted(values_int)
    for v in values_int:
        values_str.append(str(v))
    return values_str

def get_param_values(param, tools):
    param_values = set()
    if param == "Cycle":
        param_t = "Cycle Proportion"
    else:
        param_t = param
    for tool in tools:
        for run in tools[tool]:
            param_values.add(run[param_t])
    if param == "Cycle":
        param_values = sort_values(param_values)
    else:
        param_values = sorted(param_values)
    return param_values

def print_measurement(metric, line_header):
    print("\nMeasure:\t" + metric)
    print(line_header)

def print_headers(param, values):
    print("Tool\t\t" + param)
    header = ""
    if param == "Size" or param == "Cycle":
        for v in values:
            header += v + "\t\t"
    else:
        for v in values:
            if v == 'Kruskal' or v == 'Prims':
                header += v + "\t\t"
            else:
                header += v + "\t"
    print("\t\t" + header)

def get_tool(data, tool, param):
    if tool == 'eclipser' or tool == 'fuzzolic':
        row = tool + "\t"
    else:
        row = tool + "\t\t"
    tool_data = group_param(data, param)
    return tool_data, row

def print_coverage(data, tool, param, values):
    tool_data, row = get_tool(data, tool, param)
    for v in values:
        if v in tool_data:
            row += get_coverage(tool_data[v])
        else:
            row += '-'
        row += '\t\t'
    print(row)

def print_bugs(data, tool, param, values):
    tool_data, row = get_tool(data, tool, param)
    for v in values:
        if v in tool_data:
            row += get_rate(tool_data[v])
        else:
            row += '-'
        row += '\t\t'
    print(row)

def print_TTE(data, tool, param, values):
    tool_data, row = get_tool(data, tool, param)
    for v in values:
        if v in tool_data:
            row += get_TTE(tool_data[v])
        else:
            row += '-'
        row += '\t\t'
    print(row)

def print_results_paper(tools, param):
    param_values = get_param_values(param, tools)
    numb_param = len(param_values)
    line_header ="########"*(2 + numb_param*2)
    line = "--------"*(2 + numb_param*2)

    # print coverage results
    print_measurement("Coverage (%)", line_header)
    print_headers(param, param_values)
    print(line)
    for tool in tools:
        print_coverage(tools[tool], tool, param, param_values)
        print(line)

    # print bugs results
    print_measurement("Bugs (%)", line_header)
    print_headers(param, param_values)
    print(line)
    for tool in tools:
        print_bugs(tools[tool], tool, param, param_values)
        print(line)

    # print TTE results
    print_measurement("TTE (h)", line_header)
    print_headers(param, param_values)
    print(line)
    for tool in tools:
        print_TTE(tools[tool], tool, param, param_values)
        print(line)

def parse_csv(file_path, param, time, mode):
    with open(file_path, 'r') as f:
        csv_reader = csv.DictReader(f)

        # filter data by time
        data = []
        for row in csv_reader:
            if row['Number of Hours'] == time:
                data.append(row)

        # group by fuzzer
        tools = defaultdict(list)
        for row in data:
            tools[row['Tool']].append(row)

        param_list = ["Algorithm", "Size", "Cycle", "Generator"]
        # print results for each fuzzer
        if mode == 'fuzzer':
            for tool in tools:
                if param == "ALL":
                    for p in param_list:
                        print_results_fuzzer(tools[tool], tool, p)
                elif '+' in param:
                    params = param.split('+')
                    assert len(params) == 2
                    tool_data = group_param(tools[tool], params[0])
                    for first_param in tool_data:
                        print("##############################################")
                        print(params[0] + ":\t" + first_param)
                        print_results_fuzzer(tool_data[first_param], tool, params[1])
                else:
                    print_results_fuzzer(tools[tool], tool, param)

        # print results for each metric
        elif mode == 'paper':
            if param == "ALL":
                for p in param_list:
                    print_results_paper(tools, p)
            elif '+' in param:
                params = param.split('+')
                assert len(params) == 2
                first_param_values = get_param_values(params[0], tools)
                second_param_values = get_param_values(params[1], tools)
                numb_param = len(second_param_values)
                line_header ="########"*(2 + numb_param*2)
                grouped = defaultdict(list)
                for p in first_param_values:
                    for d in data:
                        if d[params[0]] == p:
                            grouped[p].append(d)
                for p in first_param_values:
                    print("\n" + line_header)
                    print("\t\t" + p)
                    print(line_header)
                    tools_grouped = defaultdict(list)
                    for row in grouped[p]:
                        tools_grouped[row['Tool']].append(row)
                    print_results_paper(tools_grouped, params[1])
            else:
                print_results_paper(tools, param)
        else:
            print("Unsupported print mode")
            exit(1)

def main(file_list, out_path, param, time, mode):
    filenames = get_files(file_list)
    f = open(out_path, 'w')
    writer = csv.writer(f)
    write_row_headers(writer)
    write_rows(writer, filenames)
    f.close()
    parse_csv(out_path, param, time, mode)

if __name__ == '__main__':
    file_list = sys.argv[1]
    out_path = sys.argv[2] + '.csv'
    param = sys.argv[3]
    time = sys.argv[4]
    mode = sys.argv[5]
    main(file_list, out_path, param, time, mode)
