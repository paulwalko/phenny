# coding=utf-8
"""
test_musicbrainz.py - tests for the mz module
author: paulwalko <paulsw.pw@gmail.com>
"""

import unittest
from mock import MagicMock, Mock
from modules.musicbrainz import mz


class TestMusicBrainz(unittest.TestCase):
    def setUp(self):
        self.phenny = MagicMock()

    def test_mz_area(self):
        input = Mock(group=lambda x: "area Blacksburg")
        mz(self.phenny, input)

        self.phenny.say.assert_called_once_with("Top area for \"Blacksburg\": https://musicbrainz.org/area/76d1e078-7861-4329-8553-f047b922c4f7")

    def test_mz_artist(self):
        input = Mock(group=lambda x: "artist electrobro")
        mz(self.phenny, input)

        self.phenny.say.assert_called_once_with("Top artist for \"electrobro\" (Sine Wave Surfers member): https://musicbrainz.org/artist/e1a7a405-02f5-4efb-b293-b24586213e67")

    def test_mz_release(self):
        input = Mock(group=lambda x: "release you can swim")
        mz(self.phenny, input)

        self.phenny.say.assert_called_once_with("Top release for \"you can swim\": https://musicbrainz.org/release/5a9f79a6-526f-4b13-8d6f-4deb56bac59d")

    def test_mz_release_group(self):
        input = Mock(group=lambda x: "release-group hello")
        mz(self.phenny, input)

        self.phenny.say.assert_called_once_with("Top release-group for \"hello\": https://musicbrainz.org/release-group/ef20be97-cfb2-42f9-8a66-f650118c02e4")

    def test_mz_work(self):
        input = Mock(group=lambda x: "work 404")
        mz(self.phenny, input)

        self.phenny.say.assert_called_once_with("Top work for \"404\": https://musicbrainz.org/work/18a04f67-f105-42a5-9e6a-10bf349e5965")

    def text_mz_recording(self):
        input = Mock(group=lambda x: "recording basketball")
        mz(self.phenny, input)

        self.phenny.say.assert_called_once_with("Top recording for \"basketball\": https://musicbrainz.org/recording/b23393e7-3930-4687-b94b-970982d003e6")
