import requests
from math import radians, cos, sin, asin, sqrt
import os
import csv
from itertools import count # izip for maximum efficiency
from copy import deepcopy
import difflib

bodydoplnkey = []
def get_distance(lat_1, lng_1, lat_2, lng_2):  # vypocet vzdalenosti bodu
    lng_1, lat_1, lng_2, lat_2 = map(radians, [lng_1, lat_1, lng_2, lat_2])  # prevede uhly na radiany
    d_lat = lat_2 - lat_1
    d_lng = lng_2 - lng_1
    a = sin(d_lat / 2) ** 2 + cos(lat_1) * cos(lat_2) * sin(d_lng / 2) ** 2
    c = 2 * asin(sqrt(a))
    r = 6371
    return c * r


problemovybodosm = []


def get_keys(bod_od, bod_osm, porov):
    # bod_osm: 0)::lat, 1)::lon, 2)"official_name", 3)name, 4)"ref:CIS_JR", 5)"ref", 6)"bus", 7)"public_transport",8)::count, 9)::id)
    # bod_od: 0)lat	1)lon	2)ref	3)okres	4)name	5)stanoviste	6)typ
    # https://output.jsbin.com/xewohok
    # element;id;official_name;ref:CIS_JR;bus
    i = 2
    jm = ""
    refe = ""
    for x in bod_osm[2:]:
        # official name
        if i == 2 and not x == "":
            if not x == bod_od[4] and porov < 0.6:
                problemovybodosm.append(x)
            else:
                jm = bod_od[4]
        elif i == 2 and x == "":
            jm = bod_od[4]
        # ref
        if i == 4 and not x == "":
            if not x == bod_od[2]:
                problemovybodosm.append(x)
            else:
                refe = ""
        elif i == 4 and x == "":
            refe = bod_od[2]

        i += 1

        edittag = "node;" + bod_osm[9] + ";" + jm + ";" + refe
    return edittag


def tridit(dlat, dlon, limvzd, dx, dn, dg, pocetz, ddata):
    ddd = 0
    ddn = dn
    for xx in ddata:
        if "lat" not in str(xx) and not xx[0] == "":
            vzd = get_distance(float(dlat), float(dlon), float(xx[0]), float(xx[1]))
            if vzd < limvzd:
                ddd += 1
                ddn += 1
                # porovná názvy zastávek  (0 neshodují se, 1 shodují se)
                if not xx[3] == "" or not xx[2] == "":
                    s = difflib.SequenceMatcher(None, xx[3], oficialname)
                    similarity = s.ratio()
                    if similarity < 0.6 and not xx[2] == "":
                        s = difflib.SequenceMatcher(None, xx[2], oficialname)
                        similarity = s.ratio()

                    print(str(ddn) + ": " + str(vzd) + "---: " + str(dlat) + "," + str(dlon) + ": OSM name: " +
                          xx[3] + "-----Official name: " + oficialname + " =" + str(similarity))
                    if similarity < 0.11:
                        problemovazast.append(dx)
                    # else:
                    #     print("kuku")
                else:
                    similarity = 0

                if ddd > pocetz:
                    # v blízkosti jedne zastavky z ofiial seznamu se nachazi více jak jedna zastavvky v OSM
                    print("dd: " + str(ddd))
                    problemovazast.append(dx)
                radek = get_keys(dx, xx, float(similarity))
                josm.append(radek)

            else:
                # zapíše zastávky z oficiálího seznamu, které nejsou v OSM
                if dg == 0:
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
                    dg = 1
    return ddn


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
josm = []

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
                n = tridit(lat, lon, 0.025, x, n, g, 1, data)

                # dd = 0
                # for xx in data:
                #
                #     if "lat" not in str(xx) and not xx[0] == "":
                #         vzd = get_distance(float(lat), float(lon), float(xx[0]), float(xx[1]))
                #         if vzd < 0.025:
                #             dd += 1
                #             n += 1
                #             # porovná názvy zastávek  (0 neshodují se, 1 shodují se)
                #             if not xx[3] == "" or not xx[2] == "":
                #                 s = difflib.SequenceMatcher(None, xx[3], oficialname)
                #                 similarity = s.ratio()
                #                 if similarity < 0.6 and not xx[2] == "":
                #                     s = difflib.SequenceMatcher(None, xx[2], oficialname)
                #                     similarity = s.ratio()
                #
                #                 print(str(n) + ": " + str(vzd) + "---: " + str(lat) + "," + str(lon) + ": OSM name: " +
                #                       xx[3] + "-----Official name: " + oficialname + " =" + str(similarity))
                #                 if similarity < 0.11:
                #                     problemovazast.append(x)
                #                 # else:
                #                 #     print("kuku")
                #             else:
                #                 similarity = 0
                #
                #             if dd > 1:
                #                 # v blízkosti jedne zastavky z ofiial seznamu se nachazi více jak jedna zastavvky v OSM
                #                 print("dd: " + str(dd))
                #                 problemovazast.append(x)
                #             radek = get_keys(x, xx, float(similarity))
                #             josm.append(radek)
                #
                #         else:
                #             # zapíše zastávky z oficiálího seznamu, které nejsou v OSM
                #             if g == 0:
                #                 chybejicisinglzast = [[] for i in range(4)]
                #                 chybejicisinglzast[0] = []
                #                 chybejicisinglzast[0].append(lat)
                #                 chybejicisinglzast[1] = []
                #                 chybejicisinglzast[1].append(lon)
                #                 chybejicisinglzast[2] = []
                #                 chybejicisinglzast[2].append(ref)
                #                 chybejicisinglzast[3] = []
                #                 chybejicisinglzast[3].append(oficialname)
                #
                #                 chybejicisinglzast_list.append(chybejicisinglzast[:])
                #                 g = 1
                    # dlat, dlon, limvzd, dx, dxx, ddd, dn
            elif len(index_zast) == 2:

                for ii in index_zast:
                    ind = ii
                    lat = zastavkykraj[ii[0]][0]
                    lon = zastavkykraj[ii[0]][1]
                    oficialname = zastavkykraj[ii[0]][4]
                    ref = zastavkykraj[ii[0]][2]
                    n = tridit(lat, lon, 0.010, x, n, g, 2, data)
                    # dd = 0
                    # for xx in data:
                    #
                    #     if "lat" not in str(xx) and not xx[0] == "":
                    #         vzd = get_distance(float(lat), float(lon), float(xx[0]), float(xx[1]))
                    #         if vzd < 0.010:
                    #             dd += 1
                    #             n += 1
                    #             # porovná názvy zastávek a 0 neshodují se, 1 shodují se
                    #             if not xx[3] == '' or not xx[2] == "":
                    #                 s = difflib.SequenceMatcher(None, xx[3], oficialname)
                    #                 similarity = s.ratio()
                    #                 if similarity < 0.6 and not xx[2] == "":
                    #                     s = difflib.SequenceMatcher(None, xx[2], oficialname)
                    #                     similarity = s.ratio()
                    #                 print(str(n) + ": " + str(vzd) + "---: " + str(lat) + "," + str(lon) + ": OSM name: " +
                    #                       xx[3] + "-----Official name: " + oficialname + " =" + str(similarity))
                    #                 if similarity < 0.11:
                    #                     problemovazast.append(x)
                    #             else:
                    #                 similarity = 0
                    #
                    #             if dd > 2:
                    #                 # v blízkosti jedne zastavky z ofiial seznamu se nachazi více jak dve zastavvky v OSM
                    #                 print("dd: " + str(dd))
                    #                 problemovazast.append(x)
                    #             radek = get_keys(x, xx, float(similarity))
                    #             josm.append(radek)
                    #         else:
                    #             if g == 0:
                    #                 chybejicisinglzast = [[] for i in range(4)]
                    #                 chybejicisinglzast[0] = []
                    #                 chybejicisinglzast[0].append(lat)
                    #                 chybejicisinglzast[1] = []
                    #                 chybejicisinglzast[1].append(lon)
                    #                 chybejicisinglzast[2] = []
                    #                 chybejicisinglzast[2].append(ref)
                    #                 chybejicisinglzast[3] = []
                    #                 chybejicisinglzast[3].append(oficialname)
                    #
                    #                 chybejicisinglzast_list.append(chybejicisinglzast[:])
                    #                 g = 1

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




