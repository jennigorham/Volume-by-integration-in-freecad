#2018 NSW HSC Ext2 Maths Q5 http://educationstandards.nsw.edu.au/wps/portal/nesa/11-12/Understanding-the-curriculum/resources/hsc-exam-papers/hsc-exam-paper-detail/2018/mathematics-extension-2-2018-hsc-exam-pack
#See https://youtu.be/II97RPjbtuU?t=601

#Usage:
#Install freecad: https://www.freecadweb.org/wiki/Download
#Paste the following into the python console (if python console is not visible, go View -> Panels -> Python Console)

import math
from FreeCAD import Base
import Part
import Draft
from PySide import QtCore

#open new document
App.newDocument("Q5")
App.setActiveDocument("Q5")
App.ActiveDocument=App.getDocument("Q5")
Gui.ActiveDocument=Gui.getDocument("Q5")
doc = FreeCAD.ActiveDocument

#show the grid
Gui.activateWorkbench("DraftWorkbench")
FreeCAD.DraftWorkingPlane.alignToPointAndAxis(FreeCAD.Vector(0,0,0), FreeCAD.Vector(0,0,1), 0)
FreeCADGui.Snapper.setGrid()

#pretty turquoise :)
face_colour = (0.0,0.85,0.75)
line_colour = (0.1,0.3,0.3)

scale = 10.0 # 1unit = 10mm
offset = 0.001 # Some things need to be offset imperceptibly from their true position to keep freecad happy

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

########## Exponential ############
n = 10
dx = scale/n

points = []
def my_func(x):
	return math.exp(x*math.log(scale)/scale) #we can't actually do e^(3x) from 0 to 4 to scale, because it gets very high

for i in range(0,n+1):
	x = i*dx
	points.append(FreeCAD.Vector(x, my_func(x), 0.0))

spline = Draft.makeBSpline(points,closed=False,face=False,support=None)

#draw the axis of rotation
axis_y = -1.0
axis_of_rotation = Draft.makeWire([FreeCAD.Vector(-0.1*scale,axis_y,0),FreeCAD.Vector(1.1*scale,axis_y,0)],closed=False,face=False,support=None)


########## disks #################
dx = scale/n
disks = doc.addObject("App::DocumentObjectGroup","Disks")

def draw_cyl(x):
	cyl = doc.addObject("Part::Cylinder","Disk")
	cyl.Radius = my_func(x+dx/2) - axis_y
	cyl.Height = dx
	cyl.Placement=Base.Placement(Base.Vector(x,axis_y,0.00),App.Rotation(App.Vector(0,1,0),90))
	disks.addObject(cyl)

for i in range(0,n):
	x = i*dx
	draw_cyl(x)


disks.ViewObject.Visibility = True #work-around for bug in freecad 0.17
disks.ViewObject.Visibility = False


######## solid of revolution ####
#create a closed path with the exponential, y=-1, x=0, and x=4 (well, whatever scale is)
points=[FreeCAD.Vector(scale,scale,0.0),FreeCAD.Vector(scale,axis_y,0.0),FreeCAD.Vector(0.0,axis_y,0.0),FreeCAD.Vector(0.0,1.0,0.0)]
line = Draft.makeWire(points,closed=False,face=False,support=None)
line.ViewObject.Visibility=False

wire = Draft.upgrade([line,spline],delete=False)[0][0] #combine line and spline
wire.ViewObject.Visibility=False

#Path of the sweep - arc of a circle
circle = Draft.makeCircle(radius=3.0,placement=App.Placement(App.Vector(0,axis_y-offset,0),App.Rotation(App.Vector(1,1,1),120)),face=False,startangle=0,endangle=360.0,support=None) #need to offset the circle slightly from the wire so that the sweep doesn't fail
circle.ViewObject.Visibility=False

sweep = doc.addObject('Part::Sweep','Sweep')
sweep.Sections=[wire, ]
sweep.Spine=(circle,["Edge1"])
sweep.Solid=True
sweep.Frenet=False
sweep.ViewObject.Visibility=False


######### Incorrect y-axis rotation #############

#App.Placement(App.Vector(0,0,0),App.Rotation(App.Vector(1,0,0),90))
circle2 = Draft.makeCircle(radius=3.0,placement=App.Placement(App.Vector(-offset,0,0),App.Rotation(App.Vector(1,0,0),90)),face=False,startangle=0,endangle=360.0,support=None) #need to offset the circle slightly from the wire so that the sweep doesn't fail
circle2.ViewObject.Visibility=False
sweep2 = doc.addObject('Part::Sweep','Sweep')
sweep2.Sections=[wire, ]
sweep2.Spine=(circle2,["Edge1"])
sweep2.Solid=True
sweep2.Frenet=False
doc.recompute()
sweep2.ViewObject.Visibility=False

######### Animated sweep ##################
#step the angle of the arc up gradually to produce sweep animation
timer = QtCore.QTimer() #can't just use time.sleep because it blocks the display updating
angle = 0
angle_step = 5
y_axis_rotation = False

def sweep_step():
	global angle,angle_step,timer,y_axis_rotation
	if y_axis_rotation:
		sweep2.ViewObject.Visibility=True
		circ = circle2
	else:
		sweep.ViewObject.Visibility=True
		circ = circle
	if angle == 180: #for some reason, it disappears if the angle is exactly 180
		circ.LastAngle = 180 + offset
	else:
		circ.LastAngle = angle
	doc.recompute()
	angle += angle_step
	if angle > 360:
		timer.stop()

timer.timeout.connect(sweep_step)

def start_sweep():
	global angle
	angle = 10
	timer.start(10)



######### Incorrect cylindrical shells ##############
dx = scale/n
placement = App.Placement(App.Vector(0,axis_y,0),App.Rotation(App.Vector(1,0,0),270))

shells = doc.addObject("App::DocumentObjectGroup","Shells")

def make_shell(x):
	h = my_func(x + dx/2) + 1
	outside_cyl = App.ActiveDocument.addObject("Part::Cylinder","Cylinder")
	outside_cyl.Placement = placement
	outside_cyl.Radius = x + dx
	outside_cyl.Height = h
	
	inside_cyl = App.ActiveDocument.addObject("Part::Cylinder","Cylinder")
	inside_cyl.Placement = App.Placement(App.Vector(0,axis_y,0),App.Rotation(App.Vector(1,0,0),270))
	inside_cyl.Radius = x
	inside_cyl.Height = h
	
	shell = App.activeDocument().addObject("Part::Cut","Cut")
	shell.Base = outside_cyl
	shell.Tool = inside_cyl
	doc.recompute()
	return shell

#make the central cylinder
cyl = App.ActiveDocument.addObject("Part::Cylinder","Cylinder")
cyl.Placement = placement
cyl.Radius = dx
cyl.Height = my_func(dx/2) + 1
shells.addObject(cyl)

for i in range (1,n):
	if i != 7: #7 is the special one which we cut and flatten
		x = i*dx
		shells.addObject(make_shell(x))

########## Flattened shell ###########
x = 7*dx

#make the cross-section of the shell, which will be swept around in a circular arc
points=[
	FreeCAD.Vector(0,axis_y,-x-dx),
	FreeCAD.Vector(0.0,axis_y,-x),
	FreeCAD.Vector(0.0,my_func(x + dx/2),-x),
	FreeCAD.Vector(0.0,my_func(x + dx/2),-x-dx),
	FreeCAD.Vector(0,axis_y,-x-dx)]
shell_wire = Draft.makeWire(points,closed=True,face=False,support=None)
shell_wire.ViewObject.Visibility = False

arc = Draft.makeCircle(
	radius=3.0,
	placement=App.Placement(App.Vector(0,0,0),App.Rotation(App.Vector(1,1,-1),120)),
	face=False,
	startangle=-180,
	endangle=180-offset,
	support=None)
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
	arc.Placement = App.Placement(App.Vector(0,0,(180.0/theta-1)*x),App.Rotation(App.Vector(1,1,-1),120))
	doc.recompute()

flat_timer = QtCore.QTimer()

angle = 180

def flatten_step():
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
def next(): #step through the views, first just the graph, then the sweep around y=-1, then disks, then just the graph again, then the incorrect y-axis sweep, then cylindrical shells, then flatten a shell, then back to the graph
	global y_axis_rotation
	if sweep.ViewObject.Visibility == True:
		timer.stop()
		sweep.ViewObject.Visibility=False
		disks.ViewObject.Visibility=True
	elif disks.ViewObject.Visibility==True:
		disks.ViewObject.Visibility=False
		y_axis_rotation = True
	elif sweep2.ViewObject.Visibility==True:
		timer.stop()
		sweep2.ViewObject.Visibility=False
		shells.ViewObject.Visibility=True
	elif shells.ViewObject.Visibility==True:
		if arc.LastAngle < 90:
			flat_timer.stop()
			shells.ViewObject.Visibility=False
			shell_flat.Placement = App.Placement(App.Vector(0,0,0),App.Rotation(App.Vector(0,0,1),0)) #put that thing back where it came from or so help me
			flatten(180)
			y_axis_rotation = False
		else:
			start_flatten()
	else:
		start_sweep()

