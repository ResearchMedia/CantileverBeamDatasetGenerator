README.txt

@Author: Philippe Wyder
@Description: readme file corresponding to the COMSOL Applications: FEAFrequencyAnalysis_wMPF_cross_platform.mph and FEAStaticAnalysis_cross_platform.mph. These files can be loaded in COMSOL Multiphysics 5.4 on both Linux and Windows. To modify the underlying code, the files need to be opened in the COMSOL Multiphysics 5.4 Application Builder on Windows.

Workflow:
1. Open COMSOL Multiphysics 5.4

2. Click File-->Run Application, and select the desired file

3. Inside the application interface:
	A) Select the first body.stl file in the data set to be analyzed.
	b) To set the output directory for the CSV file, select a random file in the desired output directory.

4. Set the desired start and end data point (if you would like to analyze data points 5 through 7, then please enter 5 as the starting index and 8 as the end index)

5. Please set the beam-length used in your dataset manually (in our TwistedBeamDS or SlenderBeamDatasets it is 600mm)

6. Press [Start Beam Analysis]


Please cite the corresponding publication if you reuse this code.
