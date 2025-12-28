
import glfw
from OpenGL.GL import *
import time


WIN_WIDTH, WIN_HEIGHT = 1200, 700
plot_points = []  


def bresenham_line(x0, y0, x1, y1):
    """Bresenham's line algorithm with support for all slopes."""
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    x, y = x0, y0

    sx = 1 if x1 >= x0 else -1
    sy = 1 if y1 >= y0 else -1

    
    if dx > dy:  
        decision = 2 * dy - dx
        for step in range(dx + 1):
            print(f"> step#{step:04d} -> coord=({x:4},{y:4})  decision={decision:4d}")
            yield x, y
            x += sx
            if decision >= 0:
                y += sy
                decision += 2 * (dy - dx)
            else:
                decision += 2 * dy
    else:  
        decision = 2 * dx - dy
        for step in range(dy + 1):
            print(f"> step#{step:04d} -> coord=({x:4},{y:4})  decision={decision:4d}")
            yield x, y
            y += sy
            if decision >= 0:
                x += sx
                decision += 2 * (dx - dy)
            else:
                decision += 2 * dx


def render_pixels():
    glClear(GL_COLOR_BUFFER_BIT)
    glPointSize(4)

    glBegin(GL_POINTS)
    
    glColor3f(0.18, 0.80, 0.40)
    for px, py in plot_points:
        glVertex2i(px, py)
    glEnd()


def setup_projection():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(-60, WIN_WIDTH + 60, -60, WIN_HEIGHT + 60, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glClearColor(0.04, 0.06, 0.10, 1)


def run():
    global plot_points

    if not glfw.init():
        raise RuntimeError("Failed to initialize GLFW")
    window = glfw.create_window(WIN_WIDTH, WIN_HEIGHT, "Bresenham (Variant)", None, None)
    if not window:
        glfw.terminate()
        raise RuntimeError("Failed to create window")

    glfw.make_context_current(window)
    setup_projection()

    print("\n### BRESENHAM TRACE (variant) ###")
    print("Idx  |   coordinate   |  decision param")

    
    stream = bresenham_line(50, 600, 1150, 120)
    last = time.time()

    
    while not glfw.window_should_close(window):
        glfw.poll_events()

        if time.time() - last >= 0.005:
            try:
                px, py = next(stream)
                plot_points.append((px, py))
            except StopIteration:
                
                pass
            last = time.time()

        render_pixels()
        glfw.swap_buffers(window)

    glfw.terminate()


if __name__ == "__main__":
    run()