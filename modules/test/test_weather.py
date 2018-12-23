"""
test_weather.py - tests for the weather module
author: mutantmonkey <mutantmonkey@mutantmonkey.in>
"""

import re
import unittest
from mock import MagicMock, Mock, patch
from modules import weather


class TestWeather(unittest.TestCase):
    def setUp(self):
        self.phenny = MagicMock()

    def test_locations(self):
        def check_location(result, expected):
            self.assertAlmostEqual(result[0], expected[0], places=1)
            self.assertAlmostEqual(result[1], expected[1], places=1)

        locations = [
            ('92121', (32.9, -117.2)),
            ('94110', (37.8, -122.4)),
            ('94041', (37.4, -122.1)),
            ('27959', (36.0, -75.6)),
            ('48067', (42.5, -83.1)),
            ('23606', (37.1, -76.5)),
            ('23113', (37.5, -77.6)),
            ('27517', (42.6, -7.8)),
            ('15213', (40.4, -80.0)),
            ('90210', (34.1, -118.3)),
            ('33109', (25.8, -80.1)),
            ('80201', (22.6, 120.3)),

            ("Berlin", (52.5, 13.4)),
            ("Paris", (48.9, 2.4)),
            ("Vilnius", (54.7, 25.3)),

            ('Blacksburg, VA', (37.2, -80.4)),
            ('Granger, IN', (41.8, -86.1)),
        ]

        for query, expected in locations:
            result = weather.location(query)
            check_location(result, expected)

    def test_code_94110(self):
        icao = weather.code(self.phenny, '94110')
        self.assertEqual(icao, 'KSFO')

    def test_airport(self):
        input = Mock(group=lambda x: 'KIAD')
        weather.f_weather(self.phenny, input)
        
        assert self.phenny.say.called is True

    def test_place(self):
        input = Mock(group=lambda x: 'Blacksburg')
        weather.f_weather(self.phenny, input)
        
        assert self.phenny.say.called is True

    def test_notfound(self):
        input = Mock(group=lambda x: 'Hell')
        weather.f_weather(self.phenny, input)
        
        self.phenny.say.called_once_with('#phenny',
                "No NOAA data available for that location.")
