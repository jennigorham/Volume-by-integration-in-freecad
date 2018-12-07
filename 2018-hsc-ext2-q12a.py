#2018 NSW HSC Ext2 Maths Q12a http://educationstandards.nsw.edu.au/wps/portal/nesa/11-12/Understanding-the-curriculum/resources/hsc-exam-papers/hsc-exam-paper-detail/2018/mathematics-extension-2-2018-hsc-exam-pack
#See https://youtu.be/wrLoTWSi_X4

#Usage:
#Install freecad: https://www.freecadweb.org/wiki/Download
#Paste the following into the python console (if python console is not visible, go View -> Panels -> Python Console)

import math
from FreeCAD import Base
import Part
import Draft

#open new document
App.newDocument("Q12a")
App.setActiveDocument("Q12a")
App.ActiveDocument=App.getDocument("Q12a")
Gui.ActiveDocument=Gui.getDocument("Q12a")
doc = FreeCAD.ActiveDocument

#show the grid
Gui.activateWorkbench("DraftWorkbench")
FreeCAD.DraftWorkingPlane.alignToPointAndAxis(FreeCAD.Vector(0,0,0), FreeCAD.Vector(0,0,1), 0)
FreeCADGui.Snapper.setGrid()

#pretty turquoise :)
face_colour = (0.0,0.85,0.75)
line_colour = (0.1,0.3,0.3)

scale = 5.0 # 1unit = 10mm

######## Axes ##########
axes = doc.addObject("App::DocumentObjectGroup","Axes")

y_end = 1.2*scale
x_start = -0.3*scale
x_end = 1.2*scale
axis_radius = 0.05

#x-axis
cyl = doc.addObject("Part::Cylinder","x-axis")
cyl.Radius = axis_radius
cyl.Height = x_end - x_start
cyl.Placement=Base.Placement(Base.Vector(x_start,0.00,0.00),App.Rotation(App.Vector(0,1,0),90))
cyl.ViewObject.DiffuseColor=[(0.0,0.0,0.0)]
axes.addObject(cyl)

txt = Draft.makeText('x', point=FreeCAD.Vector(x_end + 0.5, -0.5, 0))
txt.ViewObject.FontSize = 2
axes.addObject(txt)

#y-axis
cyl = doc.addObject("Part::Cylinder","y-axis")
cyl.Radius = axis_radius
cyl.Height = 2*y_end
cyl.Placement=Base.Placement(Base.Vector(0.00,-y_end,0.00),App.Rotation(App.Vector(1,0,0),-90))
cyl.ViewObject.DiffuseColor=[(0.0,0.0,0.0)]
axes.addObject(cyl)

txt = Draft.makeText('y', point=FreeCAD.Vector(-0.5, y_end + 1, 0))
txt.ViewObject.FontSize = 2
axes.addObject(txt)


######## Parabola #########
n = 10
points = []
for i in range (-n,n+1):
	points.append(FreeCAD.Vector((1-(i*1.0/n)**2)*scale,i*scale/n,0.0))

parabola = Draft.makeBSpline(points,closed=False,face=False,support=None)


######## Single Triangle ##########

def triangular_prism(centre_y, thickness):
	p = doc.addObject("Part::Prism","Prism")
	p.Polygon=3 #number of sides of the base
	sidelength = (1 - centre_y**2) * scale
	p.Circumradius=sidelength/math.sqrt(3)
	p.Height=thickness
	p.Placement=Base.Placement(
		Base.Vector(0.5*sidelength, centre_y*scale - 0.5*thickness, 0.5*sidelength/math.sqrt(3)),
		App.Rotation(App.Vector(-1,-1,-1),120))
	p.ViewObject.DiffuseColor=[face_colour]
	p.ViewObject.LineColor=line_colour
	doc.recompute()
	return p

single = triangular_prism(0.5,0.01)


######## Triangular prism slices ##########

def draw_triangles(n): #draws 2n triangular prisms
	dy = scale/n
	prisms = []
	prisms = doc.addObject("App::DocumentObjectGroup","Triangular Slices " + str(2*n))
	for i in range(-n,n):
		centre_y = (i+0.5)/n #y value at the centre of the triangular prism
		prisms.addObject(triangular_prism(centre_y,dy))
	return prisms

slices = draw_triangles(10)
slices.ViewObject.Visibility=True #there's a bug where setting a group's visibility to false doesn't work unless you set it true first
slices.ViewObject.Visibility=False


########### Smooth Solid #########
#make the solid out of its three edges: the parabola, the upper spline, and a straight line
points = []
for i in range (-n,n+1):
	sidelength = (1-(i*1.0/n)**2)*scale
	points.append(FreeCAD.Vector(sidelength/2,i*scale/n,sidelength*math.sqrt(3)/2))

upper_spline = Draft.makeBSpline(points,closed=False,face=False,support=None)

points=[FreeCAD.Vector(0.0,-scale,0.0),FreeCAD.Vector(0.0,scale,0.0)]
line = Draft.makeWire(points,closed=False,face=False,support=None)

loft = doc.addObject('Part::Loft','Smooth')
loft.Sections=[upper_spline, parabola, line, ]
loft.Solid=True
loft.Ruled=True
loft.Closed=True
loft.ViewObject.DiffuseColor=[face_colour]
loft.ViewObject.LineColor=line_colour

upper_spline.ViewObject.Visibility=False
loft.ViewObject.Visibility=False

doc.recompute()


########## Next view #############
#see next.FCMacro for how to bind this to a keyboard shortcut
def next(): #step through the views, first the graph with one triangle, then the smooth solid, then the triangular prisms
	if single.ViewObject.Visibility == True:
		single.ViewObject.Visibility=False
		loft.ViewObject.Visibility=True
	elif loft.ViewObject.Visibility==True:
		loft.ViewObject.Visibility=False
		slices.ViewObject.Visibility=True
	elif slices.ViewObject.Visibility==True:
		slices.ViewObject.Visibility=False
		single.ViewObject.Visibility=True

