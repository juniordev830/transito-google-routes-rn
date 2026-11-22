import unittest
from urllib.parse import parse_qs, urlparse
from app import rota


class TestWaypointTypes(unittest.TestCase):
    def test_mapping_or_set_is_not_a_valid_ordered_route(self):
        for waypoints in ({"a": "b"}, {"a", "b"}, frozenset({"a"})):
            with self.subTest(waypoints=waypoints), self.assertRaises(ValueError):
                rota("Natal", "Parnamirim", paradas=waypoints)

    def test_ordered_waypoints_are_preserved(self):
        query = parse_qs(urlparse(rota("Natal", "Touros", paradas=["Ceará-Mirim", "Maxaranguape"])).query)
        self.assertEqual(query["waypoints"], ["Ceará-Mirim|Maxaranguape"])


if __name__ == "__main__":
    unittest.main()
