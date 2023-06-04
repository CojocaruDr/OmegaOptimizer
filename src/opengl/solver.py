import math
import time
from contextlib import suppress

from OpenGL.GL import *
from OpenGL.GLUT import *

import pygame
from pygame import DOUBLEBUF, OPENGL

from src.algorithms.algorithm import Algorithm
from src.opengl.object import OglObject
from src.types import DrawStyle, AS, A
from src.utils import gen_cube, flatten_vertex_list, gen_basic_grid


class OglSolver:
    def __init__(
            self,
            title='Python OpenGL Solver',
            w=1024,
            h=1024,
            display_flags=pygame.RESIZABLE | pygame.OPENGL | pygame.DOUBLEBUF,
            size=101,
            contrast=0,
            style=DrawStyle.triangles2,
            algorithms=None,
            run_algs_together=False,
            redraw_mesh_on_restart=False):

        if algorithms is None:
            algorithms = [
                Algorithm(
                    FunctionList[1])]
        self.w = w
        self.h = h
        self.displayFlags = display_flags
        self.title = title
        self.time = time.time()
        self.size = size
        self.algorithms = algorithms
        if run_algs_together:
            self.activeAlgorithm = -1
        else:
            self.activeAlgorithm = 0
            print(self.algorithms[0])
        self.redrawMeshOnRestart = redraw_mesh_on_restart
        self.solList = []
        self.solOldList = []
        self.rotation = [-60, 0, 20]
        self.scale = 1.0 / 1.1 ** 6
        self.pointSizeDivisor = 256
        self.contrast = contrast
        self.pressedKeys = set()
        self.initOgl()
        # OglObject alloc must happen after we've inited the display, since the
        # OGL buffer allocation needs an active display context
        self.objects = []
        cube, cubeCol = gen_cube(length=2, segments=8, offset=[-1, -1, -1])
        cube = flatten_vertex_list(cube)
        self.objects.append(OglObject(
            vertices=cube,
            colours=cubeCol,
            style=DrawStyle.lines,
            contrast=self.contrast,
            optimumIsMinimum=self.algorithms[0].optimumIsMinimum,
        ))
        # first list is averages, second is count (how many values yielded that
        # average)
        self.gridSource = self.init_grid_source()
        g = gen_basic_grid(self.size, self.size)
        self.objects.append(OglObject(
            grid=g,
            style=style,
            size=self.size,
            contrast=self.contrast,
            optimumIsMinimum=self.algorithms[0].optimumIsMinimum,
        ))
        self.activeObject = len(self.objects) - 1
        gpv = self.objects[self.activeObject].data[A.vert][AS.arr][:]
        gpStyle = self.objects[self.activeObject].style
        gpSize = self.objects[self.activeObject].size
        gpl = len(gpv)
        self.zDrop = -1.3
        ii = 2
        while ii < gpl:
            gpv[ii] = 0
            ii += 3
        gp = OglObject(
            vertices=gpv,
            style=gpStyle,
            size=gpSize,
            contrast=self.contrast,
            optimumIsMinimum=self.algorithms[0].optimumIsMinimum,
        )
        gp.data[A.col][AS.arr] = []
        # HACK! we use the same VRAM colour buffer, since the colour
        # information is not affected by the z-orhoProjection (flattening z,
        # projecting on xOy)
        gp.data[A.col][AS.vbo] = self.objects[self.activeObject].data[A.col][AS.vbo]
        self.objects.append(gp)
        self.activeObjectProj = len(self.objects) - 1
        self.oldPoints = []
        self.newPoints = []
        self.paused = 0
        self.doOneStep = 0
        self.doPrint = 1
        self.shouldDrawBottom = 1
        self.shouldDrawNewVertices = 1
        self.progBarZ = -1
        self.progBarHeight = 0.01

    def initOgl(self):
        pygame.init()
        # init the display size and properties; we specifically request an
        # OpenGL context and a resizable window
        # pygame.DOUBLEBUF, pygame.NOFRAME ...
        pygame.display.set_mode((self.w, self.h), self.displayFlags)
        screen = pygame.display.get_surface()
        if screen.get_flags() & DOUBLEBUF:
            print('Doublebuffered', end=' ')
        else:
            print('Singlebuffered', end=' ')
        if screen.get_flags() & OPENGL:
            print('OpenGl')
        else:
            print('No OpenGl')
        # set the window name
        pygame.display.set_caption(self.title)
        # our custom init
        # set the color used to erase the display
        glClearColor(0.0, 0.0, 0.0, 1.0)
        # set the width of lines being drawn
        glLineWidth(3)
        glEnable(GL_DEPTH_TEST)
        # glEnable(GL_MULTISAMPLE)
        # glEnable(GL_BLEND)
        # glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        # glEnable(GL_POINT_SMOOTH)
        # glEnable(GL_LINE_SMOOTH)
        # glEnable(GL_POLYGON_SMOOTH)
        # glHint(GL_POINT_SMOOTH, GL_NICEST)
        # set the thickness of points being drawn
        glPointSize(max(self.w, self.h) // max(int(self.pointSizeDivisor), 1))
        self.set_projection()

    def exit_program(self):
        pygame.quit()
        raise SystemExit

    def init_grid_source(self, old_grid=None, redraw_mesh=True, start_value=0):
        gs = [[], [0.0] * self.size * self.size, []]
        if old_grid is None:
            for ii in range(self.size):
                xi = -1 + 2 * ii / (self.size - 1)
                for jj in range(self.size):
                    yi = -1 + 2 * jj / (self.size - 1)
                    gs[2].append([xi, yi])
        else:
            gs[2] = old_grid[2]
            if not redraw_mesh:
                gs[0] = old_grid[0]
        if len(gs[0]) == 0:
            gs[0] = [start_value] * self.size * self.size
        return gs

    def display(self):
        # clears the image
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        self.draw_scene()
        # make sure the image is displayed
        glFlush()

    def key_down(self, key):
        if key == 27:
            self.exit_program()
        elif key == ord('r'):
            self.rotation = [0.1, 0, 0]
            self.scale = 1
        elif key == ord('f'):
            self.rotation = [179.9, 0, 0]
            self.scale = 1
        elif key == ord('t'):
            self.rotation = [-60, 0, 20]
            self.scale = 1 / 1.1 ** 6
        elif key == 32:
            self.paused = 1 - self.paused
        elif key == ord('n'):
            self.doOneStep = 1
        elif key == ord('p'):
            self.doPrint = 1 - self.doPrint
        elif key == ord('b'):
            self.shouldDrawBottom = 1 - self.shouldDrawBottom
        elif key == ord('v'):
            self.shouldDrawNewVertices = 1 - self.shouldDrawNewVertices
        elif key == 280:
            self.pointSizeDivisor /= 1.1
            point_size = max(
                self.w, self.h) // max(int(self.pointSizeDivisor), 1)
            point_size = max(1, point_size)
            # print(point_size)
            glPointSize(point_size)
        elif key == 281:
            self.pointSizeDivisor *= 1.1
            point_size = max(
                self.w, self.h) // max(int(self.pointSizeDivisor), 1)
            point_size = max(1, point_size)
            # print(point_size)
            glPointSize(point_size)
        elif key == 269:
            self.zDrop += 0.1
        elif key == 270:
            self.zDrop -= 0.1
        elif key == 267:
            a = self.activeAlgorithm
            steps = self.algorithms[a].steps
            steps = max(1, steps // 2)
            if a == -1:
                for alg in self.algorithms:
                    alg.steps = steps
            else:
                self.algorithms[a].steps = steps
            print('Algorithm steps per frame:', steps)
        elif key == 268:
            a = self.activeAlgorithm
            steps = self.algorithms[a].steps
            steps *= 2
            if a == -1:
                for alg in self.algorithms:
                    alg.steps = steps
            else:
                self.algorithms[a].steps = steps
            print('Algorithm steps per frame:', steps)
        elif key == ord('c'):
            self.contrast = (self.contrast + 1) % 5
            self.objects[self.activeObject].set(contrast=self.contrast)
        elif key == 44:
            self.activeAlgorithm = (
                                           self.activeAlgorithm - 1) % len(self.algorithms)
            print(self.algorithms[self.activeAlgorithm], 'repeat:',
                  self.algorithms[self.activeAlgorithm].doForever)
            # TODO eliminate workaround
            self.algorithms[self.activeAlgorithm].cr = 0
            if self.redrawMeshOnRestart:
                self.gridSource = self.init_grid_source(self.gridSource, self.redrawMeshOnRestart,
                                                        self.algorithms[self.activeAlgorithm].gimmeSomeEval())
                # self.gridSource[0] = [0] * self.size ** 2
                # self.gridSource[1] = [0] * self.size ** 2
        elif key == 46:
            self.activeAlgorithm = (
                                           self.activeAlgorithm + 1) % len(self.algorithms)
            print(self.algorithms[self.activeAlgorithm], 'repeat:',
                  self.algorithms[self.activeAlgorithm].doForever)
            # TODO eliminate workaround
            self.algorithms[self.activeAlgorithm].cr = 0
            if self.redrawMeshOnRestart:
                self.gridSource = self.init_grid_source(self.gridSource, self.redrawMeshOnRestart,
                                                        self.algorithms[self.activeAlgorithm].gimmeSomeEval())
                # self.gridSource[0] = [0] * self.size ** 2
                # self.gridSource[1] = [0] * self.size ** 2
        elif key == 47:
            self.algorithms[self.activeAlgorithm].doForever = 1 - \
                                                              self.algorithms[self.activeAlgorithm].doForever
            print('Repeat (only) for the current algorithm set to:',
                  self.algorithms[self.activeAlgorithm].doForever)
        if 303 in self.pressedKeys or 304 in self.pressedKeys:
            print(key)
        self.pressedKeys.add(key)

    def key_up(self, key):
        with suppress(KeyError):
            self.pressedKeys.remove(key)
        # print(self.pressedKeys)

    def mouse_down(self, pos, button):
        x, y = pos
        if button == 5:
            self.scale /= 1.1
        elif button == 4:
            self.scale *= 1.1

    def mouse_up(self, pos, button):
        pass

    def mouse_move(self, pos, rel, buttons):
        if buttons[2]:
            xrel, yrel = rel
            xrot = xrel / self.w * 180
            yrot = yrel / self.h * 180
            self.rotation[2] += xrot
            self.rotation[0] += yrot

    def resize(self, size):
        self.w, self.h = size
        glPointSize(max(self.w, self.h) // max(int(self.pointSizeDivisor), 1))
        print('Window resized to', size)
        glViewport(0, 0, GLsizei(self.w), GLsizei(self.h))
        pygame.display.set_mode((self.w, self.h), self.displayFlags)

    def update_grid(self, sol_list):
        for sol in sol_list:
            l = (len(sol) - 1) // 2
            z, x, y = sol[0], sol[1], sol[2]
            xi, yi = sol[l + 1], sol[l + 2]
            idx = xi * self.size + yi
            num = self.gridSource[1][idx]
            self.gridSource[0][idx] = (
                                              self.gridSource[0][idx] * num + z) / (1 + num)
            self.gridSource[1][idx] = 1 + num

    def gen_mesh_from_grid(self, grid, coords=None):
        g = []
        if coords is None:
            for ii in range(self.size):
                for jj in range(self.size):
                    x = -1 + 2.0 * ii / (self.size - 1)
                    y = -1 + 2.0 * jj / (self.size - 1)
                    z = grid[ii * self.size + jj]
                    g.extend([x, y, z])
        else:
            for gp, ge in zip(coords, grid):
                g.extend([*gp, ge])
        return (g)

    def normalise_sol_inputs(self, sol_list, dim_range):
        dim_length = dim_range[1] - dim_range[0]
        s = self.size - 1
        # sol = y, *X
        for sol in sol_list:
            p = []
            for ii in range(1, len(sol)):
                pos = (sol[ii] - dim_range[0]) / dim_length
                sol[ii] = -1 + 2 * pos
                idx = round(pos * s)
                sol.append(idx)
                p.append(sol[ii])
            self.newPoints.append(p)

    def update_algo(self):
        self.oldPoints = self.newPoints
        self.newPoints = []
        a = self.activeAlgorithm
        sol_list = []
        if a == -1:
            for alg in self.algorithms:
                sol_list.extend(alg.run())
        else:
            sol_list.extend(self.algorithms[a].run())
        alg = self.algorithms[a]
        if len(sol_list):
            dim_range = alg.dimRange
            self.normalise_sol_inputs(sol_list, dim_range)
            self.update_grid(sol_list)
            g = self.gen_mesh_from_grid(self.gridSource[0], self.gridSource[2])
            self.objects[self.activeObject].set(grid=g, size=self.size)
            if self.doPrint:
                print(
                    alg,
                    'Best:',
                    alg.be,
                    '#evals for best:',
                    alg.bstep,
                    'Total evals:',
                    alg.evals,
                    'Br / Cr / R:',
                    alg.br,
                    '/',
                    alg.repCurr,
                    '/',
                    alg.repeats)
                if alg.be in [math.inf, -math.inf]:
                    try:
                        print('Current best is:', alg.ce)
                    except BaseException:
                        pass
        else:
            print(
                alg,
                'finished. ',
                'Best:',
                alg.be,
                '#evals for best:',
                alg.bstep,
                'Total evals:',
                alg.evals,
                'Br / R:',
                alg.br,
                '/',
                alg.repeats)
            if a != -1:
                self.oldPoints = []
                a = (a + 1) % len(self.algorithms)
                self.algorithms[a].restart()
                self.activeAlgorithm = a
                self.gridSource = self.init_grid_source(
                    self.gridSource,
                    self.redrawMeshOnRestart,
                    self.algorithms[a].gimmeSomeEval())
        return sol_list

    def draw_differences(self, z):
        glBegin(GL_POINTS)
        glColor4fv([0.0, 0.0, 0.0, 0.9])
        for p in self.oldPoints:
            glVertex3f(p[0], p[1], z)
        glColor4fv([1.0, 1.0, 1.0, 0.9])
        for p in self.newPoints:
            glVertex3f(p[0], p[1], z)
        glEnd()

    def draw_scene(self):
        if self.paused == 0 or self.doOneStep == 1:
            self.update_algo()
            self.doOneStep = 0
        self.draw_progress_bar()
        self.set_projection()
        self.apply_scene_transforms()
        for ii, o in enumerate(self.objects):
            if ii == self.activeObjectProj:
                continue
            o.draw()
        self.draw_plot_projection()

    def draw_progress_bar(self):
        mn = 0
        mx = self.algorithms[self.activeAlgorithm].repeats
        dist = mx - mn
        if dist == 0:
            dist = 1
        pos = self.algorithms[self.activeAlgorithm].repCurr
        pos = (pos - mn) / dist
        br = self.algorithms[self.activeAlgorithm].br
        br = (br - mn) / dist
        x0 = -1
        x1 = 1
        dist_x = x1 - x0
        xp = x0 + pos * dist_x
        xb = x0 + br * dist_x
        y0 = -1
        y1 = y0 + self.progBarHeight
        z = self.progBarZ
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glBegin(GL_QUADS)
        glColor4fv([1, 1, 1, 0.5])
        glVertex3f(x0, y0, z)
        glVertex3f(xb, y0, z)
        glVertex3f(xb, y1, z)
        glVertex3f(x0, y1, z)

        glColor4fv([1, 0.5, 0, 0.5])
        glVertex3f(xb, y0, z)
        glVertex3f(xp, y0, z)
        glVertex3f(xp, y1, z)
        glVertex3f(xb, y1, z)

        glColor4fv([0.1, 0.1, 0.1, 0.5])
        glVertex3f(xp, y0, z)
        glVertex3f(x1, y0, z)
        glVertex3f(x1, y1, z)
        glVertex3f(xp, y1, z)
        glEnd()

    def draw_plot_projection(self):
        if self.shouldDrawBottom:
            glMatrixMode(GL_MODELVIEW)
            glPushMatrix()
            glTranslate(0, 0, self.zDrop)
            self.objects[self.activeObjectProj].draw()
            glPopMatrix()
        if self.shouldDrawBottom and self.shouldDrawNewVertices:
            self.draw_differences(self.zDrop)

    @staticmethod
    def set_projection():
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(-1, 1, -1, 1, -20, 20)

    def apply_scene_transforms(self):
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glRotatef(self.rotation[0], 1, 0, 0)
        glRotatef(self.rotation[1], 0, 1, 0)
        glRotatef(self.rotation[2], 0, 0, 2)
        glScalef(self.scale, self.scale, self.scale)

    def main(self):
        """A pygame event loop which consumes and processes events from the pygame event queue"""
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit_program()
                elif event.type == pygame.KEYDOWN:
                    self.key_down(event.key)
                elif event.type == pygame.KEYUP:
                    self.key_up(event.key)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.mouse_down(event.pos, event.button)
                elif event.type == pygame.MOUSEBUTTONUP:
                    self.mouse_up(event.pos, event.button)
                elif event.type == pygame.MOUSEMOTION:
                    self.mouse_move(event.pos, event.rel, event.buttons)
                elif event.type == pygame.VIDEORESIZE:
                    self.resize(event.size)
            self.display()
            pygame.display.flip()
            pygame.time.wait(0)

    def run(self):
        # launch the event loop
        self.main()
