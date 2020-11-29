#Author-PhilippeWyder
#Description-Random beam generated with different cross sections for data generation
from BeamGenerator import *
# Script Related Imports
import numpy as np
import Import, Mesh
from pathlib import Path
import json
import argparse
import datetime, csv

def load_src_ds_availability(src_ds, start_idx, end_idx):
	vert_dic = {}
	for i in range(start_idx, end_idx):
		cur_path = src_ds/str(i)/"numbers"/"verts.npy"
		if cur_path.is_file():
			vert_dic[str(i)] = (np.load(cur_path)).tolist()
		else:
			print(cur_path, " is missing\n")
			return False;
	return vert_dic 
def main(dataset_parameters_json):
	start_time = datetime.datetime.now()

	with open(dataset_parameters_json, mode='r') as json_file:
		ds_param = json.load(json_file)
	dataset_name = ds_param["dataset_name"]
	root_path = Path(ds_param["root_path"])
	data_path = root_path / "data"
	csv_path = root_path / "CSV_Files"

	all_verts = False
	if len(ds_param["src_dataset"]):
		src_root = Path(ds_param["src_dataset"])
		all_verts = load_src_ds_availability(src_root,
							ds_param["data_start_idx"], ds_param["data_end_idx"])
		if all_verts:
			print("Generating beams from existing cross-sections in %s dataset" % ds_param["src_dataset"])
		else:
			print("Source dataset doesn't have all necessary vert.npy")
			print("files in range %i to %i" % start_idx, end_idx)

	# initialize beam generator
	beam_gen = BeamGenerator(data_path, dataset_name, ds_param["extrude_length"], 
	ds_param["min_verts"], ds_param["max_verts"], ds_param["min_radius"], ds_param["max_radius"],
	ds_param["twist_angle"], ds_param["twist_angle_step"], ds_param["taper_ratio"], 
	ds_param["img_max_x"], ds_param["img_max_y"], ds_param["min_px_vol_accuracy"],
	ds_param["irregularity"], ds_param["spikiness"])

	# CSV File
	csv_file_name = dataset_name + "_" + str(datetime.datetime.now().strftime("%Y%m%d%H%M")) + ".csv" 
	csv_file_path = csv_path / csv_file_name
	csv_file_headers = ["ID", "nr_verts", "avgRad", "resolution", "nrpx_fill", "nrpx_outline", "volume",
						"MOI00", "MOI01", "MOI02", "MOI11", "MOI12", "MOI22"]
	with open(csv_file_path, 'w') as csv_file:
		w = csv.DictWriter(csv_file, csv_file_headers)
		w.writeheader()
		for i in range(ds_param["data_start_idx"], ds_param["data_end_idx"]):
			# generate datapoint directories
			cur_datapt_path =  data_path / dataset_name /  str(i)
			Path(cur_datapt_path / "img").mkdir(parents=True, exist_ok=True)
			Path(cur_datapt_path / "numbers").mkdir(parents=True, exist_ok=True) 
			Path(cur_datapt_path / "label").mkdir(parents=True, exist_ok=True)

			cur_verts = all_verts[str(i)] if all_verts else None

			# generate datapoint
			genStatus = -1
			while(genStatus == -1):
				genStatus = beam_gen.gen_datapoint(i, verts = cur_verts)

			# Write to CSV
			genStatus["ID"] = i
			w.writerow(genStatus)

			if (i%100==0):
				print("DataPt generated:",i)
	# write config file to folder
	conf_file_name = dataset_name + "_" + str(datetime.datetime.now().strftime("%Y%m%d%H%M")) + "_config.json"  
	conf_file_path = csv_path / conf_file_name
	with open(conf_file_path, 'w') as json_outfile:
		json.dump(ds_param, json_outfile)

	# reports data generation time duration
	time_delta = str(datetime.datetime.now()-start_time)
	print("Finished Data Generation of {} datapoints in {} time".format(
		ds_param["data_end_idx"]-ds_param["data_start_idx"],  time_delta))

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='BeamGen Parser')
	parser.add_argument('--ds_conf', type=str, default=None, metavar='ds_conf.json',
					  help='Provide a .json dataset config file path')
	args = parser.parse_args()
	if args.ds_conf and Path(args.ds_conf).is_file():
		main(args.ds_conf)
	else:
		print("Please provide a valid configuration file: e.g. --ds_conf <ds_conf.json>")