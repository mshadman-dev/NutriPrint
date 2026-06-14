"""
Allergen category mapping for intelligent allergy filtering.

This module maps user-facing allergen terms (e.g., "milk", "dairy")
to the actual ingredient keywords that appear in food names and descriptions.
Users describe allergies by category, but food names use specific ingredient terms.

Example:
    A user enters "milk" as an allergy. Without this mapping, we would only
    catch foods with the literal substring "milk". This module ensures we also
    catch "Curd Rice" (yogurt).
"""

ALLERGEN_CATEGORIES = {
    "milk": ["milk", "curd", "yogurt"],
    "dairy": ["milk", "curd", "yogurt"],
}


def get_excluded_keywords(allergy_terms: list[str]) -> set[str]:
    """
    Expand user-supplied allergy terms to the full set of ingredient keywords.

    For each user-supplied allergy term (after lowercasing and stripping),
    looks it up in ALLERGEN_CATEGORIES. If found, all keywords for that category
    are added to the result set. If NOT found (unrecognized allergen term),
    the raw term itself is added as a fallback, so existing substring behavior
    still applies for unrecognized allergens.

    Args:
        allergy_terms: List of allergy terms supplied by the user.

    Returns:
        A set of lowercase keywords to search for in food names and highlights.

    Example:
        >>> get_excluded_keywords(["milk", "unknown"])
        {'milk', 'curd', 'yogurt', 'unknown'}
    """
    excluded_keywords = set()

    for term in allergy_terms:
        term_lower = term.strip().lower()
        if not term_lower:
            continue

        # If the term is recognized in the allergen categories, add all its keywords
        if term_lower in ALLERGEN_CATEGORIES:
            excluded_keywords.update(ALLERGEN_CATEGORIES[term_lower])
        else:
            # Fallback: treat it as a raw keyword (preserves backward compatibility)
            excluded_keywords.add(term_lower)

    return excluded_keywords
