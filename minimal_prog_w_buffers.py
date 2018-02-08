import sys
import ctypes
import numpy
np = numpy
import OpenGL.GL as gl
import OpenGL.GLUT as glut



"""
def display():
    glut.glutSwapBuffers()
"""

def display():
    gl.glClear(gl.GL_COLOR_BUFFER_BIT)
    gl.glDrawArrays(gl.GL_TRIANGLE_STRIP, 0, 4)
    glut.glutSwapBuffers()
# The 0, 4 arguments in the glDrawArrays tells OpenGL we want to display 4 vertices from our array and we start at vertex 0.

def reshape(width,height):
    gl.glViewport(0, 0, width, height)

def keyboard( key, x, y ):
    #print(key)
    if key == '\033' or key == b'\x03':
        sys.exit( )
    # doesn't work this way, ctrl-c is a different byte altogether -- 0x03 = ETX = End of TeXt in ASCII
    #elif (glut.glutGetModifiers() == glut.GLUT_ACTIVE_CTRL) and (key == 'c' or key == 'C'):
    #    print("foo")
    #    sys.exit()

# let's try moving around the buffer
# UP and DOWN keys are special keys
zoom = 1.
shift_x = 0.
shift_y = 0.

zoom_step = 1.1
shift_step = 0.1

def specialkeys(key, x, y):
    global shift_x, shift_y
    print('sp.key', key)

    if key == glut.GLUT_KEY_UP:
        print("Клавиша вверх")
        #glRotatef(5, 1, 0, 0)       # Вращаем на 5 градусов по оси X
        #glTranslate(0., -0.02, 0.)
        shift_y -= shift_step / zoom
        gl.glUniform1f(PARAM_shift_Y, shift_y)
    if key == glut.GLUT_KEY_DOWN:
        print("Клавиша вниз")
        #glRotatef(-5, 1, 0, 0)      # Вращаем на -5 градусов по оси X
        #glTranslate()
        #glTranslate(0., 0.02, 0.)
        shift_y += shift_step / zoom
        gl.glUniform1f(PARAM_shift_Y, shift_y)

    # asynchorous command to redraw
    glut.glutPostRedisplay()


glut.glutInit()
glut.glutInitDisplayMode(glut.GLUT_DOUBLE | glut.GLUT_RGBA)
glut.glutCreateWindow('Hello world!')
glut.glutReshapeWindow(512,512)
glut.glutReshapeFunc(reshape)
glut.glutDisplayFunc(display)
glut.glutKeyboardFunc(keyboard)

# UP/DOWN keys
glut.glutSpecialFunc(specialkeys)
# Задаем серый цвет для очистки экрана
gl.glClearColor(0.2, 0.2, 0.2, 1)



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
  uniform float shift_x, shift_y;
  attribute vec2 position;
  attribute vec4 color;
  varying vec4 v_color;
  void main()
  {
    gl_Position = vec4(scale*position, 0.0, 1.0);
    gl_Position.x += shift_x;
    gl_Position.y += shift_y;
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

# В результате ничего не рисуется так как нечего рисовать -- нужно передать буфер с вершинами.

# Request a buffer slot from GPU
buffer = gl.glGenBuffers(1)

# Make this buffer the default one
gl.glBindBuffer(gl.GL_ARRAY_BUFFER, buffer)


data = numpy.zeros(4, dtype = [ ("position", np.float32, 2),
                                ("color",    np.float32, 4)] )
# <----------- data was defined where? in the introduction chapter

data['color']    = [ (1,0,0,1), (0,1,0,1), (0,0,1,1), (1,1,0,1) ]
data['position'] = [ (-1,-1),   (-1,+1),   (+1,-1),   (+1,+1)   ]
# -- probably the buffer data has to be filled before "upload" command

# Upload data
gl.glBufferData(gl.GL_ARRAY_BUFFER, data.nbytes, data, gl.GL_DYNAMIC_DRAW)

'''т.е. data аплоадится в default буффер?'''

# and we need to _bind_ it
# Next, we need to bind the buffer to the program and this requires some computations.
# We need to tell the GPU how to read the buffer and bind each value to the relevant attribute.
# To do this, GPU needs to kow what is the stride between 2 consecutive element and what is the offset to read one attribute:

stride = data.strides[0]

offset = ctypes.c_void_p(0)
loc = gl.glGetAttribLocation(program, "position")
gl.glEnableVertexAttribArray(loc)
gl.glBindBuffer(gl.GL_ARRAY_BUFFER, buffer)
gl.glVertexAttribPointer(loc, 3, gl.GL_FLOAT, False, stride, offset)

offset = ctypes.c_void_p(data.dtype["position"].itemsize)
loc = gl.glGetAttribLocation(program, "color")
gl.glEnableVertexAttribArray(loc)
gl.glBindBuffer(gl.GL_ARRAY_BUFFER, buffer)
gl.glVertexAttribPointer(loc, 4, gl.GL_FLOAT, False, stride, offset)

# Here we’re basically telling the program how to bind data to the relevant attribute.
# This is made by providing the stride of the array (how many bytes between each record) and the offset of a given attribute.

'''т.е. stride -- это между каждой вершиной и offset -- это разные атрибуты внутри вершины'''

# Finally, we also need to bind the uniform which is much more simpler.
# We request the location of the uniform and we upload the value using the dedicated function to upload one float only:
loc = gl.glGetUniformLocation(program, "scale")
PARAM_shift_X = gl.glGetUniformLocation(program, 'shift_x')
PARAM_shift_Y = gl.glGetUniformLocation(program, 'shift_y')


gl.glUniform1f(loc, 1.0)

#data['color']    = [ (1,0,0,1), (0,1,0,1), (0,0,1,1), (1,1,0,1) ]
#data['position'] = [ (-1,-1),   (-1,+1),   (+1,-1),   (+1,+1)   ]
## -- it's still black screen, probably the buffer data had to be filled before "upload" command

# ----------------------------------------------------------
glut.glutMainLoop()


