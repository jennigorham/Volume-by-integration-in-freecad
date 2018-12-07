#2018 NSW HSC Ext2 Maths Q13a http://educationstandards.nsw.edu.au/wps/portal/nesa/11-12/Understanding-the-curriculum/resources/hsc-exam-papers/hsc-exam-paper-detail/2018/mathematics-extension-2-2018-hsc-exam-pack
#See https://youtu.be/rCHJefPD1js

#Usage:
#Install freecad: https://www.freecadweb.org/wiki/Download
#Paste the following into the python console (if python console is not visible, go View -> Panels -> Python Console)

import math
from FreeCAD import Base
import Part
import Draft
from PyQt4.QtCore import QTimer

#open new document
App.newDocument("Q13a")
App.setActiveDocument("Q13a")
App.ActiveDocument=App.getDocument("Q13a")
Gui.ActiveDocument=Gui.getDocument("Q13a")
doc = FreeCAD.ActiveDocument

#show the grid
Gui.activateWorkbench("DraftWorkbench")
FreeCAD.DraftWorkingPlane.alignToPointAndAxis(FreeCAD.Vector(0,0,0), FreeCAD.Vector(0,0,1), 0)
FreeCADGui.Snapper.setGrid()

#pretty turquoise :)
face_colour = (0.0,0.85,0.75)
line_colour = (0.1,0.3,0.3)

scale = 10.0 # 1unit = 10mm
offset = 0.01 # Some things need to be offset imperceptibly from their true position to keep freecad happy

######## Axes ##########
axes = doc.addObject("App::DocumentObjectGroup","Axes")

y_end = 1.2*scale
x_start = -0.3*scale
x_end = 2.2*scale
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

########## Curve ############
n = 10
dx = scale/n
points = []
def my_func(x): #y^2 = x(1-x)^2
	return scale * math.sqrt(x/scale*(1-x/scale)**2)

#top half (the offset is so that it doesn't try to join the first and last points with a smooth curve)
for i in range(n,0,-1):
	x = i*dx
	points.append(FreeCAD.Vector(x, my_func(x) + offset, 0.0))

#bottom half
for i in range(0,n+1):
	x = i*dx
	points.append(FreeCAD.Vector(x, -my_func(x) - offset, 0.0))

#join the points with a spline
spline = Draft.makeBSpline(points,closed=False,face=False,support=None)

#draw in the axis of rotation (x=1) as well
axis_of_rotation = Draft.makeWire([FreeCAD.Vector(scale,-scale/2,0),FreeCAD.Vector(scale,scale/2,0)],closed=False,face=False,support=None)

######## solid of revolution ####
#join the first and last points of the spline with a straight line to make a closed path
points=[FreeCAD.Vector(scale,-offset,0.0),FreeCAD.Vector(scale,offset,0.0)]
line = Draft.makeWire(points,closed=False,face=False,support=None)
line.ViewObject.Visibility=False
wire = Draft.upgrade([line,spline],delete=False)[0][0]
wire.ViewObject.Visibility=False

#Path of the sweep - arc of a circle
circle = Draft.makeCircle(radius=3.0,placement=App.Placement(App.Vector(scale - offset,0,0),App.Rotation(App.Vector(1,0,0),90)),face=False,startangle=0,endangle=360.0,support=None)
Draft.rotate([circle],180.0,FreeCAD.Vector(scale,0.0,0.0),axis=FreeCAD.Vector(0.0,0.0,1.0),copy=False) #rotate it around the z-axis 180 degrees
circle.ViewObject.Visibility=False

sweep = doc.addObject('Part::Sweep','Sweep')
sweep.Sections=[wire, ]
sweep.Spine=(circle,["Edge1"])
sweep.Solid=True
sweep.Frenet=False
sweep.ViewObject.Visibility=False

######### Animated sweep ##################
#step the angle of the arc up gradually to produce sweep animation
timer = QTimer() #can't just use time.sleep because it blocks the display updating
angle = 0
angle_step = 5

def sweep_step():
	global angle,angle_step,timer
	sweep.ViewObject.Visibility = True
	if angle == 180: #for some reason, it disappears if the angle is exactly 180
		circle.LastAngle = 180.1
	else:
		circle.LastAngle = angle
	doc.recompute()
	angle += angle_step
	if angle > 360:
		timer.stop()

timer.timeout.connect(sweep_step)

def start_sweep():
	global angle
	angle = 10
	doc.recompute()
	timer.start(10)


######### Cylindrical shells ##############
shells = doc.addObject("App::DocumentObjectGroup","Shells")

def make_shell(x):
	h = my_func(x + dx/2)
	outside_cyl = App.ActiveDocument.addObject("Part::Cylinder","Cylinder")
	outside_cyl.Placement = App.Placement(App.Vector(scale,-h,0),App.Rotation(App.Vector(1,0,0),270))
	outside_cyl.Radius = scale - x
	outside_cyl.Height = 2*h

	inside_cyl = App.ActiveDocument.addObject("Part::Cylinder","Cylinder")
	inside_cyl.Placement = App.Placement(App.Vector(scale,-h,0),App.Rotation(App.Vector(1,0,0),270))
	inside_cyl.Radius = max(scale - x - dx,offset) #radius should never be 0
	inside_cyl.Height = 2*h

	#cut the outside cylinder with the inside cylinder
	shell = App.activeDocument().addObject("Part::Cut","Cut")
	shell.Base = outside_cyl
	shell.Tool = inside_cyl
	doc.recompute()
	return shell

for i in range (0,n):
	if i != 2: #2 is the special one which we cut and flatten
		x = i*dx
		shells.addObject(make_shell(x))

######### Flattened shell ################
x = 2*dx
h = my_func(x + dx/2)

#create the rectangular cross-section, which we'll sweep in an arc to create the shell
points=[FreeCAD.Vector(scale,-h,-scale + x),FreeCAD.Vector(scale,-h,-scale+x+dx),FreeCAD.Vector(scale,h,-scale + x+dx),FreeCAD.Vector(scale,h,-scale + x),FreeCAD.Vector(scale,-h,-scale + x)]
shell_wire = Draft.makeWire(points,closed=True,face=False,support=None)
shell_wire.ViewObject.Visibility = False

rotation = App.Rotation(App.Vector(1,1,-1),120) #default rotation is around the z-axis. this makes the arc go around the y-axis
arc = Draft.makeCircle(radius=3.0,placement=App.Placement(App.Vector(scale,0,0),rotation),face=False,startangle=-180,endangle=180-offset,support=None)
arc.ViewObject.Visibility = False

shell_flat = doc.addObject('Part::Sweep','Shell_flat')
shell_flat.Sections=[shell_wire, ]
shell_flat.Spine=(arc,["Edge1"])
shell_flat.Solid=True
shell_flat.Frenet=False

shells.addObject(shell_flat)
shells.ViewObject.Visibility = True
shells.ViewObject.Visibility = False

def flatten(theta): #theta = 0 is fully flat, theta = 180 is cylindrical shell
	if theta >= 180:
		theta = 180-offset
	elif theta <= 0:
		theta = 0.1
	arc.FirstAngle = -theta
	arc.LastAngle = theta
	#move the centre of the arc to keep the length of the shell constant
	arc.Placement = App.Placement(App.Vector(scale,0,(180.0/theta-1)*(scale - x)),rotation)
	doc.recompute()

flat_timer = QTimer()

def flatten_step(): #decrease theta
	global angle,angle_step
	flatten(angle)
	angle += -5
	if angle < 0:
		flat_timer.stop()

flat_timer.timeout.connect(flatten_step)

def start_flatten():
	global angle
	angle = 180
	flat_timer.start(10)


############# Next view ###############
#see next.FCMacro for how to bind this to a keyboard shortcut
def next(): #step through the views, first just the graph, then the sweep, then the shells, then flatten a shell
	if sweep.ViewObject.Visibility == True:
		sweep.ViewObject.Visibility = False
		shells.ViewObject.Visibility = True
	elif shells.ViewObject.Visibility == True:
		if angle < 90:
			shells.ViewObject.Visibility = False
			shell_flat.Placement = App.Placement(App.Vector(0,0,0),App.Rotation(App.Vector(0,0,1),0)) #put that thing back where it came from or so help me
			flatten(180)
		else:
			start_flatten()
	else:
		start_sweep()

