import os
import numpy as np
from scipy.misc import imread, imsave
# from skimage import img_as_float
def pngBand2rgb(dataPath, dataName, savePath, saveName, bands):
    R = imread(dataPath + "{}.{}.png".format(dataName, bands[0]))[..., 0]  # read data
    G = imread(dataPath + "{}.{}.png".format(dataName,  bands[1]))[..., 0]
    B = imread(dataPath + "{}.{}.png".format(dataName,  bands[2]))[..., 0]

    jpg_data = np.zeros([R.shape[0], R.shape[1], 3])
    jpg_data[..., 0] = R
    jpg_data[..., 1] = G
    jpg_data[..., 2] = B

    # jpg_data = data.transpose(1, 2, 0)

    if not os.path.exists(savePath):
        os.makedirs(savePath)
    imsave(savePath + saveName + ".png", jpg_data)

if __name__ == "__main__":
    # from gdal_tif2rgb import tif_swir2rgb
    dataPath = r"F:\Thomas_Wildfire_v2\Ranch_100m_SAR_PNG_collection\\"
    dataName = "S2_20180622"
    pngBand2rgb(dataPath, dataName, dataPath, dataName)
