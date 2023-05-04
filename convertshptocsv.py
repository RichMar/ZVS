import csv
import sys
from osgeo import ogr, osr, gdal
import os
#souradnice S-JTSK (EPSG:5514) prevod na GPS (EPSG:4326)
shpfile = r'.\data\zastavky_JcK_20230306.shp' #sys.argv[1]
csvfile = r'test.csv' #sys.argv[2]

if not os.path.exists(shpfile):
  print('File does not exist')

#Open files
csvfile = open(csvfile, 'w')
ds = ogr.Open(shpfile)
layer = ds.GetLayer(0)
layerDefinition = layer.GetLayerDefn()
featureCount = layer.GetFeatureCount()
print("Number of features in %s: %d" % (os.path.basename(shpfile), featureCount))



for i in range(layerDefinition.GetFieldCount()):
    fieldName = layerDefinition.GetFieldDefn(i).GetName()
    fieldTypeCode = layerDefinition.GetFieldDefn(i).GetType()
    fieldType = layerDefinition.GetFieldDefn(i).GetFieldTypeName(fieldTypeCode)
    fieldWidth = layerDefinition.GetFieldDefn(i).GetWidth()
    GetPrecision = layerDefinition.GetFieldDefn(i).GetPrecision()

    print(fieldName + " - " + fieldType + " " + str(fieldWidth) + " " + str(GetPrecision))

spatialRef = layer.GetSpatialRef() #Get Projection
#prevod S-JTSK na GPS
driver = ogr.GetDriverByName('ESRI Shapefile')
# input SpatialReference
inSpatialRef = osr.SpatialReference()
inSpatialRef.ImportFromEPSG(5514)
# output SpatialReference
outSpatialRef = osr.SpatialReference()
outSpatialRef.ImportFromEPSG(4326)
# create the CoordinateTransformation
coordTrans = osr.CoordinateTransformation(inSpatialRef, outSpatialRef)

# get the input layer
inDataSet = driver.Open(shpfile)
inLayer = inDataSet.GetLayer()
# loop through the input features
inFeature = inLayer.GetNextFeature()
csvfile = open('zastavky-JCK.csv', 'w')
csvfile_vlak = open('zastavky-JCK-vlak.csv', 'w')
csvfile_bus = open('zastavky-JCK-busk.csv', 'w')
csvfile.write("lat;lon;ref;okres;name;stanoviste;typ" + "\n")
csvfile_vlak.write("lat;lon;ref;okres;name;stanoviste;typ" + "\n")
csvfile_bus.write("lat;lon;ref;okres;name;stanoviste;typ" + "\n")
aa = 0

for feature in layer:
    geom = feature.GetGeometryRef()
    geom.Transform(coordTrans)
    point = geom.Centroid().ExportToWkt()
    a = point.find('(')
    b = point.rfind(' ')
    c = point.find(')')
    lat = point[a + 1:b]
    lon = point[b + 1:c]
    ref = str(int(feature.GetField("CISLO_NUM")))
    okres = feature.GetField("OKRES")
    poplong = feature.GetField("POPIS_LONG")
    stan = feature.GetField("STANOVISTE")
    if not stan:
        stan = ""
    typ = feature.GetField("TYP")
    print(geom.Centroid().ExportToWkt() + str(okres) + " " + str(poplong) + " " + str(stan))
    csvfile.write(lat + ";" + lon + ";" + ref + ";" + okres + ";" + poplong + ";" + str(stan) + ";" + typ + "\n")
    if typ == "bus":
        csvfile_bus.write(lat + ";" + lon + ";" + ref + ";" + okres + ";" + poplong + ";" + str(stan) + ";" + typ + "\n")
    elif typ == "vlak":
        csvfile_vlak.write(
            lat + ";" + lon + ";" + ref + ";" + okres + ";" + poplong + ";" + str(stan) + ";" + typ + "\n")
    aa += 1
print("Konec - počet řádků: " + str(aa))
csvfile.close()
csvfile_vlak.close()
csvfile_bus.close()
