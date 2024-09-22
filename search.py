import overpy
import folium


# Function to calculate the distance between two coordinates
def haversine(coord1, coord2):
    from math import radians, sin, cos, sqrt, atan2

    R = 6371.0  # Radius of the Earth in kilometers
    lat1, lon1 = coord1
    lat2, lon2 = coord2

    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)

    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c  # Distance in kilometers


# Function to execute a general Overpass query and visualize the results on a map
def visualize_overpass_query(query_types, bbox, proximity_threshold_feet, map_name=None):
    """
    Visualizes results of an Overpass query for multiple query types within a proximity threshold.

    Parameters:
    - query_types: List of types of data to query (e.g., ['park', 'restaurant'])
    - bbox: Bounding box coordinates in the form of [min_lat, min_lon, max_lat, max_lon]
    - proximity_threshold_feet: Maximum distance in feet between features to be included
    - map_name: Optional name for the output HTML map file
    """
    # Convert feet to kilometers
    proximity_threshold_km = proximity_threshold_feet * 0.000189394

    # Initialize the Overpass API
    api = overpy.Overpass()

    # Generate the map name if not provided
    if map_name is None:
        map_name = f"{'_'.join(query_types)}_map.html"

    # Define tag mappings
    tag_mapping = {
        "park": '["leisure"="park"]',
        "restaurant": '["amenity"="restaurant"]',
        "cafe": '["amenity"="cafe"]',
        "school": '["amenity"="school"]',
        "hospital": '["amenity"="hospital"]',
        "shopping_mall": '["building"="shopping_centre"]',
        "bank": '["amenity"="bank"]',
        "pharmacy": '["amenity"="pharmacy"]',
        "bus_stop": '["highway"="bus_stop"]',
        "museum": '["tourism"="museum"]',
    }

    # Prepare Overpass query based on the query types
    tags = [tag_mapping.get(q) for q in query_types if tag_mapping.get(q)]

    if not tags:
        print("No valid query types provided.")
        return

    query = f"""
    [out:json];
    (
      {';'.join([f'node{tag}({bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]})' for tag in tags])};
      {';'.join([f'way{tag}({bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]})' for tag in tags])};
      {';'.join([f'relation{tag}({bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]})' for tag in tags])};
    );
    (._;>;);
    out body;
    """

    try:
        # Make the request to the Overpass API
        response = api.query(query)

        # Collect locations
        locations = []

        # Collect nodes
        for node in response.nodes:
            name = node.tags.get("name")
            if name:
                locations.append(((node.lat, node.lon), name, "node"))

        # Collect ways and relations
        for way in response.ways:
            name = way.tags.get("name")
            way_coordinates = [(n.lat, n.lon) for n in way.nodes]
            if name and way_coordinates:
                locations.append(((way_coordinates[0]), name, "way"))  # Add first node of the way

        for relation in response.relations:
            name = relation.tags.get("name")
            for member in relation.members:
                if hasattr(member, "lat") and hasattr(member, "lon"):
                    if name:
                        locations.append(((member.lat, member.lon), name, "relation"))
                        break  # Break after adding the first marker for this relation

        # Initialize the map if we have valid locations
        if locations:
            my_map = folium.Map(location=locations[0][0], zoom_start=15)

            # Track added markers
            added_markers = {}

            # Define colors for each type
            color_mapping = {
                "park": "green",
                "restaurant": "blue",
                "cafe": "orange",
                "school": "red",
                "hospital": "purple",
                "shopping_mall": "gray",
                "bank": "darkblue",
                "pharmacy": "pink",
                "bus_stop": "lightgreen",
                "museum": "darkred",
            }

            # Check proximity conditions
            for i in range(len(locations)):
                loc1, name1, type1 = locations[i]

                # Check if we already added a marker for loc1
                if loc1 in added_markers:
                    continue

                for j in range(i + 1, len(locations)):
                    loc2, name2, type2 = locations[j]

                    if haversine(loc1, loc2) <= proximity_threshold_km:
                        # Add loc1 if it's not already added
                        if loc1 not in added_markers:
                            folium.Marker(
                                location=loc1,
                                popup=name1,
                                icon=folium.Icon(color=color_mapping.get(type1, "blue"), icon="info-sign")
                            ).add_to(my_map)
                            added_markers[loc1] = type1  # Mark the location with its type

                        # Add loc2 if it's not already added
                        if loc2 not in added_markers:
                            folium.Marker(
                                location=loc2,
                                popup=name2,
                                icon=folium.Icon(color=color_mapping.get(type2, "blue"), icon="info-sign")
                            ).add_to(my_map)
                            added_markers[loc2] = type2  # Mark the location with its type

            # Save the map to an HTML file
            my_map.save(map_name)
            print(f"Map saved as '{map_name}'. Open this file in a browser to view the results.")
        else:
            print("No features found within the specified proximity.")

    except overpy.exception.OverpassTooManyRequests as e:
        print("Too many requests, please wait before making another request.")
    except Exception as e:
        print(f"An error occurred: {e}")


# Example usage
query_types = ["park", "restaurant"]  # List of query types
bbox = [42.05567711419144, -87.7312507876687, 42.06867645692852, -87.67322924441329]  # Updated bounding box
proximity_threshold_feet = 500  # Proximity threshold in feet

# Call the function with the query types and bounding box
visualize_overpass_query(query_types, bbox, proximity_threshold_feet)
