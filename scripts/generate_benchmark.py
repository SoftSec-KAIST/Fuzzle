import sys
import subprocess

GEN_CMD = './generate.sh -o %s -a %s -w %s -h %s -r %s -n %s -c %s -g %s -s %s'

def run_cmd(cmd_str):
    print("[*] Executing: %s" % cmd_str)
    cmd_args = cmd_str.split()
    try:
        subprocess.call(cmd_args)
    except Exception as e:
        print(e)
        exit(1)

def get_mazes(file_path):
    with open(file_path, 'r') as f:
        mazes = []
        for maze in f:
            mazes.append(maze.strip('\n'))
    return mazes

def generate(mazes, out_dir):
    for maze in mazes:
        tokens = maze.split(',')
        algo, width, height, seed, numb = tokens[0], tokens[1], tokens[2], tokens[3], tokens[4]
        cycle = tokens[5].strip('percent')
        if 'CVE' in tokens[6]:
            gen = 'CVE_gen'
            smt = "../CVEs/" + tokens[6].split('_')[0] + ".smt2"
        else:
            gen = tokens[6]
            smt = "default"
        cmd = GEN_CMD % (out_dir, algo, width, height, seed, numb, cycle, gen, smt)
        run_cmd(cmd)

def main(file_path, out_dir):
    mazes = get_mazes(file_path)
    generate(mazes, out_dir)

if __name__ == '__main__':
    file_path = sys.argv[1]
    out_dir = sys.argv[2]
    main(file_path, out_dir)
