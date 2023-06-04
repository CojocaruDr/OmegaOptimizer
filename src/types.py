from enum import IntEnum


class DrawStyle(IntEnum):
    triangles2 = 1
    triangles4 = 2
    quads = 3
    lines = 4


class ArrayType(IntEnum):
    vert = 1
    texSrc = 2
    tex = 3
    norm = 4
    col = 5


class ArraySubType(IntEnum):
    arr = 1
    vbo = 2
    changed = 3
    const = 4
    func = 5
    valNbr = 6


A = ArrayType
AS = ArraySubType
