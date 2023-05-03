import requests
from math import radians, cos, sin, asin, sqrt
import os
import csv
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
csvfile = 'zastavky-JCK.csv'
seznam_st = []
overpass_url = "http://overpass-api.de/api/interpreter"
overpass_query = """[out:csv(::lat, ::lon, "official_name", name, "ref:CIS_JR", "ref", "bus", "public_transport",
 ::count)]; \n ( \n"""
overpass_end = "\n ); \n out; \n out count; \n"

dotaz = """area[name="Jihočeský kraj"];
node(area)["highway"="bus_stop"];"""
overpass_query = overpass_query + dotaz + overpass_end
print(overpass_query)

response = requests.get(overpass_url, params={'data': overpass_query})
print("encoding :" + response.encoding)
response.encoding = 'UTF-8'
print("encoding :" + response.encoding)
data = [row.split('\t') for row in response.text.split('\n')]
with open('OSMzastavkyJCK.csv', 'w', newline='', encoding="UTF-8") as f:
    writer = csv.writer(f, delimiter=',')
    # writer.writerow(["lat", "lon", "official_name", "name", "ref:CIS_JR", "ref", "bus", "public_transport", "count"])
    writer.writerows(data)
m = sum(1 for line in data)
print(str(m))
for x in data:
    if "lat" not in str(x) and not x[0] == "":
        seznam_st.append(x)
        print(str(x))
if os.path.exists(csvfile):
    csvfile = open(csvfile, 'r')
    csv_reader = csv.reader(csvfile, delimiter=';')
pocet = 0
for x in csv_reader:
    if "lat" not in x:
        for y in data:
            if "@lat" not in y and not y[0] == "":
                vzd = get_distance(float(x[0]), float(x[1]), float(y[0]), float(y[1]))

                if vzd < 0.050:
                    s = difflib.SequenceMatcher(None, y[3], x[4])
                    similarity = s.ratio()
                    print(f"The similarity between the two strings is {similarity:.2f}")
                    if similarity > 0.5:
                        print(str(y) + ": " + str(vzd))
                        pocet += 1
print("pocet zastávek v OSM: " + str(pocet))



