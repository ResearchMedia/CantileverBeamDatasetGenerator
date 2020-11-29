import csv
import numpy as np
from pathlib import Path
import time
csv_file = Path('/home/ron/GeneratedData/CSV_Files/LinearDS/VolumeMaximumDispAndStrain.csv')
#dataset_path = Path('/home/ron/GeneratedData/data/TestSetRectCantilever')
dataset_path = Path('/home/ron/GeneratedData/data/Linear_DS/')
outfile_disp_field = Path('displacementFieldmm.npy')
outfile_princ_stress = Path('principalStrain.npy')
outfile_curl_disp = Path('curlDisplacement.npy')
outfile_tot_disp = Path('totalDisplacementmm.npy')
outfile_load_case = Path('FEAloadCase.npy')
outfile_tot_stress = Path('totalVonMises.npy')
np_load_case = np.array([1750,0,0])
def convert_data():
    if not csv_file.exists():
        print("csv_file doesn't exist")
        return -1
    elif not dataset_path.exists():
        print("dataset_path doesn't exist")
        return -1

    with open(csv_file) as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        for i, row in enumerate(readCSV, start = -1):
            if i < 0:
                print("read header line")
                continue
            np_disp_field = np.array(row[0:3])
            np_princ_stress = np.array(row[3:6])
            np_curl_disp = np.array(row[6:9])
            np_tot_disp = np.array(row[9])
            np_tot_VonMises = np.array(row[10])
            idx_value = row[11]
            assert int(i)==int(idx_value) # ensure datapoint correspondence
            print(np_disp_field, np_princ_stress, np_curl_disp, np_tot_disp, np_tot_VonMises)
            print("Value Nr. ", i)

            # store loadcase as potential resource
            datanumber_path = dataset_path / str(i) / 'numbers'
            np.save((datanumber_path / outfile_load_case),  np_load_case)
            # store FEA labels
            datalabel_path = dataset_path / str(i) / 'label'
            np.save((datalabel_path / outfile_disp_field),  np_disp_field)
            np.save((datalabel_path / outfile_princ_stress),np_princ_stress)
            np.save((datalabel_path / outfile_curl_disp),   np_curl_disp)
            np.save((datalabel_path / outfile_tot_disp),    np_tot_disp)
            np.save((datalabel_path / outfile_tot_stress),    np_tot_VonMises)
            #np.save(outfile, np_array)
            # if i > 2:
            #     return -1
if __name__ == '__main__':
    start_time = time.time()
    convert_data()
    print("Finished csv2numpy in %s seconds" %
            (time.time()-start_time))