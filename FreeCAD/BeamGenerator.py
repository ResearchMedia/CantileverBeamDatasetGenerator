# @Author: Philippe Wyder (pmw2125@columbia.edu)
# @Description: BeamGenerator class that can generate linearly extruded,
#				twisted, and tapered beams, and any combination thereof.
#				This class was written to replace the redundant code sections in
#				SimpleBeam.py, TwistedBeamGen.py, and TaperedBeamGen.py
# @Note: SimpleBeam.py & TwistedBeamGen.py are now obsolete due to GenerateBeamDS.py
# --------------------------------------------------------------------------- #
# FreeCAD related modules
#
import sys
sys.path.append('/home/ron/miniconda3/envs/datagencad/lib')
import FreeCAD
App = FreeCAD
import Part
import Sketcher
import Import, Mesh, Draft
import numpy as np
from pathlib import Path

# custom script imports
from DataGenUtils import *


#
# Start of beam Generator Class
#
class BeamGenerator:
	def __init__(self, data_path, dataset_name, extrude_length = 600, 
		min_verts = 3, max_verts = 30, min_radius = 24, max_radius = 63,
		twist_angle = 0.0, twist_angle_step = 5, taper_ratio = 1.0, 
		img_dim_x = 128, img_dim_y = 128, min_px_vol_accuracy = 0.4,
		poly_irregularity = 0.4, poly_spikiness = 0.15):
		self.data_path = data_path
		self.dataset_name = dataset_name
		self.extrude_length = extrude_length
		self.min_verts = min_verts
		self.max_verts = max_verts
		self.min_radius = min_radius
		self.max_radius = max_radius
		self.twist_angle = twist_angle
		self.taper_ratio = taper_ratio
		self.img_dim_x = img_dim_x
		self.img_dim_y = img_dim_y
		self.min_px_vol_accuracy = min_px_vol_accuracy
		self.irregularity = poly_irregularity
		self.spikiness = poly_spikiness

		self.twist_angle_step = twist_angle_step if twist_angle_step > 1e-7 else 1
		# twist_angle_step must be a factor of twist_angle
		assert((self.twist_angle % self.twist_angle_step) == 0)
		if twist_angle > twist_angle_step:
			self.nr_degree_steps = int(self.twist_angle/self.twist_angle_step)
		else:
			self.nr_degree_steps = 1
			self.twist_angle_step = twist_angle
		self.extrude_step_size = self.extrude_length/self.nr_degree_steps
	def gen_datapoint(self, dataPtNr, verts = None):
		
		#define current datapt path
		cur_folder = str(dataPtNr)
		cur_path = self.data_path / self.dataset_name / cur_folder	

		if verts is None:
			# randomly select Nr. of Vertices
			avg_rad = random.randint(self.min_radius,self.max_radius)
			nr_verts = random.randint(self.min_verts,self.max_verts)
			# To avoid self-intersecting polygons due to integer rounding in the generatePolygon function
			while (len(verts) > len(set(verts)) or not isNonIntersecting(verts)):
				print("Non_Intersecting?", isNonIntersecting(verts))
				avg_rad = random.randint(self.min_radius,self.max_radius)
				nr_verts = random.randint(self.min_verts,self.max_verts)
				verts = generatePolygon(0,0, avg_rad, self.irregularity, self.spikiness, nr_verts)	
		else:
			nr_verts = len(verts)
			avg_rad = self.computeAvgRad(verts)

		# Open New FreeCAD Doc
		App.newDocument("cantilever")
		App.setActiveDocument("cantilever")
		App.ActiveDocument=App.getDocument("cantilever")

		# create new object
		App.ActiveDocument.addObject('PartDesign::Body','Base_Body')

		# Start Sketch on XY-plane
		App.ActiveDocument.Base_Body.newObject('Sketcher::SketchObject','LowerPlane')
		App.ActiveDocument.LowerPlane.Support = (App.activeDocument().XY_Plane, [''])
		App.ActiveDocument.LowerPlane.MapMode = 'FlatFace'
		App.ActiveDocument.recompute()
		lower_plane_sketch = App.ActiveDocument.LowerPlane

		#Save Vertices Array
		np_verts = np.array(verts)
		np.save(Path(cur_path / "numbers" / "verts.npy"),np_verts)

		# CSV Export Variables (declare outside Try/Catch scope (necessary?))
		np_volume = None
		np_MOI = None

		try:
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
			    lower_plane_sketch.addConstraint(
			        Sketcher.Constraint("Coincident",line_nr-1,2,line_nr,1)) 
			    cur_pt = next_pt

			# Close the loop
			lower_plane_sketch.addGeometry(
			    Part.LineSegment(
			        App.Vector(cur_pt[0],cur_pt[1],0),
			        App.Vector(start_pt[0],start_pt[1],0)),False)
			line_nr += 1

			# Extrude profile
			# Get the profile defined by the polygon
			App.getDocument("cantilever").recompute()

			#
			# Get cross-section Area Moment Of Inertia
			#
			Draft.draftify(App.getDocument("cantilever").LowerPlane,delete=False)
			W_MoI = App.getDocument("cantilever").Wire.Shape.MatrixOfInertia
			np_secondMoment = np.array([W_MoI.A11, W_MoI.A22, W_MoI.A12])
			np.save(Path(cur_path / "label" / "secondMoment.npy"),np_secondMoment)

			#
			# generate 3D beam
			#
			taper_increment = (self.taper_ratio-1)/self.nr_degree_steps
			cross_section_list = [lower_plane_sketch]
			for i in range(1, self.nr_degree_steps+1):
				#  copy, scale, move up & rotate sketch
				upper_plane_sketch = Draft.scale(lower_plane_sketch,delta=FreeCAD.Vector(1+ taper_increment*i,1+ taper_increment*i,1+ taper_increment*i),
													center=FreeCAD.Vector(0.0,0.0,0.0),copy=True, legacy=False)
				upper_plane_sketch.Placement = App.Placement(App.Vector(0,0,self.extrude_step_size*i),
																App.Rotation(App.Vector(0,0,1),self.twist_angle_step*i))
				cross_section_list.append(upper_plane_sketch)
			beam_loft = App.ActiveDocument.addObject('Part::Loft','Body')
			beam_loft.Sections=cross_section_list
			beam_loft.Solid=True
			beam_loft.Ruled=False
			App.ActiveDocument.recompute()
			# save beam parameters
			np_extrude_length = np.array(self.extrude_length)
			np.save(Path(cur_path / "numbers" / "extrude_length.npy"), np_extrude_length)

			np_twist_angle = np.array(self.twist_angle)
			np.save(Path(cur_path / "numbers" / "twist_angle.npy"), np_twist_angle)

			np_taper_ratio = np.array(self.taper_ratio)
			np.save(Path(cur_path / "numbers" / "taper_ratio.npy"), np_taper_ratio)
			

			# Save beam properties
			MOI = App.ActiveDocument.Body.Shape.MatrixOfInertia
			np_MOI = np.array([	[MOI.A11, MOI.A12, MOI.A13, MOI.A14],
								[MOI.A21, MOI.A22, MOI.A23, MOI.A24],
								[MOI.A31, MOI.A32, MOI.A33, MOI.A34],
								[MOI.A41, MOI.A42, MOI.A43, MOI.A44] ])
			np.save(Path(cur_path / "label" / "MatrixOfInertia.npy"),np_MOI)
			
			np_volume = np.array(App.ActiveDocument.Body.Shape.Volume)
			np.save(Path(cur_path / "label" / "volume.npy"),np_volume)

			# save .brep, .step, .stl
			__objs__=[]
			__objs__.append(App.ActiveDocument.getObject("Body"))
			Part.export(__objs__,str(cur_path / "body.brep"))
			Import.export(__objs__,str(cur_path / "body.step"))
			Mesh.export(__objs__,str(cur_path / "body.stl"))
			del __objs__


		except RuntimeError as e:
			if (e.args[0]=="shape is invalid"):
				print("invalid shape - retry")
				App.closeDocument("cantilever")
				return -1
			else:
				raise

		#
		# Store Cross-Section Image
		#

		# Center Vertices for Image export
		cverts = []
		for pt in verts:
			cverts.append((pt[0]+round(self.img_dim_x/2), pt[1]+round(self.img_dim_y/2)))

		# Generate Image of crossection
		# Save Image to file
		# black and white
		img_path = cur_path / "img" / "img_bw.jpg"
		cur_img, nrpx_fill = getimg(cverts, 'bw', 1)
		# Verify Pixel Error Metric
		if (self.min_px_vol_accuracy < abs(np_volume-nrpx_fill*self.extrude_length)/np_volume and self.taper_ratio <1e-7):
			print("Exceeded maximum pixel error: Redo")
			App.closeDocument("cantilever")
			return -1
		cur_img.save(img_path)

		img_path = cur_path / "img" / "img_cbw.jpg"
		cur_img, nrpx_outline = getimg(cverts, 'bw', 0)
		cur_img.save(img_path)

		# save grayscale (filled in)
		img_path = cur_path / "img" / "img_grayscale.jpg"
		cur_img, nrpx_fill = getimg(cverts, 'grayscale', 1)
		cur_img.save(img_path)
		'''
		img_path = cur_path + "/img" + "/img_cgrayscale.jpg"
		cur_img, nrpx_outline = getimg(cverts, 'grayscale', 0)
		cur_img.save(img_path)
		'''
		# clear document for next itteration (delete bodies and sketches)
		App.closeDocument("cantilever")
		App.setActiveDocument("")
		App.ActiveDocument = None
		
		# Return data
		return {"nr_verts":nr_verts, "avgRad":avg_rad, "resolution": self.img_dim_x*self.img_dim_y,
				"nrpx_fill":nrpx_fill, "nrpx_outline": nrpx_outline, "volume": np_volume,
				"MOI00": np_MOI[0,0], "MOI01": np_MOI[0,1], "MOI02": np_MOI[0,2],
									  "MOI11": np_MOI[1,1], "MOI12": np_MOI[1,2],
															"MOI22": np_MOI[2,2]
				}
	# return rounded int of average radius
	def computeAvgRad(self, verts):
		nr_verts = len(verts)
		avgRad = 0
		for v in verts:
			x = v[0]
			y = v[1]
			# arctan(y/x)
			theta = np.arctan2(x,y)
			r_x = x / np.cos(theta)
			r_y = y / np.sin(theta)
			avgRad += r_x/(2*nr_verts)
			avgRad += r_y/(2*nr_verts)
		return round(avgRad)

#
#
# END OF BeamGenerator CLASS

# Run tests for BeamGenerator Class when called as script
if __name__ == '__main__':
	import datetime, csv
	dataset_name = "TestScriptBeamDS"
	root_path = Path("/home/ron/Downloads/")
	data_path = root_path / "data" / dataset_name
	data_path.mkdir(parents=False, exist_ok = True) 
	print("Test BeamGenerator class")
	print("Please see folder %s in %s for test output data" % (dataset_name, root_path))
	min_verts = 3
	max_verts = 30
	min_radius = 24 #[mm]
	max_radius = 63 #[mm]
	twist_angle = 30 #[degrees]
	twist_angle_step = 5
	extrude_length = 600.0 #[mm]
	IMG_MAX_X = 128
	IMG_MAX_Y = 128
	MIN_PX_VOLUME_ACCURACY = .05 # 10% minimum px accuracy
	POLY_IRREGULARITY = 0.4
	POLY_spikiness = 0.15
	data_start_idx = 0
	data_end_idx = 5
	start_time = datetime.datetime.now()

	#
	# Test Cases
	#
	test_cases = []
	# linearly extruded beam
	test_cases.append((data_path, "TestLinear", extrude_length, min_verts, max_verts,
					min_radius, max_radius,	0, twist_angle_step, 1.0, 
					IMG_MAX_X, IMG_MAX_Y, MIN_PX_VOLUME_ACCURACY, POLY_IRREGULARITY, POLY_spikiness))
	# tapered beam
	test_cases.append((data_path, "TestTapered", extrude_length, min_verts, max_verts,
					min_radius, max_radius,	0, 1, 0.5, 
					IMG_MAX_X, IMG_MAX_Y, MIN_PX_VOLUME_ACCURACY, POLY_IRREGULARITY, POLY_spikiness))
	# twisted beam
	test_cases.append((data_path, "TestTwisted", extrude_length, min_verts, max_verts,
					min_radius, max_radius,	35, 5, 1.0, 
					IMG_MAX_X, IMG_MAX_Y, MIN_PX_VOLUME_ACCURACY, POLY_IRREGULARITY, POLY_spikiness))
	# tapered & twisted beam
	test_cases.append((data_path, "TestTwistedTapered", extrude_length, min_verts, max_verts,
					min_radius, max_radius,	35, 5, 0.5, 
					IMG_MAX_X, IMG_MAX_Y, MIN_PX_VOLUME_ACCURACY, POLY_IRREGULARITY, POLY_spikiness))

	for test_case in test_cases:
		# CSV File
		csv_file_path = data_path / "CSV_Files"
		csv_file_path.mkdir(parents=False, exist_ok = True) 
		csv_file_name = csv_file_path / (test_case[1] + "_" + str(datetime.datetime.now().strftime("%Y%m%d%H%M")) + ".csv")
		csv_file_headers = ["ID", "nr_verts", "avgRad", "resolution", "nrpx_fill", "nrpx_outline", "volume",
							"MOI00", "MOI01", "MOI02", "MOI11", "MOI12", "MOI22"]
		with open(csv_file_name, 'w') as csv_file:
			w = csv.DictWriter(csv_file, csv_file_headers)
			w.writeheader()
			beamGen = BeamGenerator(*test_case)
			#beamGen = BeamGenerator(root_path, dataset_name, extrude_length, min_verts, max_verts,
			#			min_radius, max_radius,	twist_angle, twist_angle_step, taper_ratio, 
			#			IMG_MAX_X, IMG_MAX_Y, MIN_PX_VOLUME_ACCURACY, POLY_IRREGULARITY, POLY_spikiness)
			for i in range(data_start_idx, data_end_idx):
				cur_datapt_path = data_path / test_case[1] /  str(i)
				cur_datapt_path.mkdir(parents=True, exist_ok=True)
				Path(cur_datapt_path / "img").mkdir(parents=True, exist_ok=True)
				Path(cur_datapt_path / "numbers").mkdir(parents=True, exist_ok=True) 
				Path(cur_datapt_path / "label").mkdir(parents=True, exist_ok=True)
				genStatus = beamGen.gen_datapoint(i)
				while(genStatus == -1):
					genStatus = beamGen.gen_datapoint(i)

				# Write to CSV
				genStatus["ID"] = i
				w.writerow(genStatus)

				if (i%100==0):
					print("DataPt generated:",i)

	time_delta = str(datetime.datetime.now()-start_time)
	print("Finished Data Generation of {} datapoints in {} time".format(
			data_end_idx-data_start_idx,  time_delta))

