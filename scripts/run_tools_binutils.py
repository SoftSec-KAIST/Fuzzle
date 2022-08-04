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
            app = tokens[0]
            for tool in conf['Tools']:
                for epoch in range(conf['Repeats']):
                    target = app, tool, epoch
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
        app, tool, epoch = works[i]
        if tool == 'afl++':
            tool_ = 'aflpp'
        else:
            tool_ = tool
        image = 'maze-%s' % tool_
        container = '%s-%s-%d' % (app, tool_, epoch)
        # Spawn a container
        cmd = SPAWN_CMD % (i, container, image)
        run_cmd(cmd)

        # Copy maze in the container
        cmd = CP_MAZE_CMD % (conf['MazeDir'], container)
        run_cmd(cmd)

def get_src_path(app):
    return "src"

def get_bin_path(app):
    bin_path = '/home/maze/maze/%s' % (app)
    return bin_path

def run_tools(conf, works):
    for i in range(len(works)):
        app, tool, epoch = works[i]
        if tool == 'afl++':
            tool_ = 'aflpp'
        else:
            tool_ = tool
        container = '%s-%s-%d' % (app, tool_, epoch)

        script = '/home/maze/tools/run_%s.sh' % tool
        src_path = get_src_path(app)
        bin_path = get_bin_path(app)
        duration = conf['Duration']
        cmd = '%s %s %s %s' % (script, src_path, bin_path, duration)

        run_cmd_in_docker(container, cmd)

    time.sleep(duration*60 + 60) # sleep timeout + extra 1 min.

def store_outputs(conf, out_dir, works):
    # First, collect testcases in /home/maze/outputs
    for i in range(len(works)):
        app, tool, epoch = works[i]
        if tool == 'afl++':
            tool_ = 'aflpp'
        else:
            tool_ = tool
        container = '%s-%s-%d' % (app, tool_, epoch)

        cmd = 'python3 /home/maze/tools/get_tcs.py /home/maze/outputs'
        run_cmd_in_docker(container, cmd)

    time.sleep(60)

    # Next, store outputs to host filesystem
    for i in range(len(works)):
        app, tool, epoch = works[i]
        if tool == 'afl++':
            tool_ = 'aflpp'
        else:
            tool_ = tool
        container = '%s-%s-%d' % (app, tool_, epoch)

        maze = '%s' % (app)
        out_path = os.path.join(out_dir, maze, '%s-%d' % (tool, epoch))
        os.system('mkdir -p %s' % out_path)
        cmd = CP_CMD % (container, out_path)
        run_cmd(cmd)

    time.sleep(60)

def kill_containers(works):
    for i in range(len(works)):
        app, tool, epoch = works[i]
        if tool == 'afl++':
            tool_ = 'aflpp'
        else:
            tool_ = tool
        container = '%s-%s-%d' % (app, tool_, epoch)
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
        kill_containers(works)

if __name__ == '__main__':
    conf_path = sys.argv[1]
    out_dir = sys.argv[2]
    main(conf_path, out_dir)
