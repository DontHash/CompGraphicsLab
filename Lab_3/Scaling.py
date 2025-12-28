"""
scaling_variant.py
Variant of 2D scaling with homogeneous transforms.

Controls:
- Space: pause / resume
- Left / Right: decrease / increase amplitude (amount of scale variation)
- Up / Down: decrease / increase speed (Hz)
- C: cycle scale pivot (origin, square center, custom)
- R: reset time & trail
- Esc: quit
"""
import glfw
import time
import numpy as np
from OpenGL.GL import *

WIN_W, WIN_H = 800, 600

def make_translate(tx, ty):
    return np.array([[1.0, 0.0, tx],
                     [0.0, 1.0, ty],
                     [0.0, 0.0, 1.0]], dtype=float)

def make_scale(sx, sy):
    return np.array([[sx, 0.0, 0.0],
                     [0.0, sy, 0.0],
                     [0.0, 0.0, 1.0]], dtype=float)

def draw_quad(v, filled=True, color=(1.0, 0.4, 0.0, 1.0)):
    if filled:
        glBegin(GL_QUADS)
    else:
        glBegin(GL_LINE_LOOP)
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

def print_info(title, orig, mat, trans):
    print(f"\n=== {title} ===")
    print("Initial coords:")
    for i in range(orig.shape[1]):
        print(f" V{i+1}: ({orig[0,i]:+.3f}, {orig[1,i]:+.3f})")
    print("\nCurrent matrix:\n", mat)
    print("Transformed coords:")
    for i in range(trans.shape[1]):
        print(f" V{i+1}: ({trans[0,i]:+.3f}, {trans[1,i]:+.3f})")

def main():
    if not glfw.init():
        print("Failed to init GLFW"); return
    win = glfw.create_window(WIN_W, WIN_H, "2D Scaling (Homogeneous) — Variant", None, None)
    if not win:
        glfw.terminate(); print("Window create failed"); return

    glfw.make_context_current(win)
    glViewport(0, 0, WIN_W, WIN_H)
    glMatrixMode(GL_PROJECTION); glLoadIdentity(); glOrtho(-1, 1, -1, 1, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glClearColor(0.08, 0.08, 0.10, 1.0)

    # original square (homogeneous)
    orig = np.array([[-0.2, 0.2, 0.2, -0.2],
                     [ 0.2, 0.2,-0.2, -0.2],
                     [ 1.0, 1.0, 1.0,  1.0]], dtype=float)

    # pivots: (name, (x,y))
    center = (orig[0].mean(), orig[1].mean())
    custom = (0.4, -0.1)
    pivots = [("Origin", (0.0, 0.0)), ("Square center", center), ("Custom", custom)]
    pivot_idx = 1  # start with square center

    # animation parameters (these control the sine animation of sx, sy)
    base_sx, base_sy = 1.0, 1.0           # base scale
    amp_x, amp_y = 0.25, 0.10             # amplitude of variation (sx = base_sx + amp_x*sin(...))
    freq = 0.8                            # Hz
    phase = 0.0                           # phase offset (can be changed to get different x/y phasing)
    paused = False
    time_offset = 0.0
    trail = []
    max_trail = 50

    # print initial coords and a sample scaling matrix (like original did)
    sample_S = make_scale(1.002, 1.002)
    print("\n=== INITIAL COORDINATES ===")
    for i in range(orig.shape[1]):
        print(f"V{i+1}: ({orig[0,i]:.3f},{orig[1,i]:.3f})")
    print("\n=== SAMPLE SCALING MATRIX ===\n", sample_S, "\nAnimation running...\n")

    last_t = glfw.get_time()

    def key_cb(window, key, scancode, action, mods):
        nonlocal paused, freq, amp_x, amp_y, pivot_idx, time_offset, trail
        if action != glfw.PRESS and action != glfw.REPEAT:
            return
        if key == glfw.KEY_SPACE:
            paused = not paused
            if not paused:
                # reset baseline so animation resumes smoothly
                nonlocal last_t
                last_t = glfw.get_time()
        elif key == glfw.KEY_UP:
            freq = min(5.0, freq + 0.1)
            print(f"freq -> {freq:.2f} Hz")
        elif key == glfw.KEY_DOWN:
            freq = max(0.05, freq - 0.1)
            print(f"freq -> {freq:.2f} Hz")
        elif key == glfw.KEY_RIGHT:
            amp_x = min(1.5, amp_x + 0.01); amp_y = min(1.5, amp_y + 0.005)
            print(f"amp_x -> {amp_x:.3f}, amp_y -> {amp_y:.3f}")
        elif key == glfw.KEY_LEFT:
            amp_x = max(0.0, amp_x - 0.01); amp_y = max(0.0, amp_y - 0.005)
            print(f"amp_x -> {amp_x:.3f}, amp_y -> {amp_y:.3f}")
        elif key == glfw.KEY_C:
            pivot_idx = (pivot_idx + 1) % len(pivots)
            print(f"Pivot -> {pivots[pivot_idx][0]} at {pivots[pivot_idx][1]}")
            # print matrix for the current instant after switching
            now = glfw.get_time() - time_offset
            sx = base_sx + amp_x * np.sin(2*np.pi*freq*now)
            sy = base_sy + amp_y * np.sin(2*np.pi*freq*now + phase)
            px, py = pivots[pivot_idx][1]
            M = make_translate(px, py) @ make_scale(sx, sy) @ make_translate(-px, -py)
            trans = M @ orig
            print_info(f"After pivot change ({pivots[pivot_idx][0]})", orig, M, trans)
        elif key == glfw.KEY_R:
            # reset time & trail
            time_offset = glfw.get_time()
            trail.clear()
            print("Reset animation time and trail.")
        elif key == glfw.KEY_ESCAPE:
            glfw.set_window_should_close(window, True)

    glfw.set_key_callback(win, key_cb)

    while not glfw.window_should_close(win):
        now = glfw.get_time()
        dt = now - last_t
        last_t = now

        glfw.poll_events()

        anim_t = now - time_offset
        if paused:
            anim_t = anim_t  # frozen visual; no change to anim_t (we don't advance time_offset)
        # compute animated non-uniform scales using sine
        sx = base_sx + amp_x * np.sin(2.0 * np.pi * freq * anim_t)
        sy = base_sy + amp_y * np.sin(2.0 * np.pi * freq * anim_t + phase)

        # build scaling about current pivot: T(p) * S(sx,sy) * T(-p)
        pivot_name, pivot_coords = pivots[pivot_idx]
        px, py = pivot_coords
        M = make_translate(px, py) @ make_scale(sx, sy) @ make_translate(-px, -py)

        # always apply matrix to original square (avoid accumulation)
        transformed = M @ orig

        # push to trail and clamp
        trail.append(transformed.copy())
        if len(trail) > max_trail:
            trail.pop(0)

        # render
        glClear(GL_COLOR_BUFFER_BIT)
        glLoadIdentity()

        draw_axes(1.0)
        # original outline
        draw_quad(orig, filled=False, color=(0.9, 0.9, 0.9, 1.0))

        # faded trail
        n = len(trail)
        for i, tmat in enumerate(trail):
            alpha = 0.06 + 0.9 * (i / max(1, n-1))
            draw_quad(tmat, filled=True, color=(1.0, 0.4, 0.0, alpha * 0.75))

        # current transformed square (solid)
        draw_quad(transformed, filled=True, color=(1.0, 0.45, 0.05, 1.0))

        # pivot marker
        glPointSize(6.0)
        glBegin(GL_POINTS)
        glColor3f(0.0, 1.0, 0.0)
        glVertex2f(px, py)
        glEnd()

        # occasionally print matrix & coords when paused or at pivot changes (small rate)
        # keep prints sparse: once per ~1.5s when not paused
        if paused and (int(anim_t * 4) % 4 == 0):
            # print when paused to inspect
            print_info(f"Paused view (pivot={pivot_name})", orig, M, transformed)
            # small sleep to avoid spamming prints while paused
            time.sleep(0.25)

        glfw.swap_buffers(win)

        # cap CPU a bit
        time.sleep(1.0 / 240.0)

    glfw.terminate()

if __name__ == "__main__":
    main()