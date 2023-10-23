import rasterio
import geopandas
import numpy as np

precision = 10000


def getBBox(fileName):
    "['minx', 'miny', 'maxx', 'maxy']"
    coords = ['minx', 'miny', 'maxx', 'maxy']

    #filename = "geoJson/mask_50.geojson"
    file = open(fileName)
    df = geopandas.read_file(file)
    df_bounds = df.bounds

    final_values = []
    for cc in coords:
        values = []
        for index, row in df.bounds.iterrows():
            values.append(row[cc])
        temp = None
        if 'min' in cc:
            temp = np.amin(values)
            #temp = int(temp * precision) / precision
        if 'max' in cc:
            temp = np.amax(values)
            #temp = int(temp * precision + 1) / precision
        final_values.append( temp)
    return final_values