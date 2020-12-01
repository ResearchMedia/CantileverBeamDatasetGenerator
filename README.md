# CantileverBeamDatasetGenerator
README.txt

Author: Philippe Wyder

Description: Data Generation Workflow

This file outlines the data generation steps used in our publication. For additional informations on how to use the files in this folder-structure, please refer to the corresponding README.txt in each folder, as well as the comments within each file.
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
## Data Generation Workflow:
1) Define your desired use or create a .JSON file of the format of dataset_config/DS_Template.json to specify your dataset generation parameters.
Decide on what type of beams to generate--twisted or linearly extruded--and use TwistedBeamGen.py or SimpleBeam.py respectively.
2) Set the desired beam parameters and generate Beam data. (please refer to the corresponding publications for details)
3) Use FEAFrequencyAnalysis_wMPF_cross_platform.mph and FEAStaticAnalysis_cross_platform.mph to analyze the beams.
4) Use the CSV files resulting from step 3) in combination with csv2numpy.py for the static analysis output, and eigencsv2numpy.py for the frequency analysis output to add the analysis results to the dataset. (Please make sure to remove the dummy beam line at the beginning of the csv file\*)
5) Use set_extrude_length.py to add extrude_length.npy to each datapoint if needed
6) [optional] Use generate_antialias_img_from_verts.py to generate different size cross-section images (Warning: This script is CPU parallelized and will use all resources available while running. This may prevent you from doing other work while the script is running)


\* Each analysis output file comes pre-loaded with a dummy-beam. This beam gets analyzed first and occupies the first data line in analysis output file of the static analysis and the first three data lines in the output file of the frequency analysis. These lines need to be removed before using the CSV file to add the analysis results to the data set.


Please cite the corresponding publication if you reuse this code.

