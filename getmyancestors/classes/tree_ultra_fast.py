"""
Ultra-fast version of tree classes that only extracts essential data:
- Name
- Birth/death dates and locations  
- Profile ID
- Family relationships
- NO sources, NO notes, NO memories, NO extra facts
"""

import sys
import time
import asyncio
from urllib.parse import unquote

# global imports
import babelfish

# local imports
import getmyancestors
from getmyancestors.classes.constants import (
    MAX_PERSONS,
    FACT_EVEN,
    FACT_TAGS,
)

def cont(string):
    """parse a GEDCOM line adding CONT and CONT tags if necessary"""
    level = int(string[:1]) + 1
    lines = string.splitlines()
    res = list()
    max_len = 255
    for line in lines:
        c_line = line
        to_conc = list()
        while len(c_line.encode("utf-8")) > max_len:
            index = min(max_len, len(c_line) - 2)
            while (
                len(c_line[:index].encode("utf-8")) > max_len
                or re.search(r"[ \t\v]", c_line[index - 1 : index + 1])
            ) and index > 1:
                index -= 1
            to_conc.append(c_line[:index])
            c_line = c_line[index:]
            max_len = 248
        to_conc.append(c_line)
        res.append(("\n%s CONC " % level).join(to_conc))
        max_len = 248
    return ("\n%s CONT " % level).join(res) + "\n"

class Name:
    """GEDCOM Name class - ULTRA SIMPLIFIED"""
    def __init__(self, data=None, tree=None):
        self.given = ""
        self.surname = ""
        self.prefix = None
        self.suffix = None
        if data:
            if "parts" in data["nameForms"][0]:
                for z in data["nameForms"][0]["parts"]:
                    if z["type"] == "http://gedcomx.org/Given":
                        self.given = z["value"]
                    if z["type"] == "http://gedcomx.org/Surname":
                        self.surname = z["value"]
                    if z["type"] == "http://gedcomx.org/Prefix":
                        self.prefix = z["value"]
                    if z["type"] == "http://gedcomx.org/Suffix":
                        self.suffix = z["value"]

    def print(self, file=sys.stdout, typ=None):
        """print Name in GEDCOM format"""
        tmp = "1 NAME %s /%s/" % (self.given, self.surname)
        if self.suffix:
            tmp += " " + self.suffix
        file.write(cont(tmp))
        if self.prefix:
            file.write("2 NPFX %s\n" % self.prefix)

class Fact:
    """GEDCOM Fact class - ULTRA SIMPLIFIED"""
    def __init__(self, data=None, tree=None):
        self.value = self.type = self.date = self.place = None
        if data:
            if "value" in data:
                self.value = data["value"]
            if "type" in data:
                self.type = data["type"]
                if self.type in FACT_EVEN:
                    self.type = tree.fs._(FACT_EVEN[self.type])
                elif self.type[:6] == "data:,":
                    self.type = unquote(self.type[6:])
                elif self.type not in FACT_TAGS:
                    self.type = None
            if "date" in data:
                self.date = data["date"]["original"]
            if "place" in data:
                self.place = data["place"]["original"]

    def print(self, file=sys.stdout):
        """print Fact in GEDCOM format"""
        if self.type in FACT_TAGS:
            tmp = "1 " + FACT_TAGS[self.type]
            if self.value:
                tmp += " " + self.value
            file.write(cont(tmp))
        elif self.type:
            file.write("1 EVEN\n2 TYPE %s\n" % self.type)
            if self.value:
                file.write(cont("2 NOTE Description: " + self.value))
        else:
            return
        if self.date:
            file.write(cont("2 DATE " + self.date))
        if self.place:
            file.write(cont("2 PLAC " + self.place))

class Indi:
    """GEDCOM individual class - ULTRA SIMPLIFIED"""
    counter = 0

    def __init__(self, fid=None, tree=None, num=None):
        if num:
            self.num = num
        else:
            Indi.counter += 1
            self.num = Indi.counter
        self.fid = fid
        self.tree = tree
        self.famc_fid = set()
        self.fams_fid = set()
        self.famc_num = set()
        self.fams_num = set()
        self.name = None
        self.gender = None
        self.living = None
        self.parents = set()
        self.spouses = set()
        self.children = set()
        self.facts = set()

    def add_data(self, data):
        """add FS individual data - ULTRA SIMPLIFIED"""
        if data:
            self.living = data["living"]
            
            # Only get the preferred name
            for x in data["names"]:
                if x["preferred"]:
                    self.name = Name(x, self.tree)
                    break
            
            # Only get gender
            if "gender" in data:
                if data["gender"]["type"] == "http://gedcomx.org/Male":
                    self.gender = "M"
                elif data["gender"]["type"] == "http://gedcomx.org/Female":
                    self.gender = "F"
                elif data["gender"]["type"] == "http://gedcomx.org/Unknown":
                    self.gender = "U"
            
            # Only get birth and death facts
            if "facts" in data:
                for x in data["facts"]:
                    if x["type"] == "http://gedcomx.org/Birth" or x["type"] == "http://gedcomx.org/Death":
                        self.facts.add(Fact(x, self.tree))

    def add_fams(self, fams):
        """add family fid (for spouse or parent)"""
        self.fams_fid.add(fams)

    def add_famc(self, famc):
        """add family fid (for child)"""
        self.famc_fid.add(famc)

    def print(self, file=sys.stdout):
        """print individual in GEDCOM format - ULTRA SIMPLIFIED"""
        file.write("0 @I%s@ INDI\n" % self.num)
        if self.name:
            self.name.print(file)
        if self.gender:
            file.write("1 SEX %s\n" % self.gender)
        for o in self.facts:
            o.print(file)
        for num in self.fams_num:
            file.write("1 FAMS @F%s@\n" % num)
        for num in self.famc_num:
            file.write("1 FAMC @F%s@\n" % num)
        file.write("1 _FSFTID %s\n" % self.fid)

class Fam:
    """GEDCOM family class - ULTRA SIMPLIFIED"""
    counter = 0

    def __init__(self, husb=None, wife=None, tree=None, num=None):
        if num:
            self.num = num
        else:
            Fam.counter += 1
            self.num = Fam.counter
        self.husb_fid = husb if husb else None
        self.wife_fid = wife if wife else None
        self.tree = tree
        self.husb_num = self.wife_num = self.fid = None
        self.facts = set()
        self.chil_fid = set()
        self.chil_num = set()

    def add_child(self, child):
        """add a child fid to the family"""
        if child not in self.chil_fid:
            self.chil_fid.add(child)

    def add_marriage(self, fid):
        """retrieve and add marriage information - ULTRA SIMPLIFIED"""
        if not self.fid:
            self.fid = fid
            url = "/platform/tree/couple-relationships/%s" % self.fid
            data = self.tree.fs.get_url(url)
            if data:
                # Only get marriage facts (date/place)
                if "facts" in data["relationships"][0]:
                    for x in data["relationships"][0]["facts"]:
                        if x["type"] == "http://gedcomx.org/Marriage":
                            self.facts.add(Fact(x, self.tree))

    def print(self, file=sys.stdout):
        """print family information in GEDCOM format - ULTRA SIMPLIFIED"""
        file.write("0 @F%s@ FAM\n" % self.num)
        if self.husb_num:
            file.write("1 HUSB @I%s@\n" % self.husb_num)
        if self.wife_num:
            file.write("1 WIFE @I%s@\n" % self.wife_num)
        for num in self.chil_num:
            file.write("1 CHIL @I%s@\n" % num)
        for o in self.facts:
            o.print(file)
        if self.fid:
            file.write("1 _FSFTID %s\n" % self.fid)

class Tree:
    """family tree class - ULTRA SIMPLIFIED"""
    def __init__(self, fs=None):
        self.fs = fs
        self.indi = dict()
        self.fam = dict()
        self.places = dict()
        self.display_name = self.lang = None
        if fs:
            self.display_name = fs.display_name
            self.lang = babelfish.Language.fromalpha2(fs.lang).name

    def add_indis(self, fids):
        """add individuals to the family tree - ULTRA SIMPLIFIED"""
        async def add_datas(loop, data):
            futures = set()
            for person in data["persons"]:
                self.indi[person["id"]] = Indi(person["id"], self)
                futures.add(
                    loop.run_in_executor(None, self.indi[person["id"]].add_data, person)
                )
            for future in futures:
                await future

        new_fids = [fid for fid in fids if fid and fid not in self.indi]
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        while new_fids:
            data = self.fs.get_url(
                "/platform/tree/persons?pids=" + ",".join(new_fids[:MAX_PERSONS])
            )
            if data:
                if "places" in data:
                    for place in data["places"]:
                        if place["id"] not in self.places:
                            self.places[place["id"]] = (
                                str(place["latitude"]),
                                str(place["longitude"]),
                            )
                loop.run_until_complete(add_datas(loop, data))
                if "childAndParentsRelationships" in data:
                    for rel in data["childAndParentsRelationships"]:
                        father = (
                            rel["parent1"]["resourceId"] if "parent1" in rel else None
                        )
                        mother = (
                            rel["parent2"]["resourceId"] if "parent2" in rel else None
                        )
                        child = rel["child"]["resourceId"] if "child" in rel else None
                        if child in self.indi:
                            self.indi[child].parents.add((father, mother))
                        if father in self.indi:
                            self.indi[father].children.add((father, mother, child))
                        if mother in self.indi:
                            self.indi[mother].children.add((father, mother, child))
                if "relationships" in data:
                    for rel in data["relationships"]:
                        if rel["type"] == "http://gedcomx.org/Couple":
                            person1 = rel["person1"]["resourceId"]
                            person2 = rel["person2"]["resourceId"]
                            relfid = rel["id"]
                            if person1 in self.indi:
                                self.indi[person1].spouses.add(
                                    (person1, person2, relfid)
                                )
                            if person2 in self.indi:
                                self.indi[person2].spouses.add(
                                    (person1, person2, relfid)
                                )
            new_fids = new_fids[MAX_PERSONS:]

    def add_fam(self, father, mother):
        """add a family to the family tree"""
        if (father, mother) not in self.fam:
            self.fam[(father, mother)] = Fam(father, mother, self)

    def add_trio(self, father, mother, child):
        """add a children relationship to the family tree"""
        if father in self.indi:
            self.indi[father].add_fams((father, mother))
        if mother in self.indi:
            self.indi[mother].add_fams((father, mother))
        if child in self.indi and (father in self.indi or mother in self.indi):
            self.indi[child].add_famc((father, mother))
            self.add_fam(father, mother)
            self.fam[(father, mother)].add_child(child)

    def add_parents(self, fids):
        """add parents relationships"""
        parents = set()
        for fid in fids & self.indi.keys():
            for couple in self.indi[fid].parents:
                parents |= set(couple)
        if parents:
            self.add_indis(parents)
        for fid in fids & self.indi.keys():
            for father, mother in self.indi[fid].parents:
                if (
                    mother in self.indi
                    and father in self.indi
                    or not father
                    and mother in self.indi
                    or not mother
                    and father in self.indi
                ):
                    self.add_trio(father, mother, fid)
        return set(filter(None, parents))

    def add_spouses(self, fids):
        """add spouse relationships - ULTRA SIMPLIFIED"""
        async def add(loop, rels):
            futures = set()
            for father, mother, relfid in rels:
                if (father, mother) in self.fam:
                    futures.add(
                        loop.run_in_executor(
                            None, self.fam[(father, mother)].add_marriage, relfid
                        )
                    )
            for future in futures:
                await future

        rels = set()
        for fid in fids & self.indi.keys():
            rels |= self.indi[fid].spouses
        loop = asyncio.get_event_loop()
        if rels:
            self.add_indis(
                set.union(*({father, mother} for father, mother, relfid in rels))
            )
            for father, mother, _ in rels:
                if father in self.indi and mother in self.indi:
                    self.indi[father].add_fams((father, mother))
                    self.indi[mother].add_fams((father, mother))
                    self.add_fam(father, mother)
            loop.run_until_complete(add(loop, rels))

    def add_children(self, fids):
        """add children relationships"""
        rels = set()
        for fid in fids & self.indi.keys():
            rels |= self.indi[fid].children if fid in self.indi else set()
        children = set()
        if rels:
            self.add_indis(set.union(*(set(rel) for rel in rels)))
            for father, mother, child in rels:
                if child in self.indi and (
                    mother in self.indi
                    and father in self.indi
                    or not father
                    and mother in self.indi
                    or not mother
                    and father in self.indi
                ):
                    self.add_trio(father, mother, child)
                    children.add(child)
        return children

    def reset_num(self):
        """reset all GEDCOM identifiers"""
        for husb, wife in self.fam:
            self.fam[(husb, wife)].husb_num = self.indi[husb].num if husb else None
            self.fam[(husb, wife)].wife_num = self.indi[wife].num if wife else None
            self.fam[(husb, wife)].chil_num = set(
                self.indi[chil].num for chil in self.fam[(husb, wife)].chil_fid
            )
        for fid in self.indi:
            self.indi[fid].famc_num = set(
                self.fam[(husb, wife)].num for husb, wife in self.indi[fid].famc_fid
            )
            self.indi[fid].fams_num = set(
                self.fam[(husb, wife)].num for husb, wife in self.indi[fid].fams_fid
            )

    def print(self, file=sys.stdout):
        """print family tree in GEDCOM format - ULTRA SIMPLIFIED"""
        file.write("0 HEAD\n")
        file.write("1 CHAR UTF-8\n")
        file.write("1 GEDC\n")
        file.write("2 VERS 5.5.1\n")
        file.write("2 FORM LINEAGE-LINKED\n")
        file.write("1 SOUR getmyancestors-ultra-fast\n")
        file.write("2 VERS %s\n" % getmyancestors.__version__)
        file.write("2 NAME getmyancestors-ultra-fast\n")
        file.write("1 DATE %s\n" % time.strftime("%d %b %Y"))
        file.write("2 TIME %s\n" % time.strftime("%H:%M:%S"))
        file.write("1 SUBM @SUBM@\n")
        file.write("0 @SUBM@ SUBM\n")
        file.write("1 NAME %s\n" % self.display_name)
        file.write("1 LANG %s\n" % self.lang)

        for fid in sorted(self.indi, key=lambda x: self.indi.__getitem__(x).num):
            self.indi[fid].print(file)
        for husb, wife in sorted(self.fam, key=lambda x: self.fam.__getitem__(x).num):
            self.fam[(husb, wife)].print(file)
        file.write("0 TRLR\n") 