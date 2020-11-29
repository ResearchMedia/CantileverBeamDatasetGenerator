#Author-PhilippeWyder
#Description-Random beam generated with different cross sections for data generation

# --------------------------------------------------------------------------- #
# FreeCAD related modules
#
import sys
sys.path.append('/home/ron/miniconda3/envs/datagencad/lib')
import FreeCAD
import Part
import Sketcher


# Script Related Imports
import numpy as np
import Part
import Sketcher
root_path = "/media/ron/UbuntuData/Temp/TMPTEST"
min_verts = 3
max_verts = 30
min_radius = 24
max_radius = 63
extrude_length = 600.0 #[cm]
IMG_MAX_X = 128
IMG_MAX_Y = 128
MIN_PX_VOLUME_ACCURACY = .05 # 10% minimum px accuracy
POLY_IRREGULARITY = 0.4
POLY_SPIKEYNESS = 0.1
print("SET FIRST VARIABLE VALUES")

def gen_datapoint(dataPtNr):
	
	#define current datapt path
	cur_folder = str(dataPtNr)
	cur_path = root_path + "/" + cur_folder	


	# Open New Doc        
	App.newDocument("cantilever")
	App.setActiveDocument("cantilever")
	App.ActiveDocument=App.getDocument("cantilever")
	
	# create new object
	App.activeDocument().addObject('PartDesign::Body','Body')
	
	# Start Sketch
	App.activeDocument().Body.newObject('Sketcher::SketchObject','Sketch')
	App.activeDocument().Sketch.Support = (App.activeDocument().XY_Plane, [''])
	App.activeDocument().Sketch.MapMode = 'FlatFace'
	App.ActiveDocument.recompute()
	#print("Started Sketch successfully")
	
	# Draw Polygon
	# randomly select Nr. of Vertices
	avg_rad = random.randint(min_radius,max_radius)
	nr_verts = random.randint(min_verts,max_verts)

	verts = generatePolygon(0,0, avg_rad, POLY_IRREGULARITY, POLY_SPIKEYNESS, nr_verts)
	while (len(verts) > len(set(verts)) or not isNonIntersecting(verts)):
		print("Non_Intersecting?", isNonIntersecting(verts))
		avg_rad = random.randint(min_radius,max_radius)
		nr_verts = random.randint(min_verts,max_verts)
		verts = generatePolygon(0,0, avg_rad, POLY_IRREGULARITY, POLY_SPIKEYNESS, nr_verts)	

	#Save Vertices Array
	np_verts = np.array(verts)
	np.save(pathlib.Path(cur_path+"/numbers/verts.npy"),np_verts)

	# CSV Export Variables (declare outside Try/Catch scope (necessary?))
	np_volume = None
	np_MOI = None

	try:
		#print("Intersects:", isNonIntersecting(verts))
		# start a line
		start_pt = verts[0]
		cur_pt = verts[0]
		next_pt = verts[1]
		
		# draw initial line segment
		App.ActiveDocument.Sketch.addGeometry(
		    Part.LineSegment(
		        App.Vector(cur_pt[0],cur_pt[1],0),
		        App.Vector(next_pt[0],next_pt[1],0)),False)
		cur_pt = next_pt
		line_nr = 0 # drew 0th line
		#print("Drew First line successfully")
		for i in range(2, len(verts)):
		    next_pt = verts[i]
		    App.ActiveDocument.Sketch.addGeometry(
		        Part.LineSegment(
		            App.Vector(cur_pt[0],cur_pt[1],0),
		            App.Vector(next_pt[0],next_pt[1],0)),False)
		    line_nr += 1 # increment line counter
		    # define constraint
		    # Sketch.addConstraint(
		        #Sketcher.Constraint('Coincident',LineFixed,PointOfLineFixed,LineMoving,PointOfLineMoving))
		    App.ActiveDocument.Sketch.addConstraint(
		        Sketcher.Constraint("Coincident",line_nr-1,2,line_nr,1)) 
		    cur_pt = next_pt
		    #print("Drew %d line successfully" % line_nr)
		# Close the loop
		#print(cur_pt)
		#print(start_pt)
		App.ActiveDocument.Sketch.addGeometry(
		    Part.LineSegment(
		        App.Vector(cur_pt[0],cur_pt[1],0),
		        App.Vector(start_pt[0],start_pt[1],0)),False)
		line_nr += 1
		#App.ActiveDocument.Sketch.addConstraint(
		#    Sketcher.Constraint('Coincident',line_nr-1,2,0,1))
		#print("Closed Shape")
		# Extrude profile
		# Get the profile defined by the polygon
		App.getDocument("cantilever").recompute()

		#
		# Get cross-section Area Moment Of Inertia
		#
		Draft.draftify(App.getDocument("cantilever").LowerPlane,delete=False)
		W_MoI = App.getDocument("cantilever").Wire.Shape.MatrixOfInertia
		np_secondMoment = np.array([W_MoI.A11, W_MoI.A22, W_MoI.A33])
		np.save(Path(cur_path / "label" / "secondMoment.npy"),np_secondMoment)

		# Extrusion (Pad)
		App.activeDocument().Body.newObject("PartDesign::Pad","Pad")
		App.activeDocument().Pad.Profile = App.activeDocument().Sketch
		App.activeDocument().Pad.Length = extrude_length
		App.ActiveDocument.recompute()
		App.ActiveDocument.Pad.Length = extrude_length
		App.ActiveDocument.Pad.Length2 = 100.00
		App.ActiveDocument.Pad.Type = 0
		App.ActiveDocument.Pad.UpToFace = None
		App.ActiveDocument.Pad.Reversed = 0
		App.ActiveDocument.Pad.Midplane = 0
		App.ActiveDocument.Pad.Offset = 0.000000
		App.ActiveDocument.recompute()
		#print("Extruded Polygon")
		# Get the extrusion body
			
		#Save Volume
		np_volume = np.array(App.ActiveDocument.Pad.Shape.Volume)
		np.save(pathlib.Path(cur_path+"/label/volume.npy"),np_volume)
	
		#Save Moment Of Inertia
		MOI = App.ActiveDocument.Pad.Shape.MatrixOfInertia
		np_MOI = np.array([	[MOI.A11, MOI.A12, MOI.A13, MOI.A14],
							[MOI.A21, MOI.A22, MOI.A23, MOI.A24],
							[MOI.A31, MOI.A32, MOI.A33, MOI.A34],
							[MOI.A41, MOI.A42, MOI.A43, MOI.A44]
						])
		np.save(pathlib.Path(cur_path+"/label/MatrixOfInertia.npy"),np_MOI)
		#print(np_MOI)
	except RuntimeError as e:
		if (e.args[0]=="shape is invalid"):
			print("invalid shape - retry")
			App.closeDocument("cantilever")
			return -1
		else:
			raise

	# Center Vertices for Image export
	cverts = []
	for pt in verts:
		cverts.append((pt[0]+round(IMG_MAX_X/2), pt[1]+round(IMG_MAX_Y/2)))

	# Generate Image of crossection
	# Save Image to file
	# black and white
	img_path = cur_path + "/img" + "/img_bw.jpg"
	cur_img, nrpx_fill = getimg(cverts, 'bw', 1)
	# Verify Pixel Error Metric
	if (MIN_PX_VOLUME_ACCURACY < abs(np_volume-nrpx_fill*extrude_length)/np_volume):
		print("Exceeded maximum pixel error: Redo")
		App.closeDocument("cantilever")
		return -1
	cur_img.save(img_path)

	img_path = cur_path + "/img" + "/img_cbw.jpg"
	cur_img, nrpx_outline = getimg(cverts, 'bw', 0)
	cur_img.save(img_path)

	# save grayscale (filled in)
	img_path = cur_path + "/img" + "/img_grayscale.jpg"
	cur_img, nrpx_fill = getimg(cverts, 'grayscale', 1)
	cur_img.save(img_path)
	'''
	img_path = cur_path + "/img" + "/img_cgrayscale.jpg"
	cur_img, nrpx_outline = getimg(cverts, 'grayscale', 0)
	cur_img.save(img_path)
	'''
	# Save BREP
	__objs__=[]
	__objs__.append(FreeCAD.getDocument("cantilever").getObject("Body"))
	Part.export(__objs__,(u""+cur_path+"/body.brep"))
	del __objs__

	# Save STEP
	__objs__=[]
	__objs__.append(FreeCAD.getDocument("cantilever").getObject("Body"))
	#import ImportGui
	#ImportGui.export(__objs__,(u""+cur_path+"/body.step"))
	import Import
	Import.export(__objs__,(u""+cur_path+"/body.step"))
	del __objs__

	# Save STL
	__objs__=[]
	__objs__.append(FreeCAD.getDocument("cantilever").getObject("Body"))
	import Mesh
	Mesh.export(__objs__,(u""+cur_path+"/body.stl"))

	# clear document for next itteration (delete bodies and sketches)
	#Gui.activeDocument().resetEdit()
	App.closeDocument("cantilever")
	App.setActiveDocument("")
	App.ActiveDocument = None
	#Gui.ActiveDocument = None
	
	# Return data
	return {"nr_verts":nr_verts, "avgRad":avg_rad, "resolution": IMG_MAX_X*IMG_MAX_Y,
			"nrpx_fill":nrpx_fill, "nrpx_outline": nrpx_outline, "volume": np_volume,
			"MOI00": np_MOI[0,0], "MOI01": np_MOI[0,1], "MOI02": np_MOI[0,2],
							     "MOI11": np_MOI[1,1], "MOI12": np_MOI[1,2],
												  "MOI22": np_MOI[2,2]
			}

###
# Polygon Generator
# (Source: https://stackoverflow.com/questions/8997099/algorithm-to-generate-random-2d-polygon)
###
import math, random

def generatePolygon( ctrX, ctrY, aveRadius, irregularity, spikeyness, numVerts ) :
    '''
    Start with the centre of the polygon at ctrX, ctrY, 
    then creates the polygon by sampling points on a circle around the centre. 
    Randon noise is added by varying the angular spacing between sequential points,
    and by varying the radial distance of each point from the centre.

    Params:
    ctrX, ctrY - coordinates of the "centre" of the polygon
    aveRadius - in px, the average radius of this polygon, this roughly controls how large the polygon is, really only useful for order of magnitude.
    irregularity - [0,1] indicating how much variance there is in the angular spacing of vertices. [0,1] will map to [0, 2pi/numberOfVerts]
    spikeyness - [0,1] indicating how much variance there is in each vertex from the circle of radius aveRadius. [0,1] will map to [0, aveRadius]
    numVerts - self-explanatory

    Returns a list of vertices, in CCW order.
    '''

    irregularity = clip( irregularity, 0,1 ) * 2*math.pi / numVerts
    spikeyness = clip( spikeyness, 0,1 ) * aveRadius

    # generate n angle steps
    angleSteps = []
    lower = (2*math.pi / numVerts) - irregularity
    upper = (2*math.pi / numVerts) + irregularity
    sum = 0
    for i in range(numVerts) :
        tmp = random.uniform(lower, upper)
        angleSteps.append( tmp )
        sum = sum + tmp

    # normalize the steps so that point 0 and point n+1 are the same
    k = sum / (2*math.pi)
    for i in range(numVerts) :
        angleSteps[i] = angleSteps[i] / k

    # now generate the points
    points = []
    angle = random.uniform(0, 2*math.pi)
    for i in range(numVerts) :
        r_i = clip( random.gauss(aveRadius, spikeyness), 0, aveRadius )
        if (r_i > 64):
        	print("WTF is going on", r_i)
        x = ctrX + r_i*math.cos(angle)
        y = ctrY + r_i*math.sin(angle)
        points.append( (int(x),int(y)) )

        angle = angle + angleSteps[i]

    return points

def clip(x, min, max) :
    if( min > max ) :  return x    
    elif( x < min ) :  return min
    elif( x > max ) :  return max
    else :             return x

#import Image
from PIL import Image, ImageDraw
def getimg(verts, color, fill):
	if (color == 'grayscale'):
		c1 = (100,100,100)
		c2=(156,156,156)
	else:
		c1 = (0,0,0)
		c2=(255,255,255)
	im = Image.new('RGB', (IMG_MAX_X, IMG_MAX_Y), c2)
	draw = ImageDraw.Draw(im)
	
	# either use .polygon(), if you want to fill the area with a solid colour
	if (fill):
		draw.polygon( verts, outline=c1,fill=c1 )
	else:
		draw.polygon( verts, outline=c1,fill=c2 )

	# Count Nr of pixels made up by cross-section
	nrpx = im.histogram()[c1[0]]

	# or .line() if you want to control the line thickness, or use both methods together!
	#draw.line( tupVerts+[tupVerts[0]], width=2, fill=black )
	return(im, nrpx)
'''
Functions to check for self intersection of polygons
'''
def ccw(a, b, c):
	return( (b[0]-a[0])*(c[1]-a[1])-(c[0]-a[0])*(b[1]-a[1]) )

def intersects(a,b,c,d):
	if (ccw(a, b, c)*ccw(a,b,d) >= 0):
		return False
	elif (ccw(c, d, a)*ccw(c,d,b) >= 0):
		return False
	else:
		return True

def isNonIntersecting(verts):
	for id1 in range(1, len(verts)+1):
		for id2 in range(1, len(verts)+1):
			if intersects(verts[id1-1],verts[id1%len(verts)], verts[id2-1], verts[id2%len(verts)]):
				return False
	return True
		
import pathlib
import datetime, csv

data_start_idx = 0
data_end_idx = 500
start_time = datetime.datetime.now()
# CSV File
csv_file_path = root_path + "/" + "dataset" + str(datetime.datetime.now().strftime("%Y%m%d%H%M")) + ".csv"
csv_file_headers = ["ID", "nr_verts", "avgRad", "resolution", "nrpx_fill", "nrpx_outline", "volume",
					"MOI00", "MOI01", "MOI02", "MOI11", "MOI12", "MOI22"]
with open(csv_file_path, 'w') as csv_file:
	w = csv.DictWriter(csv_file, csv_file_headers)
	w.writeheader()
	for i in range(data_start_idx, data_end_idx):
		cur_datapt_path = root_path	 + "/" + str(i)
		pathlib.Path(cur_datapt_path + "/img").mkdir(parents=True, exist_ok=True)
		pathlib.Path(cur_datapt_path + "/numbers").mkdir(parents=True, exist_ok=True) 
		pathlib.Path(cur_datapt_path + "/label").mkdir(parents=True, exist_ok=True)
		genStatus = gen_datapoint(i)
		while(genStatus == -1):
			genStatus = gen_datapoint(i)

		# Write to CSV
		genStatus["ID"] = i
		w.writerow(genStatus)

		if (i%100==0):
			print("DataPt generated:",i)
time_delta = str(datetime.datetime.now()-start_time)
print("Finished Data Generation of {} datapoints in {} time".format(
		data_end_idx-data_start_idx,  time_delta))
