"""
NutriVision - Constants

Central location for allergen databases, dietary rules, nutrient daily values,
and other reference data used across multiple services.
"""

# ============================================================
# COMMON ALLERGENS (Big 14 - EU/FDA combined)
# ============================================================
# Each entry maps an allergen category to keywords found in ingredient lists

ALLERGEN_DATABASE = {
    "milk": [
        "milk", "cream", "butter", "cheese", "whey", "casein", "lactose",
        "ghee", "yogurt", "curd", "paneer", "buttermilk", "dairy",
        "lactalbumin", "lactoferrin", "milk powder", "skim milk",
    ],
    "eggs": [
        "egg", "eggs", "albumin", "globulin", "lysozyme", "mayonnaise",
        "meringue", "ovalbumin", "ovomucin",
    ],
    "peanuts": [
        "peanut", "peanuts", "groundnut", "groundnuts", "arachis oil",
        "peanut butter", "peanut oil",
    ],
    "tree_nuts": [
        "almond", "cashew", "walnut", "pecan", "pistachio", "macadamia",
        "brazil nut", "hazelnut", "chestnut", "pine nut", "praline",
        "marzipan", "nougat", "filbert",
    ],
    "wheat": [
        "wheat", "flour", "bread", "breadcrumbs", "bulgur", "couscous",
        "durum", "semolina", "spelt", "kamut", "einkorn", "farina",
        "wheat starch", "wheat germ",
    ],
    "gluten": [
        "gluten", "wheat", "barley", "rye", "oats", "triticale", "malt",
        "brewer's yeast", "seitan", "wheat flour", "barley malt",
    ],
    "soy": [
        "soy", "soya", "soybean", "soybeans", "soy lecithin", "soy sauce",
        "tofu", "tempeh", "edamame", "miso", "soy protein",
    ],
    "fish": [
        "fish", "cod", "salmon", "tuna", "anchovy", "anchovies", "sardine",
        "mackerel", "bass", "catfish", "tilapia", "fish sauce",
        "fish oil", "omega-3",
    ],
    "shellfish": [
        "shrimp", "crab", "lobster", "prawn", "crayfish", "crawfish",
        "clam", "mussel", "oyster", "scallop", "squid", "shellfish",
    ],
    "sesame": [
        "sesame", "sesame seeds", "sesame oil", "tahini", "halvah",
    ],
    "mustard": [
        "mustard", "mustard seed", "mustard oil", "mustard powder",
    ],
    "celery": [
        "celery", "celeriac", "celery salt", "celery seed",
    ],
    "sulfites": [
        "sulfite", "sulphite", "sulfur dioxide", "sodium bisulfite",
        "sodium metabisulfite", "potassium bisulfite",
    ],
    "lupin": [
        "lupin", "lupine", "lupini",
    ],
}

# ============================================================
# NON-VEGETARIAN INGREDIENTS
# ============================================================
NON_VEGETARIAN_INGREDIENTS = [
    "meat", "beef", "pork", "chicken", "turkey", "lamb", "veal",
    "duck", "goose", "venison", "bison", "bacon", "ham", "sausage",
    "salami", "pepperoni", "gelatin", "lard", "tallow", "suet",
    "rennet", "carmine", "cochineal", "isinglass", "anchovies",
    "anchovy", "fish", "shellfish", "shrimp", "crab", "lobster",
    "squid", "octopus",
]

# ============================================================
# NON-VEGAN INGREDIENTS (includes all non-vegetarian + dairy/eggs/honey)
# ============================================================
NON_VEGAN_INGREDIENTS = NON_VEGETARIAN_INGREDIENTS + [
    "milk", "cream", "butter", "cheese", "whey", "casein", "lactose",
    "egg", "eggs", "albumin", "honey", "beeswax", "royal jelly",
    "lanolin", "shellac", "yogurt", "ghee", "paneer", "buttermilk",
    "milk powder", "cream cheese", "sour cream", "ice cream",
]

# ============================================================
# HIGH-CARB INGREDIENTS (not keto-friendly)
# ============================================================
HIGH_CARB_INGREDIENTS = [
    "sugar", "corn syrup", "high fructose corn syrup", "dextrose",
    "maltose", "sucrose", "glucose", "fructose", "honey", "molasses",
    "maple syrup", "agave", "rice", "wheat", "flour", "corn",
    "potato", "bread", "pasta", "noodles", "oats", "cereal",
    "starch", "cornstarch", "maltodextrin",
]

# ============================================================
# DAILY RECOMMENDED VALUES (based on 2000 calorie diet)
# Used to calculate % Daily Value for nutrient breakdown
# ============================================================
DAILY_VALUES = {
    "calories": 2000.0,       # kcal
    "protein": 50.0,          # grams
    "carbohydrates": 275.0,   # grams
    "fat": 78.0,              # grams
    "fiber": 28.0,            # grams
    "sugar": 50.0,            # grams
    "sodium": 2300.0,         # milligrams
    "saturated_fat": 20.0,    # grams
    "cholesterol": 300.0,     # milligrams
    "potassium": 4700.0,      # milligrams
    "calcium": 1300.0,        # milligrams
    "iron": 18.0,             # milligrams
    "vitamin_a": 900.0,       # mcg
    "vitamin_c": 90.0,        # milligrams
    "vitamin_d": 20.0,        # mcg
}

# ============================================================
# USDA NUTRIENT IDs (FoodData Central nutrient numbers)
# Maps our nutrient names to USDA's nutrient number system
# ============================================================
USDA_NUTRIENT_MAP = {
    "calories": 1008,         # Energy (kcal)
    "protein": 1003,          # Protein
    "carbohydrates": 1005,    # Carbohydrate, by difference
    "fat": 1004,              # Total lipid (fat)
    "fiber": 1079,            # Fiber, total dietary
    "sugar": 2000,            # Sugars, total
    "sodium": 1093,           # Sodium, Na
    "saturated_fat": 1258,    # Fatty acids, total saturated
    "cholesterol": 1253,      # Cholesterol
    "potassium": 1092,        # Potassium, K
    "calcium": 1087,          # Calcium, Ca
    "iron": 1089,             # Iron, Fe
    "vitamin_a": 1106,        # Vitamin A, RAE
    "vitamin_c": 1162,        # Vitamin C
    "vitamin_d": 1114,        # Vitamin D (D2 + D3)
}

# ============================================================
# HEALTH SCORE THRESHOLDS
# ============================================================
HEALTH_SCORE_WEIGHTS = {
    "high_sugar_penalty": -1.5,      # Per 25% DV over 50%
    "high_sodium_penalty": -1.5,     # Per 25% DV over 50%
    "high_sat_fat_penalty": -1.0,    # Per 25% DV over 50%
    "fiber_bonus": 0.5,              # Per 10% DV
    "protein_bonus": 0.3,            # Per 10% DV
    "allergen_penalty": -0.5,        # Per allergen detected
    "base_score": 7.0,               # Starting score
}
