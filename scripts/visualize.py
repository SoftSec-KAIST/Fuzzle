import sys
import matplotlib.pyplot as plt
from PIL import Image

def scale_maze(maze_txt):
    wall, not_wall = '4', '1'
    with open(maze_txt, 'r+') as f:
        maze = f.read().replace('1', wall).replace('0', not_wall)
    return maze

def get_matrix(maze_txt):
    maze = scale_maze(maze_txt)
    rows = maze.split('\n')
    matrix = []
    for row in rows:
        matrix_row = []
        for c in row:
            matrix_row.append(int(c))
        if len(matrix_row) != 0:
            matrix.append(matrix_row)
    return matrix

def visualize_coverage(matrix, gcov_file, size):
    functions = list()
    custom = list()
    with open (gcov_file, 'r') as cov:
        for line in cov:
            if line.startswith("function func_bug"):
                bug_found = int(line.split(' ')[3])
            elif line.startswith("function func_start"):
                started = int(line.split(' ')[3])
            elif line.startswith("function func_"):
                functions.append(line)
            elif "flag == 1" in line:
                taken = cov.readline()
                not_taken = cov.readline()
                func_to = (cov.readline().split("_")[1].split("(")[0])
                if func_to == 'bug':
                    func_to = len(functions) - 1 + size
                else:
                    func_to = int(func_to)
                func_from = len(functions) - 1
                custom.append((func_from, func_to))

    numb_called = list()
    for idx in range(size*size):
        numb_called.append(int(functions[idx].split(' ')[3]))

    for i in range(size*size):
        if numb_called[i] == 0:
            matrix[2*int(i/size)+1][2*(i%size)+1] = 0
        else:
            matrix[2*int(i/size)+1][2*(i%size)+1] = 3

    for i in range(size*2+1):
        for j in range(size*2+1):
            if matrix[i][j] == 1:
                nodes = list()
                if i-1 > 0:
                    nodes.append(matrix[i-1][j])
                if j-1 > 0:
                    nodes.append(matrix[i][j-1])
                if i+1 < len(matrix):
                    nodes.append(matrix[i+1][j])
                if j+1 < len(matrix[0]):
                    nodes.append(matrix[i][j+1])
                matrix[i][j] = min(nodes)

    for edge in custom:
        if edge[1] == edge[0] + 1:
            matrix[2*int(int(edge[0])/size)+1][2*(int(edge[0])%size)+2] = 1
        elif edge[1] == edge[0] - 1:
            matrix[2*int(int(edge[0])/size)+1][2*(int(edge[0])%size)] = 1
        elif edge[1] == edge[0] + size:
            matrix[2*int(int(edge[0])/size)+2][2*(int(edge[0])%size)+1] = 1
        elif edge[1] == edge[0] - size:
            matrix[2*int(int(edge[0])/size)][2*(int(edge[0])%size)+1] = 1

    if bug_found == 0:
        matrix[size*2][size*2-1] = 0
    else:
        matrix[size*2][size*2-1] = 3

def fix_colours(out_path):
    img = Image.open(out_path + ".png")
    img = img.convert("RGBA")
    pix = img.load()
    for y in range(img.size[1]):
        for x in range(img.size[0]):
            if pix[x, y] == (0, 104, 55, 255):
                pix[x, y] = (0, 0, 0, 255)
            elif pix[x, y] == (183, 224, 117, 255):
                pix[x, y] = (0, 104, 55, 255)
    img.save(out_path + ".png")
    img.close()

def save_image(grid, out_path):
    plt.figure(figsize=(5, 5))
    plt.imshow(grid, cmap=plt.cm.RdYlGn, interpolation='nearest')
    plt.xticks([]), plt.yticks([])
    plt.subplots_adjust(top = 1, bottom = 0, right = 1, left = 0, hspace = 0, wspace = 0)
    plt.margins(0,0)
    plt.savefig(out_path)
    fix_colours(out_path)

def main(maze_txt, gcov_file, out_path, size):
    matrix = get_matrix(maze_txt)
    visualize_coverage(matrix, gcov_file, size)
    save_image(matrix, out_path)

if __name__ == '__main__':
    maze_txt = sys.argv[1]
    gcov_file = sys.argv[2]
    out_path = sys.argv[3]
    size = int(sys.argv[4])
    main(maze_txt, gcov_file, out_path, size)
