import json
from sys import argv

from database import Database

SQL_DAT_FILE = 'scorelib.dat'

db = Database(SQL_DAT_FILE)
print_id = int(argv[1])
composers = db.get_composers_by_print_id(print_id)
print(json.dumps(composers, indent=4, sort_keys=False, ensure_ascii=False))
db.close()
