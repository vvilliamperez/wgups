import csv
import os
from logging import getLogger
from typing import Dict, List

import res
from wgups.constants import EOD_IN_SECONDS

PACKAGE_FILE_NAME = "package_file.csv"
DISTANCE_FILE_NAME = "distance_data.csv"
LOCATION_FILE_NAME = "location_lookup.csv"
logger = getLogger(__name__)


def get_distance(distance_data: List[Dict], location1: str, location2: str) -> float:
    data = distance_data
    if data is None:
        raise Exception("No distance data available")
    if location1 == location2:
        return 0.0
    for row in data:
        loc1, loc2 = row['Location1'], row['Location2']
        if (loc1 == location1 and loc2 == location2) or (loc1 == location2 and loc2 == location1):
            return float(row['Distance'])
    return None


def ingest_distances_from_file()-> List[Dict]:
    distance_file_path = os.path.join(str(res.__path__[0]), DISTANCE_FILE_NAME)
    distance_data = csv_to_dict_list(distance_file_path)

    return distance_data


def ingest_packages_from_file() -> List[Dict]:
    package_file_path = os.path.join(str(res.__path__[0]), PACKAGE_FILE_NAME)
    #logger.info(f" {package_file_path}")
    packages = csv_to_dict_list(package_file_path)

    logger.info(f"Loaded {len(packages)} packages from CSV")
    #logger.info(f"{packages}")

    # Add full_address to each package
    for package in packages:
        package["full_address"] = f"{package['Address']}, {package['City']}, {package['State']} {package['Zip']}"

    return packages

def ingest_locations_from_file() -> List[Dict]:
    location_file_path = os.path.join(str(res.__path__[0]), LOCATION_FILE_NAME)
    locations = csv_to_dict_list(location_file_path)

    logger.info(f"Loaded {len(locations)} locations from CSV")
    #logger.info(f"{locations}")

    return locations



def csv_to_dict_list(csv_file_path: str)-> List[Dict]:
    dict_list = []
    with open(csv_file_path, mode='r', newline='', encoding='utf-8') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            dict_list.append(row)
    return dict_list


def convert_deadline(deadline_in_hhmmss):
    """
    Convert the deadline to seconds
    """
    if deadline_in_hhmmss == 'EOD':
        return EOD_IN_SECONDS

    deadline = deadline_in_hhmmss.split(':')
    return int(deadline[0]) * 3600 + int(deadline[1]) * 60 + int(deadline[2])
