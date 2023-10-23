import rasterio
import geopandas
from shapely import Polygon
import numpy as np
from rasterio.features import shapes
import glob
import os

def createGeoJson(inputFileName, outputFileName):
    src = rasterio.open(inputFileName)
    image = src.read(1) # first band
    mask = np.where(image>0,1,0)
    mask = mask.astype(rasterio.uint8)

    shapes = rasterio.features.shapes(image, mask=mask, transform=src.transform)
    polygons = [Polygon(s[0]['coordinates'][0]) for s in shapes]

    gdf = geopandas.GeoDataFrame(data={'id':range(len(polygons)),'geometry':polygons}, crs=src.crs)
    gdf.to_file(outputFileName,driver="GeoJSON")
    src = None

fileNames = glob.glob("masks/*.tif")
outPath = "geoJson"
if not os.path.exists(outPath):
   os.makedirs(outPath)

for fn in fileNames:
    prefix = fn.split("/")[-1].split(".")[0]
    outputFileName = outPath+"/"+prefix+".geojson"
    createGeoJson(fn, outputFileName)
