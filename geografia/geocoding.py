import time
import requests
from typing import Optional, Tuple

USER_AGENT = "sisvot-geocoder/1.0 (contact: admin@sisvot)"
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"


def geocode_bairro(nome_bairro: str, cidade: str = "Cuiabá", uf: str = "MT") -> Optional[Tuple[float, float]]:
    """Geocode um bairro via Nominatim. Retorna (lat, lon) ou None.
    Respeita rate limit (1 req/s)."""
    params = {
        "q": f"{nome_bairro}, {cidade} - {uf}, Brasil",
        "format": "json",
        "addressdetails": 0,
        "limit": 1,
        "countrycodes": "br",
    }
    headers = {"User-Agent": USER_AGENT}

    try:
        resp = requests.get(NOMINATIM_URL, params=params, headers=headers, timeout=15)
        resp.raise_for_status()
        results = resp.json()
        if not results:
            return None
        lat = float(results[0]["lat"])  # type: ignore[index]
        lon = float(results[0]["lon"])  # type: ignore[index]
        # Respeitar rate limit simples
        time.sleep(1.1)
        return (lat, lon)
    except Exception:
        return None


