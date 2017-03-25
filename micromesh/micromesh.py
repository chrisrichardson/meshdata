""" A super simple library for low volume two-dimensional unstructured meshes. Meshes are
    stored as python dicts containing 'geometry', 'topology' and maybe other keys
    and can be read from a URL pointing to a text-based XDMF file """

import matplotlib.pyplot as plt
import matplotlib.tri as tri
import numpy

# TODO - rectangle mesh generator


def get(url):
    """ Read a mesh in XDMF XML format (not HDF5) from a URL"""
    try:
        import requests
        import xml.etree.ElementTree as ET
    except ImportError:
        raise("Missing required library")

    r = requests.get(url)
    # FIXME: check return status

    et = ET.fromstring(r.text)
    print(et)

    # Do more checks
    grid = et[0][0]

    topology = grid.find('Topology')
    assert(topology.attrib['TopologyType'] == 'Triangle')
    tdims = numpy.fromstring(topology[0].attrib['Dimensions'], sep=' ', dtype='int')
    nptopo = numpy.fromstring(topology[0].text, sep=' ', dtype='int').reshape(tdims)

    geometry = grid.find('Geometry')
    assert(geometry.attrib['GeometryType'] == 'XY')
    gdims = numpy.fromstring(geometry[0].attrib['Dimensions'], sep=' ', dtype='int')
    npgeom = numpy.fromstring(geometry[0].text, sep=' ', dtype='float').reshape(gdims)

    # Find all attributes and put them in a list
    attr = grid.find('Attribute')
    print(attr.attrib)
    adims = numpy.fromstring(attr[0].attrib['Dimensions'], sep=' ', dtype='int')
    npattr = numpy.fromstring(attr[0].text, sep=' ', dtype='int')

    mesh = {'geometry':npgeom, 'topology':nptopo, 'marker':npattr}

    return mesh

def plot(mesh, data=None):
    """ Plot a mesh with matplotlib, possibly with associated data """

    # FIXME: check keys of mesh contain geometry and topology
    geom, topo = mesh['geometry'], mesh['topology']
    x = geom[:,0]
    y = geom[:,1]

    plt.gca(aspect='equal')

    if data is not None:
        if len(data)==len(geom):
            plt.tricontourf(x, y, topo, data, 40)
        elif len(data)==len(topo):
            tr = tri.Triangulation(x, y, topo)
            plt.tripcolor(tr, data)

    plt.triplot(x, y, topo, color='k', alpha=0.5)

    xmax = x.max()
    xmin = x.min()
    ymax = y.max()
    ymin = y.min()
    dx = 0.1*(xmax - xmin)
    dy = 0.1*(ymax - ymin)
    plt.xlim(xmin-dx, xmax+dx)
    plt.ylim(ymin-dy, ymax+dy)

    return
