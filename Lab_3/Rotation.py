
import glfw
import time
import numpy as np
from OpenGL.GL import *

WIN_W, WIN_H = 800, 600

def make_translate(tx, ty):
    return np.array([[1.0, 0.0, tx],
                     [0.0, 1.0, ty],
                     [0.0, 0.0, 1.0]], dtype=float)

def make_rotate_deg(deg):
    r = np.radians(deg)
    c, s = np.cos(r), np.sin(r)
    return np.array([[c, -s, 0.0],
                     [s,  c, 0.0],
                     [0.0, 0.0, 1.0]], dtype=float)

def draw_square(v, color=(0.0, 0.5, 1.0, 1.0), outline=False):
    if outline:
        glBegin(GL_LINE_LOOP)
    else:
        glBegin(GL_QUADS)
    glColor4f(*color)
    for p in v.T:
        glVertex2f(p[0], p[1])
    glEnd()

def draw_axes(size=1.0):
    glColor3f(0.6, 0.6, 0.6)
    glBegin(GL_LINES)
    glVertex2f(-size, 0.0); glVertex2f(size, 0.0)
    glVertex2f(0.0, -size); glVertex2f(0.0, size)
    glEnd()

def to_homog(points2d):
    """points2d: (2, N) -> (3, N) homogeneous"""
    ones = np.ones((1, points2d.shape[1]), dtype=float)
    return np.vstack([points2d, ones])

def from_homog(points3d):
    return points3d[:2] / points3d[2]

def main():
    if not glfw.init():
        print("GLFW init failed")
        return

    win = glfw.create_window(WIN_W, WIN_H, "2D Rotation (Homogeneous) — Variant", None, None)
    if not win:
        glfw.terminate(); print("Window creation failed"); return

    glfw.make_context_current(win)
    glViewport(0, 0, WIN_W, WIN_H)
    glMatrixMode(GL_PROJECTION); glLoadIdentity(); glOrtho(-1, 1, -1, 1, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glClearColor(0.08, 0.08, 0.10, 1.0)

    # Original square in homogeneous coordinates (3x4)
    orig_sq = np.array([[-0.2, 0.2, 0.2, -0.2],
                        [ 0.2, 0.2,-0.2, -0.2],
                        [ 1.0, 1.0, 1.0,  1.0]], dtype=float)

    # Useful points for pivots
    origin_pivot = (0.0, 0.0)
    # compute geometric center of square
    center_xy = (orig_sq[0].mean(), orig_sq[1].mean())
    custom_pivot = (0.4, 0.15)

    pivots = [
        ("Origin", origin_pivot),
        ("Square center", center_xy),
        ("Custom (0.4, 0.15)", custom_pivot)
    ]
    pivot_idx = 0

    # animation state
    angle_deg = 0.0                 # current angle in degrees
    angular_speed = 90.0            # degrees per second
    direction = 1                   # 1 or -1
    paused = False
    trail = []                      # list of transformed squares (3x4 arrays)
    max_trail = 60

    print("\n=== INITIAL COORDINATES ===")
    for i in range(4):
        print(f"V{i+1}: ({orig_sq[0,i]:.3f}, {orig_sq[1,i]:.3f})")
    print("\nStarting rotation demo...")

    last_time = glfw.get_time()

    def key_cb(window, key, scancode, action, mods):
        nonlocal paused, angular_speed, direction, pivot_idx, angle_deg, trail
        if action != glfw.PRESS and action != glfw.REPEAT:
            return
        if key == glfw.KEY_SPACE:
            paused = not paused
            if not paused:
                # reset baseline time so motion resumes smoothly
                nonlocal last_time
                last_time = glfw.get_time()
        elif key == glfw.KEY_LEFT:
            direction = -1
        elif key == glfw.KEY_RIGHT:
            direction = 1
        elif key == glfw.KEY_UP:
            angular_speed = min(720.0, angular_speed + 15.0)
        elif key == glfw.KEY_DOWN:
            angular_speed = max(5.0, angular_speed - 15.0)
        elif key == glfw.KEY_C:
            pivot_idx = (pivot_idx + 1) % len(pivots)
            print(f"Pivot -> {pivots[pivot_idx][0]}")
        elif key == glfw.KEY_R:
            angle_deg = 0.0
            trail.clear()
            print("Reset angle and trail.")
        elif key == glfw.KEY_ESCAPE:
            glfw.set_window_should_close(window, True)

    glfw.set_key_callback(win, key_cb)

    # initial print of rotation matrix for 1 degree as in original program
    R1 = make_rotate_deg(1.0)
    print("\n=== ROTATION MATRIX (1°) ===\n", R1, "\nAnimation running...\n")

    # main loop
    while not glfw.window_should_close(win):
        now = glfw.get_time()
        dt = now - last_time
        last_time = now

        glfw.poll_events()

        if not paused:
            angle_deg += direction * angular_speed * dt

        # Build rotation about the chosen pivot: T(p) * R(angle) * T(-p)
        pivot_name, pivot_coords = pivots[pivot_idx]
        px, py = pivot_coords
        T1 = make_translate(-px, -py)
        R = make_rotate_deg(angle_deg)
        T2 = make_translate(px, py)
        M = T2 @ R @ T1

        transformed = M @ orig_sq

        # maintain trail (store 2x4 floats for drawing or store homogeneous)
        trail.append(transformed.copy())
        if len(trail) > max_trail:
            trail.pop(0)

        # render
        glClear(GL_COLOR_BUFFER_BIT)
        glLoadIdentity()

        draw_axes(1.0)
        # draw original outline
        draw_square(orig_sq, color=(0.9,0.9,0.9,1.0), outline=True)

        # draw faded trail
        n = len(trail)
        for i, tmat in enumerate(trail):
            alpha = 0.15 + 0.85 * (i+1) / max(1, n)
            col = (0.0, 0.5, 1.0, alpha * 0.6)
            draw_square(tmat, color=col)

        # draw current transformed square (solid)
        draw_square(transformed, color=(0.0, 0.6, 0.9, 1.0))

        # draw pivot marker
        glPointSize(6.0)
        glBegin(GL_POINTS)
        glColor3f(1.0, 0.4, 0.1)
        glVertex2f(px, py)
        glEnd()

        glfw.swap_buffers(win)

        # small sleep to cap CPU usage
        time.sleep(1.0 / 240.0)

    glfw.terminate()

if __name__ == "__main__":
    main()