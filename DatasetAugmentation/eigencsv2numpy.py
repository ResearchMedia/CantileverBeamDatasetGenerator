import csv
import numpy as np
from pathlib import Path
import time
import argparse
import json

#csv_file = Path('/home/ron/GeneratedData/CSV_Files/TwistedBeamDS/EigenfrequencyData.csv')
#dataset_path = Path('/home/ron/GeneratedData/data/TwistedBeamDS/')
csv_file = Path('/home/ron/GeneratedData/CSV_Files/SlenderBeamDS/EigenfrequencyData.csv')
dataset_path = Path('/home/ron/GeneratedData/data/SlenderBeamDataTF2000Complete/SlenderBeamDataTF2000')
GET_JSON_DICTIONARY = True
GET_JSON_DICTIONARY = True
SAVE_INDIVIDUALLY = False
def convert_data(legacy_mode = False):
    with open(csv_file) as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        eig_idx = 1
        prev_idx = -1
        for i, row in enumerate(readCSV, start = -1):
            dp_idx = row[-1]
            if prev_idx == dp_idx:
                eig_idx += 1
            else:
                eig_idx = 1
            if int(dp_idx) >= 0:
                outfile_eigenvalue = Path('ef{}.npy'.format(eig_idx))

                datalabel_path = dataset_path / str(dp_idx) / 'label'

                eig_list = [row[0]] + row[2:6] # stores  frequency, quality factor, dof, etc.


                print("Value Nr. ", i, "\t datapoint number: ", dp_idx, "\t eig_val: ", eig_idx)

                # store FEA labels

                # store EF
                np_eig = np.array(eig_list)
                np.save((datalabel_path / outfile_eigenvalue),    np_eig)

                if not legacy_mode:
                    outfile_empf = Path('empf{}.npy'.format(eig_idx))
                    outfile_npf = Path('npf{}.npy'.format(eig_idx))
                    empf_list = [row[0]] + row[6:12] # stores frequency, and EMPF transl. & rot.
                    npf_list = [row[0]] + row[12:18] # store frequency, and normalized particip. fact. transl. & rot.
                    # store EMPF
                    np_empf = np.array(empf_list)
                    np.save((datalabel_path / outfile_empf),    np_empf)
                    # store npf
                    np_npf = np.array(npf_list)
                    np.save((datalabel_path / outfile_npf),    np_npf)

                #np.save(outfile, np_array)
            prev_idx = dp_idx
                #if i > 2:
                #    print("abort...")
                #    return -1
# Selects nr_beams beams in range start_idx to end_idx
def random_select_in_range(start_idx, end_idx, nr_beams):
    random_samples = np.random.choice(end_idx - start_idx, nr_beams, replace = False) + start_idx
    selected_dps = {}
    with open(csv_file) as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        for i, row in enumerate(readCSV, start = -1):
            dp_idx = row[-1]
            if int(dp_idx) in random_samples:
                if dp_idx in selected_dps.keys():
                    selected_dps[dp_idx].append(float(row[0]))
                else:
                    selected_dps[dp_idx] = [float(row[0])]
    # assert that all datapoints have 3 recorded eigenfrequencies
    assert all([len(selected_dps[x]) == 3 for x in selected_dps])
    assert len(selected_dps.keys()) == nr_beams

    datalabel_path = dataset_path.resolve().parent
    # store .npy files
    if SAVE_INDIVIDUALLY:
        for i,key in enumerate(selected_dps):
            outfile_ef123 = Path('{}_twistedBeam_{}_EF123.npy'.format(i,dp_idx))
            ef123 = selected_dps[key]
            np.save((datalabel_path / outfile_ef123), np.array(ef123))

    if GET_JSON_DICTIONARY:
        json_file = Path('{}_twistedBeams_{}_EF123.json'.format(nr_beams,time.time()))
        # save dictionary of datapoints as json 
        ## {<dp_id>: [ef1, ef2, ef3], ...}
        with open((datalabel_path / json_file), 'w') as fp:
            json.dump(selected_dps, fp)

def main():
    parser = argparse.ArgumentParser(description='eigencsv2numpy parser')
    parser.add_argument('--legacy_mode', type=bool, default=False, metavar='select legacy mode for ef',
                          help='Provides backwards compatiblity with former Frequency Analaysis implementations')
    parser.add_argument('--start', type=int, default=None, metavar='set start index',
                          help='Set starting index in eigenfrequencies csv file')
    parser.add_argument('--end', type=int, default=None, metavar='set end index',
                          help='Set end index in eigenfrequencies csv file')
    parser.add_argument('--random-samples', type=int, default=None, metavar='set value for random sample selection',
                          help='Set number of random samples to select')
    args = parser.parse_args()
    if not csv_file.exists():
        print("csv_file doesn't exist")
        return -1
    elif not dataset_path.exists():
        print("dataset_path doesn't exist")
        return -1
    start_time = time.time()
    if args.random_samples is not None:
        print("Selecting {} random samples from {}".format(args.random_samples, csv_file.stem))
        random_select_in_range(args.start, args.end, args.random_samples)
    else:
        print("Converting CSV Data to numpy dataset data")
        convert_data(args.legacy_mode)
    print("Finished eigencsv2numpy in %s seconds" %
            (time.time()-start_time))
if __name__ == '__main__':
    main()