# Parametric case for the VdMot Controller board (C2/C3 layout), FreeCAD script
#
# Two parts: a base tray the board sits in and a lid that slides down over the
# connectors. The board is not screwed, it rests on posts and is held down by
# pins of the lid. The lid is screwed to the base with 4 x M3 from the top, the
# base can be screwed to a wall with 4 screws through the floor.
#
# Coordinates are those of the board 3D model (hardware/c3-sample_3D.step):
# origin at the lower left board corner, valve jacks X1..X10 along y = 0,
# WT32-ETH01 LAN jack, terminals and X11/X12 along y = 86, z = 0 is the board top.
#
# Run:  freecadcmd -c "exec(open('vdmot_case.py').read())"
#       or open it as a macro in FreeCAD. Output is written next to this file.

import os
import FreeCAD
import Part
import Mesh
import MeshPart
from FreeCAD import Vector as V

OUT_DIR = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.getcwd()

# ---------------------------------------------------------------- parameters

BOARD_W, BOARD_D, BOARD_T = 155.6, 86.0, 1.6   # board size and thickness

WALL = 2.2           # wall thickness
FLOOR = 2.0          # floor thickness
ROOF = 2.0           # lid top thickness
GAP = 0.4            # clearance between board edge and wall
SIDE_MARGIN = 9.0    # space left/right of the board for the lid screws and wall mounting holes
STANDOFF = 5.0       # floor to board bottom, through hole pins of the 3D model stick out 1.9 mm, trim leads to <= 3 mm
INNER_H = 27.0       # board top to the inside of the lid, the LAN jack is 25.6 mm high
SPLIT = -0.5         # height of the joint between base and lid, relative to the board top
CONN_CLEAR = 0.5     # clearance around connectors in the lid openings

# connectors that need an opening in the lid: (name, side, x0, x1, z0, z1, label, enabled)
# side "front" = y 0 (valve jacks), "back" = y 86, x/z from the 3D model, z relative to the board top
CONNECTORS = [
    ("X1",  "front",   4.11,  15.31, 0.0, 11.5, "1",  True),
    ("X2",  "front",  19.24,  30.44, 0.0, 11.5, "2",  True),
    ("X3",  "front",  34.38,  45.58, 0.0, 11.5, "3",  True),
    ("X4",  "front",  49.51,  60.71, 0.0, 11.5, "4",  True),
    ("X5",  "front",  64.64,  75.84, 0.0, 11.5, "5",  True),
    ("X6",  "front",  79.78,  90.98, 0.0, 11.5, "6",  True),
    ("X7",  "front",  94.91, 106.11, 0.0, 11.5, "7",  True),
    ("X8",  "front", 110.04, 121.24, 0.0, 11.5, "8",  True),
    ("X9",  "front", 125.18, 136.38, 0.0, 11.5, "9",  True),
    ("X10", "front", 140.31, 151.51, 0.0, 11.5, "10", True),
    ("LAN", "back",   11.38,  27.42, 9.0, 25.55, "LAN", True),
    ("X18", "back",   34.90,  51.30, 0.0, 8.4, "1-WIRE", True),
    ("X17", "back",   54.70,  71.10, 0.0, 8.4, "RS485", False),   # only if RS485 is used
    ("X19", "back",   74.30,  90.70, 0.0, 8.4, "CAN", False),     # only if CAN is used
    ("X13", "back",  102.00, 113.40, 0.0, 8.4, "PWR", True),
    ("X12", "back",  125.18, 136.38, 0.0, 11.5, "12", True),
    ("X11", "back",  140.31, 151.51, 0.0, 11.5, "11", True),
]

# the pluggable terminals (header on the board, screw plug outside the case) need a higher opening:
# the latches of the plugs reach into the case just above the header (8.4 mm). Height above the
# board top, the opening is CONN_CLEAR higher, so 2 mm higher than for the header alone.
PLUG_OPENING_TOP = {"X13": 10.4, "X18": 10.4, "X17": 10.4, "X19": 10.4}

# support posts below the board and clamp pins of the lid above it, on the same spots, so the board
# is held between them. Taken from the 3D model: the posts keep >= 1.9 mm to through hole pins and
# parts below the board, the clamps >= 1.4 mm to components above it (bounding boxes)
POSTS = [(3.0, 20.5), (3.0, 45.0), (3.0, 83.0), (59.5, 23.5), (101.75, 23.75),
         (150.0, 24.75), (152.75, 46.25), (118.75, 83.0), (137.75, 43.25), (49.75, 71.5)]
POST_R = 2.5
# the board is screwed to the base through two of its mounting holes, M3 x 6 into heat set inserts
# (same inserts as for the lid screws). Hole centers measured on a real board:
# 35 mm from the right / 6.5 mm from the back edge, and 24.5 mm from the left / 45 mm from the back edge
BOARD_SCREWS = [(BOARD_W - 35.0, BOARD_D - 6.5), (24.5, BOARD_D - 45.0)]
BOARD_SCREW_POST_D = 7.6   # 0.8 mm to the pins of X12 below the board

# pins of the lid above the board, not needed with the board screwed down: the connectors along
# the front and back edge sit just below their openings and keep the edges down
CLAMPS = []
CLAMP_R = 2.0
CLAMP_GAP = 0.75     # gap between the clamp pins and the board top

# lid screws: M3 x 8 socket head (DIN 912) into heat set inserts in the base posts, default for
# ruthex M3 short (RX-M3Sx4.0, 4 mm long): hole 4.0 mm, 7.1 mm deep, chamfer at the top.
# For self tapping screws without inserts use SCREW_PILOT_D = 2.6 and INSERT_CHAMFER = 0
SCREW_PILOT_D = 4.0
INSERT_CHAMFER = 0.5
SCREW_CLEAR_D = 3.4
SCREW_HEAD_D = 6.4
LID_BOSS_D = 8.5     # bosses and posts touch the side walls
BASE_POST_D = 8.5
SCREW_Y = (8.0, BOARD_D - 8.0)

# wall mounting holes through the floor, in the side margins
MOUNT_HOLE_D = 4.5
MOUNT_Y = (26.0, BOARD_D - 26.0)

# alignment: the inner part of the base side walls rises as a lip into a rebate of the lid side walls
LIP_T, LIP_H, LIP_GAP = 1.0, 3.0, 0.2

# stops at the left and right board edges, so the board can not slide sideways (y ranges)
EDGE_STOPS_Y = ((30.0, 40.0), (50.0, 58.0))
EDGE_STOP_W = 1.6

# ventilation slots
VENT_W = 2.0
ROOF_VENTS = dict(x0=36.0, x1=152.0, pitch=5.0, y0=30.0, y1=64.0)
SIDE_VENTS = dict(z=(3.0, 8.0, 13.0, 18.0), y0=22.0, y1=BOARD_D - 22.0)

# engraved labels
FONT = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
LABEL_H = 4.5
LABEL_DEPTH = 0.6
TITLE = "VdMot"

FITCHECK_H = 14.0    # height of the fit check frame above the board top

# ---------------------------------------------------------------- derived values

xi0, xi1 = -GAP - SIDE_MARGIN, BOARD_W + GAP + SIDE_MARGIN     # inner faces
yi0, yi1 = -GAP, BOARD_D + GAP
xo0, xo1, yo0, yo1 = xi0 - WALL, xi1 + WALL, yi0 - WALL, yi1 + WALL
zb = -BOARD_T                    # board bottom
zf = zb - STANDOFF               # floor top
zf0 = zf - FLOOR                 # case bottom
zs = SPLIT                       # joint base / lid
zr = INNER_H                     # inside of the lid top
zr1 = INNER_H + ROOF             # case top
screw_x = (xi0 + LID_BOSS_D / 2 - 0.25, xi1 - LID_BOSS_D / 2 + 0.25)   # merged into the side walls


def lip_y():
    return SCREW_Y[0] + LID_BOSS_D / 2 + 1.0, SCREW_Y[1] - LID_BOSS_D / 2 - 1.0


def box(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def cyl(x, y, r, z0, z1):
    return Part.makeCylinder(r, z1 - z0, V(x, y, z0))


def fuse(shapes):
    result = shapes[0]
    for s in shapes[1:]:
        result = result.fuse(s)
    return result.removeSplitter()


def text_solid(text, height, depth):
    """text in the xy plane, reading along +x, baseline centered at the origin, extruded along +z"""
    chars = Part.makeWireString(text, os.path.dirname(FONT) + "/", os.path.basename(FONT), height, 0)
    faces = []
    for wires in chars:
        if wires:
            faces.append(Part.makeFace(wires, "Part::FaceMakerBullseye"))
    solid = Part.makeCompound([f.extrude(V(0, 0, depth)) for f in faces])
    bb = solid.BoundBox
    solid.translate(V(-(bb.XMin + bb.XMax) / 2, -(bb.YMin + bb.YMax) / 2, 0))
    return solid


def wall_label(text, x, z, side):
    """label engraved into the outer face of the front (y min) or back (y max) wall"""
    t = text_solid(text, LABEL_H, LABEL_DEPTH + 1)
    # text plane xy -> xz, readable from the outside
    t.rotate(V(0, 0, 0), V(1, 0, 0), 90)            # reading +x, up +z, extruded toward -y
    if side == "front":
        t.translate(V(x, yo0 + LABEL_DEPTH, z))       # cut from the outside into the wall
    else:
        t.rotate(V(0, 0, 0), V(0, 0, 1), 180)        # reading -x seen from the back
        t.translate(V(x, yo1 - LABEL_DEPTH, z))
    return t


def roof_label(text, x, y, height=LABEL_H, rot=0):
    t = text_solid(text, height, LABEL_DEPTH + 1)
    if rot:
        t.rotate(V(0, 0, 0), V(0, 0, 1), rot)
    t.translate(V(x, y, zr1 - LABEL_DEPTH))
    return t


# ---------------------------------------------------------------- base

def make_base():
    shell = box(xo0, xo1, yo0, yo1, zf0, zs).cut(box(xi0, xi1, yi0, yi1, zf, zs + 1))
    parts = [shell]
    # support posts, except where a screw post is
    free = [(x, y) for x, y in POSTS
            if all(((x - sx) ** 2 + (y - sy) ** 2) ** 0.5 > POST_R + BOARD_SCREW_POST_D / 2 + 1 for sx, sy in BOARD_SCREWS)]
    parts += [cyl(x, y, POST_R, zf - 0.01, zb) for x, y in free]
    parts += [cyl(x, y, BOARD_SCREW_POST_D / 2, zf - 0.01, zb) for x, y in BOARD_SCREWS]
    for x in screw_x:
        for y in SCREW_Y:
            parts.append(cyl(x, y, BASE_POST_D / 2, zf - 0.01, zs))
    # alignment lips: inner part of the left and right walls, between the screw posts
    ly0, ly1 = lip_y()
    parts.append(box(xi0 - LIP_T, xi0, ly0, ly1, zs - 0.01, zs + LIP_H))
    parts.append(box(xi1, xi1 + LIP_T, ly0, ly1, zs - 0.01, zs + LIP_H))
    # stops at the board edges, below the board top
    for y0, y1 in EDGE_STOPS_Y:
        parts.append(box(-GAP - EDGE_STOP_W, -GAP, y0, y1, zf - 0.01, zs))
        parts.append(box(BOARD_W + GAP, BOARD_W + GAP + EDGE_STOP_W, y0, y1, zf - 0.01, zs))
    base = fuse(parts)
    holes = []
    for x in screw_x:
        for y in SCREW_Y:
            holes.append(cyl(x, y, SCREW_PILOT_D / 2, zf0 + 1.0, zs + 1))
            if INSERT_CHAMFER > 0:
                r = SCREW_PILOT_D / 2
                holes.append(Part.makeCone(r, r + INSERT_CHAMFER, INSERT_CHAMFER + 0.01, V(x, y, zs - INSERT_CHAMFER)))
    # inserts for the board screws, from the top of the post
    for x, y in BOARD_SCREWS:
        holes.append(cyl(x, y, SCREW_PILOT_D / 2, zf0 + 1.0, zb + 1))
        if INSERT_CHAMFER > 0:
            r = SCREW_PILOT_D / 2
            holes.append(Part.makeCone(r, r + INSERT_CHAMFER, INSERT_CHAMFER + 0.01, V(x, y, zb - INSERT_CHAMFER)))
        for y in MOUNT_Y:
            holes.append(cyl(x, y, MOUNT_HOLE_D / 2, zf0 - 1, zf + 1))
    return base.cut(Part.makeCompound(holes))


# ---------------------------------------------------------------- lid

def make_lid():
    shell = box(xo0, xo1, yo0, yo1, zs, zr1).cut(box(xi0, xi1, yi0, yi1, zs - 1, zr))
    parts = [shell]
    for x in screw_x:
        for y in SCREW_Y:
            parts.append(cyl(x, y, LID_BOSS_D / 2, zs, zr + 0.01))
    parts += [cyl(x, y, CLAMP_R, CLAMP_GAP, zr + 0.01) for x, y in CLAMPS]
    lid = fuse(parts)

    cuts = []
    # connector openings, open at the bottom edge so the lid slides down over the connectors
    for name, side, x0, x1, z0, z1, label, enabled in CONNECTORS:
        if not enabled:
            continue
        z1 = max(z1, PLUG_OPENING_TOP.get(name, z1))
        if side == "front":
            cuts.append(box(x0 - CONN_CLEAR, x1 + CONN_CLEAR, yo0 - 1, yi0 + 0.5, zs - 1, z1 + CONN_CLEAR))
        else:
            cuts.append(box(x0 - CONN_CLEAR, x1 + CONN_CLEAR, yi1 - 0.5, yo1 + 1, zs - 1, z1 + CONN_CLEAR))
    # rebates in the left and right walls for the alignment lips of the base
    ly0, ly1 = lip_y()
    cuts.append(box(xi0 - LIP_T - LIP_GAP, xi0 + 0.01, ly0 - LIP_GAP, ly1 + LIP_GAP, zs - 1, zs + LIP_H + LIP_GAP))
    cuts.append(box(xi1 - 0.01, xi1 + LIP_T + LIP_GAP, ly0 - LIP_GAP, ly1 + LIP_GAP, zs - 1, zs + LIP_H + LIP_GAP))
    # screw holes: counterbore from the top down to 3 mm above the joint, clearance hole below
    for x in screw_x:
        for y in SCREW_Y:
            cuts.append(cyl(x, y, SCREW_HEAD_D / 2, zs + 3.0, zr1 + 1))
            cuts.append(cyl(x, y, SCREW_CLEAR_D / 2, zs - 1, zr1 + 1))
    # roof vents, keep away from clamp pins
    x = ROOF_VENTS["x0"]
    while x <= ROOF_VENTS["x1"]:
        clear = all(not (abs(cx - x) < CLAMP_R + VENT_W and ROOF_VENTS["y0"] - CLAMP_R - 1 < cy < ROOF_VENTS["y1"] + CLAMP_R + 1)
                    for cx, cy in CLAMPS)
        if clear:
            cuts.append(box(x - VENT_W / 2, x + VENT_W / 2, ROOF_VENTS["y0"], ROOF_VENTS["y1"], zr - 1, zr1 + 1))
        x += ROOF_VENTS["pitch"]
    # side vents in the left and right walls
    for z in SIDE_VENTS["z"]:
        for xa, xb in ((xo0 - 1, xi0 + 1), (xi1 - 1, xo1 + 1)):
            cuts.append(box(xa, xb, SIDE_VENTS["y0"], SIDE_VENTS["y1"], z, z + VENT_W))
    # labels
    for name, side, x0, x1, z0, z1, label, enabled in CONNECTORS:
        if not enabled or not label:
            continue
        xc = (x0 + x1) / 2
        if side == "front":
            cuts.append(wall_label(label, xc, z1 + CONN_CLEAR + 2.5 + LABEL_H / 2, "front"))
        else:
            # the openings on the back are higher, labels go on the top next to the back edge
            cuts.append(roof_label(label, xc, yi1 - 6.0, LABEL_H * 0.8, rot=0))
    cuts.append(roof_label(TITLE, (xi0 + xi1) / 2, yi0 + 12.0, 9.0))
    return lid.cut(Part.makeCompound(cuts))


# ---------------------------------------------------------------- output

def export(shape, name):
    mesh = MeshPart.meshFromShape(Shape=shape, LinearDeflection=0.02, AngularDeflection=0.2, Relative=False)
    if mesh.hasSelfIntersections() or not mesh.isSolid():
        print("WARNING: mesh of %s has defects" % name)
    mesh.write(os.path.join(OUT_DIR, name + ".stl"))


base = make_base()
lid = make_lid()
# fit check: the lower part of the lid walls with all openings, quick to print, put it over the
# soldered board to check the openings before printing the whole lid
ring = box(xo0, xo1, yo0, yo1, zs - 1, FITCHECK_H).cut(box(xi0 + 0.01, xi1 - 0.01, yi0 + 0.01, yi1 - 0.01, zs - 2, FITCHECK_H + 1))
fitcheck = lid.common(ring).removeSplitter()
for name, shape in (("vdmot_case_base", base), ("vdmot_case_lid", lid), ("vdmot_case_fitcheck", fitcheck)):
    if not shape.isValid():
        print("WARNING: %s is not a valid solid" % name)
    export(shape, name)
Part.makeCompound([base, lid]).exportStep(os.path.join(OUT_DIR, "vdmot_case.step"))
bb = base.fuse(lid).BoundBox
print("case %.1f x %.1f x %.1f mm, base %.1f cm3, lid %.1f cm3" %
      (bb.XLength, bb.YLength, bb.ZLength, base.Volume / 1000, lid.Volume / 1000))
