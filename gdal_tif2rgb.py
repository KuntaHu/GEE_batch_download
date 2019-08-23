from osgeo import gdal
import os, gc, glob
# import filetype as ftype
from scipy import misc
# from scipy.misc import imread
import numpy as np
import matplotlib.pyplot as plt
from scipy.misc import imsave
from astropy.visualization import PercentileInterval

class GRID:

    # read image files
    def read_data(self, filename):
        raster=gdal.Open(filename)       # open file

        im_width = raster.RasterXSize    # get width
        im_height = raster.RasterYSize   # get height

        im_geotrans = raster.GetGeoTransform()  # get geoTransform
        im_proj = raster.GetProjection() # get Projection
        im_data = raster.ReadAsArray(0,0,im_width,im_height) # read data as array

        del raster
        return im_proj, im_geotrans, im_data

    # write tiff file
    def write_data(self, filename, im_proj, im_geotrans, im_data, bandNameList):
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
        raster = driver.Create(filename, im_width, im_height, im_bands, datatype)

        if (raster != None):
            raster.SetGeoTransform(im_geotrans)  # write affine transformation parameter
            raster.SetProjection(im_proj)  # write Projection
        else:
            print("Fails to create output file !!!")


        if im_bands == 1:
            rasterBand = raster.GetRasterBand(1)
            rasterBand.SetNoDataValue(0)

            rasterBand.SetDescription(bandNameList[0])
            rasterBand.WriteArray(im_data)

        else:
            # print("im_bands", im_bands)
            for bandIdx, bandName in zip(range(0, im_bands), bandNameList):
                # print(bandIdx)
                # print(bandName)
                bandNum = bandIdx + 1
                rasterBand = raster.GetRasterBand(bandNum)
                rasterBand.SetNoDataValue(0)

                rasterBand.SetDescription(bandName)
                rasterBand.WriteArray(im_data[bandIdx, ...])

        del raster

def read_tif_and_get_bands(dataPath, dataName, requiredBands):

    raster = gdal.Open(dataPath + dataName + ".tif")  # open file

    data = raster.ReadAsArray(0,0) # read data as array
    mask = raster.GetRasterBand(1).GetMaskBand().ReadAsArray(0,0)
    # print("data shape: {}, mask shape: {}".format(data.shape, mask.shape))

    bandNameList = []
    numBands = raster.RasterCount

    if len(data.shape) == 2:
        data = data[np.newaxis, ...]

    DATA = np.zeros([len(requiredBands), data.shape[1], data.shape[2]])

    cnt = 0
    for i in range(numBands):
        rasterBand = raster.GetRasterBand(i+1)
        bandName = rasterBand.GetDescription()
        bandNameList.append(bandName)
        if bandName in requiredBands:
            DATA[cnt, ...] = data[i, ...]
            cnt = cnt + 1

    # print(bandNameList)
    # print("cnt: {}".format(cnt))
    if cnt != len(requiredBands):
        print("----------------------------------------------------")
        print("There is no required bands: {}".format(requiredBands))
        DATA, mask = None, None

    return DATA, mask[np.newaxis, ...]

def tif2rgb(dataPath, dataName, savePath, saveName):
    run = GRID()

    proj, geotrans, data = run.read_data(
        dataPath + dataName + ".tif")  # read data

    print("data shape {}".format(data.shape))

    if len(data.shape) == 3:
        data = data[0:3, :, :]
        jpg_data = data.transpose(1, 2, 0)


    if len(data.shape) == 2:
        # jpg_data = np.zeros([data.shape[0], data.shape[1], 3])
        # jpg_data[..., 0] = data
        # jpg_data[..., 1] = data
        # jpg_data[..., 2] = data
        # jpg_data = np.uint8(jpg_data *255)
        jpg_data = data

    if not os.path.exists(savePath):
        os.makedirs(savePath)
    print("{}".format(saveName))
    plt.imsave(savePath + saveName + ".png", jpg_data, cmap = plt.cm.Greens)

def tifBand2png_GDAL(dataPath, dataName, savePath, saveName):

    run = GRID()
    interval = PercentileInterval(98.)

    proj, geotrans, data = run.read_data(
        dataPath + dataName + ".tif")  # read data

    # print("data shape {}".format(data.shape))

    if len(data.shape) == 3:
        jpg_data = data[0, :, :]
    elif len(data.shape) == 2:
        jpg_data = interval(data)
    else:
        jpg_data = data

    if not os.path.exists(savePath):
        os.makedirs(savePath)
    print("{}".format(saveName))
    plt.imsave(savePath + saveName + ".png", jpg_data, cmap = "gray")


def bandsMerge2tif(dataPath, dataName, savePath, saveName, stretchFlag):
    run = GRID()

    bandNameList = []
    interval = PercentileInterval(98.)

    fileNameList = glob.glob(dataPath + "{}*.tif".format(dataName))
    num = len(fileNameList)

    proj, geotrans, data = run.read_data(fileNameList[0])  # read data
    bandNameList.append(fileNameList[0].split(".")[1])
    if stretchFlag:
        data = interval(data)

    if 1 == num:
        DATA = data
    else:

        DATA = np.zeros([num, data.shape[0], data.shape[1]])
        DATA[0, ...] = data

        for i in range(1, num):
            _, _, data = run.read_data(fileNameList[i])  # read data
            bandNameList.append(fileNameList[i].split(".")[1])
            if stretchFlag:
                DATA[i, ...] = interval(data)
            else:
                DATA[i, ...] = data

    if not os.path.exists(savePath):
        os.makedirs(savePath)
    print(bandNameList)
    run.write_data(savePath + saveName + ".tif", proj, geotrans, DATA, bandNameList)



def rainTif2rgb(dataPath, dataName, savePath, saveName, satName):

    if satName == 'noaa':
        maxRain = 718.62  # mm
    elif satName == 'chirps':
        maxRain = 1444.34  # mm
    else:
        maxRain = 1.0

    run = GRID()

    proj, geotrans, data = run.read_data(
        dataPath + dataName + ".tif")  # read data

    print("data shape {}".format(data.shape))

    if len(data.shape) == 3:
        data = data[0:3, :, :]
        jpg_data = data.transpose(1, 2, 0)


    if len(data.shape) == 2:
        # jpg_data = np.zeros([data.shape[0], data.shape[1], 3])
        # jpg_data[..., 0] = data
        # jpg_data[..., 1] = data
        # jpg_data[..., 2] = data
        # jpg_data = np.uint8(jpg_data *255)
        jpg_data = data/maxRain

    if not os.path.exists(savePath):
        os.makedirs(savePath)
    print("{}".format(saveName))
    plt.imsave(savePath + saveName + ".png", jpg_data, cmap = plt.cm.Greens)

if __name__ == "__main__":
    dataPath = r"F:\Thomas_Wildfire_MSI\thomasFire_100m_MSI_Tif_collection\\"
    savePath = r"F:\Thomas_Wildfire_MSI\thomasFire_100m_MSI_Tif_collection\\"
    dataName = "MSI_20171128_S2"

    # bandsMerge2tif(dataPath, dataName, savePath, dataName, stretchFlag=True)



    requiredBands = ['B11', 'B12']
    data, mask = read_tif_and_get_bands(dataPath, dataName, requiredBands)

    print(data.shape)
    print(mask.shape)

    if data.shape[0] == 1:
        data = data[0, ...]
    else:
        img = np.transpose(data, (1, 2, 0))
        data = img[..., [1, 0, 1]]

    print(np.unique(mask))

    plt.imshow(data, cmap = 'jet')
    # plt.imshow(mask[0, ...], cmap= 'gray')
    plt.show()



    # for file in os.listdir(dataPath):
    #     fileName = file[:-4]
    #     # tif2png(renamePath, fileName, pngPath)
    #     tifBand2png_GDAL(dataPath, fileName, savePath, fileName)






    # tif_swir2rgb(dataPath, dataName, dataPath, saveName=dataName)
    # tif2rgb(dataPath, dataName, dataPath, saveName=dataName)

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
