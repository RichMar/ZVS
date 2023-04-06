import csv
import sys
from osgeo import ogr, osr, gdal
import os
#souradnice S-JTSK (EPSG:5514) prevod na GPS (EPSG:4326)
shpfile = r'c:\Users\marik.AGIR\OneDrive - Agir AG\Dokumenty\GitHub\ZVS\data\zastavky_JcK_20230306.shp' #sys.argv[1]
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

# # get the output layer's feature definition
# outLayerDefn = outLayer.GetLayerDefn()
# get the input layer
inDataSet = driver.Open(shpfile)
inLayer = inDataSet.GetLayer()
# loop through the input features
inFeature = inLayer.GetNextFeature()
for feature in layer:
    geom = feature.GetGeometryRef()
    geom.Transform(coordTrans)
    okres = feature.GetField("OKRES")
    poplong = feature.GetField("POPIS_LONG")
    stan = feature.GetField("STANOVISTE")
    print(geom.Centroid().ExportToWkt() + str(okres) + " " + str(poplong) + " " + str(stan))

a = 0
while inFeature:
    # get the input geometry
    geom = inFeature.GetGeometryRef()
    # reproject the geometry
    geom.Transform(coordTrans)
    a = a + 1
    print(str(a) + " -- " + str(geom))
    # # create a new feature
    # outFeature = ogr.Feature(outLayerDefn)
    # # set the geometry and attribute
    # outFeature.SetGeometry(geom)
#Get field names
dfn = layer.GetLayerDefn()
nfields = dfn.GetFieldCount()
fields = []
for i in range(nfields):
    fields.append(dfn.GetFieldDefn(i).GetName())
fields.append('kmlgeometry')
csvwriter = csv.DictWriter(csvfile, fields)
try:
    csvwriter.writeheader() #python 2.7+
except:
    csvfile.write(','.join(fields)+'\n')

# Write attributes and kml out to csv
for feat in layer:
    attributes = feat.items()
    geom = feat.GetGeometryRef()
    attributes['kmlgeometry'] = geom.ExportToKML()
    csvwriter.writerow(attributes)

#clean up
del csvwriter, layer, ds
csvfile.close()