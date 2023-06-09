import requests
from math import radians, cos, sin, asin, sqrt
import os
import csv
from itertools import count # izip for maximum efficiency
from copy import deepcopy
import difflib
from termcolor import colored
from collections import Counter
import pandas as pd
import numpy as np
import itertools
import re

bodydoplnkey = []
edittag = [[] for i in range(4)]
autnadr = []
def get_distance(lat_1, lng_1, lat_2, lng_2):  # vypocet vzdalenosti bodu
    lng_1, lat_1, lng_2, lat_2 = map(radians, [lng_1, lat_1, lng_2, lat_2])  # prevede uhly na radiany
    d_lat = lat_2 - lat_1
    d_lng = lng_2 - lng_1
    a = sin(d_lat / 2) ** 2 + cos(lat_1) * cos(lat_2) * sin(d_lng / 2) ** 2
    c = 2 * asin(sqrt(a))
    r = 6371
    return c * r


problemovybodosm = []


def get_keys(bod_od, bod_osm, porov, dstan):
    # bod_osm: 0)::lat, 1)::lon, 2)"official_name", 3)name, 4)"ref:CIS_JR", 5)"ref", 6)"bus", 7)"public_transport",8)::count, 9)::id) 10 local_ref
    # bod_od: 0)lat	1)lon	2)ref	3)okres	4)name	5)stanoviste	6)typ
    # https://output.jsbin.com/xewohok
    # element;id;official_name;ref:CIS_JR;bus
    i = 2
    jm = ""
    refe = ""
    locref = ""
    pubtrans = ""
    bus = ""
    for x in bod_osm[2:]:
        # official name
        if i == 2 and not x == "":
            if not x == bod_od[4] and porov < 0.11:
                # name
                problemovybodosm.append(bod_osm)
                posl = len(problemovybodosm)-1
                problemovybodosm.insert(posl, "2")
            elif x == bod_od[4]:
                jm = ""
            # else:
            #     jm = bod_od[4]
        elif i == 2 and x == "":
            jm = bod_od[4]
        # name
        if i == 3 and not x == "":
            # if "Český Krumlov,,žel.st." in x:
            #     print("Český Krumlov,,žel.st.")
            # if "Český Krumlov, Železniční stanice" in x:
            #     print("Český Krumlov, Železniční stanice")
            # bod_od: 0)lat	1)lon	2)ref	3)okres	4)name	5)stanoviste	6)typ
            # if (not x == bod_od[4] and porov < 0.11) or (not x == bod_od[5]):
            #     problemovybodosm.append(bod_osm)
            #     posl = len(problemovybodosm) - 1
            #     problemovybodosm[posl].append("3")
            if porov > 0.11 and not porov == 1:
                jm = bod_od[4]
            elif x == bod_od[5]:
                if not bod_osm[2].replace('"', "") == bod_od[4]:
                    jm = bod_od[4]
                else:
                    jm = ""

            if porov == 1:
                jm = ""
        elif i == 3 and x == "" and bod_od[5] == "":
            if not bod_osm[2].replace('"', "") == bod_od[4]:
                jm = bod_od[4]
            else:
                jm = ""


        # elif i == 3 and x == "" and not bod_od[5] == "":
        #     # zapise do name stannoviste
        #     locref = bod_od[5]

        # ref:CIS_JR
        if i == 4 and not x == "":
            if not x == bod_od[2]:
                problemovybodosm.append(bod_osm)
                posl = len(problemovybodosm) - 1
                problemovybodosm[posl].append("4")
            else:
                refe = ""
        elif i == 4 and x == "":
            refe = bod_od[2]

        # bus
        if i == 6 and x == "":
            bus = "yes"

        # public_transport
        if i == 7 and x == "":
            pubtrans = "platform"

        # stanoviste local_ref
        if i == 10 and not x == "":
            if not x == bod_od[5]:
                problemovybodosm.append(bod_osm)
                posl = len(problemovybodosm) - 1
                problemovybodosm[posl].append("10")
            else:
                # locref = bod_od[5]
                locref = ""
        elif i == 10 and x == "":
            # locref = bod_od[5]
            locref = dstan
        i += 1

        if not jm == "":
            print("kuku")

        # edittag = "node;" + bod_osm[9] + ";" + jm + ";" + refe
        # edittag[0] = "node"
        # edittag[1] = bod_osm[9]
        # edittag[2] = jm
        # edittag[3] = refe
    # edittag = [[] for i in range(4)]
    edittag = ['']*9
    edittag[0] = "node"
    # edittag[1].append(bod_osm[9])
    edittag[1] = bod_osm[9]
    # edittag[2].append(jm)
    edittag[2] = jm
    # edittag[3].append(refe)
    edittag[3] = refe
    edittag[4] = locref
    edittag[5] = bus
    edittag[6] = pubtrans
    edittag[7] = bod_osm[0]
    edittag[8] = bod_osm[1]

    return edittag


def deduplicate(a, clen):
    """
    Clears Empty ip address records from list
    removes duplicates by
    :param a:
    :return:
    """

    source_ips = []
    new_list = []
    for i in range(len(a)):
        if a[i][clen] != None:
            if a[i][clen] not in source_ips and clen == 0 and a[i][2] not in source_ips:
                source_ips.append(a[i][clen])
                new_list.append(a[i])
            elif a[i][clen] not in source_ips and clen == 1:
                source_ips.append(a[i][clen])
                new_list.append(a[i])
    return new_list


def tridit(dlat, dlon, limvzd, dx, dn, dg, pocetz, ddata, dstan, doficialname, dref):
    ddd = 0
    ddn = dn
    pruchod = 1
    # prochází data z OSM
    # bod_osm: 0)::lat, 1)::lon, 2)"official_name", 3)name, 4)"ref:CIS_JR", 5)"ref", 6)"bus", 7)"public_transport",8)::count, 9)::id) 10)local_ref
    h = 0
    vzdalenost = []

    if pocetz <= 4:
        for xx in ddata:
            h += 1
            # if not xx == ['']:
                # if xx[3] == "Hvížďalka":
                #     print("Hvížďalka7")
                # if xx[9] == 9729270869:
                #     print("Hvížďalka6")
                # if str(xx[9]) == "6004769198":
                #     print("Hvížďalka5")
            if "@lat" not in str(xx) and not xx[0] == "":
                vzd = get_distance(float(dlat), float(dlon), float(xx[0]), float(xx[1]))
                vzdalenost.append(vzd)
                # if "Český Krumlov,,žel.st." in xx[3]:
                #     print("Hvížďalka2")
                # if "Český Krumlov, Železniční stanice" in xx[3]:
                #     print("Hvížďalka2")
                # if str(xx[9]) == "6004769198":
                #     print("Český Krumlov, Železniční stanice2 - " + str(vzd))
                if vzd < limvzd:
                    # if "Český Krumlov,,žel.st." in xx[3] or "Český Krumlov, Železniční stanice" in xx[3]: # Český Krumlov, Železniční stanice
                    #     print("Český Krumlov,,žel.st.")
                    # if str(xx[9]) == "6004769198":
                    #     print("Český Krumlov, Železniční stanice2")
                    # if str(xx[9]) == "9729270869":
                    #     print("Hvížďalka4")
                    ddd += 1
                    ddn += 1
                    # porovná názvy zastávek  (0 neshodují se, 1 shodují se)
                    # name 3 a official name 2
                    # if not xx[3] == "" or not xx[2] == "":
                    if not xx[2] == "" or not xx[3] == "":
                        s = difflib.SequenceMatcher(None, xx[2].replace('"',""), doficialname)
                        similarity = s.ratio()
                        if similarity < 0.11:
                            s = difflib.SequenceMatcher(None, xx[3], doficialname)
                            similarity = s.ratio()
                            if similarity < 0.11:
                                s = difflib.SequenceMatcher(None, xx[3], dstan)
                                similarity = s.ratio()
                                if similarity < 0.11:
                                    problemovazast.append(dx)
                                    posl = len(problemovazast) - 1
                                    problemovazast[posl].append("sim")
                                else:
                                    radek = get_keys(dx, xx, float(similarity), dstan)
                                    josm.append(radek)
                            # print(str(ddn) + ": " + str(vzd) + "---: " + str(dlat) + "," + str(dlon) + " (" + str(xx[0]) + "," + str(xx[1]) + ")" + ": OSM name: " +
                            #   xx[3] + "-----Official name: " + doficialname + " =" + str(similarity))
                            else:
                                radek = get_keys(dx, xx, float(similarity), dstan)
                                josm.append(radek)
                        # elif similarity < 0.11:
                        #      problemovazast.append(dx)
                        else:
                            print(str(ddn) + ": " + str(vzd) + "---: " + str(dlat) + "," + str(dlon) + " (" + str(
                                xx[0]) + "," + str(xx[1]) + ")" + ": OSM name: " +
                                  xx[3] + "-----Official name: " + doficialname + " =" + str(similarity))
                            radek = get_keys(dx, xx, float(similarity), dstan)
                            josm.append(radek)

                        #   print("kuku")
                    else:
                        # print(str(ddn) + ": " + str(vzd) + "---: " + str(dlat) + "," + str(dlon) + " (" + str(
                        #     xx[0]) + "," + str(xx[1]) + ")" + ": OSM name: " +
                        #       xx[3] + "-----Official name: " + doficialname + " =" + str(similarity))
                        radek = get_keys(dx, xx, 2, dstan)
                        josm.append(radek)

                    if ddd > pocetz:
                        # v blízkosti jedne zastavky z ofiial seznamu se nachazi více jak jedna zastavvky v OSM
                        print(colored("dd: " + str(ddd) + ": " + str(xx[0]) + "," + str(xx[1]), "red"))
                        problemovazast.append(dx)
                        posl = len(problemovazast) - 1
                        problemovazast[posl].append("ddd = " + str(ddd) + ", pocet zast: " + str(pocetz))


            # else:
                # zapíše zastávky z oficiálího seznamu, které nejsou v OSM
                # if pruchod == 1:
    minimum = min(vzdalenost)
    if minimum > limvzd:
        # chybejicisinglzast = [[] for i in range(4)]
        chybejicisinglzast = ['']*8
        chybejicisinglzast[0] = []
        # chybejicisinglzast[0].append(lat)
        chybejicisinglzast[0] = dlat
        chybejicisinglzast[1] = []
        # chybejicisinglzast[1].append(lon)
        chybejicisinglzast[1] = dlon
        chybejicisinglzast[2] = []
        # chybejicisinglzast[2].append(ref)
        chybejicisinglzast[2] = dref
        chybejicisinglzast[3] = []
        # chybejicisinglzast[3].append(oficialname)
        chybejicisinglzast[3] = doficialname
        chybejicisinglzast[4] = []
        chybejicisinglzast[4] = dstan
        chybejicisinglzast[5] = "yes"
        chybejicisinglzast[6] = "platform"
        chybejicisinglzast[7] = []
        jmenoz = ''.join(ch for ch, _ in itertools.groupby(doficialname))
        jmenoz = jmenoz.replace(",", ", ")
        jmenoz = jmenoz.replace(".", ". ")
        # jmenoz = re.sub(r'. $', '.', jmenoz, 1)
        ttt = jmenoz.rsplit(". ", 1)
        jmenoz = ".".join(ttt)
        jmenoz = jmenoz.replace("rozc.1", "rozc. 1")
        chybejicisinglzast[7] = jmenoz
        chybejicisinglzast_list.append(chybejicisinglzast[:])


    return ddn


def tisk_csv(file, name, hlavicka):
    with open(name + ".csv", 'w', newline='', encoding="utf8") as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow(hlavicka)
        writer.writerows(file)

    return

# def removedup(duplicate):
#     final_list = []
#     found = set([])
#     for num in duplicate:
#         lst = []
#         for element in num:
#             if element not in found:
#                 found.add(element)
#                 lst.append(element)
#         final_list.append(lst)
#     return final_list
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
 ::count, ::id, "local_ref")]; \n ( \n"""
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
tisk = 0
tisky = 0
tiskb = 0
tiskg = 0
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
        stan = ""
        lat = ""
        lon = ""
        ref = ""
        oficialname = ""
        g = 0
        tisk = 1
        # print("iterace:" + str(iterace))
        iterace += 1
        if ("lat" or "ref") not in x:
            ref = x[2]
            # print('ref: ' + str(ref))
            index_zast = [(i, element.index(ref)) for i, element in enumerate(zastavkykraj) if ref in element]
            # print('index_zast: ' + str(index_zast))
            if len(index_zast) == 1:
                if tisk == 1 and tiskb == 0:
                    print(colored("Zastávka s jedinečnou ref hodnotou. Ref: " + str(ref), "blue"))
                    tisk = 0
                    tiskb = 1
                    tisky = 0
                    tiskg = 0
                ind = index_zast[0][0]
                lat = zastavkykraj[index_zast[0][0]][0]
                lon = zastavkykraj[index_zast[0][0]][1]
                oficialname = zastavkykraj[index_zast[0][0]][4]
                ref = zastavkykraj[index_zast[0][0]][2]
                stan = zastavkykraj[ii[0]][5]
                n = tridit(lat, lon, 0.025, x, n, g, 1, data, stan, oficialname, ref)

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
                if tisk == 1 and tisky == 0:
                    print(colored("Dvě zastávky se stejným ref. Ref: " + str(ref), "yellow"))
                    tisk = 0
                    tiskb = 0
                    tisky = 1
                    tiskg = 0
                for ii in index_zast:
                    ind = ii
                    lat = zastavkykraj[ii[0]][0]
                    lon = zastavkykraj[ii[0]][1]
                    oficialname = zastavkykraj[ii[0]][4]
                    ref = zastavkykraj[ii[0]][2]
                    stan = zastavkykraj[ii[0]][5]
                    n = tridit(lat, lon, 0.025, x, n, g, 2, data, stan, oficialname, ref)
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
            elif 2 < len(index_zast) <= 4:
                if tisk == 1 and tiskg == 0:
                    print(colored(str(len(index_zast)) + " zastávky se stejným ref. Ref: " + str(ref), "green"))
                    tisk = 0
                    tiskb = 0
                    tisky = 0
                    tiskg = 1
                for ii in index_zast:
                        ind = ii
                        lat = zastavkykraj[ii[0]][0]
                        lon = zastavkykraj[ii[0]][1]
                        oficialname = zastavkykraj[ii[0]][4]
                        ref = zastavkykraj[ii[0]][2]
                        stan = zastavkykraj[ii[0]][5]
                        n = tridit(lat, lon, 0.015, x, n, g, len(index_zast), data, stan, oficialname, ref)
            elif len(index_zast) > 4:
                autnadr.append(x)
# res_chybejicisinglzast_list = list(set(chybejicisinglzast_list))
# kuku = removedup(chybejicisinglzast_list)
# counts = Counter(row[0] for row in chybejicisinglzast_list)
# chybejicisinglzast_list = [row for row in chybejicisinglzast_list if counts[row[0]] == 1]
# df = pd.DataFrame(chybejicisinglzast_list, columns=['lat', 'lon', 'ref', 'okres', "name", 'stanoviste', 'typ'])
# df.drop_duplicates()

# v základním seznamu existují duplicitnízastávky podle souřadnic cca 38, nutno zohlednit i ref
bezdupl_list = deduplicate(chybejicisinglzast_list, 0)
bezdupl_josm = deduplicate(josm, 1)
bezdupl_problemovazast = deduplicate(problemovazast, 0)
bezdupl_problemovybodosm = deduplicate(problemovybodosm, 0)
bezdupl_autnadr = deduplicate(autnadr, 0)

# [item for item in bezdupl_josm if not item == ""]
# vztvoří seznam bez prázných řádku
u = 0
josmdataitem = []
for x in bezdupl_josm:
        prazdne = 1
        for y in range(2, 7):
                # prazdne = 1
                if not x[y] == "":
                        prazdne = 0
                        # print(str(x[y]))

        if prazdne == 0:
                josmdataitem.append(x)
                u += 1


print("Total items in original chybejicisinglzast_list :", len(chybejicisinglzast_list))
print("Total items after deduplication bezdupl_list:", len(bezdupl_list))
print("Total items in original josm :", len(josm))
print("Total items after deduplication bezdupl_josm:", len(bezdupl_josm))
print("Total items in original autnadr :", len(autnadr))
print("Total items after deduplication bezdupl_autnadr:", len(bezdupl_autnadr))
print("Ahoj")
tisk_csv(bezdupl_list, "bezdupl_chybejicisinglzast_list", ["lat", "lon", "ref:CIS_JR", "official_name", "local_ref", "bus", "public_transport", "name"])
tisk_csv(bezdupl_josm, "bezdupl_josm", ["element", "id", "official_name", "ref:CIS_JR", "local_ref", "bus", "public_transport", "lat", "lon"])
tisk_csv(josmdataitem, "josmdataitem", ["element", "id", "official_name", "ref:CIS_JR", "local_ref", "bus", "public_transport", "lat", "lon"])
tisk_csv(bezdupl_problemovazast, "problemovazast", ["lat", "lon", "ref", "okres", "name", "stanoviste", "typ"])
# bod_osm: 0)::lat, 1)::lon, 2)"official_name", 3)name, 4)"ref:CIS_JR", 5)"ref", 6)"bus", 7)"public_transport",8)::count, 9)::id) 10)local_ref
tisk_csv(bezdupl_problemovybodosm, "problemovybodosm", ["lat", "lon", "official_name", "name","ref:CIS_JR","ref",
                                                        "bus", "public_transport", "count", "id", "local_ref"])
tisk_csv(bezdupl_autnadr, "bezdupl_autnadr", ["lat", "lon", "ref:CIS_JR", "district", "official_name", "local_ref", "typ"])
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




