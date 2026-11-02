"""Collect every runs/*/metrics.json into one table (markdown to stdout, optional --out file).

Reports the TEST block (new poses of shapes seen in training for split 'pose'; the held-out shape for
'loso:*') and, for reference, the VAL block F1. Rows are never invented: a run without metrics.json is
listed as NOT MEASURED.

  python collect_results.py [--runs runs] [--out table.md]
"""
import argparse
import glob
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))


def val_block(m):
    for k in ("val", "val_seen_shapes_new_poses"):
        if k in m:
            return m[k]
    return None


def load_all(runs):
    rows = []
    for d in sorted(glob.glob(os.path.join(runs, "*"))):
        name = os.path.basename(d)
        mp = os.path.join(d, "metrics.json")
        row = dict(run=name)
        if not os.path.exists(mp):
            row["status"] = "NOT MEASURED (no metrics.json)"
            rows.append(row)
            continue
        with open(mp) as f:
            m = json.load(f)
        t = m["test"]["all"]
        v = val_block(m)
        sched = "-"
        if m.get("epochs"):
            sched = "%d x %d" % (m["epochs"], m.get("steps_per_epoch") or 0)
        args = {}
        ap = os.path.join(d, "args.json")
        if os.path.exists(ap):
            with open(ap) as f:
                args = json.load(f)
        row.update(model=m.get("model"), split=m.get("split"), tag=m.get("tag"), tta=m.get("tta"),
                   in_ch=args.get("in_ch", "?"), loss=args.get("loss", "?"), aug=not args.get("no_aug", False),
                   f1=t["f1"], prec=t["prec"], rec=t["rec"], chamfer=t["chamfer_raw"],
                   hausdorff=t["hausdorff_raw"], topo=t["topo_ok"], n=t.get("n"),
                   val_f1=v["all"]["f1"] if v else None, sched=sched,
                   sec=m.get("sec_per_epoch_median") or m.get("sec_per_epoch"), shapes={k: x["f1"] for k, x in m["test"].items() if k != "all"},
                   topo_shapes={k: x["topo_ok"] for k, x in m["test"].items() if k != "all"},
                   status="ok")
        rows.append(row)
    return rows


def fmt(x, p=3):
    return "n/a" if x is None else ("%.*f" % (p, x))


def table(rows):
    out = ["| run | in_ch | loss | aug | schedule (ep x steps) | sec/epoch | test F1@2px | val F1 | chamfer (raw) | hausdorff (raw) | topology ok | n |",
           "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        if r["status"] != "ok":
            out.append("| %s | | | | | | %s | | | | | |" % (r["run"], r["status"]))
            continue
        sec = fmt(r["sec"], 1) if r["sec"] else "n/a"
        out.append("| %s%s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
            r["run"], " (TTA)" if r["tta"] else "", r["in_ch"], r["loss"], "yes" if r["aug"] else "no",
            r["sched"], sec, fmt(r["f1"]), fmt(r["val_f1"]), fmt(r["chamfer"]), fmt(r["hausdorff"], 2),
            fmt(r["topo"], 2), r["n"]))
    out.append("")
    out.append("Per-shape test F1 / topology ok:")
    out.append("")
    out.append("| run | " + " | ".join(["I", "L", "T", "Plus"]) + " |")
    out.append("|---|---|---|---|---|")
    for r in rows:
        if r["status"] != "ok":
            continue
        cells = []
        for s in ["I", "L", "T", "Plus"]:
            if s in r["shapes"]:
                cells.append("%s / %s" % (fmt(r["shapes"][s]), fmt(r["topo_shapes"][s], 2)))
            else:
                cells.append("-")
        out.append("| %s | %s |" % (r["run"], " | ".join(cells)))
    return "\n".join(out)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--runs", default=os.path.join(HERE, "runs"))
    p.add_argument("--out", default=None)
    a = p.parse_args()
    t = table(load_all(a.runs))
    print(t)
    if a.out:
        with open(a.out, "w") as f:
            f.write(t + "\n")


if __name__ == "__main__":
    main()
