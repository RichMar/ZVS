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

#   proměnné
csvfile = 'zastavky-JCK-bus.csv'
seznam_st = []
uzel=[]
csv_reader_kopie = []
chybejicisinglzast = [[] for i in range(4)]
chybejicisinglzast_list = []
problemovazast = []


# konstanty
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
    # zastavkykraj = [tuple(row for row in csv_reader)]
    pocet = 0
    # for y in csv_reader:
    #     csv_reader_kopie.append(y)

#https://stackoverflow.com/questions/11150155/why-cant-i-repeat-the-for-loop-for-csv-reader
    n = 0
    iterace = 0
    for x in zastavkykraj:
        g = 0
        # print("iterace:" + str(iterace))
        iterace += 1
        if ("lat" and "ref") not in x:
            ref = x[2]
            # print('ref: ' + str(ref))
            index_zast = [(i, element.index(ref)) for i, element in enumerate(zastavkykraj) if ref in element]
            # print('index_zast: ' + str(index_zast))
            if len(index_zast) == 1:
                ind = index_zast[0][0]
                lat = zastavkykraj[index_zast[0][0]][0]
                lon = zastavkykraj[index_zast[0][0]][1]
                oficialname = zastavkykraj[index_zast[0][0]][4]
                ref = zastavkykraj[index_zast[0][0]][2]
                dd = 0
                for xx in data:
                    if "lat" not in str(xx) and not xx[0] == "":
                        vzd = get_distance(float(lat), float(lon), float(xx[0]), float(xx[1]))
                        if vzd < 0.025:
                            dd += 1
                            n += 1
                            # porovná názvy zastávek  (0 neshodují se, 1 shodují se)
                            if not xx[3] == "":
                                s = difflib.SequenceMatcher(None, xx[3], oficialname)
                                similarity = s.ratio()
                                print(str(n) + ": " + str(vzd) + "---: " + str(lat) + "," + str(lon) + ": OSM name: " +
                                      xx[3] + "-----Official name: " + oficialname + " =" + str(similarity))
                                if similarity < 0.11:
                                    problemovazast.append(x)
                                # else:
                                #     print("kuku")

                            if dd > 1:
                                # v blízkosti jedne zastavky z ofiial seznamu se nachazi více jak jedna zastavvky v OSM
                                print("dd: " + str(dd))
                                problemovazast.append(x)

                        else:
                            if g == 0:
                                chybejicisinglzast = [[] for i in range(4)]
                                chybejicisinglzast[0] = []
                                chybejicisinglzast[0].append(lat)
                                chybejicisinglzast[1] = []
                                chybejicisinglzast[1].append(lon)
                                chybejicisinglzast[2] = []
                                chybejicisinglzast[2].append(ref)
                                chybejicisinglzast[3] = []
                                chybejicisinglzast[3].append(oficialname)

                                chybejicisinglzast_list.append(chybejicisinglzast[:])
                                g = 1
            elif len(index_zast) == 2:

                for ii in index_zast:
                    ind = ii
                    lat = zastavkykraj[ii[0]][0]
                    lon = zastavkykraj[ii[0]][1]
                    oficialname = zastavkykraj[ii[0]][4]
                    ref = zastavkykraj[ii[0]][2]
                    dd = 0
                    for xx in data:
                        if "lat" not in str(xx) and not xx[0] == "":
                            vzd = get_distance(float(lat), float(lon), float(xx[0]), float(xx[1]))
                            if vzd < 0.010:
                                dd += 1
                                n += 1
                                # porovná názvy zastávek a 0 neshodují se, 1 shodují se
                                if not xx[3] == "":
                                    s = difflib.SequenceMatcher(None, xx[3], oficialname)
                                    similarity = s.ratio()
                                    print(str(n) + ": " + str(vzd) + "---: " + str(lat) + "," + str(lon) + ": OSM name: " +
                                          xx[3] + "-----Official name: " + oficialname + " =" + str(similarity))
                                    if similarity < 0.11:
                                        problemovazast.append(x)
                                if dd > 2:
                                    # v blízkosti jedne zastavky z ofiial seznamu se nachazi více jak jedna zastavvky v OSM
                                    print("dd: " + str(dd))
                                    problemovazast.append(x)
                            else:
                                if g == 0:
                                    chybejicisinglzast = [[] for i in range(4)]
                                    chybejicisinglzast[0] = []
                                    chybejicisinglzast[0].append(lat)
                                    chybejicisinglzast[1] = []
                                    chybejicisinglzast[1].append(lon)
                                    chybejicisinglzast[2] = []
                                    chybejicisinglzast[2].append(ref)
                                    chybejicisinglzast[3] = []
                                    chybejicisinglzast[3].append(oficialname)

                                    chybejicisinglzast_list.append(chybejicisinglzast[:])
                                    g = 1

print("konec")
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




