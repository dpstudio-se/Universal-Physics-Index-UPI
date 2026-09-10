"""Optional source-bound multilayer observations, not an inferred infrastructure map."""

from __future__ import annotations

from collections import deque

from .analog_rf import finite, positive

LAYERS = (
    "natural_water",
    "water_supply",
    "sewer",
    "electricity",
    "district_heating",
    "fiber",
    "RF",
    "transport",
    "topography",
)
LIFECYCLES = (
    "BUILT",
    "HISTORICALLY_PLANNED_NOT_BUILT",
    "UNDER_CONSTRUCTION",
    "PROPOSED",
    "UNKNOWN",
)
STYLES = {
    "natural_water": "wavy",
    "water_supply": "double",
    "sewer": "dashed",
    "electricity": "zigzag",
    "district_heating": "parallel",
    "fiber": "dotted",
    "RF": "arcs",
    "transport": "solid",
    "topography": "contours",
}


def validate_multilayer(document: dict) -> None:
    nodes = document["nodes"]
    if len(nodes) > 150 or len(document["edges"]) > 1000:
        raise ValueError("observational graph exceeds bounded analysis size")
    by_id = {n["id"]: n for n in nodes}
    if len(by_id) != len(nodes):
        raise ValueError("duplicate node identity")
    for n in nodes:
        if (
            n["layer"] not in LAYERS
            or n["lifecycle"] not in LIFECYCLES
            or n["status"] not in ("EST", "DER", "HYP", "STOP", "ERR", "SYM")
        ):
            raise ValueError("invalid typed layer/status")
        if not n["provenance"] or not n["timestamp"]:
            raise ValueError("source and time required")
        if n["status"] == "STOP" and not (n.get("stop_reason") and n.get("next_observation")):
            raise ValueError("STOP needs missing observation")
        position = n.get("position")
        if position is not None:
            if not all(k in position for k in ("x", "y", "z", "crs", "uncertainty_m")):
                raise ValueError("coordinates need CRS and uncertainty")
            for key in ("x", "y", "z", "uncertainty_m"):
                finite(position[key], key, 0 if key == "uncertainty_m" else None)
    for e in document["edges"]:
        if e["source"] not in by_id or e["target"] not in by_id or e["source"] == e["target"]:
            raise ValueError("unknown edge endpoint")
        if (
            not e["provenance"]
            or e["status"] not in ("EST", "DER", "HYP", "STOP", "ERR", "SYM")
            or e["lifecycle"] not in LIFECYCLES
        ):
            raise ValueError("edge requires status, lifecycle and source")
        if (
            by_id[e["source"]]["layer"] != by_id[e["target"]]["layer"]
            and e["relation"] != "FORM_SIMILAR"
        ):
            raise ValueError("cross-layer physics cannot be inferred from topology")
        if e["lifecycle"] == "BUILT" and e["status"] in ("HYP", "SYM", "STOP"):
            raise ValueError("unestablished edge cannot be drawn as confirmed infrastructure")


def hydraulic(
    head_m: float,
    discharge_m3_s: float | None,
    density_kg_m3: float = 1000.0,
    gravity_m_s2: float = 9.80665,
) -> dict:
    finite(head_m, "head")
    positive(density_kg_m3, "density")
    positive(gravity_m_s2, "gravity")
    pressure = density_kg_m3 * gravity_m_s2 * head_m
    result = {
        "status": "DER",
        "pressure_difference_Pa": pressure,
        "assumptions": ["specified static head and constant density; no pipe losses included"],
    }
    if discharge_m3_s is None:
        result["power"] = {
            "status": "STOP",
            "stop_reason": "Discharge Q is not measured or supplied",
            "next_observation": "A sourced flow measurement with units, time and uncertainty",
        }
    else:
        finite(discharge_m3_s, "discharge")
        result["power"] = {
            "status": "DER",
            "value": pressure * discharge_m3_s,
            "unit": "W",
            "scope": "signed ideal gravitational power, not realized generation",
        }
    return result


def triangle_generation(g: int, selected: tuple[int, ...] = ()) -> dict:
    if isinstance(g, bool) or not isinstance(g, int) or not 0 <= g <= 20:
        raise ValueError("generation must be integer 0..20")
    total = (3 ** (g + 1) - 1) // 2
    first = (3**g - 1) // 2 + 1
    if len(set(selected)) != len(selected) or any(
        isinstance(x, bool) or not isinstance(x, int) or not first <= x <= total for x in selected
    ):
        raise ValueError("selection outside generation")
    return {
        "status": "DER",
        "generation": g,
        "triangles": 3**g,
        "cumulative": total,
        "levels": [first, total],
        "selected": selected,
        "topology": {
            "status": "STOP",
            "stop_reason": "Triangle counts do not determine shared vertices, edges or state",
            "next_observation": "Supply triangle incidence and parent/state relations",
        },
        "edges": [],
    }


def graph_metrics(vertices: tuple[str, ...], edges: tuple[tuple[str, str], ...]) -> dict:
    """Unweighted undirected simple-graph controls; labels discarded in signature.

    Brandes shortest-path betweenness; corrected closeness for disconnected graphs.
    Communities here mean connected components, not an optimized partition.
    """
    if len(vertices) > 150 or len(set(vertices)) != len(vertices):
        raise ValueError("unique bounded vertex set required")
    adj: dict[str, set[str]] = {v: set() for v in vertices}
    for a, b in edges:
        if a not in adj or b not in adj or a == b:
            raise ValueError("invalid simple graph edge")
        adj[a].add(b)
        adj[b].add(a)

    def components(omit: str | None = None) -> list[list[str]]:
        left = set(vertices) - ({omit} if omit else set())
        groups = []
        while left:
            todo = [min(left)]
            seen = set(todo)
            while todo:
                for v in adj[todo.pop()]:
                    if v in left and v not in seen:
                        seen.add(v)
                        todo.append(v)
            groups.append(sorted(seen))
            left -= seen
        return groups

    groups = components()
    central = dict.fromkeys(vertices, 0.0)
    close = {}
    all_distances: list[int] = []
    for s in vertices:
        stack = []
        parents: dict[str, list[str]] = {v: [] for v in vertices}
        sigma = dict.fromkeys(vertices, 0.0)
        sigma[s] = 1.0
        distance = {s: 0}
        queue = deque([s])
        while queue:
            v = queue.popleft()
            stack.append(v)
            for w in adj[v]:
                if w not in distance:
                    distance[w] = distance[v] + 1
                    queue.append(w)
                if distance[w] == distance[v] + 1:
                    sigma[w] += sigma[v]
                    parents[w].append(v)
        delta = dict.fromkeys(vertices, 0.0)
        for w in reversed(stack):
            for v in parents[w]:
                delta[v] += sigma[v] / sigma[w] * (1 + delta[w])
            if w != s:
                central[w] += delta[w]
        reach = len(distance) - 1
        denominator = sum(distance.values())
        close[s] = reach**2 / ((len(vertices) - 1) * denominator) if denominator else 0.0
        all_distances.extend(d for v, d in distance.items() if v != s)
    n = len(vertices)
    m = sum(map(len, adj.values())) // 2
    if n > 2:
        central = {v: value / ((n - 1) * (n - 2)) for v, value in central.items()}
    articulations = [v for v in vertices if len(components(v)) > len(groups)]
    modularity = 0.0
    if m:
        for group in groups:
            degree = sum(len(adj[v]) for v in group)
            internal = sum(len(adj[v] & set(group)) for v in group) / 2
            modularity += internal / m - (degree / (2 * m)) ** 2
    return {
        "status": "DER",
        "verification_type": "software_test",
        "assumptions": "undirected unweighted simple topology only",
        "degree_distribution": sorted(map(len, adj.values())),
        "betweenness": central,
        "closeness": close,
        "cycle_rank": m - n + len(groups),
        "redundancy_cycle_rank": m - n + len(groups),
        "articulation_points": articulations,
        "components": groups,
        "community_method": "connected components; no modularity optimization",
        "modularity": modularity,
        "mean_reachable_path_length": sum(all_distances) / len(all_distances)
        if all_distances
        else None,
        "vertex_removal_components": {v: len(components(v)) for v in vertices},
        "blinded_signature": {
            "degree": sorted(map(len, adj.values())),
            "cycle_rank": m - n + len(groups),
            "betweenness": sorted(central.values()),
            "closeness": sorted(close.values()),
        },
        "guard": "SHARED TOPOLOGY != SHARED PHYSICS",
    }


def ovik_template(timestamp: str) -> dict:
    """Verified service identities plus explicitly unlocated candidate observations."""
    nodes: list[dict] = []
    for layer, source, operator in (
        ("water_supply", "https://miva.se/vatten-och-avlopp", "Miva"),
        ("sewer", "https://miva.se/vatten-och-avlopp", "Miva"),
        ("electricity", "https://www.ovikenergi.se/", "Övik Energi"),
        ("district_heating", "https://www.ovikenergi.se/", "Övik Energi"),
        ("fiber", "https://www.ovikenergi.se/", "Övik Energi"),
    ):
        nodes.append(
            {
                "id": layer + ":service",
                "label": operator + " / " + layer,
                "layer": layer,
                "status": "EST",
                "scope": "public operator/service identity only; no route or plant coordinate",
                "lifecycle": "UNKNOWN",
                "position": None,
                "timestamp": timestamp,
                "provenance": [source],
            }
        )
    for place in ("Åsberget", "Skyttis", "Gullänget", "Bonäset", "hospital area"):
        nodes.append(
            {
                "id": "RF:" + place,
                "label": place,
                "layer": "RF",
                "status": "HYP",
                "lifecycle": "UNKNOWN",
                "position": None,
                "timestamp": timestamp,
                "provenance": ["user handoff: candidate location"],
                "scope": "candidate observation area; antenna identity and geometry unverified",
            }
        )
    nodes.extend(
        [
            {
                "id": "RF:SK3LH",
                "label": "SK3LH / Gullängets Radioklubb",
                "layer": "RF",
                "status": "EST",
                "lifecycle": "UNKNOWN",
                "position": None,
                "timestamp": timestamp,
                "provenance": ["https://www.ssa.se/distrikt3/om/medlemsklubbar-smcb/"],
                "scope": "public club/callsign listing only; no private antenna ownership inferred",
            },
            {
                "id": "RF:Skyttis-history",
                "label": "Skyttis RF activity — historical report",
                "layer": "RF",
                "status": "EST",
                "lifecycle": "UNKNOWN",
                "position": None,
                "timestamp": timestamp,
                "provenance": ["https://www.sverigesradio.se/artikel/5330316"],
                "historical_observation": {
                    "reported_year": None,
                    "source_access": "search excerpt available; direct fetch unavailable; publication date not independently resolved",
                    "scope": "club operating from a former medium-wave station",
                },
                "scope": "existence of historical report; present facility status not inferred",
            },
        ]
    )
    result = {
        "status": "DER",
        "layers": list(LAYERS),
        "nodes": nodes,
        "edges": [],
        "styles": STYLES,
        "coordinate_status": "No verified coordinates supplied; no geographic routes drawn",
        "RF_observation_fields": [
            "frequency_Hz",
            "band",
            "NR_ARFCN",
            "EARFCN",
            "PCI",
            "RSRP_dBm",
            "RSRQ_dB",
            "SINR_dB",
            "azimuth_deg",
            "timestamp",
            "location_uncertainty_m",
        ],
        "missing": {
            "status": "STOP",
            "stop_reason": "No surveyed routes, natural hydrology geometry, or calibrated RF observations",
            "next_observation": "Import public source-bound geometry or authorized measurements with CRS, time and uncertainty",
        },
    }
    validate_multilayer(result)
    return result
