import math
from collections import defaultdict
from ctypes import c_float

from OpenGL.GL import *
from OpenGL.GLUT import *

from src.const import styleDict, glConst, glFunc
from src.types import DrawStyle, AS, A


class OglObject:
    def __init__(
            self,
            grid=None,
            vertices=None,
            texSrc=None,
            texCoords=None,
            normals=None,
            colours=None,
            style=DrawStyle.triangles2,
            size=101,
            contrast=0,
            optimumIsMinimum=True):
        self.data = defaultdict(defaultdict)
        self.length = 0
        self.style = style
        self.size = size
        self.contrast = contrast
        self.optimumIsMinimum = optimumIsMinimum
        if grid is not None:
            grid = self.normaliseGrid(grid)
            vertices = styleDict[self.style][1](grid, self.size)
            colours = self.genColourVector(
                vertices, self.contrast, self.optimumIsMinimum)
        self.set(
            grid,
            vertices,
            texSrc,
            texCoords,
            normals,
            colours,
            style,
            size,
            contrast)
        if vertices is None and grid is None:
            raise "Either grid or vertices must contain information"
        self.__alloc()

    def set(
            self,
            grid=None,
            vertices=None,
            texSrc=None,
            texCoords=None,
            normals=None,
            colours=None,
            style=None,
            size=None,
            contrast=None):
        contrastChanged = 0
        if contrast is not None and self.contrast != contrast:
            self.contrast = contrast
            contrastChanged = 1
        if style is not None:
            self.style = style
        if size is not None:
            self.size = size
        if (vertices is None or len(vertices) == 0) and grid is None:
            return ()
        if grid is not None:
            grid = self.normaliseGrid(grid)
            vertices = styleDict[self.style][1](grid, self.size)
            colours = self.genColourVector(
                vertices, self.contrast, self.optimumIsMinimum)
            contrastChanged = 0
        if contrastChanged:
            colours = self.genColourVector(
                vertices, self.contrast, self.optimumIsMinimum)

        data = [
            0,
            vertices,
            texSrc,
            texCoords,
            normals,
            colours]  # opacity: colours = 4
        valNbr = [0, 3, 0, 2, 3, 3]
        for t in A:
            self.data[t].update({AS.arr: data[t],
                                 AS.changed: True,
                                 AS.const: glConst[t],
                                 AS.func: glFunc[t],
                                 AS.valNbr: valNbr[t]})
        self.length = len(self.data[A.vert][AS.arr]) // 3

    def __alloc(self):
        for t in A:
            d = self.data[t]
            if t == A.texSrc:
                continue
            elif d[AS.arr]:
                d[AS.changed] = False
                d[AS.vbo] = glGenBuffers(1)
                glBindBuffer(GL_ARRAY_BUFFER, d[AS.vbo])
                glBufferData(GL_ARRAY_BUFFER,
                             len(d[AS.arr]) * 4,
                             (c_float * len(d[AS.arr]))(*d[AS.arr]),
                             GL_DYNAMIC_DRAW)
        err = glGetError()
        if err != 0:
            print('Error during buffer allocation', err)
            sys.exit(1)

    def __update(self):
        if self.data[A.vert][AS.changed]:
            self.length = len(self.data[A.vert][AS.arr]) // 3
        for t in A:
            d = self.data[t]
            if t == A.texSrc:
                continue
            elif d[AS.changed] and d[AS.arr]:
                d[AS.changed] = False
                glBindBuffer(GL_ARRAY_BUFFER, d[AS.vbo])
                glBufferSubData(GL_ARRAY_BUFFER, 0, len(
                    d[AS.arr]) * 4, (c_float * len(d[AS.arr]))(*d[AS.arr]))

    def draw(self):
        self.__update()
        if self.data[A.vert][AS.arr] is None:
            return ()  # glDrawArrays draws nothing if GL_VERTEX_ARRAY is disabled
        for t in A:
            d = self.data[t]
            if t == A.texSrc or d[AS.arr] is None:
                continue
            glEnableClientState(d[AS.const])
            glBindBuffer(GL_ARRAY_BUFFER, d[AS.vbo])
            d[AS.func](d[AS.valNbr], GL_FLOAT, 0, None)
        glDrawArrays(styleDict[self.style][0], 0, self.length)
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        for t in A:
            d = self.data[t]
            if t == A.texSrc or d[AS.arr] is None:
                continue
            glDisableClientState(d[AS.const])

    @staticmethod
    def normaliseGrid(grid):
        valZMin, valZMax = math.inf, -math.inf
        ii = 2
        while ii < len(grid):
            if valZMin > grid[ii]:
                valZMin = grid[ii]
            if valZMax < grid[ii]:
                valZMax = grid[ii]
            ii += 3
        dist = valZMax - valZMin
        div = dist / 2
        ii = 2
        while ii < len(grid):
            try:
                grid[ii] = (grid[ii] - valZMin) / div - 1
            except ZeroDivisionError:
                grid[ii] = 0
            ii += 3
        return (grid)

    @staticmethod
    def genColourVector(vertices, contrast=0, optimumIsMinimum=True):
        ii = 2
        c = []
        if contrast == 0:
            ex = 1
        else:
            if optimumIsMinimum:
                ex = 0.3
            else:
                ex = 2
        if contrast > 1:
            mul = 2 * (contrast - 1)
        while ii < len(vertices):
            pos = (vertices[ii] + 1.0) / 2
            if contrast > 1:
                pos = pos * mul
                pos -= int(pos)
            pos = pos ** ex
            h = pos
            i = int(h * 6.)  # XXX assume int() truncates!
            f = (h * 6.) - i
            p, q, t = 0, 1. - f, f
            i %= 6
            if i == 0:
                col = (1, t, p)
            if i == 1:
                col = (q, 1, p)
            if i == 2:
                col = (p, 1, t)
            if i == 3:
                col = (p, q, 1)
            if i == 4:
                col = (t, p, 1)
            if i == 5:
                col = (1, p, q)
            c.extend(col)
            # c.extend(opacity) #opacity
            ii += 3
        return c
