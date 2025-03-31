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

        # Our custom PackageHashTable
        self.packages = PackageHashTable(initial_capacity=50)
        self.trucks = []

        # Create a fleet of trucks
        for i in range(min(TRUCK_FLEET_SIZE, DRIVER_CREW_SIZE)):
            self.trucks.append(DeliveryTruck(truck_id=i + 1, distance_data=self.distance_data))

        self.total_packages = 0
        self.default_tick_speed = None
        self.time = START_TIME

        # NEW: Dictionary that tracks which trucks each package can ride
        # Example structure: { package_id: {1, 2}, ... }
        self.truck_constraints: Dict[str, Set[int]] = {}

        # NEW: List of bundle-sets. Each set is a group of package IDs that must ride together.
        # Example: [ {"10","11","12"}, {"15","16"}, ... ]
        self.bundles: List[Set[str]] = []

        self.initialize_packages()

    # --------------------------
    # Existing Properties
    # --------------------------
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
        packages_unsorted = [p for p in self.packages.values() if p.status == PackageStatus.AT_HUB]
        return sorted(packages_unsorted, key=lambda pkg: pkg.deadline)

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
        return all(pkg.status == PackageStatus.DELIVERED for pkg in self.packages.values())

    # --------------------------
    # Main Simulation Loop
    # --------------------------
    def tick(self, seconds=1):
        if self.default_tick_speed is not None:
            seconds = self.default_tick_speed
        self.time += seconds

        if self.time == SPECIAL_UPDATE_TIME:
            self.special_update()

        if self.time == FLIGHT_ARRIVAL_TIME:
            logger.info("Flight has arrived — making delayed packages available.")
            for pkg in self.packages_unavailable:
                if pkg.package_ID == "9":
                    continue
                pkg.status = PackageStatus.AT_HUB

        # Run route assignment whenever a truck is free at the hub
        if any(t.status == TruckStatus.AT_HUB for t in self.trucks):
            self.run_route_algorithm(self.trucks_at_hub)

        # Update each truck
        for truck in self.trucks:
            truck.update(self.time, seconds=seconds)

        if self.time == EOD_IN_SECONDS:
            raise Exception("Reached midnight! Stopping simulation.")

    def start(self):
        while True:
            if self.all_packages_delivered():
                break
            self.tick()

        # Logging final time
        hours = self.time // 3600
        minutes = (self.time % 3600) // 60
        seconds = self.time % 60
        logger.info(f"Simulation complete. Time: {hours}:{minutes}:{seconds}")
        logger.info(f"All packages delivered.")

    def pause(self):
        pass

    # --------------------------
    # Modified Route Algorithm
    # --------------------------
    def run_route_algorithm(self, trucks_to_assign_routes):
        """
        Assign packages to each truck at the hub, respecting:
          - Truck constraints
          - Bundling constraints
          - Deadlines
          - Attempts to minimize driving distance,
        and ensures we add as many feasible items as possible
        before the truck departs.
        """
        # 1) Group all hub packages into bundle “items”
        available_items = self._get_available_items_as_bundles()

        for truck in trucks_to_assign_routes:
            current_location = truck.point_a  # The hub location
            manifest = []

            logger.info(f"--- Building manifest for Truck {truck.truck_id} ---")

            # Keep track of feasibility from the truck's "start_time"
            # You might consider the time the truck arrived, but we'll use self.time
            manifest_start_time = self.time

            # 2) We'll repeatedly try to add items until we can't add any more
            while True:
                if len(manifest) >= truck.available_capacity:
                    logger.info(f"Truck {truck.truck_id} is at capacity: {len(manifest)} items.")
                    break
                if not available_items:
                    logger.info(f"No more available items for Truck {truck.truck_id}.")
                    break

                best_item = None
                best_score = float('inf')
                best_idx = -1

                # Try each remaining item to see if it can fit
                for idx, item in enumerate(available_items):
                    # Check truck constraint
                    if not self._truck_can_carry_item(item, truck):
                        continue

                    # Try appending this item to a *temp* manifest
                    test_manifest = manifest + item
                    # Then do a quick route optimization
                    test_manifest_optimized = self.optimize_route_order(test_manifest, truck)

                    # Check if the new route meets all deadlines
                    if self.route_meets_deadlines(test_manifest_optimized, truck):
                        # If feasible, compute a priority score.
                        # You can do distance from current_location or
                        # recalculate total route distance, etc.
                        # We'll just do the distance from the last known location
                        # to the first package in 'item' as a quick tie-breaker.
                        distance_to_item = self._calculate_bundle_distance(current_location, item)
                        priority_score = self._compute_priority_score(item, distance_to_item)

                        if priority_score < best_score:
                            best_score = priority_score
                            best_item = item
                            best_idx = idx

                if best_item is None:
                    # Means we couldn't feasibly add *any* item
                    logger.info(f"Cannot add more items to Truck {truck.truck_id} without violating constraints.")
                    break
                else:
                    # Actually add the best_item to the manifest for real
                    manifest += best_item
                    current_location = best_item[0].destination  # simple approach
                    logger.info(
                        f"Truck {truck.truck_id} accepted item (size={len(best_item)}) with best score={best_score}.")
                    available_items.pop(best_idx)

            # 3) Final route optimization
            optimized_manifest = self.optimize_route_order(manifest, truck)

            # 4) Load them onto the truck & send it out (only if we have something)
            if optimized_manifest:
                truck.load(optimized_manifest)
                logger.info(f"Truck {truck.truck_id} loaded {len(optimized_manifest)} packages and is departing.")
                truck.start_route()
            else:
                logger.info(f"Truck {truck.truck_id} found no items to load this round.")

    # -- HELPER: Convert all AT_HUB packages into “items,” respecting bundles
    def _get_available_items_as_bundles(self) -> List[List[Package]]:
        """
        Gathers packages at the hub, groups any that share a bundle,
        and returns a list of list-of-Packages.
        (Each sub-list is a 'bundle item' or a single un-bundled package.)
        """
        # All packages currently at hub
        at_hub = [p for p in self.packages_at_hub]

        # Bucket by package_id for quick lookups
        pkg_map = {p.package_ID: p for p in at_hub}

        items = []
        used_ids = set()

        for bundle in self.bundles:
            # If ANY package in the bundle is at the hub, gather all that are at the hub
            # forming one “item.” If none are at the hub, skip.
            hub_subset = [pkg_map[pid] for pid in bundle if pid in pkg_map]
            if len(hub_subset) > 0:
                # This entire bundle is considered a single item
                items.append(hub_subset)
                # Mark them used
                used_ids.update([p.package_ID for p in hub_subset])

        # Now handle any package NOT in a declared bundle or not used yet
        for p in at_hub:
            if p.package_ID not in used_ids:
                # This package stands alone
                items.append([p])

        return items

    # -- HELPER: Check if truck can carry all packages in an item
    def _truck_can_carry_item(self, item: List[Package], truck: DeliveryTruck) -> bool:
        """
        True if *all* packages in this item are allowed on this truck
        (based on self.truck_constraints).
        """
        for pkg in item:
            # If no entry in truck_constraints, assume it can ride any truck
            allowed_trucks = self.truck_constraints.get(pkg.package_ID, set(range(1, TRUCK_FLEET_SIZE + 1)))
            if truck.truck_id not in allowed_trucks:
                return False
        return True

    # -- HELPER: Calculate distance to an item from current location
    def _calculate_bundle_distance(self, current_location: str, item: List[Package]) -> float:
        """
        Simple approach: distance from current_location to the *first* package’s destination
        (or you could average addresses if you wanted).
        """
        first_pkg = item[0]
        return get_distance(self.distance_data, current_location, first_pkg.destination)

    # -- HELPER: Compute your priority score for the entire item (bundle)
    def _compute_priority_score(self, item: List[Package], distance_to_item: float) -> float:
        """
        Adapt your existing scoring to handle multiple packages.
        For example, sum up cluster effects or pick the earliest deadline, etc.
        Below is a minimal example that sums a few factors.
        """
        # For cluster score, you might check how close these packages are to each other
        # or how many are near them at the hub. Below is a trivial example.

        # Example: We just take the earliest deadline among the item
        # and treat that as the item’s “deadline urgency.”
        earliest_deadline = min(pkg.deadline for pkg in item)
        if earliest_deadline == EOD_IN_SECONDS:
            time_urgency = EOD_IN_SECONDS
        else:
            time_urgency = max(1, earliest_deadline - self.time)

        # (Optional) compute a simple cluster score for these packages
        # For example, how many are in the same general area:
        cluster_score = len(item) - 1  # trivial approach: more packages = better cluster

        # Weighted priority, similar to your original logic:
        priority_score = (distance_to_item * 3) - (cluster_score * 1.5) + (time_urgency / 14400)

        return priority_score

    # -- HELPER: Check if all packages in item can meet their deadline
    def _can_meet_all_deadlines(self,
                                item: List[Package],
                                distance_to_item: float,
                                truck: DeliveryTruck,
                                start_time: float) -> bool:
        """
        Quick feasibility check:
         - Estimate arrival to first package
         - Then do a rough check that you can still deliver each package
           before its deadline (if it’s not EOD).

        If you want a more precise check, you’d simulate the route or rely on
        optimize_route_order’s result. But here we do a simple check.
        """
        # 1) Time to get from current location to the first package
        travel_time_sec = self._calculate_travel_time(distance_to_item, truck)
        arrival_time = start_time + travel_time_sec

        # 2) For each package in the bundle, check its deadline
        for pkg in item:
            if pkg.deadline != EOD_IN_SECONDS and arrival_time > pkg.deadline:
                return False
            # If you have multiple distinct addresses, you'd need
            # to add distances among them. This minimal version
            # checks only arrival to the first drop-off.
        return True

    # -- HELPER: Convert truck mph + distance to travel time in seconds
    def _calculate_travel_time(self, distance_miles: float, truck: DeliveryTruck) -> float:
        hours = distance_miles / truck.speed_in_mph
        return hours * 3600.0

    # --------------------------
    # Keep your route optimization, but ensure you keep bundles together
    # if they require the same truck. You could do a mini “2-opt” inside
    # each bundle if they have multiple addresses, but below is your existing approach.
    # --------------------------
    def optimize_route_order(self, manifest, truck):
        """
        Optimize the order of packages in a truck's manifest while respecting deadlines.
        Uses a simple 2-opt approach. Make sure you do NOT rearrange packages
        in a way that breaks any ‘must-deliver-together’ rule
        if that rule implies they arrive at the same time.
        """
        if len(manifest) <= 2:
            return manifest

        best_manifest = manifest.copy()
        best_distance = self.calculate_route_distance(best_manifest, truck)
        improved = True

        while improved:
            improved = False
            for i in range(1, len(best_manifest) - 2):
                for j in range(i + 1, len(best_manifest)):
                    new_manifest = best_manifest.copy()
                    # Swap two packages
                    new_manifest[i], new_manifest[j] = new_manifest[j], new_manifest[i]

                    # Check if new route meets deadlines
                    if self.route_meets_deadlines(new_manifest, truck):
                        new_distance = self.calculate_route_distance(new_manifest, truck)
                        if new_distance < best_distance:
                            best_manifest = new_manifest
                            best_distance = new_distance
                            improved = True
        return best_manifest

    def route_meets_deadlines(self, manifest, truck):
        current_time = self.time
        current_location = truck.point_a

        for package in manifest:
            distance = get_distance(self.distance_data, current_location, package.destination)
            travel_time_sec = self._calculate_travel_time(distance, truck)
            delivery_time = current_time + travel_time_sec

            if package.deadline != EOD_IN_SECONDS and delivery_time > package.deadline:
                return False

            current_time = delivery_time
            current_location = package.destination

        return True

    def calculate_route_distance(self, manifest, truck):
        if not manifest:
            return 0.0
        total_distance = get_distance(self.distance_data, truck.point_a, manifest[0].destination)
        for i in range(len(manifest) - 1):
            total_distance += get_distance(self.distance_data,
                                           manifest[i].destination,
                                           manifest[i + 1].destination)
        # Return to hub
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

        # --------------------------
        # Initialize packages + constraints
        # --------------------------

    def initialize_packages(self):
        for data in self.package_data:
            destination = self.lookup_location(data['full_address'])
            package = Package(
                package_ID=data['Package ID'],
                destination=destination,
                deadline_in_hhmmss=data['Delivery Deadline'],
                weight=data['Mass'],
                notes=data['Special Notes']
            )
            self.packages.insert(package.package_ID, package)

        logger.info(f"Added {len(self.packages.values())} packages to global system.")
        self.total_packages = len(self.packages.values())

        # Here’s how to handle your special notes differently:
        # Instead of physically loading them on a truck, just record constraints or bundles.
        packages_with_notes = [p for p in self.packages.values() if p.notes]
        for pkg in packages_with_notes:
            match pkg.notes:
                case 'Can only be on truck 2':
                    # Record this constraint
                    self.truck_constraints[pkg.package_ID] = {2}

                case 'Delayed on flight---will not arrive to depot until 9:05 am':
                    pkg.status = PackageStatus.UNAVAILABLE

                # Example of a bundling note:


        self.bundles.append({"13", "14", "15", "16", "19", "20"})


        self.packages.lookup_by_id("9").status = PackageStatus.UNAVAILABLE

        logger.info("Finished reading special notes.")

    def lookup_location(self, search_text) -> str:
        for row in self.location_data:
            if search_text in row['PackageText']:
                return row['Location']
        raise (Exception(f"Location {search_text} not found"))

    def special_update(self):
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
                nearest_truck.packages_on_truck.insert(1, route_to_package_9)
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
                package_9_copy = Package(package_9.package_ID, package_9.destination, package_9.deadline_in_hhmmss,
                                         package_9.weight, package_9.notes)
                package_9_copy.destination = self.lookup_location(revised_address)
                package_9_copy.note_on_delivery = "Delivered after correction!"
                self.trucks[package_9.truck_id - 1].load([package_9_copy])
            case PackageStatus.UNAVAILABLE:
                logger.info(f"Package 9 is unavailable.")
                logger.info("Revising route..")
                package_9.destination = self.lookup_location(revised_address)
                package_9.status = PackageStatus.AT_HUB
        logger.info(f"Package 9 updated... resuming route! \n\n")



