import sys
import ctypes
import numpy as np
import OpenGL.GL as gl
import OpenGL.GLUT as glut



def display():
    glut.glutSwapBuffers()

def reshape(width,height):
    gl.glViewport(0, 0, width, height)

def keyboard( key, x, y ):
    if key == '\033':
        sys.exit( )

glut.glutInit()
glut.glutInitDisplayMode(glut.GLUT_DOUBLE | glut.GLUT_RGBA)
glut.glutCreateWindow('Hello world!')
glut.glutReshapeWindow(512,512)
glut.glutReshapeFunc(reshape)
glut.glutDisplayFunc(display)
glut.glutKeyboardFunc(keyboard)


# ----------------------------------------------------------
'''
http://glumpy.readthedocs.io/en/latest/tutorial/hardway.html
'''

# what if we do it here? right before the mainloop call?
# pluging the shader program into the pipeline
program  = gl.glCreateProgram()
vertex   = gl.glCreateShader(gl.GL_VERTEX_SHADER)
fragment = gl.glCreateShader(gl.GL_FRAGMENT_SHADER)

vertex_code = """
  uniform float scale;
  attribute vec2 position;
  attribute vec4 color;
  varying vec4 v_color;
  void main()
  {
    gl_Position = vec4(scale*position, 0.0, 1.0);
    v_color = color;
  } """

fragment_code = """
  varying vec4 v_color;

  void main()
  {
      gl_FragColor = v_color;
  } """


'''
Как я понял:
* attribute <type> <name> -- это параметр конкретной вершины
* uniform   <type> <name> -- параметр _всех_ вершин
* varying   <type> <name> -- переменная, передающаяся от вершинных шейдеров к фрагментным, с интерполяцией по дистанции для точек между вершинами
                             т.е. это интерполяция цвета например
'''


# Set shaders source
gl.glShaderSource(vertex, vertex_code)
gl.glShaderSource(fragment, fragment_code)

# Compile shaders
gl.glCompileShader(vertex)
gl.glCompileShader(fragment)

# We can now build and link the program:
gl.glAttachShader(program, vertex)
gl.glAttachShader(program, fragment)
gl.glLinkProgram(program)

# We can not get rid of shaders, they won’t be used again:
# -- probably "we can _now_ get rid of shaders"?
gl.glDetachShader(program, vertex)
gl.glDetachShader(program, fragment)

# Finally, we make program the default program to be ran. We can do it now because we’ll use a single in this example:
# -- what is "a single"?
gl.glUseProgram(program)
# ----------------------------------------------------------
'''
В результате ничего не рисуется так как нечего рисовать -- нужно передать буфер с вершинами.
'''

glut.glutMainLoop()

