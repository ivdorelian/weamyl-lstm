import os
from glob import glob

import cv2
import xarray as xr
import numpy as np
from tqdm import tqdm

class DataReader:

    DATA_FOLDER = 'data'

    def get_seqed(self, data, seq_len):
        stacked = np.stack(data)
        seqed_data = []
        for i in range(stacked.shape[0]-seq_len):
            seqed_data.append(stacked[i:i+seq_len])
        return np.stack(seqed_data)

    def get_numpy_arrays(self, variable, seq_len=5):

        filepaths = glob(os.path.join(os.getcwd(), self.DATA_FOLDER) + '/*')
        filepaths = sorted(filepaths)
        results = []

        for filepath in tqdm(filepaths):
            net_cdf_data = xr.open_dataset(filepath, engine='netcdf4')
            numpy_array = net_cdf_data.variables[variable].data[0]
            numpy_array = np.moveaxis(numpy_array, 0, 2)
            numpy_array = cv2.resize(numpy_array, dsize=(160, 120))
            results.append(np.asarray(numpy_array, dtype=np.int32))

        return self.get_seqed(results, seq_len)
