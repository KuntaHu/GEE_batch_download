from osgeo import gdal
import os, gc
# import filetype as ftype
from scipy import misc
# from scipy.misc import imread
import numpy as np
import matplotlib.pyplot as plt
from scipy.misc import imsave

class GRID:

    # read image files
    def read_data(self, filename):
        dataset=gdal.Open(filename)       # open file

        im_width = dataset.RasterXSize    # get width
        im_height = dataset.RasterYSize   # get height

        im_geotrans = dataset.GetGeoTransform()  # get geoTransform
        im_proj = dataset.GetProjection() # get Projection
        im_data = dataset.ReadAsArray(0,0,im_width,im_height) # read data as array

        del dataset
        return im_proj, im_geotrans, im_data

    # write tiff file
    def write_data(self, filename, im_proj, im_geotrans, im_data):
        #gdal data types include:
        #gdal.GDT_Byte,
        #gdal .GDT_UInt16, gdal.GDT_Int16, gdal.GDT_UInt32, gdal.GDT_Int32,
        #gdal.GDT_Float32, gdal.GDT_Float64

        # check the datatype of raster data
        if 'int8' in im_data.dtype.name:
            datatype = gdal.GDT_Byte
        elif 'int16' in im_data.dtype.name:
            datatype = gdal.GDT_UInt16
        else:
            datatype = gdal.GDT_Float32

        # get the dimension
        if len(im_data.shape) == 3:
            im_bands, im_height, im_width = im_data.shape
        else:
            im_bands, (im_height, im_width) = 1, im_data.shape

        # create the output file
        driver = gdal.GetDriverByName("GTiff")  # specify the format
        dataset = driver.Create(filename, im_width, im_height, im_bands, datatype)

        if (dataset != None):
            dataset.SetGeoTransform(im_geotrans)  # write affine transformation parameter
            dataset.SetProjection(im_proj)  # write Projection
        else:
            print("Fails to create output file !!!")

        if im_bands == 1:
            dataset.GetRasterBand(1).WriteArray(im_data)  # write array data
        else:
            for i in range(im_bands):
                dataset.GetRasterBand(i + 1).WriteArray(im_data[i])

        del dataset

def scale_to_01(data):
    data_plot = data.reshape([-1, 1])  # [np.where(data!=0)].reshape([-1,1])
    MAX = max(data_plot)
    MIN = min(data_plot)
    data_plot01 = (data - MIN) / (MAX - MIN)
    return data_plot01


def tif2rgb(dataPath, dataName, savePath, saveName):
    run = GRID()

    proj, geotrans, data = run.read_data(
        dataPath + dataName + ".tif")  # read data

    if len(data.shape) == 2:
        # jpg_data = scale_to_01(data)*255
        jpg_data = data

    if len(data.shape) == 3:
        data = data[0:3, :, :]
        jpg_data = data.transpose(1, 2, 0)

    if not os.path.exists(savePath):
        os.makedirs(savePath)

    # print("jpg.shape: {}".format(jpg_data.shape))
    imsave(savePath + saveName + ".png", jpg_data)


if __name__ == "__main__":
    dataPath = r"F:\Thomas_Wildfire_v2\ref_maps_based_on_offical_docs\\"
    dataName = "Thomas_offical_progression_map_from_pdf_100m"
    tif2rgb(dataPath, dataName, dataPath, saveName=dataName)

# if __name__ == "__main__":
#     # os.chdir(r'D:\Desktop\processing\Thomas_fire_SWIR_PseudoColorImage_auxil')      # change path into your workspace
#
#     batchProcessingFlag = False
#     if batchProcessingFlag: # batch processing
#         dataPath = r"F:\Thomas_Wildfire\png2tif\\"
#         savePath = r"F:\Thomas_Wildfire\png2tif\\"
#
#         if not os.path.exists(savePath):
#             os.makedirs(savePath)
#
#         run = GRID()
#         # fileNames = []
#         for file in os.listdir(dataPath):
#             gc.enable()
#
#             dataName = file[:-4]
#             print(dataName)
#             print(dataPath + dataName + ".tif")
#
#             # read data
#             proj, geotrans, data = run.read_data(dataPath + dataName + ".tif")  # read data
#
#             # band operation
#             # data = data[[5, 4, 5], :, :]  # operation on bands, SWIR-1/2
#             #
#             # NIR = data[0, :, :]
#             # Red = data[1, :, :]
#             # NDVI = (NIR - Red) / (NIR + Red)
#             #
#             # print("NDVI: ", NDVI)
#
#             SWIR2 = data[5, :, :]
#
#             # write data
#             # export bands.
#             saveBandPath = "D:\Desktop\Thomas_Wildfire\Thomas_fire_SWIR2_band_tif\\"
#             if not os.path.exists(saveBandPath):
#                 os.makedirs(saveBandPath)
#
#             saveBandName = dataName + '_SWIR2'
#             run.write_data(saveBandPath + saveBandName + ".tif", proj, geotrans, SWIR2)  # write data
#
#             # jpgData = data.transpose(1, 2, 0)
#             # misc.imsave(savePath + "test_" + saveName + ".jpg", jpgData)
#
#     else: # non-batch processing
#         run = GRID()
#         dataPath = r"F:\Thomas_Wildfire_v2\png2tif\\"
#         savePath = r"F:\Thomas_Wildfire_v2\png2tif\\"
#
#         if not os.path.exists(savePath):
#             os.makedirs(savePath)
#
#         pngName = "DSC_1104_1128_VV_VH_cnn_fireConfMap_lr_0.0001_acc_96.92_gray"
#         tifName = "dem.elevation"
#
#         data = misc.imread(dataPath + pngName + ".png")[..., 0]/255.0
#         print(np.unique(data))
#
#         # data[np.where(data == 32)] = 255
#         # data[np.where(data == 253)] = 0
#         # data[np.where(data == 68)] = 0
#
#
#         print("read data: " + dataPath + tifName + ".tif")
#         proj, geotrans, _ = run.read_data(dataPath + tifName + ".tif")  # read data
#
#
#         # data = data[[5, 4, 5], :, :]  # operation on bands, SWIR-1/2
#         # data = data[[0, 1, 2], :, :]  # NIR
#         #
#         print("============ Info for the Written tiff =============")
#         print("Projection", proj)
#         print("GeoTransformation: ", geotrans)
#         print("Shape of written data: ", data.shape)
#         print("============ Info for the Written tiff =============")
#
#         os.chdir(savePath)
#         saveName = pngName
#         run.write_data(savePath + pngName + ".tif", proj, geotrans, data)  # write data
#
#         # plt.imsave(savePath + pngName + "_nofire_confMap.png", 1 - data, cmap = 'jet')
#
#         # export bands.
#         # saveBandPath = "D:\Desktop\Thomas_Wildfire\Thomas_fire_SWIR2_band_tif\\"
#         # if not os.path.exists(saveBandPath):
#         #     os.makedirs(saveBandPath)
#         #
#         # bands = ['NIR', 'R', 'G', 'B', 'SWIR1', 'SWIR2']
#         # for i in range(0, len(bands)):
#         #     band = data[i, :, :]
#         #     saveBandName = dataName + '_' + bands[i] + ".tif"
#         #     run.write_data(saveBandPath + saveBandName, proj, geotrans, band)  # write data
#
#         # fileNames.append(file[:-4])
#
#     # sourcefile = r"D:\Desktop\processing\ThomasFire_SWIR_PseudoColorImages\ThomasFire_S2_20171128_SWIR.tif"
#     # destinationfile = r"D:\Desktop\processing\ThomasFire_SWIR_PseudoColorImages\ThomasFire_S2_20171128_SWIR_v3.jpg"
#     #
#     # print("gdal_translate -of GTiff " + sourcefile + " " +  destinationfile)
#     # os.system("gdal_translate -of GTiff " + sourcefile + " " +  destinationfile)
