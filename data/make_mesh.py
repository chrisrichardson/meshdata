import pygmsh as pg
import meshio
import numpy

geom = pg.Geometry()

lcar = 0.1

circle = geom.add_circle([0.5, 0.5, 0.0], 1.0, lcar)

p0 = geom.add_point([0.5, 0.0, 0.0], lcar)
p1 = geom.add_point([0.7, 0.7, 0.0], lcar)
p2 = geom.add_point([0.0, 0.5, 0.0], lcar)

circle_arc = geom.add_circle_arc([p0, p1, p2])

triangle = geom.add_polygon([
    [2.0, -0.5, 0.0],
    [4.0, -0.5, 0.0],
    [4.0, 1.5, 0.0],
], lcar
)

rectangle = geom.add_rectangle(4.75, 6.25, -0.24, 1.25, 0.0, lcar)

# hold all domain
geom.add_polygon([
    [-1.0, -1.0, 0.0],
    [+7.0, -1.0, 0.0],
    [+7.0, +2.0, 0.0],
    [-1.0, +2.0, 0.0]], lcar,
    holes=[circle.line_loop, triangle.line_loop, rectangle.line_loop]
)


print(geom.get_code())

out = pg.generate_mesh(geom)

geom = out[0]
topo = out[1]['triangle']
cell_mark = out[3]['triangle']['geometrical']

# Remove geometry points which are not in topology
# and remap range
mp = numpy.zeros(len(geom), dtype='int')
c = 0
for i in range(len(geom)):
    if i in topo:
        mp[i] = c
        c += 1
    else:
        mp[i] = -1

# Now create mesh in dolfin and save to XDMF
from dolfin import *

ed = MeshEditor()
mesh = Mesh()
ed.open(mesh, 2, 2)
print(topo.shape, geom.shape)
ed.init_cells(topo.shape[0])
ed.init_vertices(c)
for i,p in enumerate(geom):
    if mp[i] != -1:
        print(i, mp[i])
        ed.add_vertex(mp[i], p[0], p[1])

for i,c in enumerate(topo):
    ed.add_cell(i, mp[c[0]], mp[c[1]], mp[c[2]])

ed.close()

marker = CellFunction("int", mesh, 0)
for c in cells(mesh):
    marker[c] = cell_mark[c.index()]

xdmf = XDMFFile("rectangle_mesh.xdmf")
xdmf.write(mesh, XDMFFile.Encoding_ASCII)
xdmf.write(marker, XDMFFile.Encoding_ASCII)
