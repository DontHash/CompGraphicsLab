import glfw
import time
from OpenGL.GL import *
import numpy as np

WIN_W, WIN_H = 800, 600

def make_scale(sx, sy):
    return np.array([[sx, 0.0, 0.0],
                     [0.0, sy, 0.0],
                     [0.0, 0.0, 1.0]], dtype=float)

def make_rotate(degrees):
    r = np.radians(degrees)
    return np.array([[np.cos(r), -np.sin(r), 0.0],
                     [np.sin(r),  np.cos(r), 0.0],
                     [0.0,        0.0,       1.0]], dtype=float)

def make_shear(shx, shy):
    # shear matrix (x shear, y shear)
    return np.array([[1.0, shx, 0.0],
                     [shy, 1.0, 0.0],
                     [0.0, 0.0, 1.0]], dtype=float)

def make_translate(tx, ty):
    return np.array([[1.0, 0.0, tx],
                     [0.0, 1.0, ty],
                     [0.0, 0.0, 1.0]], dtype=float)

def draw_polygon(v, filled=True, color=(0.0, 0.5, 1.0)):
    # v is 3xN homogeneous coordinates
    if filled:
        glBegin(GL_POLYGON)
    else:
        glBegin(GL_LINE_LOOP)
    glColor3f(*color)
    for p in v.T:
        glVertex2f(p[0], p[1])
    glEnd()

def draw_axes(size=1.0):
    glColor3f(0.8, 0.8, 0.8)
    glBegin(GL_LINES)
    # X axis
    glVertex2f(-size, 0.0); glVertex2f(size, 0.0)
    # Y axis
    glVertex2f(0.0, -size); glVertex2f(0.0, size)
    glEnd()

def ease_in_out(t):
    # smoothstep-like easing: 3t^2 - 2t^3
    return t * t * (3 - 2 * t)

def main():
    if not glfw.init():
        print("Failed to initialize GLFW")
        return

    win = glfw.create_window(WIN_W, WIN_H, "Composite Transform — Variant", None, None)
    if not win:
        glfw.terminate()
        print("Failed to create window")
        return

    glfw.make_context_current(win)
    glViewport(0, 0, WIN_W, WIN_H)
    glMatrixMode(GL_PROJECTION); glLoadIdentity(); glOrtho(-1, 1, -1, 1, -1, 1)
    glMatrixMode(GL_MODELVIEW)

  
    square = np.array([
        [-0.2,  0.2,  0.2, -0.2],   # x
        [ 0.2,  0.2, -0.2, -0.2],   # y
        [ 1.0,  1.0,  1.0,  1.0]
    ], dtype=float)

    # Different transform parameters than the original:
    S = make_scale(1.2, 0.9)         # slightly different non-uniform scale
    R = make_rotate(45.0)           # rotate 45 degrees instead of 30
    Sh = make_shear(-0.4, 0.2)      # shear with negative x-shear
    T = make_translate(-0.25, 0.15) # translate in different direction

    # Composite matrix: translate @ rotate @ scale @ shear
    M = T @ R @ S @ Sh
    transformed = M @ square

    print("\nInitial coords:\n", square[:2].T)
    print("\nComposite matrix:\n", M)
    print("\nTransformed coords:\n", transformed[:2].T)

    glClearColor(0.1, 0.1, 0.1, 1.0)
    paused = False
    direction = 1  # 1 forward, -1 backwards
    duration = 1.6  # seconds for one-way animation
    t0 = glfw.get_time()

    # GLFW key callback to pause/unpause and close on ESC
    def key_cb(window, key, scancode, action, mods):
        nonlocal paused
        if key == glfw.KEY_SPACE and action == glfw.PRESS:
            paused = not paused
        if key == glfw.KEY_ESCAPE and action == glfw.PRESS:
            glfw.set_window_should_close(window, True)

    glfw.set_key_callback(win, key_cb)

    while not glfw.window_should_close(win):
        now = glfw.get_time()
        if not paused:
            elapsed = now - t0
        else:
            # if paused, keep elapsed frozen by not updating t0
            elapsed = (now - t0)  # but we'll not advance t0 until unpaused

        # normalized progress in [0,1]
        raw_t = (elapsed % duration) / duration
        # If we want ping-pong, flip with direction based on whole cycles
        cycle = int((elapsed // duration))
        if cycle % 2 == 1:
            raw_t = 1.0 - raw_t

        t = ease_in_out(raw_t)  # smooth interpolation value

        # Interpolate between original and transformed
        interp = (1.0 - t) * square + t * transformed

        glClear(GL_COLOR_BUFFER_BIT)
        glLoadIdentity()

        # draw axes
        draw_axes(1.0)

        # draw original outline in light color
        draw_polygon(square, filled=False, color=(0.9, 0.9, 0.9))

        # draw interpolated filled polygon with a color that shifts slightly with t
        color = (0.0 + 0.6 * t, 0.4, 0.8 - 0.4 * t)
        draw_polygon(interp, filled=True, color=color)

        glfw.swap_buffers(win)
        glfw.poll_events()

        # simple frame cap
        time.sleep(1.0 / 120.0)

    glfw.terminate()

if __name__ == "__main__":
    main()