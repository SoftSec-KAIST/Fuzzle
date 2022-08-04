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

# generate a simple image of the maze
def show_png(maze, label):
    plt.figure(figsize=(width/10, height/10))
    plt.imshow(maze.grid, cmap=plt.cm.binary, interpolation='nearest')
    plt.xticks([]), plt.yticks([])
    plt.subplots_adjust(top = 1, bottom = 0, right = 1, left = 0, hspace = 0, wspace = 0)
    plt.margins(0,0)
    plt.savefig(label)

def main(algorithm, width, height, seed, maze_exit, index):
    maze = generate_maze(algorithm, width, height, seed, maze_exit)
    label = algorithm + "_" + str(width) + "x" + str(height) + "_" + str(seed) + "_" + index
    store_maze(maze, label)
    store_solution(maze, label, width, height)
    show_png(maze, label)

if __name__ == '__main__':
    algorithm = sys.argv[1]
    width, height = int (sys.argv[2]), int (sys.argv[3])
    seed = sys.argv[4]
    maze_exit = sys.argv[5]
    index = sys.argv[6]
    main(algorithm, width, height, seed, maze_exit, index)
