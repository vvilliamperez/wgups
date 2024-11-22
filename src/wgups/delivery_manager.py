from logging import getLogger
from typing import List, Dict

from wgups.delivery_truck import DeliveryTruck, TruckStatus
from wgups.package import PackageStatus, Package
from wgups.utils import get_distance

TRUCK_FLEET_SIZE = 3
DRIVER_CREW_SIZE = 2

START_TIME = 32755 # 8:00:00 AM in seconds

SPECIAL_UPDATE_TIME = 37200 # 10:20:00 AM in seconds

logger = getLogger(__name__)

class DeliveryManager:

    def __init__(self, package_data: List[Dict], distance_data: List[Dict], location_data: List[Dict]):

        self.package_data = package_data
        self.distance_data = distance_data
        self.location_data = location_data

        self.packages = []
        self.initialize_packages()

        self.trucks = []
        # Create a fleet of trucks, based on the TRUCK_FLEET_SIZE and DRIVER_CREW_SIZE
        for i in range(min(TRUCK_FLEET_SIZE, DRIVER_CREW_SIZE)):
            self.trucks.append(DeliveryTruck(truck_id=i+1, distance_data=self.distance_data))

        self.time = START_TIME

    @property
    def trucks_at_hub(self):
        return [truck for truck in self.trucks if truck.status == TruckStatus.AT_HUB]

    @property
    def trucks_in_transit(self):
        return [truck for truck in self.trucks if truck.status == TruckStatus.EN_ROUTE]

    @property
    def trucks_returning(self):
        return [truck for truck in self.trucks if truck.status == TruckStatus.RETURNING]

    @property
    def packages_at_hub(self):
        return [package for package in self.packages if package.status == PackageStatus.AT_HUB]

    @property
    def packages_on_trucks(self):
        packages = []
        for truck in self.trucks:
            packages.extend(truck.packages_on_truck)
        return packages

    @property
    def packages_delivered(self):
        packages = []
        for truck in self.trucks:
            packages.extend(truck.packages_delivered)
        return packages


    def all_packages_delivered(self):
        return len(self.packages_delivered) == len(self.packages)

    def tick(self, seconds=1):
        """
        Update the simulation by a number of seconds

        If any trucks are at the hub, run the route algorithm to assign packages to trucks at the hub.
        Algorithm is dependent on the remaining packages and the available drivers.

        :param seconds:
        :return:
        """
        self.time += seconds

        if self.time == SPECIAL_UPDATE_TIME:
             # Update package 9 - Correct address: 410 S State St., Salt Lake City, UT 84111
            pass

        if any(truck.status == TruckStatus.AT_HUB for truck in self.trucks):
            self.run_route_algorithm(self.trucks_at_hub)

        for truck in self.trucks:
            truck.update(seconds)

        if self.time == 86400:
            raise Exception("Reached midnight! Stopping simulation.")

    def lookup_location(self, search_text)-> str:
        for row in self.location_data:
            if search_text in row['PackageText']:
                return row['Location']
        raise(Exception(f"Location {search_text} not found"))

    def run_route_algorithm(self, trucks_to_assign_routes):
        print(trucks_to_assign_routes)
        # Assign packages to trucks, based on the remaining packages and the available drivers
        # Based on all available information, assigns packages to be delivered in order to trucks

        # Sort packages by deadline to prioritize urgent deliveries
        self.packages = sorted(self.packages, key=lambda pkg: pkg.deadline)

        # Assign packages to trucks using a greedy nearest neighbor algorithm
        # The distance is calculated using the distance data
        packages_at_hub = self.packages_at_hub
        for truck in trucks_to_assign_routes:
            current_location = truck.point_a
            manifest = []

            while len(manifest) < truck.max_capacity:
                # Find the nearest package
                nearest_package = None
                nearest_distance = float('inf')

                for package in packages_at_hub:
                    if package not in manifest:
                        distance = get_distance(self.distance_data, current_location, package.destination)
                        if float(distance) < float(nearest_distance):
                            nearest_package = package
                            nearest_distance = distance
                if nearest_package is not None:
                    manifest.append(nearest_package)
                    # Update the current location
                    current_location = nearest_package.destination
                else:
                    break
            truck.load(manifest)
            truck.start_route()

        print(self.packages)



    def start(self):
        while True:
            if self.all_packages_delivered():
                break
            self.tick()

        # convert time to hh:mm:ss
        hours = self.time // 3600
        minutes = (self.time % 3600) // 60
        seconds = self.time % 60
        logger.info(f"Simulation complete. Time: {hours}:{minutes}:{seconds}")

    def pause(self):
        pass

    def initialize_packages(self)-> None:
        # Extract data from each dictionary and convert to a Package object
        for data in self.package_data:

            destination = self.lookup_location(data['full_address'])
            package = Package(package_ID=data['Package ID'], destination=destination, deadline_in_hhmmss=data['Delivery Deadline'], weight=data['Mass'], notes=data['Special Notes'])
            self.packages.append(package)
            logger.info(f"Added package {package.package_ID}")
        logger.info(f"Added {len(self.packages)} packages")


