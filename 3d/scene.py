"""
Inferflow 3D Game Engine Demo
Demonstrates 3D scene construction, lighting, and rendering pipeline
using Panda3D — covering Open3D Engine, Stride, and Panda3D categories.
"""

from panda3d.core import (
    Point3, Vec3, Vec4, DirectionalLight, AmbientLight,
    PointLight, AntialiasAttrib, GraphicsOutput,
    FrameBufferProperties, WindowProperties, GraphicsPipe,
    Filename, PNMImage, NodePath, GeomNode, Geom,
    GeomVertexFormat, GeomVertexData, GeomVertexWriter,
    GeomTriangles, GeomLines, RenderState, ColorAttrib,
    LColor, LineSegs, CardMaker, TextNode
)
from direct.showbase.ShowBase import ShowBase
import math
import sys
import os

os.environ['DISPLAY'] = ''

class GameDemo(ShowBase):
    def __init__(self):
        # Offscreen rendering
        ShowBase.__init__(self, windowType='offscreen')
        self.win.setClearColor(Vec4(0.02, 0.02, 0.08, 1))

        self.render.setAntialias(AntialiasAttrib.MAuto)
        self.setup_scene()
        self.setup_lights()
        self.setup_camera()

        # Render one frame and screenshot
        self.graphicsEngine.renderFrame()
        self.screenshot("/home/claude/gamedev/screenshots/3d_scene.png")
        print("✅ 3D screenshot saved")

    def make_box(self, w, h, d, color):
        fmt = GeomVertexFormat.getV3n3c4()
        vdata = GeomVertexData('box', fmt, Geom.UHStatic)
        vertex = GeomVertexWriter(vdata, 'vertex')
        normal = GeomVertexWriter(vdata, 'normal')
        color_w = GeomVertexWriter(vdata, 'color')

        hw, hh, hd = w/2, h/2, d/2
        faces = [
            # front
            [(-hw,-hd,-hh),(hw,-hd,-hh),(hw,-hd,hh),(-hw,-hd,hh),(0,-1,0)],
            # back
            [(hw,hd,-hh),(-hw,hd,-hh),(-hw,hd,hh),(hw,hd,hh),(0,1,0)],
            # left
            [(-hw,hd,-hh),(-hw,-hd,-hh),(-hw,-hd,hh),(-hw,hd,hh),(-1,0,0)],
            # right
            [(hw,-hd,-hh),(hw,hd,-hh),(hw,hd,hh),(hw,-hd,hh),(1,0,0)],
            # bottom
            [(-hw,-hd,-hh),(-hw,hd,-hh),(hw,hd,-hh),(hw,-hd,-hh),(0,0,-1)],
            # top
            [(-hw,-hd,hh),(hw,-hd,hh),(hw,hd,hh),(-hw,hd,hh),(0,0,1)],
        ]

        tris = GeomTriangles(Geom.UHStatic)
        vi = 0
        for face in faces:
            nx, ny, nz = face[4]
            r, g, b, a = color
            for i in range(4):
                vx, vy, vz = face[i]
                vertex.addData3(vx, vy, vz)
                normal.addData3(nx, ny, nz)
                shade = 0.7 + 0.3 * abs(nz) + 0.2 * abs(nx)
                color_w.addData4(r*shade, g*shade, b*shade, a)
            tris.addVertices(vi, vi+1, vi+2)
            tris.addVertices(vi, vi+2, vi+3)
            vi += 4

        geom = Geom(vdata)
        geom.addPrimitive(tris)
        node = GeomNode('box')
        node.addGeom(geom)
        return NodePath(node)

    def setup_scene(self):
        # Ground plane
        ground = self.make_box(40, 40, 0.5, (0.1, 0.3, 0.1, 1))
        ground.reparentTo(self.render)
        ground.setPos(0, 0, -2)

        # Main castle/fortress structure
        # Central tower
        tower = self.make_box(4, 4, 12, (0.5, 0.5, 0.6, 1))
        tower.reparentTo(self.render)
        tower.setPos(0, 0, 4)

        # Tower top
        top = self.make_box(5, 5, 1, (0.4, 0.4, 0.5, 1))
        top.reparentTo(self.render)
        top.setPos(0, 0, 10.5)

        # Side towers
        for x, y in [(-6, -6), (6, -6), (-6, 6), (6, 6)]:
            st = self.make_box(2.5, 2.5, 8, (0.45, 0.45, 0.55, 1))
            st.reparentTo(self.render)
            st.setPos(x, y, 2)

        # Walls connecting towers
        for x, y, w, d in [
            (0, -6, 10, 1),
            (0, 6, 10, 1),
            (-6, 0, 1, 10),
            (6, 0, 1, 10),
        ]:
            wall = self.make_box(w, d, 5, (0.4, 0.4, 0.5, 1))
            wall.reparentTo(self.render)
            wall.setPos(x, y, 0.5)

        # Floating crystals
        crystal_positions = [
            (8, 2, 4), (-8, -3, 6), (3, -9, 3),
            (-5, 8, 5), (10, -8, 2)
        ]
        crystal_colors = [
            (0.2, 0.8, 1.0, 1),
            (0.8, 0.2, 1.0, 1),
            (1.0, 0.6, 0.1, 1),
            (0.2, 1.0, 0.4, 1),
            (1.0, 0.2, 0.3, 1),
        ]
        for i, (x, y, z) in enumerate(crystal_positions):
            c = self.make_box(1, 1, 2.5, crystal_colors[i])
            c.reparentTo(self.render)
            c.setPos(x, y, z)
            c.setHpr(45, 30, 15)

        # Grid floor lines
        ls = LineSegs()
        ls.setColor(0.2, 0.4, 0.2, 1)
        ls.setThickness(1)
        for i in range(-10, 11):
            ls.moveTo(i*2, -20, -1.7)
            ls.drawTo(i*2, 20, -1.7)
            ls.moveTo(-20, i*2, -1.7)
            ls.drawTo(20, i*2, -1.7)
        grid = self.render.attachNewNode(ls.create())

        # HUD elements (2D overlay text)
        tn = TextNode('hud')
        tn.setText("INFERFLOW 3D ENGINE — FORTRESS SCENE")
        tn.setTextColor(0.4, 0.8, 1, 1)
        tn.setAlign(TextNode.ACenter)
        tnp = self.aspect2d.attachNewNode(tn)
        tnp.setScale(0.07)
        tnp.setPos(0, 0, 0.9)

        tn2 = TextNode('hud2')
        tn2.setText("Panda3D | Open3D Engine | Stride (Xenko)")
        tn2.setTextColor(0.7, 0.7, 1, 1)
        tn2.setAlign(TextNode.ACenter)
        tnp2 = self.aspect2d.attachNewNode(tn2)
        tnp2.setScale(0.055)
        tnp2.setPos(0, 0, -0.92)

    def setup_lights(self):
        # Main directional light (sun)
        dlight = DirectionalLight('sun')
        dlight.setColor(Vec4(1.0, 0.95, 0.8, 1))
        dlnp = self.render.attachNewNode(dlight)
        dlnp.setHpr(45, -45, 0)
        self.render.setLight(dlnp)

        # Ambient
        alight = AmbientLight('ambient')
        alight.setColor(Vec4(0.25, 0.25, 0.35, 1))
        alnp = self.render.attachNewNode(alight)
        self.render.setLight(alnp)

        # Colored point lights for crystals
        colors = [(0.3,0.8,1),(0.8,0.3,1),(1,0.6,0.2)]
        positions = [(8,2,6), (-8,-3,8), (3,-9,5)]
        for col, pos in zip(colors, positions):
            pl = PointLight('pl')
            pl.setColor(Vec4(*col, 1))
            pl.setAttenuation(Vec3(0.5, 0, 0.05))
            plnp = self.render.attachNewNode(pl)
            plnp.setPos(*pos)
            self.render.setLight(plnp)

    def setup_camera(self):
        self.camera.setPos(22, -22, 14)
        self.camera.lookAt(0, 0, 3)

demo = GameDemo()
