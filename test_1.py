import unittest
from proj1 import *
#proj1.py should contain your data class and function definitions
#these tests are very minimal but ensure your data definitions and functions have valid structure and type compatibility before implementing logic.
#these don't contribute to the grade

class TestRegionFunctions(unittest.TestCase):

    def setUp(self):
        self.rect = GlobeRect(lo_lat=10.0, hi_lat=20.0, west_long=30.0, east_long=40.0)
        self.region = Region(rect=self.rect, name="Testland", terrain="other")
        self.rc = RegionCondition(region=self.region, year=2025, pop=1000, ghg_rate=5000.0)

    def test_data_classes_exist(self):
        self.assertIsInstance(self.rect, GlobeRect)
        self.assertIsInstance(self.region, Region)
        self.assertIsInstance(self.rc, RegionCondition)

    def test_emissions_per_capita(self):
        result = emissions_per_capita(self.rc)
        self.assertIsInstance(result, float)

    def test_area(self):
        result = area(self.rect)
        self.assertIsInstance(result, float)

    def test_emissions_per_square_km(self):
        result = emissions_per_square_km(self.rc)
        self.assertIsInstance(result, float)

    def test_densest_single(self):
        result = densest([self.rc])
        self.assertEqual(result, "Testland")

    def test_project_condition(self):
        projected = project_condition(self.rc, 5)
        self.assertIsInstance(projected, RegionCondition)
        self.assertEqual(projected.year, self.rc.year + 5)

if __name__ == '__main__':
    unittest.main()
