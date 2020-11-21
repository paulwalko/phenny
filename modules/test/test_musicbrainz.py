# coding=utf-8
"""
test_musicbrainz.py - tests for the mb module
author: paulwalko <paulsw.pw@gmail.com>
"""

import unittest
from mock import MagicMock, Mock
from modules.musicbrainz import mb


class TestMusicBrainz(unittest.TestCase):
    def setUp(self):
        self.phenny = MagicMock()

    def test_mb_area(self):
        input = Mock(group=lambda x: "area Blacksburg")
        mb(self.phenny, input)

        self.phenny.say.assert_called_once_with("Blacksburg, City: https://musicbrainz.org/area/76d1e078-7861-4329-8553-f047b922c4f7")

    def test_mb_artist(self):
        input = Mock(group=lambda x: "artist Queen")
        mb(self.phenny, input)

        self.phenny.say.assert_called_once_with("Queen, Group (UK rock group) : https://musicbrainz.org/artist/0383dadf-2a4e-4d10-a46a-e9e041da8eb3")

    def test_mb_release(self):
        input = Mock(group=lambda x: "release The Dark Side Of The Moon")
        mb(self.phenny, input)

        self.phenny.say.assert_called_once_with("The Dark Side of the Moon: https://musicbrainz.org/release/90a5f2b9-e3ba-4742-8a35-e68c40f13839")

    def test_mb_release_group(self):
        input = Mock(group=lambda x: "release-group hello")
        mb(self.phenny, input)

        self.phenny.say.assert_called_once_with("HELLO,HELLO,HELLO, Album: https://musicbrainz.org/release-group/ef20be97-cfb2-42f9-8a66-f650118c02e4")

    def test_mb_work(self):
        input = Mock(group=lambda x: "work 404")
        mb(self.phenny, input)

        self.phenny.say.assert_called_once_with("404, Song: https://musicbrainz.org/work/18a04f67-f105-42a5-9e6a-10bf349e5965")

    def text_mb_recording(self):
        input = Mock(group=lambda x: "recording basketball")
        mb(self.phenny, input)

        self.phenny.say.assert_called_once_with("Top recording for \"basketball\": https://musicbrainz.org/recording/b23393e7-3930-4687-b94b-970982d003e6")
