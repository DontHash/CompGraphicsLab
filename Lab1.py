from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import ctypes
def init():
    glClearColor(1.0, 1.0, 1.0, 1.0)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, 1400, 0, 600)

def draw_rect(x, y, w, h, color):
    glColor3f(*color)
    glBegin(GL_POLYGON)
    glVertex2f(x, y)
    glVertex2f(x + w, y)
    glVertex2f(x + w, y + h)
    glVertex2f(x, y + h)
    glEnd()

def getRes():
    ctypes.windll.user32.SetProcessDPIAware()
    glutInit(sys.argv)
    width = glutGet(GLUT_SCREEN_WIDTH)
    height = glutGet(GLUT_SCREEN_HEIGHT)

    return width, height

def draw_name():
    glClear(GL_COLOR_BUFFER_BIT)

    #B 
    draw_rect(50, 100, 40, 400, (0.2, 0.5, 0.9))
    draw_rect(90, 460, 120, 40, (0.2, 0.5, 0.9))
    draw_rect(210, 340, 40, 120, (0.2, 0.5, 0.9))
    draw_rect(90, 300, 120, 40, (0.2, 0.5, 0.9))
    draw_rect(210, 100, 40, 200, (0.2, 0.5, 0.9))
    draw_rect(90, 100, 120, 40, (0.2, 0.5, 0.9))

    # H
    draw_rect(300, 100, 40, 400, (0.9, 0.2, 0.2))
    draw_rect(420, 100, 40, 400, (0.9, 0.2, 0.2))
    draw_rect(340, 300, 80, 40, (0.9, 0.2, 0.2))

    # I
    draw_rect(500, 100, 40, 400, (0.2, 0.8, 0.2))

    # S
    draw_rect(580, 460, 140, 40, (0.6, 0.2, 0.8))
    draw_rect(580, 300, 40, 160, (0.6, 0.2, 0.8))
    draw_rect(580, 300, 140, 40, (0.6, 0.2, 0.8))
    draw_rect(680, 100, 40, 200, (0.6, 0.2, 0.8))
    draw_rect(580, 100, 140, 40, (0.6, 0.2, 0.8))

    # H
    draw_rect(760, 100, 40, 400, (0.9, 0.5, 0.2))
    draw_rect(880, 100, 40, 400, (0.9, 0.5, 0.2))
    draw_rect(800, 300, 80, 40, (0.9, 0.5, 0.2))

    # M
    draw_rect(950,100,40,400,(0.6, 0.2, 0.8))
    draw_rect(990,400,60,40,(0.6, 0.2, 0.8))
    draw_rect(1050,370,40,70,(0.6, 0.2, 0.8))
    draw_rect(1090,400,60,40,(0.6, 0.2, 0.8))
    draw_rect(1150,100,40,400,(0.6, 0.2, 0.8))

    # A
    draw_rect(1230, 100, 40, 400, (0.8, 0.3, 0.2))
    draw_rect(1350, 100, 40, 400, (0.8, 0.3, 0.2))
    draw_rect(1270, 300, 80, 40, (0.8, 0.3, 0.2))
    draw_rect(1270, 460, 80, 40, (0.8, 0.3, 0.2))

    glFlush()

def main():
    
    w, h = getRes()
    glutInit()
    print(f"Screen resolution: {w} x {h}")
    glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB)
    glutInitWindowSize(1400, 600)
    glutCreateWindow(b"BHISHMA - Rectangular OpenGL Letters")
    init()
    glutDisplayFunc(draw_name)
    glutMainLoop()
    
    

if __name__ == "__main__":
    main()
