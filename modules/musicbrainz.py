#!/usr/bin/env python3
# coding=utf-8
"""
musicbrainz.py - MusicBrainz API lookup
Paul Walko
"""

from modules.search import musicbrainz_api

entity_types = {"area", "artist", "event", "genre", "instrument", "label", "place", "recording", "release", "release-group", "series", "work", "url"}
entity_types_unimplemented = {"genre"}

def mb(phenny, input):
    """MusicBrainz API lookup."""
    if not input.group(2):
        return phenny.reply("Nothing to lookup.")
    q = input.group(2)
    q = q.split(" ", 1)

    if len(q) > 1:
        entity_type = q[0]
        query = q[1]
    else:
        phenny.reply("Invalid input. Expected input: .mb|.mbz|.mz {} QUERY".format("|".join(entity_types)))
        return

    if entity_type in entity_types_unimplemented:
        phenny.reply("entity type {} exists, however is unimplemented".format(entity_type))
        return
    if entity_type not in entity_types:
        phenny.reply("entity type {} does not exist. Allowed entities: {}".format(entity_type, ", ".join(entity_types)))
        return

    result = musicbrainz_api(entity_type, query)

    if not result:
        phenny.reply("Sorry, no result.")
        return

    if entity_type == "url":
        phenny.say(result["resource"])
        return

    name = ""
    if "name" in result:
        name = result["name"]
    elif "title" in result:
        name = result["title"]

    type = ""
    if "type" in result:
        type = str(", " + result["type"])
    elif "primary-type" in result:
        type = str(", " + result["primary-type"])

    d = ""
    if "disambiguation" in result:
        d = str(" (" + result["disambiguation"] + ") ")

    phenny.say("{}{}{}: https://musicbrainz.org/{}/{}".format(name, type, d, entity_type, result["id"]))

mb.commands = ["mb", "mbz", "mz"]
mb.example = ".mz artist Queen"
mb.example = ".mz release The Dark Side Of The Moon"


if __name__ == "__main__":
    print(__doc__.strip())
