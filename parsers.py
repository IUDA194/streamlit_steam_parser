# parsers.py

import re
import pandas as pd

def parse_followers(x):
    """
    Parse follower gain strings like "1,234+" or "5678" into integer.
    Returns None if parsing fails.
    """
    if isinstance(x, str):
        # keep digits and plus sign
        cleaned = re.sub(r"[^\d+]", "", x)
        if "+" in cleaned:
            cleaned = cleaned.replace("+", "")
        try:
            return int(cleaned)
        except ValueError:
            return None
    return None

def parse_price(x):
    """
    Parse price strings like "€19,99" or "Free" into float euros.
    Returns None if parsing fails or price not recognized.
    """
    if isinstance(x, str):
        if "€" in x:
            # Replace comma with dot, remove euro sign
            cleaned = x.replace("€", "").replace(",", ".").strip()
            try:
                return float(cleaned)
            except ValueError:
                return None
        if x.strip().lower() == "free":
            return 0.0
    return None

def parse_rating(x):
    """
    Parse rating percentage strings like "85%" into float.
    Returns None if parsing fails.
    """
    if isinstance(x, str) and "%" in x:
        cleaned = x.replace("%", "").replace(",", ".").strip()
        try:
            return float(cleaned)
        except ValueError:
            return None
    return None

def parse_discount(x):
    """
    Detect if a discount string contains a negative percentage like "-20%".
    Returns True if so, False otherwise.
    """
    if isinstance(x, str) and re.search(r"-\d+%", x):
        return True
    return False

def parse_peak(x):
    """
    Parse peak owner/online strings by stripping non-digits and converting to int.
    Returns None if parsing fails.
    """
    if isinstance(x, str):
        cleaned = re.sub(r"[^\d]", "", x)
        if cleaned:
            try:
                return int(cleaned)
            except ValueError:
                return None
    return None

def parse_release_date(x):
    """
    Parse release_date strings into pandas Timestamp.
    Returns None if parsing fails.
    """
    try:
        return pd.to_datetime(x)
    except Exception:
        return None
