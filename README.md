**Status:** Archive (code is provided as-is, no updates expected)

# CantileverBeamDatasetGenerator

#### [ [Paper] ](https://doi.org/10.1098/rsif.2021.0571) [ [Video] ](TBD)

## Overview
This file outlines the data generation steps used in our publication: Visual design intuition: Predicting dynamic properties of beams from raw cross-section images. For additional informations on how to use the files in this folder-structure, please refer to the corresponding README.txt in each folder, as well as the comments within each file.
```bash
The directory structure of the repository is as follows:
├── COMSOL
│   ├── FEAFrequencyAnalysis_wMPF_cross_platform.mph
│   ├── README.txt
│   └── StaticvAnalysis_cross_platform.mph
├── DatasetAugmentation
│   ├── csv2numpy.py
│   ├── eigencsv2numpy.py
│   ├── generate_antialias_img_from_verts.py
│   ├── PyTorchNN.yml
│   ├── README.md
│   └── set_extrude_length.py
├── FreeCAD
│   ├── BeamGenerator.py
│   ├── datagencad.yml
│   ├── DataGenUtils.py
│   ├── dataset_config
│   │   ├── DS_Linear.json
│   │   ├── DS_TA50.json
│   │   ├── DS_Template.json
│   │   ├── DS_TW15.json
│   │   ├── DS_TW15TA50.json
│   │   └── DS_TW30TA50.json
│   ├── GenerateBeamDS.py
│   ├── README.md
│   ├── secondMomentGen.py
│   ├── SimpleBeam.py
│   └── TwistedBeamGen.py
└── README.md
```
### Data Generation Workflow:
1) Define your desired dataset configuration following the .json file format of [FreeCAD/dataset_config/DS_Template.json](dataset_config/DS_Template.json) to specify your dataset generation parameters.
Example json configuration:
```
{
	"root_path": "<dataset_directory_path>",
	"dataset_name": "<name of dataset>",
	"src_dataset": "<source dataset path, if beams are generated from existing cross-sections>",
	"extrude_length": <beam length in mm>,
	"min_verts": 3,
	"max_verts": 30,
	"min_radius": 24,
	"max_radius": 63,
	"twist_angle": 30,
	"twist_angle_step": 5,
	"taper_ratio": 1.0,
	"img_max_x": 128,
	"img_max_y": 128,
	"min_px_vol_accuracy": 0.05,
	"irregularity": 0.4,
	"spikiness": 0.15,
	"data_start_idx": 0,
	"data_end_idx": 17501
}
```
3) Generate Beam (please refer to the corresponding publications for details)
```
python GenerateBeamDS.py --ds_conf beam_configuration.json
```
5) Use [FEAFrequencyAnalysis_wMPF_cross_platform.mph](COMSOL/FEAFrequencyAnalysis_wMPF_cross_platform.mph) and [COMSOL/StaticvAnalysis_cross_platform.mph](FEAStaticAnalysis_cross_platform.mph) to analyze the beams. Please note that an installation of COMSOL Multiphysics 5.4 including the CAD Import Module is required to run these analyses.
6) Use the CSV files resulting from step 3) in combination with csv2numpy.py for the static analysis output, and eigencsv2numpy.py for the frequency analysis output to add the analysis results to the dataset. (Please make sure to remove the dummy beam line at the beginning of the csv file\*)
7) Use set_extrude_length.py to add extrude_length.npy to each datapoint if needed
8) (optional) Use generate_antialias_img_from_verts.py to generate different size cross-section images (Warning: This script is CPU parallelized and will use all resources available while running. This may prevent you from doing other work while the script is running)



\* Each analysis output file comes pre-loaded with a dummy-beam. This beam gets analyzed first and occupies the first data line in analysis output file of the static analysis and the first three data lines in the output file of the frequency analysis. These lines need to be removed before using the CSV file to add the analysis results to the data set.

## Downloading existing datasets corresponding to our publication:
Download our datasets from Mendeley Data: https://doi.org/10.17632/y3m8xm6kfk

## Citation
Wyder Philippe M. and Lipson Hod. 2021 Visual design intuition: predicting dynamic properties of beams from raw cross-section images. J. R. Soc. Interface.182021057120210571
[https://doi.org/10.1098/rsif.2021.0571](https://doi.org/10.1098/rsif.2021.0571)

Please cite using the following BibTeX entry:
```
@article{VisualDesignIntuition2021,
  author = {Philippe M. Wyder, Hod Lipson},
  title = {Visual design intuition: predicting dynamic properties of beams from raw cross-section images},
  journal = {J. R. Soc. Interface},
  year = {2021},
  doi = {10.1098/rsif.2021.0571}
}
```
## (Depreciated) Data Generation Workflow:
1) Define your desired use or create a .json file of the format of dataset_config/DS_Template.json to specify your dataset generation parameters.
Decide on what type of beams to generate--twisted or linearly extruded--and use TwistedBeamGen.py or SimpleBeam.py respectively.
2) Set the desired beam parameters and generate Beam data. (please refer to the corresponding publications for details)
3) Use FEAFrequencyAnalysis_wMPF_cross_platform.mph and FEAStaticAnalysis_cross_platform.mph to analyze the beams. Please note that an installation of COMSOL Multiphysics 5.4 including the CAD Import Module is required to run these analyses.
4) Use the CSV files resulting from step 3) in combination with csv2numpy.py for the static analysis output, and eigencsv2numpy.py for the frequency analysis output to add the analysis results to the dataset. (Please make sure to remove the dummy beam line at the beginning of the csv file\*)
5) Use set_extrude_length.py to add extrude_length.npy to each datapoint if needed
6) [optional] Use generate_antialias_img_from_verts.py to generate different size cross-section images (Warning: This script is CPU parallelized and will use all resources available while running. This may prevent you from doing other work while the script is running)
