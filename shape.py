import json
import requests

with open('cities.geojson') as f:
    geojson = json.load(f)


glyphs = set({})

for feature in geojson['features']:
    name_ne = feature['properties']['name:ne']
    r = requests.get('http://localhost:3000/shape?text=' + name_ne)
    shaped = json.loads(r.text)

    feature['properties']['name_ne_glyphs'] = []
    # only do the first word
    for glyph in shaped[0]['glyphs']:
        item = (glyph['index'], glyph['x_offset'], glyph['y_offset'], glyph['x_advance'], glyph['y_advance'])
        glyphs.add(item)
        feature['properties']['name_ne_glyphs'].append(item)
    

mapping_index = []
mapping_x_offset = []
mapping_y_offset = []
mapping_x_advance = []

glyphs = list(glyphs)

for glyph in glyphs:
    mapping_index.append(glyph[0])
    mapping_x_offset.append(glyph[1])
    mapping_y_offset.append(glyph[2])
    mapping_x_advance.append(glyph[3])

first_indexed_codepoint = 58000
last_indexed_codepoint = first_indexed_codepoint + len(mapping_index) - 1

mapping = f'''
const int first_indexed_codepoint = {first_indexed_codepoint};
const int last_indexed_codepoint = {last_indexed_codepoint};
const std::vector<int> mapping_index = {{{", ".join([str(x) for x in mapping_index])}}};
const std::vector<int> mapping_x_offset = {{{", ".join([str(x) for x in mapping_x_offset])}}};
const std::vector<int> mapping_y_offset = {{{", ".join([str(x) for x in mapping_y_offset])}}};
const std::vector<int> mapping_x_advance = {{{", ".join([str(x) for x in mapping_x_advance])}}};
'''


print(mapping)

glyph_to_codepoint = {}
for i, glyph in enumerate(glyphs):
    glyph_to_codepoint[glyph] = i + first_indexed_codepoint


for feature in geojson['features']:
    feature['properties']['name_ne_encoded'] = ''
    for glyph in feature['properties']['name_ne_glyphs']:
        feature['properties']['name_ne_encoded'] += chr(glyph_to_codepoint[glyph])

with open('cities_encoded.geojson', 'w') as f:
    json.dump(geojson, f)
