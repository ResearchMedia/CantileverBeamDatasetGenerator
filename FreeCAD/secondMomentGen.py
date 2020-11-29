###############################################################################
# @Author: PhilippeWyder
# @Description: Generates secondMoment.npy for each datapoint based on the 
#  cross-section geometry resulting from verts.npy
# --------------------------------------------------------------------------- #
###############################################################################

# FreeCAD related modules
import sys
sys.path.append('/home/<username>/miniconda3/envs/datagencad/lib')
import FreeCAD
import Part
import Sketcher
import Part
import Sketcher
import Draft
import Import, Mesh

# Script Related Imports
import csv
import time
import numpy as np
from pathlib import Path

# specify dataset folder path
root_path = Path("/home/<username>/GeneratedData") # Please set root path

def computeSecondMoment(i):
	cur_path = root_path / str(i)
	np_verts = np.load(root_path / str(i) / 'numbers' / 'verts.npy')
	verts = [ (v[0], v[1]) for v in np_verts ] # bring verts in tuple format
	print(cur_path)
	print(verts)
	# Open New Doc
	App.newDocument("cantilever")
	App.setActiveDocument("cantilever")
	App.ActiveDocument=App.getDocument("cantilever")

	# create new object
	App.ActiveDocument.addObject('PartDesign::Body','Base_Body')

	# Start Sketch
	App.ActiveDocument.Base_Body.newObject('Sketcher::SketchObject','LowerPlane')
	App.ActiveDocument.LowerPlane.Support = (App.activeDocument().XY_Plane, [''])
	App.ActiveDocument.LowerPlane.MapMode = 'FlatFace'
	App.ActiveDocument.recompute()
	lower_plane_sketch = App.ActiveDocument.LowerPlane
	
	# start a line
	start_pt = verts[0]
	cur_pt = verts[0]
	next_pt = verts[1]
	
	# draw initial line segment
	lower_plane_sketch.addGeometry(
	    Part.LineSegment(
	        App.Vector(cur_pt[0],cur_pt[1],0),
	        App.Vector(next_pt[0],next_pt[1],0)),False)
	cur_pt = next_pt
	line_nr = 0 # drew 0th line
	for i in range(2, len(verts)):
	    next_pt = verts[i]
	    lower_plane_sketch.addGeometry(
	        Part.LineSegment(
	            App.Vector(cur_pt[0],cur_pt[1],0),
	            App.Vector(next_pt[0],next_pt[1],0)),False)
	    line_nr += 1 # increment line counter
	    # define constraint
	    # Sketch.addConstraint(
	    #    Sketcher.Constraint('Coincident',LineFixed,PointOfLineFixed,LineMoving,PointOfLineMoving))
	    lower_plane_sketch.addConstraint(
	        Sketcher.Constraint("Coincident",line_nr-1,2,line_nr,1)) 
	    cur_pt = next_pt
	    #print("Drew %d line successfully" % line_nr)
	# Close the loop
	lower_plane_sketch.addGeometry(
	    Part.LineSegment(
	        App.Vector(cur_pt[0],cur_pt[1],0),
	        App.Vector(start_pt[0],start_pt[1],0)),False)
	line_nr += 1

	# Extrude profile
	# Get the profile defined by the polygon
	App.ActiveDocument.recompute()

	#
	# Get cross-section Area Moment Of Inertia
	#
	print(lower_plane_sketch.Shape.MatrixOfInertia)
	Draft.draftify(lower_plane_sketch,delete=False)
	W_MoI = App.ActiveDocument.Wire.Shape.MatrixOfInertia

	# Second Diagonal Terms
	np_secondMoment = np.array([W_MoI.A11, W_MoI.A22, W_MoI.A12])
	np.save(Path(cur_path / "label" / "secondMoment.npy"),np_secondMoment)

	# clear document for next itteration (delete bodies and sketches)
	App.closeDocument("cantilever")
	App.setActiveDocument("")
	App.ActiveDocument = None
	return np_secondMoment	

if __name__ == "__main__":
	# Time Operation
	start_time = time.time()

	start_dp = 0
	end_dp   = 17501
	for i in range(start_dp, end_dp):
		computeSecondMoment(i)

	print("Finished img data generation in %s seconds" %
		(time.time()-start_time))
