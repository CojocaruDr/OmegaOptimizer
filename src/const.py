from OpenGL.GL import *

from src.types import DrawStyle
from src.utils import grid_to_triangles2, grid_to_triangles4, grid_to_quads

# opacity = 1

glConst = [0, GL_VERTEX_ARRAY, 0, 0, 0, GL_COLOR_ARRAY]
glFunc = [0, glVertexPointer, 0, 0, 0, glColorPointer]

styleDict = dict()
styleDict[DrawStyle.triangles2] = [GL_TRIANGLES, grid_to_triangles2]
styleDict[DrawStyle.triangles4] = [GL_TRIANGLES, grid_to_triangles4]
styleDict[DrawStyle.quads] = [GL_QUADS, grid_to_quads]
styleDict[DrawStyle.lines] = [GL_LINES, grid_to_triangles2]
