import csv
import numpy as np
from pathlib import Path
dataset_path = Path('/media/ron/UbuntuData/Temp/RegularizedBeamData')
outfile_extrude_length = Path('extrude_length.npy')
np_extrude_length = np.array([2000]) # in mm
def convert_data():
    if not dataset_path.exists():
        print("dataset_path doesn't exist")
        return -1

    for i in range(0,15001):
        print(i, "processed ", np_extrude_length)
        # store extrusion length as potential resource
        datanumber_path = dataset_path / str(i) / 'numbers'
        np.save((datanumber_path / outfile_extrude_length),  np_extrude_length)
#        if i > 2:
#            return -1

convert_data()
