# Popis funkce ZVS
**Zdrojová data**

zdrojová data jsou převzata [Geoportálu Jihočeského kraje](https://geoportal.kraj-jihocesky.gov.cz/portal/mapy/doprava-a-silnicni-hospodarstvi/zastavky-verejne-dopravy). 

**Zastávky veřejné dopravy pro Openstreetmap**

**convertshptocsv.py** - převede data zastávek do z shp formátu do csv.
Vstupní data se berou z adresáře data. Cesta ke vstupnímu souboru je uložena v proměnné shpfile.

Výstupní soubory: 
-  zastavky-JCK-bus.csv
-  zastavky-JCK-vlak.csv
                 
Pozn: při prohlížení dat jsem zjistil, že existují zdvojené zastávky, kdy zastávka má stejnou souřadnic, ale jiné referenční číslo.

**searchst.py** - vytvoří dotaz pro overpass turbo pro autobusové zastávky v JCK *"highway"="bus_stop"*.
Výstupní data obsahují, souřadnice lat, lon a klíče: official_name, name, ref:CIS_JR, ref, bus, public_transport, count, id, local_ref.

Následně se načtou data od JČK, ve kterých se hledají zastávky se stejným ref. Pokud je zastávek se stejným ref více jak 4, uloží se tyto 
do souboru bezdupl_autnadr.csv. Tyto data se dále nezpracovávají, protože jde většinou o nádraží s vícero nástupišti a rozmístění 
nástupišť v reálu je někdy jiné než podle dodaných dat. Nádraží bude třeba doplnit či editovat v OSM ručně, nejlépe se znalostí 
místní lokality.

Následně se porovnávají sobory zastávek od JČK a z OSM. Zde se hledají zastávky, které jsou blíže než 25 metrů.
Pokud má zastávka z OSM vyplněný klíč name či officeial_name porovnává se s oficiálními názvy. Použil jsem metodu [difflib](https://docs.python.org/3/library/difflib.html) s třídou SequenceMatcher. Tato metoda porovnává dva řetězce. Pokud se shodují vrátí hodnotu 1 při úplné neshodě vrátí hodnotu 0. Pokud porovnání názvů vyjde menší, než 0,11 zastávka se uloží do souboru problemovybodosm.csv.

Zastávky v OSM jsou branné jako polohově správné. Pokud se od dat JČK nějakým způsobem významně liší, je třeba polohu zkontrolovat v reálu a poté polohu upravit ručně.
Do souboru bezdupl_josm.csv se ukládají hodnoty klíčů official_name a ref:CIS_JR, local_ref zastávek v OSM, které je potřeba doplnit. Pokud zastávka ty hodnoty v OSM obsahuje a shodují se s těmi, které jsou od JČK. Hodnoty zůstávají prázdné. Tento soubor může být následně použit pro aktualizaci klíčů zastávek pomocí nástroje [Editing OSM Tags](https://community.openstreetmap.org/t/editing-osm-tags-poi-data-in-a-spreadsheet/96843).
Soubor obsahuje tyto prvky: element, id, official_name, ref:CIS_JR, local_ref a souřadnice.
Tento nástroj vygeneruje soubor xml, který lze naimportovat do JOSM.

**Vizualizace**

Zpacovaná data jsou zobrazena na servereru [UMap](https://umap.openstreetmap.fr/cs-cz/map/zastavky-jck_908833#10/48.9405/14.3131).
Barevné body znázorňují jednotlivé zastávky (nástupiště).

Význam barev:
+ Magenta - zastávkay, které v současnosti nejsou v OSM
+ Cyan - zastávky, které jsou v OSM, ale budou jim přiřazeny nové klíče.
+ ČerNá - nástupiště na větších přestupních uzlech (vice jak 4 zastávky se stejnou hodnotou REF)
