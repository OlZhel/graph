from   lxml import etree
import numpy
import json
import math

tree  = etree.parse(open('map.osm', 'rb'))
query_node  = etree.XPath("/osm/node")
query_ways  = etree.XPath(
"""
/osm/way[./tag/@k = "highway" and 
( 
  ./tag/@v = "motorway"  or ./tag/@v = "motorway_link"  or
  ./tag/@v = "trunk"     or ./tag/@v = "trunk_link"     or
  ./tag/@v = "primary"   or ./tag/@v = "primary_link"   or
  ./tag/@v = "secondary" or ./tag/@v = "secondary_link" or
  ./tag/@v = "tertiary"  or ./tag/@v = "tertiary_link"  or
  ./tag/@v = "unclassified"  or 
  ./tag/@v = "residential"   or
  ./tag/@v = "service"       or
  ./tag/@v = "living_street" or
  ./tag/@v = "road"
)]
""")

points_all = query_node(tree)
ways_xml = query_ways(tree)

id_to_index = dict()
i = 0
for p in points_all:
    ref_id = p.attrib['id']
    id_to_index[ref_id] = i
    i += 1

points_road = list()
AdjDict     = dict()
get_np = etree.XPath("./nd")
i = 0
for way in ways_xml:
    i += 1
    print(f"Обработано путей {i} из {len(ways_xml)}")

    nps = get_np(way)
    p_ind_old = None
    p_ind = 0
    for np in nps:
        np_ref = np.attrib['ref']
        np_ind = id_to_index[np_ref]
        if points_all[np_ind] not in points_road:
            points_road.append(points_all[np_ind])
            p_ind = len(points_road)-1   
        else:
            p_ind = points_road.index(points_all[np_ind])

        if p_ind_old is not None:
            if p_ind     not in AdjDict.keys(): AdjDict[p_ind]     = set()
            if p_ind_old not in AdjDict.keys(): AdjDict[p_ind_old] = set()
            AdjDict[p_ind].add(p_ind_old)
            AdjDict[p_ind_old].add(p_ind)
        p_ind_old = p_ind

csv_out = open('./result/AdjMatrix.csv', 'w')

N = len(points_road)

pattern_str = ""
for i in range(0, N):
    pattern_str += "0,"
pattern_str += "\n"

for i in range(0, N):
    if i % 100 == 0: print(f"Вывод строк матрицы {i} из {N}")
    line = pattern_str
    for j in AdjDict[i]:
        line = line[0:2*j] + "1," + line[2*j+2:]
    csv_out.write(line)

csv_out.close()

AdjList = list()
for (k,v) in AdjDict.items():
    item = (k, list(v))
    AdjList.append(item)

AdjList_Serialized = json.dumps(AdjList, indent=4)
AdjListFile = open("./result/AdjList.json", "w")
AdjListFile.write(AdjList_Serialized)
AdjListFile.close()

bounds = tree.xpath("/osm/bounds")[0]
lon_min = float(bounds.attrib["minlon"])
lon_max = float(bounds.attrib["maxlon"])
lat_min = float(bounds.attrib["minlat"])
lat_max = float(bounds.attrib["maxlat"])

imgH = 1080
coef = imgH/(lat_max-lat_min)
x_mult = 0.7
imgW = int((lon_max-lon_min)*coef*x_mult)

mapSvg = open("./result/map.svg", "w")
mapSvg.write(
f"""<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg version = "1.1"
     baseProfile="full"
     xmlns = "http://www.w3.org/2000/svg" 
     xmlns:xlink = "http://www.w3.org/1999/xlink"
     xmlns:ev = "http://www.w3.org/2001/xml-events"
     height = "{imgH}px"  width = "{imgW}px">
        <g stroke="black" stroke-width="1px">
 """
)
i = 0
for way in ways_xml:
    i += 1
    print(f"Формирование svg {i} из {len(ways_xml)}")
    nps = get_np(way)
    x1 = None
    y1 = None
    for np in nps:
        np_ref  = np.attrib['ref']
        node_id = id_to_index[np_ref]
        node = points_all[node_id]
        lon = float(node.attrib["lon"])
        lat = float(node.attrib["lat"])
        x2 = int((lon-lon_min)*coef*x_mult)
        y2 = int((lat-lat_min)*coef)
        if x1 is None or y1 is None:
            x1 = x2
            y1 = y2
            continue
        svgLine = f"\t\t\t<line x1=\"{x1}\" y1=\"{y1}\" x2=\"{x2}\" y2=\"{y2}\"/>\n"
        mapSvg.write(svgLine)
        x1 = x2
        y1 = y2

mapSvg.write(
"""
        </g>
</svg>
"""
)       
mapSvg.close()
print("Готово!")
