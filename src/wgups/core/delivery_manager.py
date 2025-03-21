from copy import copy
from logging import getLogger
from typing import List, Dict

from wgups.constants import TRUCK_FLEET_SIZE, DRIVER_CREW_SIZE, START_TIME, SPECIAL_UPDATE_TIME, FLIGHT_ARRIVAL_TIME, \
    EOD_IN_SECONDS
from wgups.core.delivery_truck import DeliveryTruck, TruckStatus
from wgups.core.package import PackageStatus, Package
from wgups.core.special_route import SpecialRoute
from wgups.utils import get_distance
from wgups.data_structures.min_heap import MinHeap
from wgups.data_structures.hash_table import PackageHashTable

logger = getLogger(__name__)

class DeliveryManager:

    def __init__(self, package_data: List[Dict], distance_data: List[Dict], location_data: List[Dict]):

        self.package_data = package_data
        self.distance_data = distance_data
        self.location_data = location_data


        # PART E - Custom hash table to store packages
        self.packages = PackageHashTable(initial_capacity=50)
        self.trucks = []

        # Create a fleet of trucks, based on the TRUCK_FLEET_SIZE and DRIVER_CREW_SIZE
        for i in range(min(TRUCK_FLEET_SIZE, DRIVER_CREW_SIZE)):
            self.trucks.append(DeliveryTruck(truck_id=i+1, distance_data=self.distance_data))

        self.total_packages = 0
        self.initialize_packages()
        self.default_tick_speed = None

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
        return [package for package in self.packages.values() if package.status == PackageStatus.AT_HUB]

    @property
    def packages_at_hub_sorted(self):
        packages_unsorted = [package for package in self.packages.values() if package.status == PackageStatus.AT_HUB]
        packages = sorted(packages_unsorted, key=lambda pkg: pkg.deadline)
        return packages

    @property
    def packages_unavailable(self):
        return [package for package in self.packages.values() if package.status == PackageStatus.UNAVAILABLE]

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
        return [package for package in self.packages.values() if package.status != PackageStatus.DELIVERED] == []

    def tick(self, seconds=1):
        """
        Update the simulation by a number of seconds

        If any trucks are at the hub, run the route algorithm to assign packages to trucks at the hub.
        Algorithm is dependent on the remaining packages and the available drivers.

        :param seconds:
        :return:
        """
        if self.default_tick_speed is not None:
            seconds = self.default_tick_speed
        self.time += seconds

        if self.time == SPECIAL_UPDATE_TIME:
             # Update package 9 with revised address
            revised_address = "410 S State St, Salt Lake City, UT 84111"
            logger.info("\n\n")
            logger.warning(f"Special update!! Updating package 9 with revised address: {revised_address}")

            package_9 = [package for package in self.packages.values() if package.package_ID == "9"][0]

            match package_9.status:
                # if package 9 is delivered, go get it and redeliver
                case PackageStatus.DELIVERED:
                    # find truck nearest to package 9
                    logger.warning("\n\nPackage 9 has already been delivered. Will need to pick up and redeliver.")
                    logger.info("Finding nearest truck to package 9")

                    nearest_truck = None
                    nearest_distance = float('inf')
                    for truck in self.trucks:
                        distance = get_distance(self.distance_data, truck.point_b, package_9.destination)
                        if distance < nearest_distance:
                            nearest_truck = truck
                            nearest_distance = distance
                    # add special route to nearest truck
                    # finishes current delivery, heads to and picks up package 9,
                    route_to_package_9 = SpecialRoute(package_9.destination, reason="Pick up package 9")
                    route_to_package_9.truck_id = nearest_truck.truck_id
                    nearest_truck.packages_on_truck.insert(1,route_to_package_9)
                    # Update original package 9's destination
                    package_9.destination = self.lookup_location(revised_address)
                    package_9.note_on_delivery = "Delivered to wrong address initially"
                    # delivers package 9, continues route
                    package_9_copy = copy(package_9)
                    package_9_copy.note_on_delivery = "Delivered after correction!"
                    nearest_truck.packages_on_truck.insert(2, package_9_copy)
                    logger.info(f"Truck {nearest_truck.truck_id} is making a special pickup and delivery for package 9")
                # if package 9 is on truck, update the destination
                case PackageStatus.ON_TRUCK:
                    logger.info(f"Package 9 is on truck {package_9.truck_id}.")
                    logger.warning("Revising routing, but may cause delay")
                    package_9.destination = self.lookup_location(revised_address)
                    logger.info(f"Package 9 destination updated to {revised_address}")
                case PackageStatus.AT_HUB:
                    logger.info(f"Package 9 is at hub. Updating destination.")
                    package_9.destination = self.lookup_location(revised_address)
                    logger.info(f"Package 9 destination updated to {revised_address}")
                case PackageStatus.IN_TRANSIT:
                    logger.info(f"Package 9 is in transit on truck {package_9.truck_id}.")
                    logger.info("Revising routing, but may cause delay.")
                    package_9.destination = self.lookup_location(revised_address)
                    logger.info(f"Package 9 destination updated to {revised_address}")
                case PackageStatus.NEXT_STOP:
                    logger.info(f"Package 9 is next stop")
                    package_9.note_on_delivery = "Went to wrong address! Did not deliver."
                    # Continue to "deliver" package 9, but add a duplicate to the manifest
                    # so that the truck will deliver the revised package 9
                    package_9_copy = Package(package_9.package_ID, package_9.destination, package_9.deadline_in_hhmmss, package_9.weight, package_9.notes)
                    package_9_copy.destination = self.lookup_location(revised_address)
                    package_9_copy.note_on_delivery = "Delivered after correction!"
                    self.trucks[package_9.truck_id - 1].load([package_9_copy])
                case PackageStatus.UNAVAILABLE:
                    logger.info(f"Package 9 is unavailable.")
                    logger.info("Revising route..")
                    package_9.destination = self.lookup_location(revised_address)
            logger.info(f"Package 9 updated... resuming route! \n\n")


        if self.time == FLIGHT_ARRIVAL_TIME:
            logger.info("\n\n")
            logger.info("Flight has arrived")
            # Flight has arrived, mark packages available
            for package in self.packages_unavailable:
                package.status = PackageStatus.AT_HUB
                logger.info(f"Package {package.package_ID} is now available")
            logger.info("All packages are now available\n\n")


        if any(truck.status == TruckStatus.AT_HUB for truck in self.trucks):
            self.run_route_algorithm(self.trucks_at_hub)

        for truck in self.trucks:
            truck.update(self.time, seconds=seconds)

        if self.time == EOD_IN_SECONDS:
            raise Exception("Reached midnight! Stopping simulation.")

    def lookup_location(self, search_text)-> str:
        for row in self.location_data:
            if search_text in row['PackageText']:
                return row['Location']
        raise(Exception(f"Location {search_text} not found"))

    def run_route_algorithm(self, trucks_to_assign_routes):
        """
        Assign packages to trucks, optimizing for minimum distance while meeting deadlines.
        Uses a modified nearest neighbor algorithm with clustering and deadline constraints.

        :param trucks_to_assign_routes: List of trucks available at the hub
        :return: None
        """
        # First, sort packages by deadline to ensure we handle urgent deliveries
        packages_heap = MinHeap()
        for package in self.packages_at_hub:
            packages_heap.push(package)
        
        # Convert to list for easier manipulation
        available_packages = []
        while pack := packages_heap.pop():
            available_packages.append(pack)

        for truck in trucks_to_assign_routes:
            current_location = truck.point_a  # Start at hub
            manifest = []
            estimated_delivery_time = self.time  # Track estimated delivery time

            while len(manifest) < truck.available_capacity and available_packages:
                best_package = None
                best_score = float('inf')
                best_idx = -1

                # Look for clusters of packages - try to find packages close to current location
                for idx, package in enumerate(available_packages):
                    distance_to_package = get_distance(self.distance_data, current_location, package.destination)
                    
                    # Calculate estimated delivery time for this package
                    travel_time_hours = distance_to_package / truck.speed_in_mph
                    estimated_time = estimated_delivery_time + (travel_time_hours * 3600)  # Convert hours to seconds
                    
                    # Skip if we can't meet the deadline
                    if package.deadline != EOD_IN_SECONDS and estimated_time > package.deadline:
                        continue

                    # Calculate cluster score - how many other packages are nearby?
                    cluster_score = 0
                    for other_package in available_packages:
                        if other_package != package:
                            distance_between = get_distance(self.distance_data, package.destination, other_package.destination)
                            if distance_between < 2:  # Tighter cluster radius for better optimization
                                cluster_score += 1

                    # Priority score calculation:
                    # 1. Distance is primary factor (higher weight for shorter distances)
                    # 2. Cluster bonus (packages near each other)
                    # 3. Time until deadline (normalized and weighted less)
                    time_urgency = max(1, package.deadline - self.time) if package.deadline != EOD_IN_SECONDS else EOD_IN_SECONDS
                    
                    # New priority score formula optimized for shorter routes
                    priority_score = (distance_to_package * 3) - (cluster_score * 1.5) + (time_urgency / 14400)

                    if priority_score < best_score:
                        best_score = priority_score
                        best_package = package
                        best_idx = idx

                if best_package:
                    manifest.append(best_package)
                    available_packages.pop(best_idx)
                    current_location = best_package.destination
                    # Update estimated delivery time using correct speed calculation
                    distance = get_distance(self.distance_data, current_location, best_package.destination)
                    travel_time_hours = distance / truck.speed_in_mph
                    estimated_delivery_time += (travel_time_hours * 3600)  # Convert hours to seconds
                else:
                    # If we can't find a suitable next package, stop loading this truck
                    break

            # After building manifest, optimize the route order
            optimized_manifest = self.optimize_route_order(manifest, truck)
            truck.load(optimized_manifest)
            truck.start_route()

    def optimize_route_order(self, manifest, truck):
        """
        Optimize the order of packages in a truck's manifest while respecting deadlines.
        Uses a simple 2-opt optimization approach.
        """
        if len(manifest) <= 2:
            return manifest

        best_manifest = manifest.copy()
        best_distance = self.calculate_route_distance(best_manifest, truck)
        improved = True

        while improved:
            improved = False
            for i in range(1, len(manifest) - 2):
                for j in range(i + 1, len(manifest)):
                    new_manifest = best_manifest.copy()
                    # Swap two packages
                    new_manifest[i], new_manifest[j] = new_manifest[j], new_manifest[i]
                    
                    # Check if new route meets all deadlines
                    if self.route_meets_deadlines(new_manifest, truck):
                        new_distance = self.calculate_route_distance(new_manifest, truck)
                        if new_distance < best_distance:
                            best_manifest = new_manifest
                            best_distance = new_distance
                            improved = True

        return best_manifest

    def route_meets_deadlines(self, manifest, truck):
        """Check if a proposed route meets all package deadlines."""
        current_time = self.time
        current_location = truck.point_a

        for package in manifest:
            distance = get_distance(self.distance_data, current_location, package.destination)
            travel_time_hours = distance / truck.speed_in_mph
            delivery_time = current_time + (travel_time_hours * 3600)  # Convert hours to seconds
            
            if package.deadline != EOD_IN_SECONDS and delivery_time > package.deadline:
                return False
                
            current_time = delivery_time
            current_location = package.destination

        return True

    def calculate_route_distance(self, manifest, truck):
        """Calculate total distance for a proposed route."""
        if not manifest:
            return 0

        total_distance = get_distance(self.distance_data, truck.point_a, manifest[0].destination)
        
        for i in range(len(manifest) - 1):
            total_distance += get_distance(self.distance_data, 
                                        manifest[i].destination,
                                        manifest[i + 1].destination)

        # Add return distance to hub
        total_distance += get_distance(self.distance_data, manifest[-1].destination, truck.point_a)
        
        return total_distance

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
        logger.info(f"All {len(self.packages_delivered)} routes ran. ({len(self.packages_delivered)-self.total_packages} extra routes made for special deliveries)")

    def pause(self):
        pass

    def initialize_packages(self)-> None:
        # Extract data from each dictionary and convert to a Package object
        for data in self.package_data:

            destination = self.lookup_location(data['full_address'])
            package = Package(package_ID=data['Package ID'], destination=destination, deadline_in_hhmmss=data['Delivery Deadline'], weight=data['Mass'], notes=data['Special Notes'])
            self.packages.insert(package.package_ID, package)

            #logger.info(f"Added package {package.package_ID}")

        logger.info(f"Added {len(self.packages.values())} packages to global system\n\n")
        self.total_packages = len(self.packages.values())
        logger.info("Handling special delivery notes:")

        # Handle special notes
        packages_with_notes = [package for package in self.packages.values() if package.notes != '']
        for package in packages_with_notes:
            match package.notes:
                case 'Can only be on truck 2':
                    self.trucks[1].load([package])
                    logger.info(f"Loaded package {package.package_ID} onto Truck 2")
                case 'Delayed on flight---will not arrive to depot until 9:05 am':
                    package.status = PackageStatus.UNAVAILABLE
                    logger.info(f"Package {package.package_ID} is delayed on a flight and unavailable until 9:05 am")
                    # Check later if package is available
        logger.info("All finished with special notes.\n\n")


