# synonym_mapping.py

# Define synonym mapping for various categories
synonym_mapping = {
    "restaurants": [
        "restaurant", "cafe", "bistro", "diner", "coffee shop",
        "eatery", "food joint", "brasserie", "takeaway", "pizzeria"
    ],
    "parks": [
        "park", "green space", "playground", "recreation area",
        "nature reserve", "garden", "public garden", "square", "field"
    ],
    "schools": [
        "school", "educational institution", "academy", "college", "university",
        "institute", "learning center", "high school", "middle school", "primary school"
    ],
    "hospitals": [
        "hospital", "medical center", "clinic", "healthcare facility", "urgent care"
    ],
    "shopping": [
        "shopping mall", "mall", "shopping center", "market", "store",
        "boutique", "shop", "retail outlet"
    ],
    "banks": [
        "bank", "financial institution", "credit union", "savings bank"
    ],
    "pharmacies": [
        "pharmacy", "drugstore", "chemist", "medicinal shop"
    ],
    "transportation": [
        "bus stop", "train station", "subway station", "metro station",
        "taxi stand", "transport hub"
    ],
    "museums": [
        "museum", "gallery", "exhibition center", "art museum", "science museum"
    ]
}

# Dynamically create tag mappings based on synonyms
tag_mapping = {
    category: f'["amenity"~"{"|".join(synonyms)}"]' for category, synonyms in synonym_mapping.items()
}

# Define color mapping for each category
color_mapping = {
    "restaurants": "blue",
    "parks": "green",
    "schools": "red",
    "hospitals": "purple",
    "shopping": "gray",
    "banks": "darkblue",
    "pharmacies": "pink",
    "transportation": "orange",
    "museums": "darkred",
}

def get_query_tags(user_input):
    tags = set()
    for category, synonyms in synonym_mapping.items():
        if any(synonym in user_input.lower() for synonym in synonyms):
            tags.add(category)
    return list(tags)
