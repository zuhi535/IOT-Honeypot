"""
Gyanús MQTT üzenetek felismerése.

Egyszerű kulcsszó-alapú detekció: ha a topic vagy a payload tartalmazza
a config.py-ban felsorolt gyanús kulcsszavak valamelyikét (pl. admin, root,
password), az üzenetet gyanúsnak jelöljük.
"""

from honeypot.config import SUSPICIOUS_KEYWORDS


def is_suspicious(topic: str, payload: str) -> bool:
    """Visszaadja, hogy a topic vagy a payload gyanúsnak számít-e.

    Args:
        topic: az MQTT topic neve.
        payload: az üzenet törzse (dekódolt string).

    Returns:
        True, ha legalább egy gyanús kulcsszó előfordul a topicban
        vagy a payloadban (kis/nagybetű független egyezés).
    """
    haystack = f"{topic} {payload}".lower()
    return any(keyword.lower() in haystack for keyword in SUSPICIOUS_KEYWORDS)


def matched_keywords(topic: str, payload: str) -> list[str]:
    """Visszaadja, hogy konkrétan mely kulcsszavak illeszkedtek.
    Hasznos a logüzenetekhez és a hibakereséshez."""
    haystack = f"{topic} {payload}".lower()
    return [keyword for keyword in SUSPICIOUS_KEYWORDS if keyword.lower() in haystack]
