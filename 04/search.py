import json
from sys import argv
from database import Database

SQL_DAT_FILE = 'scorelib.dat'
db = Database(SQL_DAT_FILE)

name_substring = argv[1]
composers = db.get_composers_by_name(name_substring)

c_results = {}

for c in composers:
    p_results = []
    prints = db.get_prints_by_composer_id(c['id'])
    for p, e_id, s_id in prints:
        composers = db.get_composers_by_score_id(s_id)
        editors = db.get_editors_by_edition_id(e_id)
        voices = db.get_voices_by_score_id(s_id)
        p['Composer'] = composers
        p['Editor'] = editors
        p['Voices'] = voices
        p_results.append(p)
    c_results[c['name']] = p_results

print(json.dumps(c_results, indent=4, sort_keys=False, ensure_ascii=False))

db.close()

