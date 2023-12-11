import sys
import numpy as np
import matplotlib.pyplot as plt
from mazelib import Maze
from mazelib.generate.BacktrackingGenerator import BacktrackingGenerator
from mazelib.generate.Kruskal import Kruskal
from mazelib.generate.Prims import Prims
from mazelib.generate.Wilsons import Wilsons
from mazelib.generate.Sidewinder import Sidewinder
from mazelib.solve.ShortestPath import ShortestPath
from mazelib.solve.BacktrackingSolver import BacktrackingSolver

def generate_maze(algorithm, width, height, seed, maze_exit):
    if seed == "NONE":
        m = Maze()
    else:
        m = Maze(int (seed))

    # choose a generator for maze
    if algorithm == "Backtracking":
        m.generator = BacktrackingGenerator(height, width)
    elif algorithm == "Kruskal":
        m.generator = Kruskal(height, width)
    elif algorithm == "Prims":
        m.generator = Prims(height, width)
    elif algorithm == "Wilsons":
        m.generator = Wilsons(height, width)
    elif algorithm == "Sidewinder":
        m.generator = Sidewinder(height, width)
    else:
        print("No such algorithm supported")
        exit(1)

    m.solver = ShortestPath()

    # default solution length = r*(M + N) where r=1.5 with 0.05 padding
    length_min = int(1.45*(2*width+2*height+2))
    length_max = int(1.55*(2*width+2*height+2))

    # default exit site
    height_bug = height*2
    width_bug = width*2 - 1

    # make a maze with a solution length within min-max range
    sol_len = 0
    while sol_len < length_min or sol_len > length_max:
        m.generate()
        m.start = (0, 1)
        m.grid[0][1] = 0
        if maze_exit == "random":
            height_bug = np.random.randint(2, height)*2 - 1
            width_bug = np.random.randint(2, width)*2 - 1
        m.end = (height_bug, width_bug)
        m.grid[height_bug][width_bug] = 0
        m.solve()
        sol_len = len(m.solutions[0])
    return m

#######################################################
# Code borrowed from mazelib, a Python library
# Title: mazelib
# Author: John Stilley
# Date: 2023/07/04
# Code version: 0.9.13
# Availabiltiy: https://github.com/john-science/mazelib
#######################################################

def find_neighbors(maze, cell):
    r, c = cell
    ns = []

    if r > 1 and not maze.grid[r - 1, c] and not maze.grid[r - 2, c]:
            ns.append((r - 2, c))
    if (
        r < maze.grid.shape[0] - 2
        and not maze.grid[r + 1, c]
        and not maze.grid[r + 2, c]
    ):
        ns.append((r + 2, c))
    if c > 1 and not maze.grid[r, c - 1] and not maze.grid[r, c - 2]:
        ns.append((r, c - 2))
    if (
        c < maze.grid.shape[1] - 2
        and not maze.grid[r, c + 1]
        and not maze.grid[r, c + 2]
    ):
        ns.append((r, c + 2))

    return ns

def is_deadend(maze, cell):
    neighbors = find_neighbors(maze, cell)
    if maze.grid[cell[0], cell[1]] == 1:
        return False
    elif len(neighbors) < 2:
        return True
    else:
        return False

#######################################################

# print grid to a file
def store_maze(maze, label):
    np.set_printoptions(threshold=sys.maxsize, linewidth=310)
    with open(label + ".txt", 'w') as f:
        print(maze.grid, file = f)

# print solution path to a file
def store_solution(maze, label, width, height):
    f = open(label + "_solution.txt", 'w')
    xy_to_num = dict()
    lis = list(range(width*height))
    for i in range(width*height):
        xy_to_num[(i // width, i % width)] = lis[i]
    for idx in range(len(maze.solutions[0])):
        if idx % 2 == 0:
            i = maze.solutions[0][idx][0]
            j = maze.solutions[0][idx][1]
            x = int((i-1)/2)
            y = int((j-1)/2)
            print(xy_to_num[(x, y)], file = f)
    f.close()

def get_path_len(maze, start, end):
    maze.solver = BacktrackingSolver()
    path_len = 0
    temp_start, temp_end = maze.start, maze.end
    # change the maze's entrance and exit
    maze.start, maze.end = start, end
    maze.solve()
    path_len = len(maze.solutions[0])
    # restore the original maze
    maze.start, maze.end = temp_start, temp_end
    return path_len

def find_targets(maze):
    targets = []
    for r in range(1, maze.grid.shape[0], 2):
        for c in range(1, maze.grid.shape[1], 2):
            cell = (r, c)
            # FIX: do not assume the start and end points are fixed
            if r == maze.start[0] + 1 and c == maze.start[1]:
                continue
            elif r == maze.end[0] - 1 and c == maze.end[1]:
                continue
            elif (is_deadend(maze, cell)):
                width = int((len(maze.grid[0]) - 1)/2)
                height = int((len(maze.grid) - 1)/2)
                length_min = int(1.45*(2*width+2*height+2))
                length_max = int(1.55*(2*width+2*height+2))
                path_len = get_path_len(maze, maze.start, cell)
                if path_len >= length_min and path_len <= length_max:
                    targets.append(cell)
    return targets

# Sort the target cells based on the distance from exit
def sort_targets(maze, targets):
    target_dist = dict()
    for target in targets:
        length = get_path_len(maze, target, maze.end)
        target_dist[target] = length
    targets = list(target_dist.keys())
    lengths = list(target_dist.values())
    sorted_length_index = np.argsort(lengths)
    sorted_dict = {targets[i]: lengths[i] for i in sorted_length_index}
    return list(sorted_dict.keys())

def get_func_idx(maze, cell):
    width = int((len(maze.grid[0]) - 1)/2)
    r, c = cell
    row = int((r - 1) / 2)
    col = int((c - 1) / 2)
    func_idx = row * width + col
    return str(func_idx)

def write_target(maze, target, filename):
    with open(filename, 'a') as f:
        print(get_func_idx(maze, target), file = f)

def store_targets(maze, label, num_targets, spread):
    filename = label + "_" + str(num_targets) + "_targets.txt"
    # one default at the exit
    write_target(maze, maze.end, filename)
    num_to_add =  num_targets - 1
    if num_to_add < 1:
        return
    targets = find_targets(maze)
    if len(targets) < num_to_add:
        print("ERROR: Cannot find enough targets." \
              "There are not enough dead-ends that are 'solution length' away from the entry point")
        exit(2)
    else:
        sorted_targets = sort_targets(maze, targets)
        if spread:
            sorted_targets.reverse()
            selected = list()
            while len(selected) < num_to_add:
                if len(sorted_targets) == 0:
                    print("ERROR: Cannot find enough targets." \
                          "The candidate dead-ends are too close to each other")
                    exit(2)
                next = sorted_targets.pop(0)
                selected.append(next)
                # check if the added cell is at least width away from all targets
                for s in selected:
                    dist = get_path_len(maze, next, s)
                    if dist < len(maze.grid[0]) - 1 and dist != 1:
                        selected.remove(next)
                        break
            for target in selected:
                write_target(maze, target, filename)
        else:
            for i in range(num_to_add):
                write_target(maze, sorted_targets[i], filename)

# generate a simple image of the maze
def show_png(maze, label):
    plt.figure(figsize=(width/10, height/10))
    plt.imshow(maze.grid, cmap=plt.cm.binary, interpolation='nearest')
    plt.xticks([]), plt.yticks([])
    plt.subplots_adjust(top = 1, bottom = 0, right = 1, left = 0, hspace = 0, wspace = 0)
    plt.margins(0,0)
    plt.savefig(label)

def main(algorithm, width, height, seed, maze_exit, num_targets):
    maze = generate_maze(algorithm, width, height, seed, maze_exit)
    label = algorithm + "_" + str(width) + "x" + str(height) + "_" + str(seed)
    store_maze(maze, label)
    store_solution(maze, label, width, height)
    store_targets(maze, label, num_targets, spread=True)
    show_png(maze, label)

if __name__ == '__main__':
    algorithm = sys.argv[1]
    width, height = int (sys.argv[2]), int (sys.argv[3])
    seed = sys.argv[4]
    maze_exit = sys.argv[5]
    num_targets = int(sys.argv[6])
    main(algorithm, width, height, seed, maze_exit, num_targets)
