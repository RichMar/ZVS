import requests
from math import radians, cos, sin, asin, sqrt
import os
import csv
from itertools import count # izip for maximum efficiency
from copy import deepcopy
import difflib

def get_distance(lat_1, lng_1, lat_2, lng_2):  # vypocet vzdalenosti bodu
    lng_1, lat_1, lng_2, lat_2 = map(radians, [lng_1, lat_1, lng_2, lat_2])  # prevede uhly na radiany
    d_lat = lat_2 - lat_1
    d_lng = lng_2 - lng_1
    a = sin(d_lat / 2) ** 2 + cos(lat_1) * cos(lat_2) * sin(d_lng / 2) ** 2
    c = 2 * asin(sqrt(a))
    r = 6371
    return c * r


  # area[name="Jihočeský kraj"];
  # node(area)["highway"="bus_stop"];
csvfile = 'zastavky-JCK-bus.csv'
seznam_st = []
uzel=[]
csv_reader_kopie = []
overpass_url = "http://overpass-api.de/api/interpreter"
overpass_query = """[out:csv(::lat, ::lon, "official_name", name, "ref:CIS_JR", "ref", "bus", "public_transport",
 ::count, ::id)]; \n ( \n"""
overpass_end = "\n ); \n out; \n out count; \n"

dotaz = """area[name="Jihočeský kraj"];
node(area)["highway"="bus_stop"];"""
overpass_query = overpass_query + dotaz + overpass_end
print(overpass_query)

response = requests.get(overpass_url, params={'data': overpass_query})
print("encoding :" + response.encoding)
response.encoding = 'utf8'
print("encoding :" + response.encoding)
data = [row.split('\t') for row in response.text.split('\n')]
# uloží data z OSM do csv souboru
with open('OSMzastavkyJCK.csv', 'w', newline='', encoding="utf8") as f:
    writer = csv.writer(f, delimiter=',')
    # writer.writerow(["lat", "lon", "official_name", "name", "ref:CIS_JR", "ref", "bus", "public_transport", "count"])
    writer.writerows(data)
m = sum(1 for line in data)
print(str(m))
# vytvoří list s daty z OSM
for x in data:
    if "lat" not in str(x) and not x[0] == "":
        seznam_st.append(x)
        print(str(x))
    # else:
    #     print('22222222')

# načte scv soubor se zastavákami od kraje
if os.path.exists(csvfile):
    csvfile = open(csvfile, newline='', encoding='utf8')
    csv_reader = csv.reader(csvfile, delimiter=';')
    zastavkykraj = list(csv_reader)
    pocet = 0
    # for y in csv_reader:
    #     csv_reader_kopie.append(y)

#https://stackoverflow.com/questions/11150155/why-cant-i-repeat-the-for-loop-for-csv-reader

    for x in zastavkykraj:
        # print("x:" + str(x))
        if ("lat" and "ref") not in x:
            ref = x[2]
            print('ref: ' + str(ref))
            index_zast = [(i, element.index(ref)) for i, element in enumerate(zastavkykraj) if ref in element]
            print('index_zast: ' + str(index_zast))


    # for x in csv_reader:
#     if "lat" not in x:
#         for y in data:
#             if "@lat" not in y and not y[0] == "":
#                 vzd = get_distance(float(x[0]), float(x[1]), float(y[0]), float(y[1]))
#
#                 if vzd < 0.050:
#                     s = difflib.SequenceMatcher(None, y[3], x[4])
#                     similarity = s.ratio()
#                     print(f"The similarity between the two strings is {similarity:.2f}")
#                     if similarity > 0.5:
#                         print(str(y) + ": " + str(vzd))
#                         pocet += 1

# for x in csv_reader:
#     print(x)
#     if ("lat" and "ref") not in x:
#         ref = x[2]
#         print("ref: " + str(ref))
#         index_zast = [(i, element.index(ref)) for i, element in enumerate(csv_reader) if ref in element]
#         uzel.append(index_zast)
#         for i in uzel:
#             print("index: " + str(i))




