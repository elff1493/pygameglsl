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
  gl_Position = vec4(vetex, 1)*trans;
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
  gl_FragColor = vec4(fragcoord, 1, 0);
}
"""

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
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, surface.width, surface.height, 0, GL_RGB, GL_UNSIGNED_BYTE, surface)
    else:
        glTexImage2D(GL_TEXTURE_2D, 0, GL_DEPTH_COMPONENT, size[0], size[1], 0, GL_DEPTH_COMPONENT, GL_FLOAT, None)
    #glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, filter)
    #glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, filter)
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
    glVertexAttribPointer(0, 2, GL_INT, False, 0, ctypes.c_void_p(0))
    glBindBuffer(GL_ARRAY_BUFFER, make_vbo(vdata))
    glVertexAttribPointer(1, 3, GL_FLOAT, False, 0, ctypes.c_void_p(0))

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

def render(p, fb, vao, ebo):
    #glViewport(*self._viewport)
    glUseProgram(p)

    glBindVertexArray(vao)
    glBindFramebuffer(GL_FRAMEBUFFER, fb)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo)

    glDrawElements(GL_TRIANGLES, len(ebodata), GL_UNSIGNED_INT, None)

    glBindFramebuffer(GL_FRAMEBUFFER, 0)
    glUseProgram(0)

def uniforms(names, p):
    out = {}
    for i in names:
        out[i] = glGetUniformLocation(p, i)
    return out

def draw_top(tex):
    #glViewport(rect[0], rect[1], rect[2], rect[3])
    glActiveTexture(GL_TEXTURE0)
    glBindTexture(GL_TEXTURE_2D, tex)
    glBindFramebuffer(GL_FRAMEBUFFER, 0)
    glEnable(GL_TEXTURE_2D)

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
    running = True
    clock = pg.time.Clock()

    p = make_program()
    depth = make_texture(size=(640, 480))
    fb = make_framebuffer(0, depth)
    vao = make_vao()
    ebo = make_vbo(ebodata, GL_ELEMENT_ARRAY_BUFFER)

    u = uniforms(["trans", "projectionmatrix", "textureObj", "iResolution"], p)
    t = glm.mat4(1.0)
    t = glm.translate(t, (0, 0, -4))
    glUseProgram(p)
    glUniformMatrix4fv(u["trans"], 1, 1, t.to_list())
    glUniformMatrix4fv(u["projectionmatrix"], 1, 1, glm.perspectiveRH(70, 1, 1, 1000).to_list())

    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
        render(p, fb, vao, ebo)
        pg.display.flip()
        glClearColor(0.1, 0.1, 0.1, 1)
        glClear(GL_COLOR_BUFFER_BIT)
        clock.tick(30)


    pg.quit()


if __name__ == "__main__":
    main()