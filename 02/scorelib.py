import re


def value_if_nonempty(value):
    return value if value != "" else None


class Person:
    def __init__(self, name, born, died):
        self.name = name.strip()
        self.born = int(born) if born is not None else None
        self.died = int(died) if died is not None else None

    def __str__(self):
        if self.born and self.died:
            return "%s (%s--%s)" % (self.name, self.born, self.died)
        elif self.born and not self.died:
            return "%s (%s--)" % (self.name, self.born)
        elif not self.born and self.died:
            return "%s (--%s)" % (self.name, self.died)
        else:
            return "%s" % self.name


class Voice:
    def __init__(self, name, range):
        self.name = value_if_nonempty(name)
        self.range = range

    def __str__(self):
        if self.range and self.name:
            return "%s, %s" % (self.range, self.name)
        elif self.name:
            return "%s" % self.name
        elif self.range:
            return "%s" % self.range
        else:
            return ""


class Composition:
    def __init__(self, name, authors, genre, key, year, voices, incipit):
        self.name = value_if_nonempty(name)
        self.authors = authors
        self.genre = value_if_nonempty(genre)
        self.key = value_if_nonempty(key)
        self.year = int(year) if year is not None else None
        self.voices = voices
        self.incipit = value_if_nonempty(incipit)

    def get_values(self):
        return self.name, self.authors, self.genre, self.key, self.year, self.voices, self.incipit


class Edition:
    def __init__(self, name, authors, composition):
        self.name = value_if_nonempty(name)
        self.authors = authors
        self.composition = composition

    def get_values(self):
        return self.name, self.authors


class Print:
    def __init__(self, id, edition, partiture):
        self.print_id = id
        self.edition = edition
        self.partiture = partiture

    def composition(self):
        return self.edition.composition

    def format(self):
        title, composers, genre, key, year, voices, incipit = self.composition().get_values()
        edition, editors = self.edition.get_values()

        print("Print Number: %d" % self.print_id)
        if composers:
            print("Composer: %s" % ("; ".join([c.__str__() for c in composers])))
        if title:
            print("Title: %s" % title)
        if genre:
            print("Genre: %s" % genre)
        if key:
            print("Key: %s" % key)
        if year:
            print("Composition Year: %s" % (year if year else ""))
        if edition:
            print("Edition: %s" % edition)
        if editors:
            print("Editor: %s" % (", ".join([e.__str__() for e in editors])))
        format_voices(voices)
        print("Partiture: %s" % ('yes' if self.partiture else 'no'))
        if incipit:
            print("Incipit: %s" % incipit)


def format_voices(voices):
    for i in range(voices.__len__()):
        print("Voice %d: %s" % (i + 1, voices[i]))


class Parser:
    def __init__(self):
        self.re_print_number = re.compile(r"^Print Number:\s(\d+)")
        self.re_composer = re.compile(r"Composer:\s(.*)")
        self.re_title = re.compile(r"Title: ?(.*)")
        self.re_genre = re.compile(r"Genre: ?(.*)")
        self.re_key = re.compile(r"Key: ?(.*)")
        self.re_composition_year = re.compile(r"Composition Year:.*(\d{4})")
        self.re_edition = re.compile(r"Edition: (.*)")
        self.re_editor = re.compile(r"Editor: (.*)")
        self.re_voices = re.compile(r"Voice \d{1,2}: ?(.*)")
        self.re_partiture = re.compile(r"Partiture: ?(.*)")
        self.re_incipit = re.compile(r"Incipit: ?(.*)")
        self.re_name = re.compile(r"(.*)(?:\((\d{4})?-{0,2}\+?(\d{4})?\))")

    def parse_print_number(self, content):
        evaluation = self.re_print_number.search(content)
        if evaluation:
            return int(evaluation.group(1).strip())
        return None

    def parse_composers(self, content):
        evaluation = self.re_composer.search(content)
        splitted = evaluation.group(1).split(';') if evaluation else []
        composers = []
        for c in splitted:
            p = self.parse_person(c.strip())
            if p is not None:
                composers.append(p)
        return composers

    def parse_title(self, content):
        evaluation = self.re_title.search(content)
        if evaluation:
            return evaluation.group(1).strip()
        return None

    def parse_genre(self, content):
        evaluation = self.re_genre.search(content)
        if evaluation:
            return evaluation.group(1).strip()
        return None

    def parse_key(self, content):
        evaluation = self.re_key.search(content)
        if evaluation:
            return evaluation.group(1).strip()
        return None

    def parse_composition_year(self, content):
        evaluation = self.re_composition_year.search(content)
        if evaluation:
            return int(evaluation.group(1).strip())
        return None

    def parse_edition(self, content):
        evaluation = self.re_edition.search(content)
        if evaluation:
            return evaluation.group(1).strip()
        return None

    def parse_editors(self, content):
        editors = []
        editors_eval = self.re_editor.search(content)
        if editors_eval is not None:
            split = editors_eval.group(1).split(",")
            if split.__len__() > 1:
                i = 0
                while i < split.__len__():
                    editors.append(Person(split[i].strip() + ", " + split[i + 1].strip(), None, None))
                    i += 2
            elif split[0].strip() != "":
                editors.append(Person(split[0].strip(), None, None))
        return editors

    def parse_voices(self, content):
        voices = []
        voices_eval = self.re_voices.findall(content)
        for voice in voices_eval:
            voice_eval = re.compile(r"(.*)--([^,]*), (.*)").search(voice)
            if voice_eval is not None:
                voices.append(
                    Voice(voice_eval.group(3).strip(), voice_eval.group(1) + "--" + voice_eval.group(2)))
            else:
                voices.append(Voice(voice.strip(), None))

        return voices

    def parse_partiture(self, content):
        evaluation = self.re_partiture.search(content)
        if evaluation:
            return evaluation.group(1).strip() == 'yes'
        return False

    def parse_incipit(self, content):
        evaluation = self.re_incipit.search(content)
        if evaluation:
            return evaluation.group(1)
        return None

    def parse_person(self, person):
        if person == "":
            return None
        evaluation = self.re_name.match(person)
        if evaluation:
            return Person(evaluation.group(1), evaluation.group(2), evaluation.group(3))
        return Person(person, None, None)


def parse_block(data_block, parser):
    print_number = parser.parse_print_number(data_block)
    if print_number is None:
        return None

    composers = parser.parse_composers(data_block)
    title = parser.parse_title(data_block)
    genre = parser.parse_genre(data_block)
    key = parser.parse_key(data_block)
    composition_year = parser.parse_composition_year(data_block)
    edition = parser.parse_edition(data_block)
    editors = parser.parse_editors(data_block)
    voices = parser.parse_voices(data_block)
    incipit = parser.parse_incipit(data_block)
    partiture = parser.parse_partiture(data_block)

    composition = Composition(title, composers, genre, key, composition_year, voices, incipit)
    edition = Edition(edition, editors, composition)
    print_instance = Print(int(print_number), edition, partiture)

    return print_instance


def parse_data(data):
    results = []
    parser = Parser()
    for data_block in data:
        result = parse_block(data_block.strip(), parser)
        if result is not None:
            results.append(result)
    return results


def load(filename):
    file = open(filename, 'r', encoding="utf8").read()
    data = file.split("\n\n")

    results = parse_data(data)
    return results

def findVoices(results):
    res = []
    for r in results:
        id = r.print_id
        voices = r.composition().voices
        for v in voices:
            if v.name == "" or v.range == "":
                res.append(id)
    return res
