# WGUPS Route Optimization Project


# Part A - Self Adjusting Algorithm

I'm using a greedy nearest neighbor algorithm with a priority score to assign packages to trucks. 
It starts with a sorted list of the packages available at the hub using a bundle-aware min-heap.
Then the algorithm assigns packages to trucks based on the priority score,
which is calculated based on the deadline and distance to the next package as well as accounting 
for clustering groups of packages in the same area. 

The algorithm repeats this for each package, and each truck, 
until all the trucks are full or there are no more packages left to assign.

This algorithm runs anytime there is a truck at the hub, and packages available to be delivered.

# Part B - Program Overview

## 1. Algorithm Overview in Pseudocode

BEGIN run_route_algorithm
    // Step 1: Sort packages by deadline using bundle-aware min heap
    CREATE min_heap
    COLLECT packages from hub
    
    // Add packages to min heap, respecting bundles
    BEGIN package sorting
        GET next bundle from bundles
        CHECK if any packages in bundle are at hub
            COLLECT all hub packages from bundle
            CREATE bundle_item
            ASSIGN bundle_item to min_heap using earliest deadline
            MARK packages as used
        END CHECK
        
        GET next package from hub
        CHECK if package not in any bundle or not used
            CREATE single_item
            ASSIGN single_item to min_heap using deadline
        END CHECK
        CONTINUE until no more packages
    END package sorting
    
    CREATE available_items list
    BEGIN heap extraction
        GET item from min_heap
        ASSIGN item to available_items
        CONTINUE until min_heap empty
    END heap extraction

    // Step 2: Assign items to each available truck
    COLLECT trucks at hub
    BEGIN truck assignment
        GET next truck
        ASSIGN starting point to current_location
        CREATE manifest list
        INITIALIZE estimated_delivery_time
        
        BEGIN item assignment
            CHECK manifest size < truck capacity
            CHECK available_items not empty
            
            ASSIGN infinity to best_score
            
            BEGIN find best item
                GET next item from available_items
                CHECK if truck can carry all packages in item
                    CALCULATE distance_to_item
                    CALCULATE estimated_delivery_time
                    
                    CHECK can meet all deadlines in item
                        // Calculate cluster score
                        INITIALIZE cluster_score to 0
                        BEGIN find nearby items
                            GET other_item from available_items
                            CALCULATE distance_between items
                            IF distance < 2 miles
                                INCREMENT cluster_score
                            END IF
                        END find nearby items
                        
                        // Calculate priority score with new weights
                        CALCULATE time_urgency using earliest deadline in item
                        SET priority_score = (distance * 3) - (cluster_score * 1.5) + (time_urgency / 14400)
                        
                        CHECK priority_score < best_score
                            UPDATE best_score
                            UPDATE best_item
                        END CHECK
                    END CHECK
                END CHECK
            END find best item
            
            CHECK best_item exists
                APPEND all packages from best_item to manifest
                UPDATE available_items
                UPDATE current_location
                UPDATE estimated_delivery_time
            END CHECK
            
            CONTINUE until manifest full or no items
        END item assignment
        
        // Step 3: Optimize final route
        BEGIN route optimization
            CALCULATE initial_route_distance
            
            WHILE route can be improved AND iterations < max_iterations
                FOR each possible package swap in sorted order
                    CREATE new_route_order
                    CHECK new route meets all deadlines
                        CALCULATE new_route_distance
                        IF new_route_distance < best_distance - epsilon
                            UPDATE best_route
                            UPDATE best_distance
                            SET improved to true
                        END IF
                    END CHECK
                END FOR
            END WHILE
        END route optimization
        
        LOAD optimized route to truck
        START truck route
        
        CONTINUE until all trucks checked
    END truck assignment
END run_route_algorithm

## 2. Programming Environment

This project is implemented using Python 3.13. The code is written with compatibility for Python 3.8 or later. Below are some details about the programming environment and resources used:

- Python Standard Library: The code relies solely on the standard library to ensure portability and ease of use.

- tkinter: A simple GUI is built using tkinter. Note that tkinter is not installed by default in some Python distributions, so users may need to ensure that it is available in their Python environment.

The IDE used was PyCharm 2024.2.4 (Professional Edition)
Build #PY-242.23726.102, built on October 22, 2024
Licensed to William Perez
Subscription is active until May 4, 2025.
For educational use only.



### Preprocessed Data
A `/res` folder contains preprocessed data files used by the algorithm. The following files are included:
- distance_data.csv: Contains the distances between all locations.
- location_lookup.csv: Maps written addresses (as seen on the packages) to actual addresses used in the system.
- package_file.csv: Contains all package data.

These files were preprocessed manually using the provided Excel files before being converted into CSV format.

## 3. Time Space Complexity Analysis
For the purposes of algorithm analysis, I have separated these variables as they are distinct and not directly related to each other:
- $n$: Number of packages to be delivered.
- $t$: Number of trucks at the hub.
- $k$: Number of times the route algorithm is called.
- $b$: Number of bundles (typically much smaller than n).

### Big O Notation Analysis

- Route Algorithm `run_route_algorithm()::delivery_manager.py` (Greedy Nearest Neighbor with Priority Score Approach):
  - Time Complexity: $O(t * n^3)$ where n is the number of packages to be delivered and t is the number of trucks at the hub. 
    - Treating all data as constant, the time complexity is $O(n^3)$.
    This complexity arises from three nested operations:
      1. Iterating through each package slot (n)
      2. Evaluating each remaining item as next candidate (n)
      3. Calculating cluster score by checking nearby items (n)
    - Additional $O(n^2)$ complexity from route optimization using 2-opt
    - The bundle-aware sorting step is $O(n * log(n))$, but the dominant time complexity remains the route assignment and clustering step.
  - Space Complexity: $O(n)$ due to the linear storage of the data for the priority score calculation for each package. 

- Bundle-Aware Sorting Step `MinHeap::min_heap.py` (Min-Heap Sort with Bundle Support):
  - Time Complexity: $O(n * log(n))$ due to the use of a min-heap to sort the items by deadline.
    - Building the min-heap: $O(n)$ for n insertions
    - Each insertion/extraction: $O(log(n))$
    - Bundle handling adds $O(b)$ overhead for bundle processing
    - Total for n elements: $O(n * log(n))$
  - Space Complexity: $O(n)$ due to the storage of the items in the heap array.

- Preprocessing Step:
  - Time Complexity: $O(n)$ for single-pass processing of package and distance data.
  - Space Complexity: $O(n)$ for storing the processed data.

- Overall Complexity:
  - Time Complexity: $O(k * t * n^3)$ due to the dominant time complexity of the route algorithm's nested loops and clustering calculations.
    - Treating all data as constant, the time complexity is $O(n^3)$. 
  - Space Complexity: $O(k * t * n)$ due to the storage of packages and manifests across multiple algorithm runs.
    - Treating all data as constant, the space complexity is $O(n)$.

## 4. Scalability and Adaptability 

The algorithm is designed to be scalable and adaptable to handle a large number of packages and trucks.
- Scalability:
  - The algorithm can handle a large number of packages and trucks efficiently due to its time complexity of O(n^2) for the route assignment step.
  - The use of a greedy nearest neighbor approach allows for optimization of routes even with a large number of packages.
- Adaptability:
  - The algorithm can adapt to changes in the number of packages, trucks, and delivery locations.
  - The route algorithm is ran each time there is a truck at the hub, and uses the most up to date information to assign packages to trucks.
  - In addition to the routing algorithm, the system updates the packages across the network if the address was changed or the package was delayed.
    - If the package is on a truck or at the hub and the address was changed, the system will update the truck's manifest and reroute the truck to the new address.
    - If the package was delivered incorrectly, we send a special route to pick up the package and deliver it to the correct address.

## 5. Efficiency and Maintainability

The program is written using object orientated principles to ensure modularity and maintainability. 

The main program logic is in `main.py`.
- The program is able to be called with the `--cli` command line argument to run the full simulation with no GUI.
- Default behaviour will set up the Tkinter GUI and allow the user to interact with the program. TKinter should be installed with most standard Python distributions.

Small helper functions are in `utils.py`

Constants are stored in `constants.py`

The core object classes live in `/core` and consist of:
- `DeliveryManager`: Manages the delivery process and assigns packages to trucks.
- `DeliverTruck`: Represents a delivery truck with a capacity, current location, manifest, and speed and status.
- `Package`: Represents a package with a destination, deadline, and status.
- `SpecialRoute`: Represents a route that is not a package. Used for rerouting trucks to pick up or deliver incorrectly delivered packages. 
This inherites from `Package` and has a special delivery note.

Data structures are stores in `/data_structures`
- `MinHeap`: A min-heap data structure used to sort packages by deadline.

- `PackageHashTable`: A hash table data structure used to store and quickly lookup package data by package ID.

- `AVLTree (UNUSED)`: An AVL tree data structure used to store the package data for quick lookup by package ID. (Unused)

The data structures can easily be swapped in and out for the main route claogirhm in `DeliveryManager.py` 
to test different data structures for performance.


## 6.  Strengths and weaknesses of the MinHeap data structure

### Strengths
- **Efficient Initial Sort**: The MinHeap provides O(n log n) sorting of packages by deadline, ensuring urgent deliveries are considered first in the routing algorithm
- **Priority Maintenance**: The heap property ensures that packages with earlier deadlines are always at the root
- **Space Efficiency**: The array-based implementation uses minimal extra space beyond the package references
- **Quick Access to Most Urgent**: O(1) access to the package with the earliest deadline
- **Efficient Updates**: O(log n) operations for both inserting new packages and removing the most urgent package

### Weaknesses
- **Single Priority Key**: The implementation only sorts by deadline, while the actual routing decisions need to consider multiple factors (distance, clustering, etc.)
- **Loss of Original Order**: Once packages are extracted from the heap into the available_packages list, the deadline ordering must be balanced against other routing factors
- **No Direct Access**: Cannot efficiently access or update packages in the middle of the heap
- **Limited Flexibility**: Cannot easily modify the priority criteria without rebuilding the heap

# Part D - Self Adjusting Data Structure

I'm using a min-heap data structure to pre-sort packages by deadline before they are fed into the routing algorithm.
This is implemented in the `MinHeap` class in `min_heap.py` using a list-based binary heap implementation.

The min-heap is used specifically in the `run_route_algorithm` method of `DeliveryManager` where it:
1. Takes all packages currently at the hub
2. Sorts them by deadline using the min-heap
3. Extracts them in deadline order into an `available_packages` list
4. This pre-sorted list is then used by the routing algorithm to ensure urgent packages are considered first

The relationship between the packages being stored in the min-heap is based on the deadline of the packages.


The min-heap maintains the heap property through standard heapification operations:
- `_heapify_up`: Maintains heap property when pushing new packages
- `_heapify_down`: Maintains heap property when popping packages
- `_swap`: Helper function for swapping elements during heapification

# Part E - Hash Table for Packages

I've implemented a hash table in `hash_table.py` for the packages. 
I'm using the package ID as the key, and the package object as the value. 
Each hash node contains all the regular package object data as set up in `package.py`

The hash table also supports dictionary-style access:
```python
# Get a package by ID
package = hash_table[package_id]

# Check if package exists
if package_id in hash_table:
    # do something
```

# Part F - Lookup Functions

The hash table implementation provides several lookup functions with different capabilities:

1. `lookup(self, **criteria)`: A flexible generic lookup function that can search for packages based on any combination of attributes:
   - `package_ID`: The unique identifier of the package
   - `destination`: The delivery location address
   - `deadline`: The delivery deadline in seconds after midnight
   - `weight`: The package weight
   - `notes`: Any special notes about the package
   - `delivered_at_time`: When the package was delivered (in seconds after midnight)
   - `status`: The package status (PackageStatus enum)
   - `truck_id`: The ID of the truck the package is assigned to
   - `note_on_delivery`: Any notes added during delivery
   
   Example usage:
   ```python
   # Find packages with specific deadline and status
   packages = hash_table.lookup(deadline=32400, status=PackageStatus.AT_HUB)
   
   # Find packages by destination and weight
   packages = hash_table.lookup(destination="410 S State St", weight=15)
   ```

2. `lookup_by_id(self, package_id)`: A fast O(1) lookup function specifically for finding packages by their ID
   - Uses direct hash table access
   - Returns a single package or None if not found
   - Most efficient when you know the package ID

If a package ID is not found, the lookup functions will either return None or an empty list, depending on the function used. This allows for safe operation without raising exceptions during normal use.

# Part G - Screenshots of the system at work
It is difficult to show the system at work in a single screenshot, 
but I have included logs that contain the output of the package statuses at the reuqested times.
There simulation completes at 11:12am, so I have included logs for 9:00am, 10:00am, and 11:12am.
This last log would be the same as 12pm.

To accomplish the same log, a user can run the program, and use the `Tick Number of Seconds` button
to advance the simulation to the desired time. To get to 9:00am, input `3600` seconds. Then press `Check All Packages Status`.
To get to 10:00am, input another `3600` seconds. Then press `Check All Packages Status`.
To get to 11:12am, press `Run to Complition` seconds. Then press `Check All Packages Status`.
The simulation completes all deliveries by 11:12am and does not proceed. 

- [9:00am](/0900log.txt)
- [10:00am](/1000log.txt)
- [11:12am](/1112.txt)

# Part H - Screenshot of Successful Completion and Total Miles

Completion Screenshot:
![Completion Screenshot](/CompletionScreenshot.png)

# Part I - Justification of the algorithm

The greedy nearest neighbor algorithm with priority score approach is a good choice for this problem due to the following reasons:
- **Efficiency**: The algorithm has a time complexity of O(n^2) for the route assignment step, which is sufficient for handling a large number of packages and trucks.
- **Adaptability**: The algorithm can adapt to changes in the number of packages, trucks, and delivery locations.
- **Priority Score**: The priority score calculation based on the deadline and distance allows for optimization of routes based on urgency and distance. This allows for tweaking the weight of the deadline and distance to optimize the routes.

Two other algorithms that could be considered are:
- **Greedy Algorithm**: A simple greedy algorithm that assigns packages to trucks based on the closest package at each step.
  - This algorithm may not consider the urgency of the delivery. It may also not self adjust well as new information is available. 
- **Nearest Neighbor Algorithm**: A nearest neighbor algorithm that assigns packages to trucks based on the closest package. 
  - Similar to the greedy algorithm, this may not consider the urgency of the delivery. It may also not self adjust well as new information is available.


# Part J - Reflection

If I were to do this project again, I would adjust the algorithm to consider the current location of all trucks when assigning packages.
Currently, the algorithm only runs when one or more trucks are at the hub, and assigns packages based on that information. (Trucks and packages at hub).
In a more optimal system, the algorithm could run at each step of the way taking into account the location of all trucks. 
This could allow for:
- **truck to truck transfers**
- **considering trucks that may be incoming to the hub**
- **rerouting trucks to return packages to the hub for another truck to pick up**
- **returning to the hub to pick up new packages that have arrived**

# Part K - Data Structure Analysis

## K1: Data Structures Used

This implementation uses two primary data structures:

1. **Min Heap** (`MinHeap` class):
   - Used for sorting packages by deadline before route assignment
   - Maintains packages in a binary heap where parent nodes have earlier deadlines than children
   - Implemented using a dynamic array (Python list)

2. **Hash Table** (`PackageHashTable` class):
   - Used for storing and retrieving package data
   - Uses chaining for collision resolution via linked lists
   - Implemented with a fixed initial capacity of 40 buckets

### K1A: Efficiency (Big O Analysis)

**Min Heap Operations:**
- Insert (push): O(log n)
- Extract minimum (pop): O(log n)
- Build heap: O(n)
- Space complexity: O(n)

**Hash Table Operations:**
- Insert: O(1) average case, O(n) worst case
- Lookup by ID: O(1) average case, O(n) worst case
- Generic lookup: O(n)
- Space complexity: O(n)

### K1B: Overhead Analysis

**Min Heap Scaling:**
- Space usage grows linearly with the number of packages (O(n))
- Each package requires:
  - Reference to package object
  - Array overhead for dynamic resizing
- Memory overhead is minimal as it's a temporary structure used only during route assignment

**Hash Table Scaling:**
- Space usage is O(n) where n is the number of packages
- Additional overhead per package:
  - HashNode object (key, package reference, next pointer)
  - Collision chain pointers
- Fixed bucket array size (40) means more collisions as n grows
- Could be optimized by implementing dynamic resizing

### K1C: System Scale Implications

**Impact of Additional Trucks:**
- Min Heap: No direct impact on structure
- Hash Table: No direct impact on structure
- Indirect effects:
  - More concurrent package status updates
  - More frequent lookups for route optimization

**Impact of Additional Cities:**
- Min Heap: No direct impact on structure
- Hash Table: No direct impact on structure
- Indirect effects:
  - Larger package objects (more address data)
  - More complex route calculations

## K2: Alternative Data Structures

### K2A: Comparison of Alternatives

**For Package Sorting (Currently Min Heap):**
1. **Sorted Array:**
   - Pros: Simple implementation, good cache locality
   - Cons: O(n) insertion, O(n) removal
   - Why not chosen: Less efficient for dynamic updates

2. **Binary Search Tree:**
   - Pros: O(log n) operations if balanced
   - Cons: Can become unbalanced, more complex implementation
   - Why not chosen: Min heap better guarantees for priority operations

3. **Priority Queue:**
   - Pros: Similar performance to min heap
   - Cons: Less control over implementation details
   - Why not chosen: Custom min heap provides more flexibility

**For Package Storage (Currently Hash Table):**
1. **AVL Tree:**
   - Pros: Guaranteed O(log n) operations, sorted traversal
   - Cons: More complex implementation, higher memory overhead
   - Why not chosen: Hash table provides better average-case lookup

2. **Array/List:**
   - Pros: Simple implementation, good cache locality
   - Cons: O(n) lookup time, no efficient ID-based access
   - Why not chosen: Poor performance for random access by ID

3. **Dictionary (Python's built-in):**
   - Pros: Optimized implementation, similar performance
   - Cons: Less control over collision handling
   - Why not chosen: Custom implementation provides better visibility and control

The combination of min heap for deadline sorting and hash table for package storage provides an optimal balance of performance and functionality for this specific application. The min heap efficiently handles the temporal aspects of package routing, while the hash table provides fast package lookup by ID, which is crucial for status updates and route optimization.