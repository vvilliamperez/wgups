import csv
import os
from logging import getLogger
from typing import Dict, List

import res

PACKAGE_FILE_NAME = "package_file.csv"
DISTANCE_FILE_NAME = "distance_data.csv"
logger = getLogger(__name__)


def ingest_distances_from_file()-> List[Dict]:
    distance_file_path = os.path.join(str(res.__path__[0]), DISTANCE_FILE_NAME)
    distance_data = csv_to_dict_list(distance_file_path)

    return distance_data


def ingest_packages_from_file() -> List[Dict]:
    package_file_path = os.path.join(str(res.__path__[0]), PACKAGE_FILE_NAME)
    logger.info(f" {package_file_path}")
    packages = csv_to_dict_list(package_file_path)

    logger.info(f"Loaded {len(packages)} packages from CSV")
    logger.info(f"{packages}")

    # Add full_address to each package
    for package in packages:
        package["full_address"] = f"{package['Address']}, {package['City']}, {package['State']} {package['Zip']}"

    return packages


def get_distance(data: List[Dict], location1: str, location2: str)-> float:
    for row in data:
        loc1, loc2 = row['Location1'], row['Location2']
        if (loc1 == location1 and loc2 == location2) or (loc1 == location2 and loc2 == location1):
            return row['Distance']
    return None


def csv_to_dict_list(csv_file_path: str)-> List[Dict]:
    dict_list = []
    with open(csv_file_path, mode='r', newline='', encoding='utf-8') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            dict_list.append(row)
    return dict_list
