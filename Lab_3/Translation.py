import glfw, time
from OpenGL.GL import *
import numpy as np

WIN_W, WIN_H = 800, 600

def draw_square():
    glBegin(GL_QUADS); glColor3f(0,1,0)
    glVertex2f(-0.2,0.2); glVertex2f(0.2,0.2)
    glVertex2f(0.2,-0.2); glVertex2f(-0.2,-0.2)
    glEnd()

def main():
    if not glfw.init(): return
    win = glfw.create_window(WIN_W,WIN_H,"2D Translation Homogeneous",None,None)
    if not win: glfw.terminate(); return
    glfw.make_context_current(win)
    glViewport(0,0,WIN_W,WIN_H); glMatrixMode(GL_PROJECTION); glLoadIdentity(); glOrtho(-1,1,-1,1,-1,1); glMatrixMode(GL_MODELVIEW)

    pos = np.array([[-0.8],[-0.8],[1.0]],float)
    trans = np.array([[1,0,0.002],[0,1,0.0015],[0,0,1]],float)

    print("Starting Position:\n", pos)
    print("Translation Matrix:\n", trans)

    while not glfw.window_should_close(win):
        glClear(GL_COLOR_BUFFER_BIT); glLoadIdentity()
        pos = trans @ pos
        glTranslatef(pos[0,0], pos[1,0],0); draw_square()
        glfw.swap_buffers(win); glfw.poll_events(); time.sleep(0.01)
    glfw.terminate()

if __name__=="__main__": main()