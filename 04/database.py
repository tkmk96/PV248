import sqlite3


def person_dict(row):
    c = {
        'name': row[0],
        'born': row[1],
        'died': row[2],
    }
    return c


class Database:
    def __init__(self, dat_file):
        self.connection = sqlite3.connect(dat_file)
        self.cursor = self.connection.cursor()

    def close(self):
        self.connection.commit()
        self.connection.close()

    def get_composers_by_print_id(self, print_id):
        query = """SELECT p.name, p.born, p.died 
                   FROM print
                    JOIN edition ON print.edition = edition.id
                    JOIN score ON edition.score = score.id
                    JOIN score_author ON score.id = score_author.score
                    JOIN person p on score_author.composer = p.id
                   WHERE print.id=?"""
        composers = []

        for row in self.cursor.execute(query, (print_id,)).fetchall():
            composers.append(person_dict(row))
        return composers

    def get_composers_by_name(self, name_substring):
        query = "SELECT id, name FROM person WHERE name LIKE ?"
        params = ('%' + name_substring + '%',)
        composers = []
        for row in self.cursor.execute(query, params).fetchall():
            c = {'id': row[0]}
            name = row[1].strip()
            if name == "":
                continue
            c['name'] = name
            composers.append(c)
        return composers

    def get_prints_by_composer_id(self, composer_id):
        query = """SELECT p.id, p.partiture, e.id, e.name, s.id, s.name, s.genre, s.incipit, s.key, s.year
                   FROM score s
                    JOIN score_author sa on s.id = sa.score 
                    JOIN edition e on s.id = e.score 
                    JOIN print p on e.id = p.edition
                   WHERE sa.composer =?"""

        prints = []
        for row in self.cursor.execute(query, (composer_id,)).fetchall():
            edition_id = row[2]
            score_id = row[4]
            p = {
                'Print Number': row[0],
                'Composer': [],
                'Title': row[5],
                'Genre': row[6],
                'Key': row[8],
                'Composition Year': row[9],
                'Edition': row[3],
                'Editor': [],
                'Voices': [],
                'Partiture': row[1],
                'Incipit': row[7],
            }
            prints.append((p, edition_id, score_id))
        return prints

    def get_edition_by_print_id(self, print_id):
        pass

    def get_editors_by_edition_id(self, edition_id):
        query = """SELECT p.name, p.born, p.died 
                   FROM edition_author ea
                    JOIN person p on ea.editor = p.id
                   WHERE ea.edition=?"""
        editors = []
        for row in self.cursor.execute(query, (edition_id,)).fetchall():
            editors.append(person_dict(row))
        return editors

    def get_voices_by_score_id(self, score_id):
        query = """SELECT v.name, v.range
                   FROM voice v
                    JOIN score s on v.score = s.id
                   WHERE s.id=?"""
        voices = []
        for row in self.cursor.execute(query, (score_id,)).fetchall():
            voice = {
                'name': row[0],
                'range': row[1]
            }
            voices.append(voice)
        return voices

    def get_composers_by_score_id(self, score_id):
        query = """SELECT p.name, p.born, p.died 
                   FROM score_author sa
                    JOIN person p on sa.composer = p.id
                   WHERE sa.score=?"""
        composers = []
        for row in self.cursor.execute(query, (score_id,)).fetchall():
            composers.append(person_dict(row))
        return composers

