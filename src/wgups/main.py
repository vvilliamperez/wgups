# William Perez, STUDENT ID 001438917
import logging
import os
from logging import getLogger
import res
from wgups.delivery_manager import DeliveryManager
from wgups.utils import ingest_packages_from_file, ingest_distances_from_file, ingest_locations_from_file

logger = getLogger(__name__)
logging.basicConfig(level=logging.INFO, handlers=[logging.StreamHandler()])


def main()-> None:

    # Create hash tables to store the package
    # In python, these are implemented as Dictionaries
    # These two helper functions create Lists of Dictionaries.
    package_data = ingest_packages_from_file()
    distance_data = ingest_distances_from_file()
    location_data = ingest_locations_from_file()

    delivery_manager = DeliveryManager(package_data, distance_data, location_data)
    delivery_manager.start()
    logger.info("All packages delivered")


if __name__ == '__main__':
    main()
