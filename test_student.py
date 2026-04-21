import unittest
import math
from proj1 import *


class TestRegionFunctions(unittest.TestCase):

    def setUp(self):
        self.rect = GlobeRect(lo_lat=10.0, hi_lat=20.0, west_long=30.0, east_long=40.0)
        self.region = Region(rect=self.rect, name="Testland", terrain="other")
        self.rc = RegionCondition(region=self.region, year=2025, pop=1000, ghg_rate=5000.0)

        self.wrap_rect = GlobeRect(lo_lat=-10.0, hi_lat=10.0, west_long=170.0, east_long=-170.0)
        self.small_rect = GlobeRect(lo_lat=0.0, hi_lat=1.0, west_long=0.0, east_long=1.0)
        self.big_rect = GlobeRect(lo_lat=0.0, hi_lat=1.0, west_long=0.0, east_long=2.0)

        self.small_region = Region(rect=self.small_rect, name="Small", terrain="other")
        self.big_region = Region(rect=self.big_rect, name="Big", terrain="other")

        self.small_dense = RegionCondition(region=self.small_region, year=2025, pop=100, ghg_rate=50.0)
        self.big_dense = RegionCondition(region=self.big_region, year=2025, pop=500, ghg_rate=50.0)

    def test_example_data_exists(self):
        self.assertEqual(len(region_conditions), 4)

    def test_emissions_per_capita(self):
        self.assertAlmostEqual(emissions_per_capita(self.rc), 5.0, places=4)

    def test_emissions_per_capita_zero_population(self):
        zero_rc = RegionCondition(region=self.region, year=2025, pop=0, ghg_rate=5000.0)
        self.assertEqual(emissions_per_capita(zero_rc), 0.0)

    def test_area(self):
        expected = (6378.1 ** 2) * math.radians(10.0) * abs(math.sin(math.radians(20.0)) - math.sin(math.radians(10.0)))
        self.assertAlmostEqual(area(self.rect), expected, places=4)

    def test_area_wraparound(self):
        expected = (6378.1 ** 2) * math.radians(20.0) * abs(math.sin(math.radians(10.0)) - math.sin(math.radians(-10.0)))
        self.assertAlmostEqual(area(self.wrap_rect), expected, places=4)

    def test_emissions_per_square_km(self):
        expected = self.rc.ghg_rate / area(self.rect)
        self.assertAlmostEqual(emissions_per_square_km(self.rc), expected, places=4)

    def test_densest(self):
        self.assertEqual(densest([self.small_dense, self.big_dense]), "Big")

    def test_densest_empty_list(self):
        with self.assertRaises(ValueError):
            densest([])

    def test_project_condition(self):
        projected = project_condition(self.big_dense, 1)
        self.assertEqual(projected.year, 2026)
        self.assertEqual(projected.pop, 500)
        self.assertAlmostEqual(projected.ghg_rate, 50.0, places=4)

    def test_project_condition_multiple_years(self):
        growing = RegionCondition(region=self.region, year=2025, pop=10000, ghg_rate=20000.0)
        projected = project_condition(growing, 2)
        self.assertEqual(projected.year, 2027)
        self.assertEqual(projected.pop, 10006)
        self.assertAlmostEqual(projected.ghg_rate, 20012.0, places=4)

    def test_project_condition_negative_years(self):
        with self.assertRaises(ValueError):
            project_condition(self.rc, -1)


if __name__ == '__main__':
    unittest.main()
