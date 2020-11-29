# DataGenCAD

This file is an aggregate of  relevant packages to run the files presnt in this directory.

## Beam Generator dependencies
Please use the datagencad.yml file for a list of all packages present in the original data generation environment. Due to versioning issues, a direct install from the .yml file may produce errors.

The below comments outline known challenges:

Vtk may not get pinned the right way in the ordinary Conda-install:
to install FreeCAD use either

the newest version (dev)
conda create -n freecad freecad qt=5.9.* -c freecad/label/dev -c conda-forge

Or install it with a compatible vtk version
conda create -n freecad freecad vtk=8.1.* -c conda-forge

Ensure the following packages are present:
numpy, pillow, pygmsh
e.g.
conda install numpy
conda install pillow
conda install -c mrossi pygmsh
