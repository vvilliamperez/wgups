class HashNode:
    """A node in the hash table's linked list for handling collisions"""
    def __init__(self, key, package):
        self.key = key  # Package ID
        self.package = package  # Package object
        self.next = None

class PackageHashTable:
    """
    A custom hash table implementation for the WGUPS package delivery system.
    Uses chaining for collision resolution.
    
    The hash table stores Package objects using their package ID as keys.

    Details about the values of packages are in the `package.py` file.

    """
    def __init__(self, initial_capacity=40):  # We know we have ~40 packages
        self.capacity = initial_capacity
        self.size = 0
        self.buckets = [None] * initial_capacity
    
    def _hash(self, key):
        """
        Hash function for package IDs.
        Since package IDs are integers and we know roughly how many packages we have,
        we can use a simple modulo operation.
        """
        return int(key) % self.capacity
    
    def insert(self, key, package):
        """Insert a package into the hash table using its ID as key"""
        index = self._hash(key)
        
        if self.buckets[index] is None:
            # No collision, create new node
            self.buckets[index] = HashNode(key, package)
            self.size += 1
        else:
            # Handle collision with chaining
            current = self.buckets[index]
            while current:
                if current.key == key:
                    # Update existing package
                    current.package = package
                    return
                if current.next is None:
                    break
                current = current.next
            # Add new node to chain
            current.next = HashNode(key, package)
            self.size += 1
    
    def get(self, key):
        """Retrieve a package by its ID"""
        index = self._hash(key)
        current = self.buckets[index]
        
        while current:
            if current.key == key:
                return current.package
            current = current.next
        return None

    def lookup_by_id(self, package_id):
        """
        Lookup a package by its ID number.
        This is O(1) average case since we use the ID as the key.
        """
        return self.get(package_id)

    def lookup_by_hash_id(self, hash_id):
        """
        Lookup a package by its hash ID (the bucket index).
        This returns all packages in that bucket.
        O(k) where k is the number of packages in the bucket.
        """
        if 0 <= hash_id < self.capacity:
            packages = []
            current = self.buckets[hash_id]
            while current:
                packages.append(current.package)
                current = current.next
            return packages
        return []

    def get_bucket_info(self, bucket_index):
        """
        Get information about a specific bucket including:
        - Number of packages in bucket (chain length)
        - Package IDs in bucket
        Useful for analyzing hash table performance and collisions.
        """
        if 0 <= bucket_index < self.capacity:
            count = 0
            ids = []
            current = self.buckets[bucket_index]
            while current:
                count += 1
                ids.append(current.key)
                current = current.next
            return {
                "bucket_index": bucket_index,
                "chain_length": count,
                "package_ids": ids
            }
        return None
    
    def remove(self, key):
        """Remove a package from the hash table"""
        index = self._hash(key)
        current = self.buckets[index]
        prev = None
        
        while current:
            if current.key == key:
                if prev:
                    prev.next = current.next
                else:
                    self.buckets[index] = current.next
                self.size -= 1
                return current.package
            prev = current
            current = current.next
        return None
    
    def values(self):
        """Return all packages in the hash table"""
        packages = []
        for bucket in self.buckets:
            current = bucket
            while current:
                packages.append(current.package)
                current = current.next
        return packages
    
    def __getitem__(self, key):
        """Allow dictionary-style access with []"""
        return self.get(key)
    
    def __setitem__(self, key, package):
        """Allow dictionary-style assignment with []"""
        self.insert(key, package)
    
    def __contains__(self, key):
        """Allow 'in' operator"""
        return self.get(key) is not None
    
    def __len__(self):
        """Return number of packages in the hash table"""
        return self.size

    def lookup(self, **criteria):
        """
        Generic lookup function that returns packages matching all specified criteria.
        
        Args:
            **criteria: Arbitrary keyword arguments representing package attributes to match.
                       Supported attributes: 
                       - package_ID: The unique identifier of the package
                       - destination: The delivery location address
                       - deadline: The delivery deadline in seconds after midnight
                       - weight: The package weight
                       - notes: Any special notes about the package
                       - delivered_at_time: When the package was delivered (in seconds after midnight)
                       - status: The package status (PackageStatus enum)
                       - truck_id: The ID of the truck the package is assigned to
                       - note_on_delivery: Any notes added during delivery
        
        Returns:
            list: List of packages matching ALL specified criteria. Empty list if no matches found.
        
        Example:
            # Find all packages with specific deadline and status
            packages = hash_table.lookup(deadline=32400, status=PackageStatus.AT_HUB)
            
            # Find packages for a specific destination and weight
            packages = hash_table.lookup(destination="123 Main St", weight=15)
            
            # Find packages on a specific truck with a certain status
            packages = hash_table.lookup(truck_id=2, status=PackageStatus.IN_TRANSIT)
        """
        matching_packages = []
        
        # Iterate through all packages in the hash table
        for bucket in self.buckets:
            current = bucket
            while current:
                package = current.package
                matches_all = True
                
                # Check each criterion against the package
                for attr, value in criteria.items():
                    if not hasattr(package, attr) or getattr(package, attr) != value:
                        matches_all = False
                        break
                
                if matches_all:
                    matching_packages.append(package)
                    
                current = current.next
        
        return matching_packages
