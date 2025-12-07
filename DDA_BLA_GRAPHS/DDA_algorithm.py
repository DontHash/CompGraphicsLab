#!/usr/bin/env python3
import glfw
from OpenGL.GL import *
import time


WIN_WIDTH, WIN_HEIGHT = 1100, 650
pixel_list = []  


def dda_raster(x0, y0, x1, y1):
    """DDA rasterization supporting any slope (variant)."""
    dx = x1 - x0
    dy = y1 - y0

    steps = int(max(abs(dx), abs(dy)))
    if steps == 0:
        # single point
        print("single-point ->", round(x0), round(y0))
        yield round(x0), round(y0)
        return

    x_step = dx / steps
    y_step = dy / steps

    x = x0
    y = y0

    for idx in range(steps + 1):
        
        print(f"TRACE {idx:04d} | pix=({round(x):4},{round(y):4}) | fx={x:7.3f}, fy={y:7.3f}")
        yield round(x), round(y)
        x += x_step
        y += y_step


def render_pixels():
    glClear(GL_COLOR_BUFFER_BIT)
    
    glPointSize(5)

    glBegin(GL_POINTS)
    
    glColor3f(1.0, 0.55, 0.10)
    for px, py in pixel_list:
        glVertex2i(px, py)
    glEnd()


def setup_projection():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    
    glOrtho(-40, WIN_WIDTH + 40, -40, WIN_HEIGHT + 40, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
    glClearColor(0.06, 0.04, 0.02, 1.0)


def run():
    global pixel_list

    if not glfw.init():
        raise RuntimeError("GLFW initialization failed (variant)")
    window = glfw.create_window(WIN_WIDTH, WIN_HEIGHT, "DDA Raster (variant)", None, None)
    if not window:
        glfw.terminate()
        raise RuntimeError("Window creation failed (variant)")

    glfw.make_context_current(window)
    setup_projection()

    print("\n++ DDA RASTER TRACE ++")
    print("Idx  | pixel (x,y) | float coords (x,y)")

   
    stream = dda_raster(60, 590, 1040, 90)
    last = time.time()

    while not glfw.window_should_close(window):
        glfw.poll_events()

        
        if time.time() - last >= 0.006:
            try:
                px, py = next(stream)
                pixel_list.append((px, py))
            except StopIteration:
                
                pass
            last = time.time()

        render_pixels()
        glfw.swap_buffers(window)

    glfw.terminate()


if __name__ == "__main__":
    run()