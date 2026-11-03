"""
prompts.py -- ONE prompt builder, used by training and by every kind of inference.

    messages, answer = build_messages(row, fmt, pose="canonical", shots=(), style="fewshot")

Template files live in prompts/<style>.txt (header lines, '---', system text, optional
'===USER===' + user template). Shots become alternating user / assistant messages.
"""
import hashlib
import os

import numpy as np

from text_based.common import dataset, formats, recipes

HERE = os.path.dirname(os.path.abspath(__file__))
STYLE_DIR = os.path.join(HERE, "prompt_templates")  # was prompts/ (renamed: a package cannot share a name with prompts.py)

FORMAT_SPEC = {
    "json": ("Profile and midcurve are BRep JSON: {\"Points\": [[x, y], ...], \"Lines\": [[i, j], ...], "
             "\"Segments\": [[k], ...]}. Lines index into Points (0-based)."),
    "mcv1": ("Profile format: 'profile n=<N>' then one line of N 'x,y' integer points. Midcurve format: "
             "'midcurve n=<N> e=<E>', then one line of N 'x,y' points, then one line of E edges 'a-b' "
             "(indices into the midcurve points)."),
    "mcv2": ("Profile format: 'profile n=<N>' then one line of N 'x,y' integer points. Midcurve format: one line "
             "per midcurve vertex, 'v<k> = mean(i,j,...)' meaning the mean of those profile point indices "
             "(or 'v<k> = (x,y)' if no such mean exists), then a last line 'e a-b a-b ...' listing the "
             "edges between midcurve vertices."),
    "lines": ("A shape is a list of lines [((x1, y1), (x2, y2)), ...]; the profile is a closed loop of lines, "
              "the midcurve is a set of lines that may branch."),
}


def list_styles():
    return sorted(f[:-4] for f in os.listdir(STYLE_DIR) if f.endswith(".txt"))


def load_style(name):
    path = os.path.join(STYLE_DIR, name + ".txt")
    if not os.path.isfile(path):
        raise KeyError("unknown prompt style %r; available: %s" % (name, list_styles()))
    with open(path, "r", encoding="utf-8") as fh:
        text = fh.read()
    head, _, body = text.partition("\n---\n")
    meta = {}
    for line in head.splitlines():
        if ":" in line:
            k, _, v = line.partition(":")
            meta[k.strip()] = v.strip()
    system, _, user = body.partition("===USER===")
    return dict(name=meta.get("name", name), format=meta.get("format") or None, pose=meta.get("pose") or None,
                description=meta.get("description", ""), system=system.strip(),
                user=(user.strip() if user.strip() else "{profile}"))


def describe(profile):
    """Plain-English description of a closed polygon (used by the 'description' style)."""
    P = np.asarray(profile, dtype=float)
    n = len(P)
    E = np.roll(P, -1, axis=0) - P
    L = np.linalg.norm(E, axis=1)
    mn, mx = P.min(axis=0), P.max(axis=0)
    axis = bool(np.all((np.abs(E[:, 0]) < 1e-6 * (L + 1e-12)) | (np.abs(E[:, 1]) < 1e-6 * (L + 1e-12))))
    kind = "all edges are horizontal or vertical" if axis else "edges are at general angles"
    return ("closed polygon with %d vertices, bounding box %s by %s, %s; shortest edge %s, longest edge %s."
            % (n, formats.fmt_num(mx[0] - mn[0]), formats.fmt_num(mx[1] - mn[1]), kind,
               formats.fmt_num(L.min()), formats.fmt_num(L.max())))


def render(row, fmt, pose):
    """(profile_text, midcurve_text) of a row in the given format and pose."""
    profile, midcurve, edges = dataset.view(row, pose)
    codec = formats.get_codec(fmt)
    return (codec.encode_profile(profile),
            codec.encode_midcurve(midcurve, edges, profile, recipes.recipe_tol(pose)))


def resolve(fmt, pose, style):
    st = load_style(style)
    return st, (st["format"] or fmt), (st["pose"] or pose)


def build_messages(row, fmt, pose="canonical", shots=(), style="fewshot"):
    """Return (messages, answer_text). The answer is the gold midcurve text of `row`."""
    st, fmt, pose = resolve(fmt, pose, style)
    system = st["system"].replace("{format_spec}", FORMAT_SPEC[fmt])
    msgs = [{"role": "system", "content": system}]

    def user_text(r):
        ptxt, _ = render(r, fmt, pose)
        prof = dataset.view(r, pose)[0]
        return st["user"].replace("{description}", describe(prof)).replace("{profile}", ptxt)

    for s in shots:
        msgs.append({"role": "user", "content": user_text(s)})
        msgs.append({"role": "assistant", "content": render(s, fmt, pose)[1]})
    msgs.append({"role": "user", "content": user_text(row)})
    return msgs, render(row, fmt, pose)[1]


def select_shots(query, pool, n, seed=0):
    """Deterministic shots from `pool`: one per shape different from the query shape first, then
    further poses of those shapes. Never uses the query's own shape (no leak)."""
    if n <= 0:
        return []
    others = [r for r in pool if r["shape"] != query["shape"]]
    by = {}
    for r in others:
        by.setdefault(r["shape"], []).append(r)
    names = sorted(by)
    out, i = [], 0
    while len(out) < n and names and any(i < len(by[s]) for s in names):
        for s in names:
            if i < len(by[s]) and len(out) < n:
                out.append(by[s][i])
        i += 1
    return out


def merge_system_into_user(messages):
    """For chat templates without a system role (e.g. Gemma 2): prepend system text to the first user turn."""
    if not messages or messages[0]["role"] != "system":
        return list(messages)
    sys_text = messages[0]["content"]
    rest = [dict(m) for m in messages[1:]]
    for m in rest:
        if m["role"] == "user":
            m["content"] = sys_text + "\n\n" + m["content"]
            break
    return rest


def prompt_hash(messages):
    return hashlib.sha1("\n".join(m["role"] + ":" + m["content"] for m in messages).encode("utf-8")).hexdigest()[:12]
