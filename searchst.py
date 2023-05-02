import requests

  # area[name="Jihočeský kraj"];
  # node(area)["highway"="bus_stop"];
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
m = sum(1 for line in data)
print(str(m))
for x in data:
    if "lat" not in str(x) and not x[0] == "":
        seznam_st.append(x)
        print(str(x))