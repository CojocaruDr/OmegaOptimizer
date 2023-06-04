#!/usr/bin/python3
# cython: language_level=3
# This program is (c) Eugen Croitoru, "Al. I. Cuza" University of Iasi, Romania, 2020
# Licensed under GPLv3+
# References: function definitions were taken from:
#  - http://www.geatbx.com/docu/fcnindex-01.html
#  - Molga, M., & Smutnicki, C. Test functions for optimization needs (2005)

from src.algorithms.algorithm import Algorithm
from src.algorithms.bf import AlgorithmBf
from src.algorithms.bihc import AlgorithmBihc
from src.algorithms.ga import AlgorithmGa
from src.algorithms.gabihc import AlgorithmGaBihc
from src.algorithms.pso import AlgorithmPso
from src.functions.functions import FunctionList, FE
from src.opengl.solver import OglSolver

from src.types import DrawStyle

help_menu = '''
Section 1:
if you don't have a C compiler:
pip install PyOpenGL pygame
if you do have a C compiler, accessible system-wide:
pip install PyOpenGL PyOpenGL_accelerate pygame

pyOpenGl reference at:
http://pyopengl.sourceforge.net/documentation/manual-3.0/index.html

pygame reference at e.g.:
https://www.pygame.org/docs/ref/event.html

Usage:
this program displays various optimisation/search algorithms searching benchmark functions.
Keys:
  Esc: exit
  r: reset view
  f: 2d view (3d bottom), see the points the algorithm has visited (white: current, black: previous)
  t: 2d view (3d top)
  space: pause
  n: if paused, advance 1 step
  p: toggle verbose message printing, such as after every algorithm step
  b: toggle plot projection drawing
  v: toggle plot projection visited points drawing
  PgUp: increase point visual size
  PgDown: decrease point visual size
  +, - (Numpad): modify the vertical position of the projection. The projection can be moved above the plot.
  *, / (Numpad): double or halve the number a steps the algorithm does every frame
  c: cycle through contrast/colouring settings
  <, >: switch to the prev / next algorithm (loops)
  /: toggles the currently selected algorithm to run forever


=============
Section 2:
The following is optional, for faster program execution:

This program works with cython.
How-to: create script named:
setup.py
------------------------------------------
#!/usr/bin/env python3
from setuptools import setup
from Cython.Build import cythonize

setup(
    name='Solver GL',
    ext_modules=cythonize("solverGl.pyx"),
    zip_safe=False,
)
------------------------------------------
run the cython-built module:
$ cp solverGl.py solverGl.pyx -f; python3 setup.py build_ext --inplace; python3 -c 'import solverGl; solverGl.main()'
The above section is optional. You can skip above to Section 1 for basic running instructions.
===============================
'''
print(help_menu)


# needs a compiler to install, provided by PyOpenGL_accelerate
# from OpengGL.GLU import *


def main():
    style = DrawStyle.quads  # for speed
    # style = DrawStyle.triangles4 #for looks
    gen_no = 1
    gen_grace = 200
    pop_size = 50
    dimensions = 2
    precision = 20
    steps = 1
    algos = []
    for fe in FE:
        algos.extend([
            Algorithm(func=FunctionList[fe], precision=precision, dimensions=dimensions, doForever=0,
                      steps=steps * pop_size, repeats=pop_size * (gen_no + 5 * gen_grace), optimumIsMinimum=True),
            # only as a small demo, that's why we lower the precision
            AlgorithmBf(
                func=FunctionList[fe],
                precision=1,
                dimensions=dimensions,
                steps=steps,
                optimumIsMinimum=True),
            AlgorithmBihc(func=FunctionList[fe], precision=precision, dimensions=dimensions, steps=steps,
                          optimumIsMinimum=True, repeats=gen_no + 5 * gen_grace),
            AlgorithmPso(func=FunctionList[fe], dimensions=dimensions, steps=steps, doForever=0, popSize=pop_size,
                         genNo=gen_no, genGrace=gen_grace, optimumIsMinimum=True, w=[1, 2.05, 2.05, 0.99, 0.1, 0.01]),
            AlgorithmGa(func=FunctionList[fe], precision=precision, dimensions=dimensions, steps=steps,
                        popSize=pop_size,
                        selPressure=1, doForever=0, genNo=gen_no, genGrace=gen_grace, optimumIsMinimum=True),
            AlgorithmGa(func=FunctionList[fe], precision=precision, dimensions=dimensions, steps=steps,
                        popSize=pop_size,
                        selPressure=1, doForever=0, genNo=gen_no, genGrace=gen_grace, optimumIsMinimum=True, pm=0.5),
            AlgorithmGa(func=FunctionList[fe], precision=precision, dimensions=dimensions, steps=steps,
                        popSize=pop_size,
                        selPressure=1, doForever=0, genNo=gen_no, genGrace=gen_grace, optimumIsMinimum=True, pm=0.95),
            AlgorithmGaBihc(func=FunctionList[fe], precision=precision, dimensions=dimensions, steps=steps,
                            popSize=pop_size, selPressure=1, doForever=0, genNo=gen_no, genGrace=gen_grace,
                            optimumIsMinimum=True),
            AlgorithmGaBihc(func=FunctionList[fe], precision=precision, dimensions=dimensions, steps=steps,
                            popSize=pop_size, selPressure=1, doForever=0, genNo=gen_no, genGrace=gen_grace,
                            optimumIsMinimum=True, pm=0.5),
            AlgorithmGaBihc(func=FunctionList[fe], precision=precision, dimensions=dimensions, steps=steps,
                            popSize=pop_size, selPressure=1, doForever=0, genNo=gen_no, genGrace=gen_grace,
                            optimumIsMinimum=True, pm=0.95),
        ])

    algos.append(AlgorithmGa(func=FunctionList[FE.rastrigin],
                             precision=precision,
                             dimensions=dimensions,
                             steps=steps,
                             popSize=pop_size,
                             selPressure=1,
                             doForever=1,
                             genNo=gen_no,
                             genGrace=gen_grace,
                             optimumIsMinimum=True))
    # alg = AlgorithmBIHC(func = FunctionList[FE.rhe], precision = 5, dimensions = 2, steps = 1, doForever = 1)
    app = OglSolver(
        size=101,
        style=style,
        contrast=1,
        algorithms=algos,
        redraw_mesh_on_restart=True)
    app.run()


if __name__ == "__main__":
    main()
