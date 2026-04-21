import sys
import math
from typing import *
from dataclasses import dataclass

sys.setrecursionlimit(10**6)

Terrain: TypeAlias = str
RegionConditionList: TypeAlias = list["RegionCondition"]


@dataclass(frozen=True)
class GlobeRect:
    lo_lat: float
    hi_lat: float
    west_long: float
    east_long: float


@dataclass(frozen=True)
class Region:
    rect: GlobeRect
    name: str
    terrain: Terrain


@dataclass(frozen=True)
class RegionCondition:
    region: Region
    year: int
    pop: int
    ghg_rate: float


TOKYO_RECT: GlobeRect = GlobeRect(35.5, 35.9, 139.5, 140.0)
TOKYO_REGION: Region = Region(TOKYO_RECT, "Tokyo", "other")
TOKYO_2024: RegionCondition = RegionCondition(TOKYO_REGION, 2024, 14000000, 70000000.0)

LAGOS_RECT: GlobeRect = GlobeRect(6.2, 6.7, 3.0, 3.7)
LAGOS_REGION: Region = Region(LAGOS_RECT, "Lagos", "other")
LAGOS_2024: RegionCondition = RegionCondition(LAGOS_REGION, 2024, 15000000, 50000000.0)

PACIFIC_RECT: GlobeRect = GlobeRect(-10.0, 10.0, 170.0, -150.0)
PACIFIC_REGION: Region = Region(PACIFIC_RECT, "Central Pacific Patch", "ocean")
PACIFIC_2024: RegionCondition = RegionCondition(PACIFIC_REGION, 2024, 0, 2000000.0)

CAL_POLY_RECT: GlobeRect = GlobeRect(35.1, 35.5, -120.9, -120.5)
CAL_POLY_REGION: Region = Region(CAL_POLY_RECT, "San Luis Obispo Area", "other")
CAL_POLY_2024: RegionCondition = RegionCondition(CAL_POLY_REGION, 2024, 120000, 400000.0)

region_conditions: RegionConditionList = [
    TOKYO_2024,
    LAGOS_2024,
    PACIFIC_2024,
    CAL_POLY_2024
]


# Purpose: Return the yearly greenhouse gas emissions per person in a region.
# emissions_per_capita: RegionCondition -> float
# Parameters: rc: a RegionCondition
# Returns: A float representing tons of CO2-equivalent per person per year.
# Preconditions: rc.pop is greater than or equal to 0.
# Postconditions: Returns 0.0 if the population is 0.
def emissions_per_capita(rc: RegionCondition) -> float:
    if rc.pop == 0:
        return 0.0
    return rc.ghg_rate / rc.pop


# Purpose: Return the estimated surface area of a globe rectangle in square km.
# area: GlobeRect -> float
# Parameters: gr: a GlobeRect
# Returns: A float representing the spherical surface area in square kilometers.
# Preconditions: The latitude and longitude values describe a valid globe rectangle.
# Postconditions: The result is non-negative.
def area(gr: GlobeRect) -> float:
    earth_radius: float = 6378.1
    west_radians: float = math.radians(gr.west_long)
    east_radians: float = math.radians(gr.east_long)
    low_radians: float = math.radians(gr.lo_lat)
    high_radians: float = math.radians(gr.hi_lat)

    longitude_width: float = east_radians - west_radians
    if longitude_width < 0:
        longitude_width = longitude_width + (2 * math.pi)

    latitude_height: float = math.sin(high_radians) - math.sin(low_radians)

    return (earth_radius**2) * abs(longitude_width) * abs(latitude_height)


# Purpose: Return yearly greenhouse gas emissions per square kilometer.
# emissions_per_square_km: RegionCondition -> float
# Parameters: rc: a RegionCondition
# Returns: A float representing tons of CO2-equivalent per square kilometer.
# Preconditions: rc contains a valid region rectangle.
# Postconditions: Returns 0.0 if the region area is 0.
def emissions_per_square_km(rc: RegionCondition) -> float:
    region_area: float = area(rc.region.rect)
    if region_area == 0:
        return 0.0
    return rc.ghg_rate / region_area


# Purpose: Return the population density of a region condition.
# population_density: RegionCondition -> float
# Parameters: rc: a RegionCondition
# Returns: A float representing people per square kilometer.
# Preconditions: rc contains a valid region rectangle.
# Postconditions: Returns 0.0 if the region area is 0.
def population_density(rc: RegionCondition) -> float:
    region_area: float = area(rc.region.rect)
    if region_area == 0:
        return 0.0
    return rc.pop / region_area


# Purpose: Return the name of the region with the highest population density.
# densest: RegionConditionList -> str
# Parameters: rc_list: a list of RegionCondition values
# Returns: The name of the region with the highest population density.
# Preconditions: rc_list is not empty.
# Postconditions: Raises ValueError if rc_list is empty.
def densest(rc_list: RegionConditionList) -> str:
    if rc_list == []:
        raise ValueError("rc_list cant be empty")
    return densest_helper(rc_list, 1, rc_list[0]).region.name


# Purpose: Recursively find the RegionCondition with the highest population density.
# densest_helper: RegionConditionList int RegionCondition -> RegionCondition
# Parameters: rc_list: a list of RegionCondition values, index: the current index, current_best: the best RegionCondition found so far
# Returns: The RegionCondition with the highest population density.
# Preconditions: index is greater than or equal to 0 and current_best is a RegionCondition from rc_list.
# Postconditions: Returns one RegionCondition from rc_list.
def densest_helper(rc_list: RegionConditionList,
                   index: int,
                   current_best: RegionCondition) -> RegionCondition:
    if index >= len(rc_list):
        return current_best

    next_best: RegionCondition = current_best
    if population_density(rc_list[index]) > population_density(current_best):
        next_best = rc_list[index]

    return densest_helper(rc_list, index + 1, next_best)


# Purpose: Return the annual growth rate for a terrain type.
# terrain_growth_rate: Terrain -> float
# Parameters: terrain: a terrain string
# Returns: A float representing the annual population growth rate.
# Preconditions: terrain is one of "ocean", "mountains", "forest", or "other".
# Postconditions: Raises ValueError if the terrain is unknown.
def terrain_growth_rate(terrain: Terrain) -> float:
    if terrain == "ocean":
        return 0.0001
    elif terrain == "mountains":
        return 0.0005
    elif terrain == "forest":
        return -0.00001
    elif terrain == "other":
        return 0.0003
    else:
        raise ValueError("unknown terrain")


# Purpose: Recursively project a population forward by a number of years.
# project_population: int float int -> int
# Parameters: pop: the starting population, growth_rate: the annual growth rate, years: the number of years to project
# Returns: An int representing the projected population.
# Preconditions: years is greater than or equal to 0.
# Postconditions: Returns the original population if years is 0.
def project_population(pop: int, growth_rate: float, years: int) -> int:
    if years == 0:
        return pop
    next_pop: int = int(pop * (1 + growth_rate))
    return project_population(next_pop, growth_rate, years - 1)


# Purpose: Return a new projected RegionCondition after a given number of years.
# project_condition: RegionCondition int -> RegionCondition
# Parameters: rc: a RegionCondition, years: the number of years to project forward
# Returns: A new RegionCondition with updated year, population, and ghg_rate.
# Preconditions: years is greater than or equal to 0.
# Postconditions: Raises ValueError if years is negative and does not mutate the original RegionCondition.
def project_condition(rc: RegionCondition, years: int) -> RegionCondition:
    if years < 0:
        raise ValueError("years must be non negative")

    growth_rate: float = terrain_growth_rate(rc.region.terrain)
    new_pop: int = project_population(rc.pop, growth_rate, years)
    per_capita: float = emissions_per_capita(rc)
    new_ghg_rate: float = per_capita * new_pop

    return RegionCondition(rc.region, rc.year + years, new_pop, new_ghg_rate)
