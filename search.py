import overpy
import folium
from synonym_mapping import tag_mapping, color_mapping, get_query_tags


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
def visualize_overpass_query(user_input, bbox, proximity_threshold_feet=500, map_name=None):
    proximity_threshold_km = proximity_threshold_feet * 0.000189394

    api = overpy.Overpass()

    if map_name is None:
        map_name = f"search_results_map.html"

    # Get query types based on user input
    query_types = get_query_tags(user_input)

    if not query_types:
        print("No valid query types found in user input.")
        return

    tags = [tag_mapping.get(q) for q in query_types if tag_mapping.get(q)]

    if not tags:
        print("No valid tags found for query types.")
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
        response = api.query(query)

        locations = []

        for node in response.nodes:
            name = node.tags.get("name")
            if name:
                locations.append(((node.lat, node.lon), name))

        for way in response.ways:
            name = way.tags.get("name")
            way_coordinates = [(n.lat, n.lon) for n in way.nodes]
            if name and way_coordinates:
                locations.append(((way_coordinates[0]), name))

        for relation in response.relations:
            name = relation.tags.get("name")
            for member in relation.members:
                if hasattr(member, "lat") and hasattr(member, "lon"):
                    if name:
                        locations.append(((member.lat, member.lon), name))
                        break

        if locations:
            my_map = folium.Map(location=locations[0][0], zoom_start=15)

            added_markers = set()
            for loc1, name1 in locations:
                for loc2, name2 in locations:
                    if loc1 != loc2 and haversine(loc1, loc2) <= proximity_threshold_km:
                        if loc1 not in added_markers:
                            folium.Marker(
                                location=loc1,
                                popup=name1,
                                icon=folium.Icon(color=color_mapping[query_types[0]])
                            ).add_to(my_map)
                            added_markers.add(loc1)

                        if loc2 not in added_markers:
                            folium.Marker(
                                location=loc2,
                                popup=name2,
                                icon=folium.Icon(color=color_mapping[query_types[1]])
                            ).add_to(my_map)
                            added_markers.add(loc2)

            my_map.save(map_name)
            print(f"Map saved as '{map_name}'. Open this file in a browser to view the results.")
        else:
            print("No features found within the specified proximity.")

    except overpy.exception.OverpassTooManyRequests as e:
        print("Too many requests, please wait before making another request.")
    except Exception as e:
        print(f"An error occurred: {e}")


# Example usage
user_input = "I want to find a park and a cafe"  # Example user input
bbox = [42.05567711419144, -87.7312507876687, 42.06867645692852, -87.67322924441329]  # Bounding box
proximity_threshold_feet = 500  # Proximity threshold in feet

visualize_overpass_query(user_input, bbox, proximity_threshold_feet)
