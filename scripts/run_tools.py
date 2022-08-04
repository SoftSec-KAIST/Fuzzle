import os, sys
import json
import time
import subprocess

# FIX accordingly (num maximum cores)
NUM_WORKERS = 1

TOOLS = ['afl', 'afl++', 'aflgo', 'eclipser', 'fuzzolic']

# FIX accordingly (memory limit)
SPAWN_CMD = 'docker run --rm -m=8g --cpuset-cpus=%d -it -d --name %s %s'
CP_MAZE_CMD = 'docker cp %s %s:/home/maze/maze'
CP_CMD = 'docker cp %s:/home/maze/outputs %s'
COMPILE_CMD = 'gcc -fprofile-arcs -ftest-coverage -o %s %s'
REPLAY_CMD = 'cat %s | ./%s'
GCOV_CMD = 'gcov -b -c -s %s %s > %s'
CP_FRCON_CMD = 'docker cp %s:%s %s'
MOVE_CMD = 'mv %s %s'
REMOVE_CMD = 'rm %s %s %s %s'
KILL_CMD = 'docker kill %s'

def run_cmd(cmd_str):
    print("[*] Executing: %s" % cmd_str)
    cmd_args = cmd_str.split()
    try:
        subprocess.call(cmd_args)
    except Exception as e:
        print(e)
        exit(1)

def run_cmd_in_docker(container, cmd_str):
    print("[*] Executing (in container): %s" % cmd_str)
    cmd_prefix = "docker exec -d %s /bin/bash -c" %  container
    cmd_args = cmd_prefix.split()
    cmd_args += [cmd_str]
    try:
        subprocess.call(cmd_args)
    except Exception as e:
        print(e)
        exit(1)

def load_config(path):
    with open(path) as f:
        txt = f.read()
    conf = json.loads(txt)

    assert os.path.exists(conf['MazeList']) and os.path.isfile(conf['MazeList'])
    assert conf['Repeats'] > 0
    assert conf['Duration'] > 0
    assert os.path.exists(conf['MazeDir']) and os.path.isdir(conf['MazeDir'])
    for tool in conf['Tools']:
        assert tool in TOOLS

    return conf

def get_targets(conf):
    targets = []

    with open(conf['MazeList']) as f:
        for line in f.readlines():
            tokens = line.strip().split(',')
            algo, width, height, seed, num, cycle, gen = tokens[0], tokens[1], tokens[2], tokens[3], tokens[4], tokens[5], tokens[6]
            for tool in conf['Tools']:
                for epoch in range(conf['Repeats']):
                    target = algo, width, height, seed, num, cycle, gen, tool, epoch
                    targets.append(target)

    return targets

def fetch_works(targets):
    works = []
    for i in range(NUM_WORKERS):
        if len(targets) <= 0:
            break
        works.append(targets.pop(0))
    return works

def spawn_containers(conf, works):
    for i in range(len(works)):
        algo, width, height, seed, num, cycle, gen, tool, epoch = works[i]
        if tool == 'afl++':
            tool_ = 'aflpp'
        else:
            tool_ = tool
        image = 'maze-%s' % tool_
        container = '%s-%sx%s-%s-%s-%s-%s-%s-%d' % (algo, width, height, seed, num, cycle, gen, tool_, epoch)
        # Spawn a container
        cmd = SPAWN_CMD % (i, container, image)
        run_cmd(cmd)

        # Copy maze in the container
        cmd = CP_MAZE_CMD % (conf['MazeDir'], container)
        run_cmd(cmd)

def get_src_path(algo, width, height, seed, num, cycle, gen, tool):
    if tool == 'klee':
        src_path = '/home/maze/maze/src/%s_%sx%s_%s_%s_%s_%s_klee.c' % \
            (algo, width, height, seed, num, cycle, gen)
    else:
        src_path = '/home/maze/maze/src/%s_%sx%s_%s_%s_%s_%s.c' % \
            (algo, width, height, seed, num, cycle, gen)
    return src_path

def get_bin_path(algo, width, height, seed, num, cycle, gen):
    bin_path = '/home/maze/maze/bin/%s_%sx%s_%s_%s_%s_%s.bin' % (algo, width, height, seed, num, cycle, gen)
    return bin_path

def run_tools(conf, works):
    for i in range(len(works)):
        algo, width, height, seed, num, cycle, gen, tool, epoch = works[i]
        if tool == 'afl++':
            tool_ = 'aflpp'
        else:
            tool_ = tool
        container = '%s-%sx%s-%s-%s-%s-%s-%s-%d' % (algo, width, height, seed, num, cycle, gen, tool_, epoch)

        script = '/home/maze/tools/run_%s.sh' % tool
        src_path = get_src_path(algo, width, height, seed, num, cycle, gen, tool)
        bin_path = get_bin_path(algo, width, height, seed, num, cycle, gen)
        duration = conf['Duration']
        cmd = '%s %s %s %s' % (script, src_path, bin_path, duration)

        run_cmd_in_docker(container, cmd)

    time.sleep(duration*60 + 60) # sleep timeout + extra 1 min.

def store_outputs(conf, out_dir, works):
    # First, collect testcases in /home/maze/outputs
    for i in range(len(works)):
        algo, width, height, seed, num, cycle, gen, tool, epoch = works[i]
        if tool == 'afl++':
            tool_ = 'aflpp'
        else:
            tool_ = tool
        container = '%s-%sx%s-%s-%s-%s-%s-%s-%d' % (algo, width, height, seed, num, cycle, gen, tool_, epoch)

        cmd = 'python3 /home/maze/tools/get_tcs.py /home/maze/outputs'
        run_cmd_in_docker(container, cmd)

    time.sleep(60)

    # Next, store outputs to host filesystem
    for i in range(len(works)):
        algo, width, height, seed, num, cycle, gen, tool, epoch = works[i]
        if tool == 'afl++':
            tool_ = 'aflpp'
        else:
            tool_ = tool
        container = '%s-%sx%s-%s-%s-%s-%s-%s-%d' % (algo, width, height, seed, num, cycle, gen, tool_, epoch)

        maze = '%s-%sx%s-%s-%s-%s-%s' % (algo, width, height, seed, num, cycle, gen)
        out_path = os.path.join(out_dir, maze, '%s-%d' % (tool, epoch))
        os.system('mkdir -p %s' % out_path)
        cmd = CP_CMD % (container, out_path)
        run_cmd(cmd)

    time.sleep(60)

def store_coverage(conf, out_dir, works):
    # Measure coverage and save results
    for i in range(len(works)):
        algo, width, height, seed, num, cycle, gen, tool, epoch = works[i]
        if tool == 'afl++':
            tool_ = 'aflpp'
        else:
            tool_ = tool
        container = '%s-%sx%s-%s-%s-%s-%s-%s-%d' % (algo, width, height, seed, num, cycle, gen, tool_, epoch)
        maze = '%s_%sx%s_%s_%s_%s_%s' % (algo, width, height, seed, num, cycle, gen)
        maze_tool = maze + '_%s_%d' % (tool_, epoch)

        if tool == 'klee':
            is_klee = '_klee'
        else:
            is_klee = ''

        script = '/home/maze/tools/get_coverage.sh'
        tc_dir = '/home/maze/outputs'
        src_dir = '/home/maze/maze/src'
        src_name = maze + is_klee
        duration = conf['Duration']
        cmd = '%s %s %s %s %s %s' % (script, tc_dir, src_dir, src_name, maze_tool, duration)
        run_cmd_in_docker(container, cmd)

    time.sleep(60)

    # Store coverage results to host filesystem
    for i in range(len(works)):
        algo, width, height, seed, num, cycle, gen, tool, epoch = works[i]
        if tool == 'afl++':
            tool_ = 'aflpp'
        else:
            tool_ = tool
        container = '%s-%sx%s-%s-%s-%s-%s-%s-%d' % (algo, width, height, seed, num, cycle, gen, tool_, epoch)
        maze = '%s_%sx%s_%s_%s_%s_%s' % (algo, width, height, seed, num, cycle, gen)
        maze_tool = maze + '_%s_%d' % (tool_, epoch)

        cmd = CP_FRCON_CMD % (container, '/home/maze/outputs/cov_txt_' + maze_tool, out_dir)
        run_cmd(cmd)
        cmd = CP_FRCON_CMD % (container, '/home/maze/outputs/cov_gcov_' + maze_tool, out_dir)
        run_cmd(cmd)

    time.sleep(60)

def kill_containers(works):
    for i in range(len(works)):
        algo, width, height, seed, num, cycle, gen, tool, epoch = works[i]
        if tool == 'afl++':
            tool_ = 'aflpp'
        else:
            tool_ = tool
        container = '%s-%sx%s-%s-%s-%s-%s-%s-%d' % (algo, width, height, seed, num, cycle, gen, tool_, epoch)
        cmd = KILL_CMD % container
        run_cmd(cmd)

def main(conf_path, out_dir):
    os.system('mkdir -p %s' % out_dir)

    conf = load_config(conf_path)
    targets = get_targets(conf)

    while len(targets) > 0:
        works = fetch_works(targets)
        spawn_containers(conf, works)
        run_tools(conf, works)
        store_outputs(conf, out_dir, works)
        store_coverage(conf, out_dir, works)
        kill_containers(works)

if __name__ == '__main__':
    conf_path = sys.argv[1]
    out_dir = sys.argv[2]
    main(conf_path, out_dir)
