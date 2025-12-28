import glfw
import time
import math
from OpenGL.GL import *

WIN_W, WIN_H = 900, 550

def midpoint_ellipse_points(cx, cy, rx, ry):
    """
    Generator for points on an ellipse using the midpoint algorithm.
    Yields symmetric integer points (x, y) in screen coordinates.
    """
    x, y = 0, ry
    rx2 = rx * rx
    ry2 = ry * ry
    dx = 2 * ry2 * x
    dy = 2 * rx2 * y

    # Decision parameter for region 1
    d1 = ry2 - (rx2 * ry) + (0.25 * rx2)
    while dx < dy:
        yield (cx + x, cy + y)
        yield (cx - x, cy + y)
        yield (cx + x, cy - y)
        yield (cx - x, cy - y)
        if d1 < 0:
            x += 1
            dx += 2 * ry2
            d1 += dx + ry2
        else:
            x += 1
            y -= 1
            dx += 2 * ry2
            dy -= 2 * rx2
            d1 += dx - dy + ry2

    # Decision parameter for region 2
    d2 = (ry2 * (x + 0.5) * (x + 0.5)) + (rx2 * (y - 1) * (y - 1)) - (rx2 * ry2)
    while y >= 0:
        yield (cx + x, cy + y)
        yield (cx - x, cy + y)
        yield (cx + x, cy - y)
        yield (cx - x, cy - y)
        if d2 > 0:
            y -= 1
            dy -= 2 * rx2
            d2 += rx2 - dy
        else:
            y -= 1
            x += 1
            dx += 2 * ry2
            dy -= 2 * rx2
            d2 += dx - dy + rx2

def ellipse_parametric(cx, cy, rx, ry, segments=200):
    """
    Parametric polygon approximation of the ellipse (useful for outline/fill).
    Returns a list of (x,y) floats.
    """
    pts = []
    for i in range(segments):
        theta = 2.0 * math.pi * i / segments
        x = cx + rx * math.cos(theta)
        y = cy + ry * math.sin(theta)
        pts.append((x, y))
    return pts

def setup_gl():
    glMatrixMode(GL_PROJECTION); glLoadIdentity()
    glOrtho(0, WIN_W, 0, WIN_H, -1, 1)
    glMatrixMode(GL_MODELVIEW); glLoadIdentity()
    glClearColor(0.06, 0.06, 0.08, 1.0)
    glEnable(GL_POINT_SMOOTH)
    glEnable(GL_LINE_SMOOTH)
    glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
    glHint(GL_POINT_SMOOTH_HINT, GL_NICEST)

def draw_points(points, size=4):
    glPointSize(size)
    glBegin(GL_POINTS)
    n = max(1, len(points))
    for i, (x, y) in enumerate(points):
        t = i / n
        # gradient: green -> teal -> cyan
        r = 0.0 + 0.2 * t
        g = 0.6 + 0.4 * (1 - abs(0.5 - t) * 2)
        b = 0.3 + 0.7 * t
        glColor3f(r, g, b)
        glVertex2f(x, y)
    glEnd()

def draw_line_strip(points, width=2.0):
    glLineWidth(width)
    glBegin(GL_LINE_STRIP)
    glColor3f(0.9, 0.9, 0.9)
    for x, y in points:
        glVertex2f(x, y)
    # close the loop by repeating first point
    if points:
        glVertex2f(points[0][0], points[0][1])
    glEnd()

def draw_filled(pts):
    glColor3f(0.05, 0.6, 0.4)
    glBegin(GL_POLYGON)
    for x, y in pts:
        glVertex2f(x, y)
    glEnd()

def main():
    if not glfw.init():
        raise RuntimeError("GLFW init failed")

    win = glfw.create_window(WIN_W, WIN_H, "Midpoint Ellipse — Variant", None, None)
    if not win:
        glfw.terminate()
        raise RuntimeError("Window creation failed")

    glfw.make_context_current(win)
    setup_gl()

    # initial ellipse parameters
    cx, cy = WIN_W // 2, WIN_H // 2
    rx, ry = 300, 150

    # precompute symmetric points from midpoint generator (keeps order but will contain duplicates)
    def build_midpoint_list(rx, ry):
        gen = midpoint_ellipse_points(cx, cy, rx, ry)
        pts = []
        seen = set()
        for x, y in gen:
            key = (int(x), int(y))
            if key not in seen:
                seen.add(key)
                pts.append((float(x), float(y)))
        return pts

    mid_pts = build_midpoint_list(rx, ry)
    parametric_pts = ellipse_parametric(cx, cy, rx, ry, segments=300)

    # animated buffer (progressively revealed indices into mid_pts)
    idx = 0
    forward = True
    speed = 400.0  # points per second
    paused = False
    mode = 0  # 0: points, 1: outline, 2: filled

    last_time = glfw.get_time()

    def key_cb(window, key, scancode, action, mods):
        nonlocal paused, rx, ry, mid_pts, parametric_pts, idx, speed, mode
        if action == glfw.PRESS or action == glfw.REPEAT:
            if key == glfw.KEY_SPACE:
                paused = not paused
            elif key == glfw.KEY_ESCAPE:
                glfw.set_window_should_close(window, True)
            elif key == glfw.KEY_R:
                # reset drawing
                idx = 0
            elif key == glfw.KEY_M:
                mode = (mode + 1) % 3
            elif key == glfw.KEY_UP:
                ry = min(WIN_H // 2, ry + 8); mid_pts = build_midpoint_list(rx, ry); parametric_pts = ellipse_parametric(cx, cy, rx, ry); idx = 0
            elif key == glfw.KEY_DOWN:
                ry = max(8, ry - 8); mid_pts = build_midpoint_list(rx, ry); parametric_pts = ellipse_parametric(cx, cy, rx, ry); idx = 0
            elif key == glfw.KEY_RIGHT:
                rx = min(WIN_W // 2, rx + 8); mid_pts = build_midpoint_list(rx, ry); parametric_pts = ellipse_parametric(cx, cy, rx, ry); idx = 0
            elif key == glfw.KEY_LEFT:
                rx = max(8, rx - 8); mid_pts = build_midpoint_list(rx, ry); parametric_pts = ellipse_parametric(cx, cy, rx, ry); idx = 0
            elif key == glfw.KEY_KP_ADD or key == glfw.KEY_EQUAL:
                speed = min(2000.0, speed + 100.0)
            elif key == glfw.KEY_KP_SUBTRACT or key == glfw.KEY_MINUS:
                speed = max(50.0, speed - 50.0)

    glfw.set_key_callback(win, key_cb)

    # Ping-pong bounds
    max_count = len(mid_pts)
    if max_count == 0:
        print("No points generated for initial radii.")
        glfw.terminate()
        return

    while not glfw.window_should_close(win):
        now = glfw.get_time()
        dt = now - last_time
        last_time = now

        glfw.poll_events()

        if not paused:
            advance = speed * dt
            if forward:
                idx += int(round(advance))
                if idx >= max_count:
                    idx = max_count
                    forward = False
            else:
                idx -= int(round(advance))
                if idx <= 0:
                    idx = 0
                    forward = True

        # render
        glClear(GL_COLOR_BUFFER_BIT)
        glLoadIdentity()

        # Draw depending on mode
        if mode == 0:
            # progressive points (up to idx)
            draw_points(mid_pts[:idx], size=4)
        elif mode == 1:
            # outline: draw full parametric outline and highlight progressive points on it
            draw_line_strip(parametric_pts, width=2.0)
            draw_points(mid_pts[:idx], size=3)
        else:
            # filled with parametric polygon (full), and overlay progressive perimeter as points
            draw_filled(parametric_pts)
            draw_points(mid_pts[:idx], size=3)

        # Draw a small HUD text using points: show mode and instructions (simple)
        # (No text rendering; we provide a small legend using colored points.)
        # Top-left corner indicators:
        hud_x, hud_y = 10, WIN_H - 18
        # Mode indicator (as colored square)
        glPointSize(8)
        glBegin(GL_POINTS)
        if mode == 0: glColor3f(0.1, 0.9, 0.4)
        elif mode == 1: glColor3f(0.9, 0.9, 0.2)
        else: glColor3f(0.2, 0.6, 0.9)
        glVertex2f(hud_x, hud_y)
        glEnd()

        glfw.swap_buffers(win)

        # small sleep to limit CPU usage
        time.sleep(1.0 / 240.0)

    glfw.terminate()

if __name__ == "__main__":
    main()