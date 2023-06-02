# Popis funkce ZVS
**Zastávky veřejné dopravy pro Openstreetmap**

**convertshptocsv.py** - převede data zastávek do z shp formátu do csv.
Vstupní data se berou z adresáře data. Cesta ke vstupnímu souboru je uložena v proměnné shpfile.

Výstupní soubory: 
-  zastavky-JCK-bus.csv
-  zastavky-JCK-vlak.csv
                 
Pozn: při prohlížení dat jsem zjistil, že exitují zdvojené zastávky, kdy zastávka má stejnou souřadnic, ale jiné referenční číslo.

**searchst.py** - vytvoří dotaz pro overpass turbo pro autobusové zastávaky v JCK *"highway"="bus_stop"*.
Výstupní data obsahují, souřadnice lat, lon a klíče: official_name, name, ref:CIS_JR, ref, bus, public_transport, count, id, local_ref.

Následně se načtou data od JČK, ve kterých se hledají zastávky se stejným ref. Pokud je zastávek se stejným ref více jak 4, uloží se tyto 
do souboru bezdupl_autnadr.csv. Tyto data se dále nezpracovávají, protože jde vetšinou o nádraží s vícero nástupišti a rozmístění 
nástupišť v reálu je někdy jiné než podle dodaných dat. Nádraží bude třeba doplnit či editovat v OSM ručně, nejlépe se znalostí 
místní lokality.

