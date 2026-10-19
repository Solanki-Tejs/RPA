# -----------------------------
# PENDING PROPERTIES (Waiting Admin Approval)
# -----------------------------
PENDING_PROPERTIES = []


# -----------------------------
# MAIN VERIFIED PROPERTY STORE
# -----------------------------
PROPERTIES = []


# -----------------------------
# CATEGORY FILTER HELPERS
# -----------------------------
def get_buy_properties():
    return [p for p in PROPERTIES if p.get("category") == "Sell"]


def get_rent_properties():
    return [p for p in PROPERTIES if p.get("category") == "Rent"]


def get_commercial_properties():
    return [p for p in PROPERTIES if p.get("category") == "Commercial"]
