import csv
import sys
from osgeo import ogr, osr, gdal
import os
#souradnice S-JTSK (EPSG:5514) prevod na GPS (EPSG:4326)
# shpfile = r'.\data\zastavky_JcK_20230306.shp' #sys.argv[1]
shpfile = r'.\data\zastavky_shp_wgs84.shp'
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
csvfile = open('zastavky-LK.csv', 'w', encoding='utf8')
#UTF-8, windows-1250,ISO 8859-2, CP852
csvfile_vlak = open('zastavky-LK-vlak.csv', 'w', encoding="utf8")
csvfile_bus = open('zastavky-LK-bus.csv', 'w', encoding="utf8")

# data Jihoceskeho kraje nemazat
# csvfile.write("lat;lon;ref;okres;name;stanoviste;typ;obsluhovano" + "\n")

# data Libereckeho kraje
csvfile.write("lat;lon;ref;name;cislo zony;nazev zony" + "\n")

csvfile_vlak.write("lat;lon;ref;okres;name;stanoviste;typ;obsluhovano" + "\n")
csvfile_bus.write("lat;lon;ref;okres;name;stanoviste;typ;obsluhovano" + "\n")
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

    # data Jihoceskeho kraje nemazat ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # ref = str(int(feature.GetField("CISLO_NUM")))
    # okres = feature.GetField("OKRES")
    # poplong = feature.GetField("POPIS_LONG")
    # stan = feature.GetField("STANOVISTE")
    # obsluh = feature.GetField("OBSLUHOVAN")
    # typ = feature.GetField("TYP")
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # data Libereckeho kraje
    ref = str(int(feature.GetField("ID")))
    try:
        okres = bytes(feature.GetField("NAZEV").encode('ISO-8859-2', 'surrogateescape')).decode('cp1250')
    except:
        okres = "kuk"
        print("kuk")
    try:
        okres = bytes(feature.GetField("NAZEV").encode('utf8', 'surrogateescape')).decode('cp1250')
    except:
        okres = "kuk2"
        print("kuk2")

    print("okres: " + okres)
    # poplong = feature.GetField("NAZEV_ZONY")
    poplong = bytes(feature.GetField("NAZEV_ZONY").encode('ISO-8859-2', 'surrogateescape')).decode('cp1250')
    print("poplong: " + poplong)
    stan = feature.GetField("CISLO_ZONY")
    print("stan: " + stan)
    wgslon = feature.GetField("WGS_LON")
    wgslat = feature.GetField("WGS_LAT")
    print("wgs: " + str(wgslat) + ";" + str(wgslon))

    if not stan:
        stan = ""

    # # data JČK nemazat~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # print(geom.Centroid().ExportToWkt() + str(okres) + " " + str(poplong) + " " + str(stan))
    # csvfile.write(lat + ";" + lon + ";" + ref + ";" + okres + ";" + poplong + ";" + str(stan) + ";" + typ + ";" + str(obsluh) + "\n")
    # if typ == "bus" and obsluh == 1:
    #     csvfile_bus.write(lat + ";" + lon + ";" + ref + ";" + okres + ";" + poplong + ";" + str(stan) + ";" + typ + ";" + str(obsluh) + "\n")
    # elif typ == "vlak" and obsluh == 1:
    #     csvfile_vlak.write(
    #         lat + ";" + lon + ";" + ref + ";" + okres + ";" + poplong + ";" + str(stan) + ";" + typ + ";" + str(obsluh) + "\n")
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    # Data LK nemazat
    text_ble = str(wgslat) + ";" + str(wgslon) + ";" + ref + ";" + okres + ";" + stan + ";" + poplong
    # sem = json.loads(r'"\udcec"')
    print("surogate: " + text_ble.encode("cp1250", "surrogatepass").decode("cp1250"))

    print(str(wgslat) + ";" + str(wgslon) + ";" + ref + ";" + okres + ";" + stan + ";" + poplong)
    csvfile.write(str(wgslat) + ";" + str(wgslon) + ";" + ref + ";" + okres + ";" + stan + ";" + poplong + ";" + "\n")

    aa += 1
print("Konec - počet řádků: " + str(aa))
csvfile.close()
csvfile_vlak.close()
csvfile_bus.close()
