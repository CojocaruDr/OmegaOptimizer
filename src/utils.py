def grid_to_triangles2(grid, width=101):
    """transforms a grid, defined as a list containing 3 float coordinates per vertex, and a width, into a triangle
    strip"""
    # quad points: i, i + 1, i + width, i + width + 1, up a quad strip
    s = []
    g = grid
    length = len(grid) // 3
    w = width
    h = length // width
    for ii in range(w - 1):
        # p = [ii * h + jj, (ii + 1) * h + jj, ii * h + jj + 1, (ii + 1) * h + jj + 1]
        xs = ii * h
        points: list[int] = [
            xs * 3,
            (xs + h) * 3,
            (xs + h + 1) * 3,
            (xs + 1) * 3]
        for jj in range(h - 1):
            tri1 = g[points[0]:points[0] + 3]
            tri1.extend(g[points[1]:points[1] + 3])
            tri1.extend(g[points[2]:points[2] + 3])
            tri2 = g[points[0]:points[0] + 3]
            tri2.extend(g[points[2]:points[2] + 3])
            tri2.extend(g[points[3]:points[3] + 3])
            s.extend(tri1)
            s.extend(tri2)
            points[0] += 3
            points[1] += 3
            points[2] += 3
            points[3] += 3
    return s


def quad_to_four_triangles(p0, p1, p2, p3):
    p5 = []
    for ii in zip(p0, p1, p2, p3):
        p5.append(sum(ii) / 4)
    r = p5 + p0 + p1 + p5 + p1 + p2 + p5 + p2 + p3 + p5 + p3 + p0
    return r


def grid_to_triangles4(grid, width=101):
    """transforms a grid, defined as a list containing 3 float coordinates per vertex, and a width, into a triangle
    strip"""
    # quad points: i, i + 1, i + width, i + width + 1, up a quad strip
    s = []
    g = grid
    length = len(grid) // 3
    w = width
    h = length // width
    for ii in range(w - 1):
        # p = [ii * h + jj, (ii + 1) * h + jj, ii * h + jj + 1, (ii + 1) * h + jj + 1]
        xs = ii * h
        points = [xs * 3, (xs + h) * 3, (xs + h + 1) * 3, (xs + 1) * 3]
        for jj in range(h - 1):
            s.extend(quad_to_four_triangles(g[points[0]:points[0] + 3],
                                            g[points[1]:points[1] + 3],
                                            g[points[2]:points[2] + 3],
                                            g[points[3]:points[3] + 3],
                                            ))
            points[0] += 3
            points[1] += 3
            points[2] += 3
            points[3] += 3
    return s


def grid_to_quads(grid, width=101):
    """transforms a grid, defined as a list containing 3 float coordinates per vertex, and a width, into a triangle
    strip"""
    # quad points: i, i + 1, i + width, i + width + 1, up a quad strip
    s = []
    g = grid
    length = len(grid) // 3
    w = width
    h = length // width
    xs = 0
    for ii in range(w - 1):
        # p = [ii * h + jj, (ii + 1) * h + jj, ii * h + jj + 1, (ii + 1) * h + jj + 1]
        points = [xs * 3, (xs + h) * 3, (xs + h + 1) * 3, (xs + 1) * 3]
        for jj in range(h - 1):
            s.extend(g[points[0]:points[0] + 3]
                     + g[points[1]:points[1] + 3]
                     + g[points[2]:points[2] + 3]
                     + g[points[3]:points[3] + 3]
                     )
            points[0] += 3
            points[1] += 3
            points[2] += 3
            points[3] += 3
        xs += h
    return s


def gen_basic_grid(width, height):
    g = []
    for ii in range(width):
        for jj in range(height):
            xs = (2.0 * ii) / (width - 1) - 1
            y = (2.0 * jj) / (height - 1) - 1
            # z = 20 * random.random() - 10
            z = xs - y
            g.extend([xs, y, z])
    # g[2] = -100
    return g


def get_minmax_hline(ps, pe):
    mn = 0
    mx = 0
    for ii, jj in zip(ps, pe):
        if ii != jj:
            mn = min(ii, jj)
            mx = max(ii, jj)
    return mn, mx


def interpolate(ps, pe, segments):
    mn, mx = get_minmax_hline(ps, pe)
    md = mx - mn
    r = []
    rc = []
    for i in range(segments):
        a0 = i / segments
        a1 = (i + 1) / segments
        p0 = []
        p1 = []
        for jj in range(len(ps)):
            p0.append(ps[jj] + (pe[jj] - ps[jj]) * a0)
            p1.append(ps[jj] + (pe[jj] - ps[jj]) * a1)
        r.extend([p0, p1])
        for ii, jj in zip(p0, p1):
            if ii != jj:
                pos1 = (ii - mn) / md
                pos2 = (jj - mn) / md
                # opacity
                rc.extend([1 - pos1, 1 - abs(0.5 - pos1) * 1.7, pos1])
                rc.extend([1 - pos2, 1 - abs(0.5 - pos2) * 1.7, pos2])
    return r, rc


def gen_cube(length=1, segments=1, point=None, offset=None):
    if offset is None:
        offset = [0, 0, 0]
    if point is None:
        point = [0, 0, 0]

    ret = []
    ret_c = []
    ps = []
    for ii in range(3):
        ps.append(point[ii] * length + offset[ii])
    for ii in range(3):
        if point[ii] == 0:
            p = point[:]
            p[ii] = 1
            pe = []
            for jj in range(3):
                pe.append(p[jj] * length + offset[jj])
            # ret.extend([ ps[:], pe[:] ])
            lines, colours = interpolate(ps, pe, segments)
            ret.extend(lines)
            ret_c.extend(colours)
            if p != [1, 1, 1]:
                r, c = gen_cube(length, segments, p, offset)
                ret.extend(r)
                ret_c.extend(c)
    return ret, ret_c


def flatten_vertex_list(vertices):
    ret = []
    for ii in vertices:
        for jj in ii:
            ret.append(jj)
    return ret
