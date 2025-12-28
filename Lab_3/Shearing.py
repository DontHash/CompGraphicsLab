import glfw, time
from OpenGL.GL import *
import numpy as np

WIN_W, WIN_H = 800, 600

def draw_square(v, color=(0.8,0.3,1)):
    glBegin(GL_QUADS); glColor3f(*color)
    for p in v.T: glVertex2f(p[0],p[1])
    glEnd()

def print_info(title, orig, mat, trans):
    print(f"\n===== {title} =====")
    print("\nInitial coords:"); [print(f"V{i+1}: ({orig[0,i]:.3f},{orig[1,i]:.3f})") for i in range(4)]
    print("\nShear matrix:\n", mat)
    print("\nTransformed coords:"); [print(f"V{i+1}: ({trans[0,i]:.3f},{trans[1,i]:.3f})") for i in range(4)]

def main():
    if not glfw.init(): return
    win=glfw.create_window(WIN_W,WIN_H,"Shearing Animation",None,None)
    if not win: glfw.terminate(); return
    glfw.make_context_current(win)
    glViewport(0,0,WIN_W,WIN_H); glMatrixMode(GL_PROJECTION); glLoadIdentity(); glOrtho(-1,1,-1,1,-1,1); glMatrixMode(GL_MODELVIEW)

    square=np.array([[-0.2,0.2,0.2,-0.2],[0.2,0.2,-0.2,-0.2],[1,1,1,1]],float)
    shears={
        "Shear in X": np.array([[1,0.5,0],[0,1,0],[0,0,1]]),
        "Shear in Y": np.array([[1,0,0],[0.5,1,0],[0,0,1]]),
        "Shear X&Y": np.array([[1,0.5,0],[0.5,1,0],[0,0,1]])
    }

    for title, mat in shears.items():
        trans = mat @ square
        print_info(title, square, mat, trans)
        for t in np.linspace(0,1,60):
            glClear(GL_COLOR_BUFFER_BIT); glLoadIdentity()
            draw_square((1-t)*square + t*trans)
            glfw.swap_buffers(win); glfw.poll_events(); time.sleep(0.01)
        time.sleep(0.5)
    time.sleep(1); glfw.terminate()

if __name__=="__main__": main()