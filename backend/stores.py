"""
stores.py – GreenScan Store Locator
Uses OpenStreetMap Overpass API to find nearby agricultural/pesticide stores.
No API key required – completely free.
"""

import httpx
import math

OVERPASS_URL = "https://overpass-api.de/api/interpreter"

# Broad query covering many tag combos relevant to Indian agri stores
OVERPASS_QUERY_TEMPLATE = """
[out:json][timeout:30];
(
  node["shop"="agrarian"](around:{radius},{lat},{lon});
  node["shop"="farm"](around:{radius},{lat},{lon});
  node["shop"="garden_centre"](around:{radius},{lat},{lon});
  node["shop"="doityourself"](around:{radius},{lat},{lon});
  node["shop"="hardware"](around:{radius},{lat},{lon});
  node["amenity"="marketplace"](around:{radius},{lat},{lon});
  node["shop"="seeds"](around:{radius},{lat},{lon});
  node["shop"="fertilizer"](around:{radius},{lat},{lon});
  node["shop"="pesticide"](around:{radius},{lat},{lon});
  node["agricultural"="yes"](around:{radius},{lat},{lon});
  node["name"~"agro|agri|kisan|farmer|seed|fertilizer|nursery|pesticide|krishi",i](around:{radius},{lat},{lon});
  way["name"~"agro|agri|kisan|farmer|seed|fertilizer|nursery|pesticide|krishi",i](around:{radius},{lat},{lon});
);
out center body;
"""

FALLBACK_STORES = [
    {
        "id": "demo_1",
        "name": "Kisan Agro Centre",
        "address": "Agricultural Market, Sector 12",
        "distance_km": 1.2,
        "lat": None,
        "lon": None,
        "directions_url": "https://www.google.com/maps/search/agricultural+store+near+me",
        "phone": "+91-9876543210",
        "is_demo": True,
    },
    {
        "id": "demo_2",
        "name": "Green Fields Pesticide Shop",
        "address": "Farmers Market Road, Block A",
        "distance_km": 2.5,
        "lat": None,
        "lon": None,
        "directions_url": "https://www.google.com/maps/search/pesticide+shop+near+me",
        "phone": "+91-9765432109",
        "is_demo": True,
    },
    {
        "id": "demo_3",
        "name": "Agri Input Store",
        "address": "Main Bazaar, Near Bus Stand",
        "distance_km": 3.8,
        "lat": None,
        "lon": None,
        "directions_url": "https://www.google.com/maps/search/agri+input+store+near+me",
        "phone": "+91-9654321098",
        "is_demo": True,
    },
]


def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def _google_maps_directions(user_lat, user_lon, dest_lat, dest_lon):
    return f"https://www.google.com/maps/dir/{user_lat},{user_lon}/{dest_lat},{dest_lon}"


async def find_nearby_stores(lat: float, lon: float, radius_m: int = 25000, limit: int = 10):
    query = OVERPASS_QUERY_TEMPLATE.format(radius=radius_m, lat=lat, lon=lon)
    stores = []
    is_demo = False

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(OVERPASS_URL, data={"data": query})
            response.raise_for_status()
            data = response.json()

        seen_names = set()
        for elem in data.get("elements", []):
            tags = elem.get("tags", {})

            # Handle both node (lat/lon) and way (center lat/lon)
            elem_lat = elem.get("lat") or (elem.get("center") or {}).get("lat")
            elem_lon = elem.get("lon") or (elem.get("center") or {}).get("lon")

            if not elem_lat or not elem_lon:
                continue

            name = (
                tags.get("name")
                or tags.get("shop", "").replace("_", " ").title()
                or tags.get("amenity", "").replace("_", " ").title()
                or "Agricultural Store"
            )

            # Deduplicate by name (keep nearest)
            if name in seen_names:
                continue
            seen_names.add(name)

            address_parts = [
                tags.get(f) for f in ["addr:housenumber", "addr:street", "addr:city", "addr:state"]
                if tags.get(f)
            ]
            address = ", ".join(address_parts) if address_parts else "Address not available"
            distance = haversine_distance(lat, lon, elem_lat, elem_lon)

            stores.append({
                "id": str(elem.get("id", "")),
                "name": name,
                "address": address,
                "distance_km": round(distance, 2),
                "lat": elem_lat,
                "lon": elem_lon,
                "directions_url": _google_maps_directions(lat, lon, elem_lat, elem_lon),
                "phone": tags.get("phone") or tags.get("contact:phone") or "Not available",
                "is_demo": False,
            })

        stores.sort(key=lambda x: x["distance_km"])
        stores = stores[:limit]
        print(f"[StoreLocator] Found {len(stores)} real stores within {radius_m/1000:.0f}km of ({lat:.4f},{lon:.4f})")

    except Exception as e:
        print(f"[StoreLocator] OSM query failed: {e}. Using fallback data.")
        stores = FALLBACK_STORES
        is_demo = True

    if not stores:
        print(f"[StoreLocator] No stores found within {radius_m/1000:.0f}km. Returning demo data.")
        stores = FALLBACK_STORES
        is_demo = True

    return {
        "stores": stores,
        "total": len(stores),
        "is_demo": is_demo,
        "search_center": {"lat": lat, "lon": lon},
        "radius_km": radius_m / 1000,
    }
