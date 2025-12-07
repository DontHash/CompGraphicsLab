import glfw
from OpenGL.GL import *
import time

WIN_W, WIN_H = 1200, 800
points = []


def midpoint_circle(cx, cy, radius):
    """Midpoint circle generator (yields 8-way symmetric integer points)."""
    x = 0
    y = radius
    d = 1 - radius
    step = 0

    while x <= y:
        p0 = (cx + x, cy + y)
        p1 = (cx - x, cy + y)
        p2 = (cx + x, cy - y)
        p3 = (cx - x, cy - y)
        p4 = (cx + y, cy + x)
        p5 = (cx - y, cy + x)
        p6 = (cx + y, cy - x)
        p7 = (cx - y, cy - x)

        print(f"STEP {step:04d} | x={x:3d} y={y:3d} d={d:4d}  -> primary={p0}")
        step += 1

        yield p0
        yield p1
        yield p2
        yield p3
        yield p4
        yield p5
        yield p6
        yield p7

        
        if d < 0:
            d += (2 * x) + 3
        else:
            d += (2 * (x - y)) + 5
            y -= 1
        x += 1


def render():
    glClear(GL_COLOR_BUFFER_BIT)
    glPointSize(4)

    
    glColor3f(0.12, 0.62, 0.95)

    glBegin(GL_POINTS)
    for x, y in points:
        glVertex2i(int(x), int(y))
    glEnd()


def configure_projection():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(-80, WIN_W + 80, -80, WIN_H + 80, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glClearColor(0.02, 0.03, 0.06, 1.0)


def run():
    if not glfw.init():
        raise RuntimeError("GLFW initialization failed (variant)")
    win = glfw.create_window(WIN_W, WIN_H, "Midpoint Circle (variant)", None, None)
    if not win:
        glfw.terminate()
        raise RuntimeError("Window creation failed (variant)")

    glfw.make_context_current(win)
    configure_projection()

    
    center_x = WIN_W // 2 + 30
    center_y = WIN_H // 2 - 20
    r = 260

    print("\n~~~ MIDPOINT CIRCLE TRACE (variant) ~~~")
    print("Format: STEP #### | x Y d -> primary_point")
    gen = midpoint_circle(center_x, center_y, r)

    last = time.time()

    
    tick = 0.0015

    while not glfw.window_should_close(win):
        glfw.poll_events()

        if time.time() - last >= tick:
            try:
                points.append(next(gen))
            except StopIteration:
                
                pass
            last = time.time()

        render()
        glfw.swap_buffers(win)

    glfw.terminate()


if __name__ == "__main__":
    run()