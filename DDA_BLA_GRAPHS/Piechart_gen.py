import glfw
from OpenGL.GL import *
import math
import time
import random

WIN_W, WIN_H = 1100, 700
sectors_buffer = []

# different random segments and range
random.seed()  
sector_values = [random.randint(10, 80) for _ in range(8)]
sum_vals = sum(sector_values)
sector_degrees = [360.0 * v / sum_vals for v in sector_values]


PALETTE = [
    (0.95, 0.47, 0.60),  # soft pink
    (0.60, 0.87, 0.73),  # mint
    (0.64, 0.76, 0.96),  # light blue
    (0.99, 0.84, 0.59),  # peach
    (0.82, 0.63, 0.88),  # lavender
    (0.98, 0.72, 0.72),  # salmon
    (0.58, 0.84, 0.97),  # aqua
    (0.88, 0.95, 0.70),  # pale lime
]


def generate_sector(cx, cy, radius, start_deg, end_deg, steps=120):
    """Yield an animated list of points that form a filled pie-sector (triangle fan).
    Each yielded value is a copy of the fan points so far (so it can be drawn incrementally)."""
    fan = [(cx, cy)]
    for s in range(steps + 1):
        t = s / steps
        angle_rad = math.radians(start_deg + (end_deg - start_deg) * t)
        x = cx + radius * math.cos(angle_rad)
        y = cy + radius * math.sin(angle_rad)
        fan.append((int(round(x)), int(round(y))))
        # yield a shallow copy to avoid external mutation issues
        yield list(fan)


def draw_scene():
    glClear(GL_COLOR_BUFFER_BIT)
    for i, fan_pts in enumerate(sectors_buffer):
        col = PALETTE[i % len(PALETTE)]
        glColor3f(*col)
        glBegin(GL_TRIANGLE_FAN)
        for x, y in fan_pts:
            glVertex2i(x, y)
        glEnd()


def configure_projection():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(-120, WIN_W + 120, -120, WIN_H + 120, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glClearColor(0.06, 0.07, 0.10, 1.0)


def run():
    global sectors_buffer
    if not glfw.init():
        raise RuntimeError("GLFW initialization failed")
    window = glfw.create_window(WIN_W, WIN_H, "Pastel Pie Chart (variant)", None, None)
    if not window:
        glfw.terminate()
        raise RuntimeError("Window creation failed")
    glfw.make_context_current(window)
    configure_projection()

    # center and radius slightly offset from exact center
    cx = WIN_W // 2 + 60
    cy = WIN_H // 2 - 40
    radius = 240 

    print("\n>>> SECTOR SUMMARY <<<")
    print("ID | start°  -> end°   | value ")
    print("---+----------------------+-------")

    # create sector generators
    gens = []
    start = 90.0  # start at 90° so first sector points upward (different orientation)
    for idx, deg in enumerate(sector_degrees):
        end = start + deg
        print(f"{idx:2d} | {start:7.2f} -> {end:7.2f} | {sector_values[idx]:5d}")
        gens.append(generate_sector(cx, cy, radius, start, end, steps=100))
        start = end


    sectors_buffer = [[] for _ in gens]
    current = 0
    last = time.time()

    tick = 0.0035

    while not glfw.window_should_close(window):
        glfw.poll_events()

        if time.time() - last >= tick:
            if current < len(gens):
                try:
                    sectors_buffer[current] = next(gens[current])
                except StopIteration:
                    current += 1
            last = time.time()

        draw_scene()
        glfw.swap_buffers(window)

    glfw.terminate()


if __name__ == "__main__":
    run()