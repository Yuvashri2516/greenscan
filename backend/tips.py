"""
tips.py - Daily Agricultural & Plant Health Tips for Farmers
"""

import random

TIPS = [
    "Always irrigate crops at the soil base using drip lines to keep foliage dry and prevent fungal spore germination.",
    "Practice a 3-year crop rotation schedule with non-solanaceous crops to disrupt soil-borne pathogens.",
    "Mulch around tomato plant bases with clean straw to reduce soil splashing onto lower leaf surfaces.",
    "Inspect lower leaves weekly for early signs of concentric ring spots or chlorosis.",
    "Prune lower suckers and branches below the first fruit cluster to promote air circulation in the canopy.",
    "Disinfect pruning tools with 70% isopropyl alcohol between plants to stop cross-contamination.",
    "Apply balanced compost enriched with calcium nitrate to prevent blossom end rot and strengthen plant walls."
]

def get_daily_tips(count: int = 3) -> list:
    return random.sample(TIPS, min(count, len(TIPS)))
