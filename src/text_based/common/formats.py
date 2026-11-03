"""
formats.py -- text codecs for profiles and midcurves, with strict and lenient decoders.

Codecs: json (BRep JSON), mcv1 (compact coordinates), mcv2 (index recipes), lines (line list,
as in the user's 'pointlist' prompt). All share the interface

    encode_profile(points) -> str
    encode_midcurve(points, edges, profile=None, tol=1e-6) -> str
    decode_midcurve(text, profile=None) -> (Graph | None, strict_ok: bool)

The decoders NEVER fabricate edges: a missing edge list stays empty (graph metrics then punish it).
"""
import ast
import json
import re
from collections import namedtuple

import numpy as np

from text_based.common import recipes as _recipes

Graph = namedtuple("Graph", ["points", "edges"])  # points: (n,2) float array, edges: list of (i,j)

NUM = r"-?\d+(?:\.\d+)?"
_PAIR = re.compile(r"(%s)\s*,\s*(%s)" % (NUM, NUM))


def fmt_num(x):
    x = float(x)
    r = round(x)
    if abs(x - r) < 1e-9:
        return str(int(r))
    s = ("%.2f" % x).rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def _jn(x):
    """JSON-friendly number: int if integral else 2 dp float."""
    x = float(x)
    r = round(x)
    if abs(x - r) < 1e-9:
        return int(r)
    return round(x, 2)


def loop_edges(n):
    return [(i, (i + 1) % n) for i in range(n)]


def make_graph(points, edges):
    """Validate and build a Graph; None if invalid (bad shape, NaN, index out of range, self loop)."""
    try:
        P = np.asarray(points, dtype=float)
    except (ValueError, TypeError):
        return None
    if P.ndim != 2 or P.shape[1] != 2 or len(P) == 0 or not np.all(np.isfinite(P)):
        return None
    E = []
    for e in edges:
        try:
            a, b = int(e[0]), int(e[1])
        except (ValueError, TypeError, IndexError):
            return None
        if a == b or not (0 <= a < len(P)) or not (0 <= b < len(P)):
            return None
        E.append((a, b))
    return Graph(P, E)


def strip_noise(text):
    """Remove <think> blocks and surrounding whitespace."""
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.S)
    return text.strip()


# ---------------------------------------------------------------------------
# json (BRep)
# ---------------------------------------------------------------------------

def _balanced_blocks(text):
    """All top-level {...} substrings in order."""
    out, depth, start = [], 0, -1
    for i, ch in enumerate(text):
        if ch == "{":
            if depth == 0:
                start = i
            depth += 1
        elif ch == "}" and depth > 0:
            depth -= 1
            if depth == 0:
                out.append(text[start:i + 1])
    return out


def _load_obj(s):
    for parser in (json.loads, ast.literal_eval):
        try:
            d = parser(s)
        except Exception:
            continue
        for _ in range(2):
            if isinstance(d, str):
                try:
                    d = json.loads(d)
                except Exception:
                    break
        if isinstance(d, dict):
            return d
    return None


def _brep_to_graph(d):
    if "Midcurve_brep" in d and isinstance(d["Midcurve_brep"], dict):
        d = d["Midcurve_brep"]
    if "Points" not in d:
        return None
    return make_graph(d["Points"], d.get("Lines", []) or [])


class JsonCodec:
    name = "json"

    @staticmethod
    def encode_profile(points):
        n = len(points)
        return json.dumps({"Points": [[_jn(x), _jn(y)] for x, y in points],
                           "Lines": [list(e) for e in loop_edges(n)],
                           "Segments": [list(range(n))]})

    @staticmethod
    def encode_midcurve(points, edges, profile=None, tol=1e-6):
        return json.dumps({"Points": [[_jn(x), _jn(y)] for x, y in points],
                           "Lines": [[int(a), int(b)] for a, b in edges],
                           "Segments": [[k] for k in range(len(edges))]})

    @staticmethod
    def decode_midcurve(text, profile=None):
        text = strip_noise(text)
        try:
            d = json.loads(text)
        except Exception:
            d = None
        if isinstance(d, dict):
            g = _brep_to_graph(d)
            if g is not None and (len(g.points) < 2 or g.edges):
                return g, True
        cands = [text]
        for fence in re.findall(r"```(?:json|python)?\s*(.*?)```", text, flags=re.S):
            cands.append(fence)
        cands = cands + [c for t in list(cands) for c in _balanced_blocks(t)]
        for c in reversed(cands):  # prefer the last block (models restate the input first)
            for variant in (c, re.sub(r"#[^\n]*", "", c)):
                d = _load_obj(variant)
                if d is not None:
                    g = _brep_to_graph(d)
                    if g is not None:
                        return g, False
        return None, False


# ---------------------------------------------------------------------------
# lines  ( [((x1,y1),(x2,y2)), ...] )
# ---------------------------------------------------------------------------

def _line_text(p, q):
    return "((%s, %s), (%s, %s))" % (fmt_num(p[0]), fmt_num(p[1]), fmt_num(q[0]), fmt_num(q[1]))


class LinesCodec:
    name = "lines"

    @staticmethod
    def encode_profile(points):
        n = len(points)
        return "[" + ", ".join(_line_text(points[a], points[b]) for a, b in loop_edges(n)) + "]"

    @staticmethod
    def encode_midcurve(points, edges, profile=None, tol=1e-6):
        return "[" + ", ".join(_line_text(points[a], points[b]) for a, b in edges) + "]"

    @staticmethod
    def decode_midcurve(text, profile=None):
        text = strip_noise(text)
        m = re.search(r"output\s*:?\s*(\[.*\])", text, flags=re.S | re.I)
        body = m.group(1) if m else text
        pts = [(float(a), float(b)) for a, b in _PAIR.findall(body)]
        if len(pts) < 2:
            return None, False
        strict = len(pts) % 2 == 0 and re.fullmatch(r"\s*\[[\s\S]*\]\s*", body) is not None
        index, points, edges = {}, [], []
        for k in range(0, len(pts) - 1, 2):
            ids = []
            for p in (pts[k], pts[k + 1]):
                key = (round(p[0], 4), round(p[1], 4))
                if key not in index:
                    index[key] = len(points)
                    points.append(p)
                ids.append(index[key])
            if ids[0] != ids[1]:
                edges.append((ids[0], ids[1]))
        g = make_graph(points, edges)
        return (g, bool(strict and g is not None)) if g is not None else (None, False)


# ---------------------------------------------------------------------------
# mcv1
# ---------------------------------------------------------------------------

class Mcv1Codec:
    name = "mcv1"

    @staticmethod
    def encode_profile(points):
        return "profile n=%d\n%s" % (len(points), " ".join("%s,%s" % (fmt_num(x), fmt_num(y)) for x, y in points))

    @staticmethod
    def encode_midcurve(points, edges, profile=None, tol=1e-6):
        return "midcurve n=%d e=%d\n%s\n%s" % (
            len(points), len(edges),
            " ".join("%s,%s" % (fmt_num(x), fmt_num(y)) for x, y in points),
            " ".join("%d-%d" % (a, b) for a, b in edges))

    @staticmethod
    def _strict(text):
        lines = [l for l in text.strip().split("\n")]
        if len(lines) < 2:
            return None
        h = re.fullmatch(r"midcurve n=(\d+) e=(\d+)", lines[0].strip())
        if not h:
            return None
        n, e = int(h.group(1)), int(h.group(2))
        ptoks = lines[1].split()
        if len(ptoks) != n or not all(re.fullmatch(r"%s,%s" % (NUM, NUM), t) for t in ptoks):
            return None
        etoks = lines[2].split() if len(lines) > 2 else []
        if len(etoks) != e or len(lines) > 3 or not all(re.fullmatch(r"\d+-\d+", t) for t in etoks):
            return None
        pts = [tuple(float(v) for v in t.split(",")) for t in ptoks]
        edges = [tuple(int(v) for v in t.split("-")) for t in etoks]
        return make_graph(pts, edges)

    @staticmethod
    def decode_midcurve(text, profile=None):
        text = strip_noise(text)
        g = Mcv1Codec._strict(text)
        if g is not None:
            return g, True
        pts, edges = [], []
        for line in text.split("\n"):
            if line.strip().lower().startswith("profile"):
                continue
            if "," in line:
                pts += [(float(a), float(b)) for a, b in _PAIR.findall(line)]
            else:
                edges += [(int(a), int(b)) for a, b in re.findall(r"\b(\d+)\s*-\s*(\d+)\b", line)]
        if not pts:
            return None, False
        g = make_graph(pts, edges)
        return g, False


# ---------------------------------------------------------------------------
# mcv2 (recipes)
# ---------------------------------------------------------------------------

class Mcv2Codec:
    name = "mcv2"

    @staticmethod
    def encode_profile(points):
        return Mcv1Codec.encode_profile(points)

    @staticmethod
    def encode_midcurve(points, edges, profile=None, tol=1e-6):
        if profile is None:
            raise ValueError("mcv2 needs the profile points")
        lines = []
        for k, v in enumerate(np.asarray(points, dtype=float)):
            r = _recipes.find_recipe(profile, v, tol)
            if r is None:
                lines.append("v%d = (%s,%s)" % (k, fmt_num(v[0]), fmt_num(v[1])))
            else:
                lines.append("v%d = mean(%s)" % (k, ",".join(str(i) for i in r)))
        lines.append("e " + " ".join("%d-%d" % (a, b) for a, b in edges))
        return "\n".join(lines)

    @staticmethod
    def _parse(text, profile, strict):
        P = np.asarray(profile, dtype=float)
        verts, edges = {}, []
        mean_re = re.compile(r"v(\d+)\s*=\s*mean\(\s*([\d\s,]+?)\s*\)")
        xy_re = re.compile(r"v(\d+)\s*=\s*\(\s*(%s)\s*,\s*(%s)\s*\)" % (NUM, NUM))
        lines = [l.strip() for l in text.strip().split("\n") if l.strip()]
        for l in lines:
            m = mean_re.search(l)
            if m:
                idx = [int(t) for t in re.split(r"[\s,]+", m.group(2).strip()) if t]
                if not idx or any(i >= len(P) for i in idx):
                    return None
                verts[int(m.group(1))] = P[idx].mean(axis=0)
                continue
            m = xy_re.search(l)
            if m:
                verts[int(m.group(1))] = np.array([float(m.group(2)), float(m.group(3))])
                continue
            if re.match(r"e\b", l, flags=re.I):
                edges += [(int(a), int(b)) for a, b in re.findall(r"(\d+)\s*-\s*(\d+)", l)]
        if not verts:
            return None
        n = max(verts) + 1
        if strict and sorted(verts) != list(range(n)):
            return None
        if sorted(verts) != list(range(n)):
            return None
        return make_graph([verts[i] for i in range(n)], edges)

    @staticmethod
    def decode_midcurve(text, profile=None):
        if profile is None:
            raise ValueError("mcv2 needs the profile points")
        text = strip_noise(text)
        strict_ok = all(
            re.fullmatch(r"v\d+ = (mean\(\d+(,\d+)*\)|\(%s,%s\))" % (NUM, NUM), l.strip())
            or re.fullmatch(r"e( \d+-\d+)*", l.strip())
            for l in text.split("\n") if l.strip())
        g = Mcv2Codec._parse(text, profile, strict_ok)
        return g, bool(g is not None and strict_ok)


CODECS = {"json": JsonCodec, "mcv1": Mcv1Codec, "mcv2": Mcv2Codec, "lines": LinesCodec}


def get_codec(name):
    if name not in CODECS:
        raise KeyError("unknown format %r; choose from %s" % (name, sorted(CODECS)))
    return CODECS[name]
