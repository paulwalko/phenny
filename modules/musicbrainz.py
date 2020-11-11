#!/usr/bin/env python
# coding=utf-8
"""
musicbrainz.py - MusicBrainz API lookup
Paul Walko
"""

from modules.search import musicbrainz_api

def mz(phenny, input):
    """MusicBrainz API lookup."""
    if not input.group(2):
        return phenny.reply("Nothing to lookup.")
    q = input.group(2)
    q = q.split(" ", 1)

    if len(q) > 1:
        entity_type = q[0]
        query = q[1]
    else:
        phenny.reply("Invalid input. Expected input: .mz ENTITY_TYPE QUERY")

    result = musicbrainz_api(entity_type, query)

    if result:
        if "disambiguation" in result:
            phenny.say("Top {} for \"{}\" ({}): https://musicbrainz.org/{}/{}".format(entity_type, query, result["disambiguation"], entity_type, result["id"]))
        else:
            phenny.say("Top {} for \"{}\": https://musicbrainz.org/{}/{}".format(entity_type, query, entity_type, result["id"]))
    else:
        phenny.reply("Sorry, no result.")
mz.commands = ["mz"]
mz.example = ".mz artist electrobro"
mz.example = ".mz release you can swim"


if __name__ == "__main__":
    print(__doc__.strip())
