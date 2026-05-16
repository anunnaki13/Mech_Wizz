from app.services.port_intelligence import haversine_distance_km, nearest_port_to, normalize_wpi_port


def _raw_port(port_number: int, name: str, latitude: float, longitude: float) -> dict:
    return {
        "portNumber": port_number,
        "portName": name,
        "countryCode": "ID",
        "countryName": "Indonesia",
        "xcoord": longitude,
        "ycoord": latitude,
        "harborSize": "L",
        "harborType": "CN",
        "chDepth": "14",
        "anDepth": "12",
        "loWharves": "Y",
        "loContainer": "Y",
        "loLiquidBulk": "Y",
        "firstPortOfEntry": "Y",
        "tugsAssist": "Y",
        "cmRadio": "Y",
        "turningArea": "Y",
        "etaMessage": "Y",
    }


def test_normalize_wpi_port_scores_readiness():
    port = normalize_wpi_port(_raw_port(1, "Test Port", -6.0, 106.0))

    assert port is not None
    assert port["port_name"] == "Test Port"
    assert port["latitude"] == -6.0
    assert port["longitude"] == 106.0
    assert port["readiness_label"] == "high"
    assert port["readiness_score"] >= 0.75


def test_nearest_port_uses_haversine_distance():
    nearby = normalize_wpi_port(_raw_port(1, "Nearby", -6.0, 106.0))
    faraway = normalize_wpi_port(_raw_port(2, "Faraway", -1.0, 120.0))

    nearest = nearest_port_to(-6.1, 106.1, (nearby, faraway))  # type: ignore[arg-type]

    assert nearest is not None
    assert nearest[0]["port_name"] == "Nearby"
    assert nearest[1] < haversine_distance_km(-6.1, 106.1, -1.0, 120.0)
