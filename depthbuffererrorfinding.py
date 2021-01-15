from OpenGL.GL import *
from OpenGL.GL.shaders import *
import pygame as pg
import numpy as np
import glm

ebodata = np.array([
            0, 1, 3,
            3, 1, 2,
            4, 5, 7,
            7, 5, 6,
            8, 9, 11,
            11, 9, 10,
            12, 13, 15,
            15, 13, 14,
            16, 17, 19,
            19, 17, 18,
            20, 21, 23,
            23, 21, 22], np.uintc)

tdata = np.array([0, 0,
                  0, 1,
                  1, 1,
                  1, 0,
                  0, 0,
                  0, 1,
                  1, 1,
                  1, 0,
                  0, 0,
                  0, 1,
                  1, 1,
                  1, 0,
                  0, 0,
                  0, 1,
                  1, 1,
                  1, 0,
                  0, 0,
                  0, 1,
                  1, 1,
                  1, 0,
                  0, 0,
                  0, 1,
                  1, 1,
                  1, 0
                  ], np.intc)

vdata = np.array([-0.5, 0.5, -0.5,
                  -0.5, -0.5, -0.5,
                  0.5, -0.5, -0.5,
                  0.5, 0.5, -0.5,

                  -0.5, 0.5, 0.5,
                  -0.5, -0.5, 0.5,
                  0.5, -0.5, 0.5,
                  0.5, 0.5, 0.5,

                  0.5, 0.5, -0.5,
                  0.5, -0.5, -0.5,
                  0.5, -0.5, 0.5,
                  0.5, 0.5, 0.5,

                  -0.5, 0.5, -0.5,
                  -0.5, -0.5, -0.5,
                  -0.5, -0.5, 0.5,
                  -0.5, 0.5, 0.5,

                  -0.5, 0.5, 0.5,
                  -0.5, 0.5, -0.5,
                  0.5, 0.5, -0.5,
                  0.5, 0.5, 0.5,

                  -0.5, -0.5, 0.5,
                  -0.5, -0.5, -0.5,
                  0.5, -0.5, -0.5,
                  0.5, -0.5, 0.5
                  ], np.float32)
#m50 = lambda a: a*50
#np.vectorize(m50)(vdata)
VERTEX_SHADER = """
#version 120
attribute vec2 frag;
attribute vec3 vetex;
varying vec2 fragcoord;

uniform vec3 iResolution;
uniform sampler2D textureObj;
uniform mat4 projectionmatrix;
uniform mat4 trans;

void main (){
  fragcoord = frag;
  gl_Position = (vec4(vetex, 1)*trans*projectionmatrix);
}

"""

FRAGMENT_SHADER = """
#version 120
varying vec2 fragcoord;
uniform sampler2D textureObj;
uniform mat4 projectionmatrix;
uniform mat4 trans;
vec2 get_p (vec2 p){
  return ((abs(p)/dot(p, p))-0.63);
}
void main (){
  vec2 p  = (2.0*fragcoord);
  p *= 4;
  p = (mod(p, 4.0)-2.0);
  for (int i=0;i<4;i+=1){
    p = get_p(p);
    p *= 2.0;
  };
  p = (p/2.0);
  //float de  = abs(dot(p, vec2(cos(iTime), sin(iTime))));
  //gl_FragColor = vec4(vec3(de), 1.0);
  //gl_FragColor = texture2D(textureObj, fragcoord);
  gl_FragColor = vec4(fragcoord, 1, 0.5);
}
"""

#ebodata = np.array([0, 1, 2, 1, 2, 3], np.uintc)

#tdata = np.array([[0, 0], [1, 0], [0, 1], [1, 1]
 #        ], np.float32)
#vdata = np.array([[-0.5, -0.5, -1], [0.5, -0.5, -1],
 #        [-0.5, 0.5, -1], [0.5, 0.5, -1]
#], np.float32)

def make_depth(w, h):
    tex = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tex)

    glTexImage2D(GL_TEXTURE_2D, 0, GL_DEPTH_COMPONENT, w, h, 0, GL_DEPTH_COMPONENT, GL_UNSIGNED_BYTE, None)
    # glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, filter)
    # glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, filter)
    glBindTexture(GL_TEXTURE_2D, 0)
    return tex

def make_texture(surface=None, size=None):
    tex = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tex)
    if surface:
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, surface.get_width(), surface.get_height(), 0, GL_RGB, GL_UNSIGNED_BYTE, pg.image.tostring(surface, "RGB", True))
    else:
        glTexImage2D(GL_TEXTURE_2D, 0, GL_DEPTH_COMPONENT, size[0], size[1], 0, GL_DEPTH_COMPONENT, GL_FLOAT, None)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glBindTexture(GL_TEXTURE_2D, 0)
    return tex

def make_program():
    p = glCreateProgram()

    vir = compileShader(VERTEX_SHADER, GL_VERTEX_SHADER)
    frag = compileShader(FRAGMENT_SHADER, GL_FRAGMENT_SHADER)

    glAttachShader(p, vir)
    glAttachShader(p, frag)

    glLinkProgram(p)

    glDeleteShader(vir)
    glDeleteShader(frag) # cleanup
    return p

def make_vao():
    v = glGenVertexArrays(1)

    glBindVertexArray(v)

    glBindBuffer(GL_ARRAY_BUFFER, make_vbo(tdata))
    glEnableVertexAttribArray(0)
    glVertexAttribPointer(0, 2, GL_INT, False, 0, ctypes.c_void_p(0))
    glBindBuffer(GL_ARRAY_BUFFER, make_vbo(vdata))
    glVertexAttribPointer(1, 3, GL_FLOAT, False, 0, ctypes.c_void_p(0))
    glEnableVertexAttribArray(1)
    glBindBuffer(GL_ARRAY_BUFFER, 0)
    glBindVertexArray(0)

    return v

def make_vbo(data, b=GL_ARRAY_BUFFER):
    buff = glGenBuffers(1)
    glBindBuffer(b, buff)
    glBufferData(b, data, GL_DYNAMIC_DRAW)
    glBindBuffer(b, 0)
    return buff

def make_framebuffer(texture, depth):
    fb = glGenFramebuffers(1)
    glBindFramebuffer(GL_FRAMEBUFFER, fb)
    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, texture, 0)
    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_TEXTURE_2D, depth, 0)
    if glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE:
        t = glCheckFramebufferStatus(GL_FRAMEBUFFER)
        raise Exception("frame buffer error - incomplete " + str(t))

    glBindFramebuffer(GL_FRAMEBUFFER, 0)

    return fb

def render(p, fb, vao, ebo, u):
    t = glm.mat4(1.0)
    t = glm.translate(t, (0, 0, -4))
    t = glm.rotate(t, pg.time.get_ticks()/500, (1, 1, 0))

    glEnable(GL_DEPTH_TEST)
    glViewport(0, 0, 640, 480)
    glUseProgram(p)
    glUniformMatrix4fv(u["trans"], 1, 1, t.to_list())
    glBindVertexArray(vao)
    glBindFramebuffer(GL_FRAMEBUFFER, fb)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo)

    glDrawElements(GL_TRIANGLES, len(ebodata), GL_UNSIGNED_INT, ctypes.c_void_p(0))
    #print(glGetError())
    glBindFramebuffer(GL_FRAMEBUFFER, 0)
    glUseProgram(0)

def uniforms(names, p):
    out = {}
    for i in names:
        out[i] = glGetUniformLocation(p, i)
    return out

def draw_top(tex):
    #glViewport(rect[0], rect[1], rect[2], rect[3])
    #glActiveTexture(GL_TEXTURE0)
    glUseProgram(0)
    glBindTexture(GL_TEXTURE_2D, tex)
    glBindFramebuffer(GL_FRAMEBUFFER, 0)
    glEnable(GL_TEXTURE_2D)
    glDisable(GL_DEPTH_TEST)

    glBegin(GL_QUADS)
    glTexCoord2f(0, 0)
    glVertex2f(-1, 1)
    glTexCoord2f(0, 1)
    glVertex2f(-1, -1)
    glTexCoord2f(1, 1)
    glVertex2f(1, -1)
    glTexCoord2f(1, 0)
    glVertex2f(1, 1)
    glEnd()
    glDisable(GL_TEXTURE_2D)


def main():
    pg.init()
    window = pg.display.set_mode((640, 480), pg.HWSURFACE | pg.OPENGL | pg.DOUBLEBUF)
    pg.draw.circle(window, (255, 0, 0), (100, 100), 100)
    window.fill((0, 255, 0))
    running = True
    clock = pg.time.Clock()


    p = make_program()
    tex = make_texture(window)
    depth = make_texture(size=(640, 480))
    fb = make_framebuffer(tex, depth)
    vao = make_vao()
    ebo = make_vbo(ebodata, GL_ELEMENT_ARRAY_BUFFER)
    print(glGetAttribLocation(p, "frag"))
    print(glGetAttribLocation(p, "vetex"))

    u = uniforms(["trans", "projectionmatrix"], p)

    glUseProgram(p)
    glUniformMatrix4fv(u["projectionmatrix"], 1, 1, glm.perspective(70, 640/480, 0.1, 1000).to_list())
    glEnable(GL_DEPTH_TEST)
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
        render(p, fb, vao, ebo, u)
        draw_top(tex)
        pg.display.flip()
        glClearColor(0.1, 0.1, 0.1, 1)
        glBindFramebuffer(GL_FRAMEBUFFER, fb)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        clock.tick(30)

    pg.quit()


if __name__ == "__main__":
    main()
