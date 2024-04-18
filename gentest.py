import numpy as np

def draw_line(grid, p0, p1):
    x0, y0 = p0
    x1, y1 = p1
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy

    while True:
        # Set pixel at current position
        if 0 <= x0 < len(grid) and 0 <= y0 < len(grid[x0]):
            grid[x0][y0] = 1  # You may need to adjust this to match your LED matrix library

        if x0 == x1 and y0 == y1:
            break

        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy


def print_grid(grid):
    # for row in grid:
    #     print(''.join(['*' if pixel else ' ' for pixel in row]))

    print(np.flip(np.array(grid).T,0))


def bits2byte(bit_list):
        if len(bit_list) != 8:
            raise ValueError("Length of bit list must be 8")
        out = 0
        for bit in bit_list:
            out = (out << 1) | bit

        return out

def conv_frame(frame):
    out = []
    for row in frame:
        byte_val = bits2byte(row)
        out.append(byte_val)
    return out

def gen_one(angles):
    L1 = 5
    L2 = 6
    ORIG = 5, 1
    ORIG_LEFT = ORIG[0] - 1, ORIG[1]

    _, j2, j3 = angles

    p1 = round(ORIG[0] + L1*np.cos(j2)), round(ORIG[1] + L1*np.sin(j2))
    p1_left = p1[0] -1, p1[1]
    p2 = round(p1[0] + L2*np.cos(j2 + j3)), round(p1[1] + L2*np.sin(j2 + j3))
    p3 = p2[0], p2[1]-1

    grid = [[0] * 8 for _ in range(16)]
    draw_line(grid, (2, 0), (7, 0))
    draw_line(grid, (2, 1), (7, 1))
    
    draw_line(grid, ORIG, p1)
    draw_line(grid, ORIG_LEFT, p1_left)
    draw_line(grid, p1, p2)
    draw_line(grid, p2, p3)

    return grid





grid = gen_one((0, np.pi/2, -np.pi/2))
print(grid)
print_grid(grid)
print(conv_frame(grid))

def gen():
    L1 = 5
    L2 = 6
    ORIG = 5, 1

    frames = []

    for j1 in np.linspace(0, np.pi, 10):
        for j2 in np.linspace(-np.pi, 0, 10):
            if j1 + j2 > np.pi * (0.1):
                continue
            p1 = ORIG[0] + L1*np.cos(j1), ORIG[1] + L1*np.sin(j1)
            p1_left = ORIG[0] - 1 + L1*np.cos(j1), ORIG[1] + L1*np.sin(j1)
            p2 = p1[0] + L2*np.cos(j1 + j2), p1[1] + L2*np.sin(j1 + j2)

            grid = [[0] * 8 for _ in range(16)]
            draw_line(grid, 2, 0, 7, 0)  # Draw a line from (1, 2) to (6, 12)
            draw_line(grid, 2, 1, 7, 1)
            draw_line(grid, ORIG[0], ORIG[1], round(p1[0]), round(p1[1]))  # Draw a line from (1, 2) to (6, 12)
            draw_line(grid, ORIG[0] - 1, ORIG[1] - 1, round(p1_left[0]), round(p1_left[1]))
            draw_line(grid, round(p1[0]), round(p1[1]), round(p2[0]), round(p2[1]))
            print_grid(grid)
            print()
            frames.append(conv_frame(grid))
    return frames