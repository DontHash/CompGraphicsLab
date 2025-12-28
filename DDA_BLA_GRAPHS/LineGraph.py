#!/usr/bin/env python3
import glfw
from OpenGL.GL import *
import time
import random


WIDTH, HEIGHT = 1000, 600
points_buffer = []  


def dda_segment(x0, y0, x1, y1, tag=""):
    dx = x1 - x0
    dy = y1 - y0
    steps = int(max(abs(dx), abs(dy)))

    if steps == 0:
        rx, ry = int(round(x0)), int(round(y0))
        print(f"[{tag}] single -> ({rx},{ry})")
        yield rx, ry
        return

    sx = dx / steps
    sy = dy / steps
    x = x0
    y = y0

    for i in range(steps + 1):
        rx, ry = int(round(x)), int(round(y))
        print(f"SEG {tag} | step={i:04d} | float=(x={x:7.4f}, y={y:7.4f}) -> int=({rx:4d},{ry:4d})")
        yield rx, ry
        x += sx
        y += sy


def draw_scene():
    glClear(GL_COLOR_BUFFER_BIT)
    glPointSize(6)

    
    glBegin(GL_POINTS)
    glColor3f(0.85, 0.95, 0.20)  
    for px, py in points_buffer:
        glVertex2i(px, py)
    glEnd()

    
    glBegin(GL_LINE_STRIP)
    glColor3f(0.55, 0.20, 0.75)  # violet
    for px, py in points_buffer:
        glVertex2i(px, py)
    glEnd()


def configure_projection():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    
    glOrtho(-50, WIDTH + 50, -50, HEIGHT + 50, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
    glClearColor(0.10, 0.09, 0.12, 1.0)


def run():
    global points_buffer

    if not glfw.init():
        raise RuntimeError("GLFW initialization error")
    window = glfw.create_window(WIDTH, HEIGHT, "DDA Graph (alternative)", None, None)
    if not window:
        glfw.terminate()
        raise RuntimeError("Window creation failed")

    glfw.make_context_current(window)
    configure_projection()

    
    N = 20
    margin = 70
    x_spacing = (WIDTH - 2 * margin) / (N - 1)
    
    data = [random.randint(80, HEIGHT - 80) for _ in range(N)]

    print("\n>>> DDA GRAPH TRACE (alternative) <<<")
    print("Format: SEG <id> | step=#### | float=(x=..., y=...) -> int=(x,y)")

   
    segment_generators = []
    for idx in range(N - 1):
        x0 = margin + idx * x_spacing
        y0 = data[idx]
        x1 = margin + (idx + 1) * x_spacing
        y1 = data[idx + 1]
        tag = f"{idx}->{idx+1}"
        segment_generators.append(dda_segment(x0, y0, x1, y1, tag=tag))

    last = time.time()
    seg_idx = 0

   
    tick = 0.0055

    while not glfw.window_should_close(window):
        glfw.poll_events()

        if time.time() - last >= tick:
            if seg_idx < len(segment_generators):
                try:
                    points_buffer.append(next(segment_generators[seg_idx]))
                except StopIteration:
                    seg_idx += 1
            last = time.time()

        draw_scene()
        glfw.swap_buffers(window)

    glfw.terminate()


if __name__ == "__main__":
    run()