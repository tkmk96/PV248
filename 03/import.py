from sys import argv
import os
import sqlite3

from scorelib import load
SQL_SCHEME_FILE = 'scorelib.sql'


def db_connect(file_path):
    connection = sqlite3.connect(file_path)
    cursor = connection.cursor()
    return connection, cursor


class VoiceEntity:
    def __init__(self, id, number, name, range):
        self.id = id
        self.number = number
        self.name = name
        self.range = range


class EditionEntity:
    def __init__(self, id, name, score_id):
        self.id = id
        self.name = name
        self.score_id = score_id


class CompositionEntity:
    def __init__(self, id, name, genre, key, incipit, year):
        self.id = id
        self.name = name
        self.genre = genre
        self.key = key
        self.incipit = incipit
        self.year = year


class Database:
    def __init__(self, dat_file, init_db_file=None):
        self.connection, self.cursor = db_connect(dat_file)

        if init_db_file is not None:
            self.init_from_script(init_db_file)

    def init_from_script(self, script_file):
        with open(script_file, 'r') as file:
            script = file.read()
            self.cursor.executescript(script)
            self.connection.commit()

    def close(self):
        self.connection.commit()
        self.connection.close()

    def store_print(self, print_id, partiture, edition_id):
        query = "INSERT INTO print(id, partiture, edition) VALUES (?, ?, ?)"
        params = (print_id, partiture, edition_id)
        self.cursor.execute(query, params)
        return self.cursor.lastrowid

    def store_edition(self, score_id, name):
        query = "INSERT INTO edition(score, name, year) VALUES (?, ?, NULL )"
        params = (score_id, name)
        self.cursor.execute(query, params)
        return self.cursor.lastrowid

    def load_edition(self, edition_id):
        query = "SELECT id, name, score FROM edition WHERE id=?"
        self.cursor.execute(query, (edition_id,))
        row = self.cursor.fetchone()
        return EditionEntity(row[0], row[1], row[2]) if row else None

    def store_edition_author(self, edition_id, editor_id):
        query = "INSERT INTO edition_author(edition, editor) VALUES (?, ?)"
        params = (edition_id, editor_id)
        self.cursor.execute(query, params)
        return self.cursor.lastrowid

    def load_edition_author_ids(self, edition_id):
        query = "SELECT editor FROM edition_author WHERE edition=?"
        self.cursor.execute(query, (edition_id,))
        ids = []
        for row in self.cursor.fetchall():
            ids.append(row[0])
        return ids

    def store_score(self, score):
        query = "INSERT INTO score(name, genre, key, incipit, year) VALUES (?, ?, ?, ?, ?)"
        params = (score.name, score.genre, score.key, score.incipit, score.year)
        self.cursor.execute(query, params)
        return self.cursor.lastrowid

    def load_score(self, id):
        query = "SELECT id, name, genre, key, incipit, year FROM score WHERE id=?"
        self.cursor.execute(query, (id,))
        row = self.cursor.fetchone()
        return CompositionEntity(row[0], row[1], row[2], row[3], row[4], row[5]) if row else None

    def load_score_author_ids(self, score_id):
        query = "SELECT composer FROM score_author WHERE score=?"
        self.cursor.execute(query, (score_id,))
        ids = []
        for row in self.cursor.fetchall():
            ids.append(row[0])
        return ids

    def store_score_author(self, score_id, composer_id):
        query = "INSERT INTO score_author(score, composer) VALUES (?, ?)"
        params = (score_id, composer_id)
        self.cursor.execute(query, params)
        return self.cursor.lastrowid

    def store_voice(self, voice, index, score_id):
        query = "INSERT INTO voice(number, score, range, name) VALUES (?, ?, ?, ?)"
        params = (index, score_id, voice.range, voice.name)
        self.cursor.execute(query, params)
        return self.cursor.lastrowid

    def load_voices(self, score_id):
        query = "SELECT id, number, name, range FROM voice WHERE score=? ORDER BY number"
        self.cursor.execute(query, (score_id,))
        voices = []
        for row in self.cursor.fetchall():
            voices.append(VoiceEntity(row[0], row[1], row[2], row[3]))
        voices.sort(key=lambda x: x.number)
        return voices

    def store_person(self, person):
        query = "INSERT INTO person(born, died, name) VALUES(?, ?, ?)"
        params = (person.born, person.died, person.name)
        self.cursor.execute(query, params)
        return self.cursor.lastrowid

    def load_person(self, name):
        pass

    def update_person_born(self, name, born):
        query = "UPDATE person SET born=? WHERE name=?"
        params = (born, name)
        self.cursor.execute(query, params)

    def update_person_died(self, name, died):
        query = "UPDATE person SET died=? WHERE name=?"
        params = (died, name)
        self.cursor.execute(query, params)

    def get_person_id(self, name):
        query = "SELECT id FROM person WHERE name=?"
        self.cursor.execute(query, (name,))
        row = self.cursor.fetchone()
        return row[0] if row else None

    def get_score_id(self, name):
        query = "SELECT id FROM score WHERE name=?"
        self.cursor.execute(query, (name,))
        row = self.cursor.fetchone()
        return row[0] if row else None

    def get_edition_id(self, name):
        query = "SELECT id FROM edition WHERE name=?"
        self.cursor.execute(query, (name,))
        row = self.cursor.fetchone()
        return row[0] if row else None


def process_person(person):
    p2_id = db.get_person_id(person.name)
    if p2_id is not None:
        if person.born is not None:
            db.update_person_born(person.name, person.born)
        if person.died is not None:
            db.update_person_died(person.name, person.died)
        return p2_id
    return db.store_person(person)


def process_people(people):
    people_ids = []
    for p in people:
        p_id = process_person(p)
        people_ids.append(p_id)
    return people_ids


def process_voice(voice, index, score_id):
    return db.store_voice(voice, index, score_id)


def process_voices(voices, score_id):
    voice_ids = []
    for i in range(voices.__len__()):
        v_id = process_voice(voices[i], i+1, score_id)
        voice_ids.append(v_id)
    return voice_ids


def check_voices(voices1, score2_id):
    voices2 = db.load_voices(score2_id)
    if voices1.__len__() != voices2.__len__():
        return False
    for i in range(voices1.__len__()):
        if voices1[i].name != voices2[i].name:
            return False
        if voices1[i].range != voices2[i].range:
            return False
    return True


def is_equal_score(score1, score2, composer_ids):
    if score1.name != score2.name:
        return False
    if score1.genre != score2.genre:
        return False
    if score1.key != score2.key:
        return False
    if score1.year != score2.year:
        return False
    score2_composer_ids = db.load_score_author_ids(score2.id)
    if composer_ids.__len__() != score2_composer_ids.__len__():
        return False
    for c in composer_ids:
        if c not in score2_composer_ids:
            return False
    return check_voices(score1.voices, score2.id)


def process_composition(composition):
    composer_ids = process_people(composition.authors)

    score2_id = db.get_score_id(composition.name)
    if score2_id is not None:
        score2 = db.load_score(score2_id)
        if is_equal_score(composition, score2, composer_ids):
            return score2.id

    score_id = db.store_score(composition)
    process_voices(composition.voices, score_id)

    for c_id in composer_ids:
        db.store_score_author(score_id, c_id)

    return score_id


def is_equal_edition(edition1, edition2, editor_ids, composition_id):
    if composition_id != edition2.score_id:
        return False
    editor2_ids = db.load_edition_author_ids(edition2.id)
    if editor_ids.__len__() != editor2_ids.__len__():
        return False
    for e in editor_ids:
        if e not in editor2_ids:
            return False
    return True


def process_edition(edition):
    composition_id = process_composition(edition.composition)
    editor_ids = process_people(edition.authors)
    edition2_id = db.get_edition_id(edition.name)
    if edition2_id is not None:
        edition2 = db.load_edition(edition2_id)
        if is_equal_edition(edition, edition2, editor_ids, composition_id):
            return edition2_id

    edition_id = db.store_edition(composition_id, edition.name)

    for e_id in editor_ids:
        db.store_edition_author(edition_id, e_id)

    return edition_id


def process_print(p):
    edition_id = process_edition(p.edition)
    db.store_print(p.print_id, 'Y' if p.partiture else 'N', edition_id)


def process_data(data_file):
    prints = load(data_file)
    for p in prints:
        process_print(p)


input_txt_file = argv[1]
output_db_file = argv[2]

if os.path.isfile(output_db_file):
    os.remove(output_db_file)

db = Database(output_db_file, SQL_SCHEME_FILE)
process_data(input_txt_file)
db.close()


