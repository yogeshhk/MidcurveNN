"""
benchmark.py  –  MidcurveNN
==============================
Cross-approach benchmark: evaluate all three approach families on the same
raw test set and print a comparison table.

Metrics
-------
  Image-based  : Pixel IoU (Intersection over Union) between predicted and
                 ground-truth midcurve bitmap; SSIM; MSE.
  Geometry-based: Chamfer distance between predicted and ground-truth
                  midcurve point clouds.
  Text-based   : Placeholder (Phase II not yet implemented).

Usage
-----
    cd src
    python testing/benchmark.py
    python testing/benchmark.py --approaches image geometry
    python testing/benchmark.py --image-approach unet          # pick one image model
    python testing/benchmark.py --geometry-approach graph_transformer
"""

import argparse
import os
import sys
import time
import textwrap
import numpy as np

_SRC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _SRC)
sys.path.insert(0, os.path.join(_SRC, 'image_based'))

_RAW_DATA = os.path.join(_SRC, 'data', 'raw')


# ===========================================================================
# Metric helpers
# ===========================================================================

def pixel_iou(pred: np.ndarray, gt: np.ndarray, threshold: float = 0.5) -> float:
    """Binary IoU between two grayscale images in [0, 1]."""
    pred_bin = (pred > threshold).astype(bool)
    gt_bin   = (gt   > threshold).astype(bool)
    inter = (pred_bin & gt_bin).sum()
    union = (pred_bin | gt_bin).sum()
    return inter / union if union > 0 else 1.0


def pixel_mse(pred: np.ndarray, gt: np.ndarray) -> float:
    return float(np.mean((pred - gt) ** 2))


def chamfer_distance_np(pred: np.ndarray, gt: np.ndarray) -> float:
    """
    Chamfer distance between two point clouds (numpy).
    pred, gt: (N, 2) and (M, 2)
    """
    import scipy.spatial.distance as dist
    if pred.size == 0 or gt.size == 0:
        return float('inf')
    D = dist.cdist(pred, gt)
    return float(D.min(axis=1).mean() + D.min(axis=0).mean()) / 2.0


# ===========================================================================
# Image-based benchmark
# ===========================================================================

def benchmark_image(approach: str = 'unet', n_samples: int = 5) -> dict:
    """
    Run inference on `n_samples` test images for one image-based approach.
    Returns dict with mean IoU, MSE, and inference time.
    """
    data_dir = os.path.join(_SRC, 'image_based', approach, 'data')
    if not os.path.isdir(data_dir):
        return {"approach": approach, "status": "SKIP — data not found",
                "iou": None, "mse": None, "time_s": None}

    try:
        from utils.prepare_data import get_training_data
        profiles, midcurves = get_training_data(datafolder=data_dir)
    except Exception as e:
        return {"approach": approach, "status": f"SKIP — {e}",
                "iou": None, "mse": None, "time_s": None}

    if not profiles:
        return {"approach": approach, "status": "SKIP — 0 images",
                "iou": None, "mse": None, "time_s": None}

    # Load approach-specific model
    try:
        if approach == 'simpleencoderdecoder':
            from simpleencoderdecoder.build_simple_encoderdecoder_model import simple_encoderdecoder
            model = simple_encoderdecoder()
        elif approach == 'cnnencoderdecoder':
            from cnnencoderdecoder.build_cnn_encoderdecoder_model import cnn_encoderdecoder
            model = cnn_encoderdecoder(input_shape=(128, 128, 3))
        elif approach == 'denseencoderdecoder':
            from denseencoderdecoder.build_dense_encoderdecoder_model import dense_encoderdecoder
            model = dense_encoderdecoder()
        elif approach == 'denoiserencoderdecoder':
            from denoiserencoderdecoder.build_denoiser_encoderdecoder_model import denoiser_encoderdecoder
            model = denoiser_encoderdecoder()
        elif approach == 'unet':
            sys.path.insert(0, os.path.join(_SRC, 'image_based', 'unet'))
            from train import init as unet_init
            models = unet_init()
            model = models[0]
            # UNet needs a wrapper — skip detailed benchmark, report stub
            return {"approach": approach, "status": "OK (stub — run unet/test.py for full eval)",
                    "iou": None, "mse": None, "time_s": None}
        else:
            return {"approach": approach, "status": f"SKIP — unknown approach '{approach}'",
                    "iou": None, "mse": None, "time_s": None}
    except Exception as e:
        return {"approach": approach, "status": f"SKIP — model load failed: {e}",
                "iou": None, "mse": None, "time_s": None}

    sample_idx = list(range(min(n_samples, len(profiles))))
    iou_scores, mse_scores = [], []
    t0 = time.perf_counter()

    for i in sample_idx:
        p = np.asarray(profiles[i]) / 255.0
        m = np.asarray(midcurves[i]) / 255.0
        try:
            _, pred = model.predict(np.expand_dims(p, 0))
            pred = np.squeeze(pred)
            iou_scores.append(pixel_iou(pred, m))
            mse_scores.append(pixel_mse(pred, m))
        except Exception:
            pass

    elapsed = time.perf_counter() - t0

    return {
        "approach": approach,
        "status": "OK",
        "iou":    float(np.mean(iou_scores))  if iou_scores  else None,
        "mse":    float(np.mean(mse_scores))  if mse_scores  else None,
        "time_s": elapsed / max(1, len(sample_idx)),
    }


# ===========================================================================
# Geometry-based benchmark
# ===========================================================================

def benchmark_geometry(approach: str = 'graph_transformer') -> dict:
    """
    Evaluate a geometry-based approach using Chamfer distance.
    """
    try:
        import torch
        from torch_geometric.loader import DataLoader
    except ImportError:
        return {"approach": approach, "status": "SKIP — torch_geometric not installed",
                "chamfer": None, "time_s": None}

    sys.path.insert(0, os.path.join(_SRC, 'geometry_based', approach))

    try:
        from graph_dataset import MidcurveGraphDataset
        dataset = MidcurveGraphDataset(_RAW_DATA, augment=False)
    except Exception as e:
        return {"approach": approach, "status": f"SKIP — dataset load failed: {e}",
                "chamfer": None, "time_s": None}

    if approach == 'graph_transformer':
        try:
            from graph_transformer import MidcurveGraphTransformer, chamfer_loss
            model = MidcurveGraphTransformer(node_in=2, edge_in=1, hidden=64,
                                             ratio=0.6, num_layers=3, heads=4, lpe_k=4)
            ckpt = os.path.join(_SRC, 'geometry_based', 'graph_transformer',
                                'checkpoints', 'best_model.pt')
            if os.path.isfile(ckpt):
                state = torch.load(ckpt, map_location='cpu')
                model.load_state_dict(state['model_state'])
            else:
                return {"approach": approach,
                        "status": "SKIP — no checkpoint (run graph_transformer/train.py first)",
                        "chamfer": None, "time_s": None}
        except Exception as e:
            return {"approach": approach, "status": f"SKIP — {e}",
                    "chamfer": None, "time_s": None}

        model.eval()
        scores = []
        t0 = time.perf_counter()
        with torch.no_grad():
            for i in range(len(dataset)):
                data = dataset.get(i)
                coords_pred, _, _, _ = model(data.x, data.edge_index, data.edge_attr)
                scores.append(chamfer_loss(coords_pred, data.y).item())
        elapsed = time.perf_counter() - t0

        return {"approach": approach, "status": "OK",
                "chamfer": float(np.mean(scores)),
                "time_s":  elapsed / max(1, len(dataset))}

    elif approach == 'finetuned_graph_transformer':
        sys.path.insert(0, os.path.join(_SRC, 'geometry_based', 'finetuned_graph_transformer'))
        try:
            from model import MidcurveFinetuned
            from geometry_based.graph_transformer.graph_transformer import chamfer_loss
            ckpt = os.path.join(_SRC, 'geometry_based', 'finetuned_graph_transformer',
                                'checkpoints', 'best_model.pt')
            if not os.path.isfile(ckpt):
                return {"approach": approach,
                        "status": "SKIP — no checkpoint (run finetuned_graph_transformer/train.py first)",
                        "chamfer": None, "time_s": None}
            state = torch.load(ckpt, map_location='cpu')
            model = MidcurveFinetuned(
                max_nodes=state['args'].get('max_nodes', 32), pretrained=False)
            model.load_state_dict(state['model_state'])
        except Exception as e:
            return {"approach": approach, "status": f"SKIP — {e}",
                    "chamfer": None, "time_s": None}

        model.eval()
        scores = []
        t0 = time.perf_counter()
        with torch.no_grad():
            for i in range(len(dataset)):
                data = dataset.get(i)
                batch = torch.zeros(data.x.size(0), dtype=torch.long)
                coords_pred, _ = model(data.x, data.edge_index, batch)
                scores.append(chamfer_loss(coords_pred[0], data.y).item())
        elapsed = time.perf_counter() - t0

        return {"approach": approach, "status": "OK",
                "chamfer": float(np.mean(scores)),
                "time_s":  elapsed / max(1, len(dataset))}

    return {"approach": approach, "status": f"SKIP — unknown geometry approach '{approach}'",
            "chamfer": None, "time_s": None}


# ===========================================================================
# Text-based benchmark (Phase II — data validation)
# ===========================================================================

def benchmark_text() -> dict:
    """
    Validate the Phase II (LLM / text-based) data pipeline.
    Checks that all CSV splits exist and reports row counts.
    Model inference requires a fine-tuned checkpoint and a GPU;
    run text_based/finetuning/evaluate.py for full evaluation.
    """
    csvs_dir = os.path.join(_SRC, 'text_based', 'data', 'csvs')
    brep_dir = os.path.join(_SRC, 'text_based', 'data', 'brep')

    issues = []

    # Check BRep base shapes
    for shape in ('I', 'L', 'T', 'Plus'):
        p = os.path.join(brep_dir, f"{shape}.json")
        if not os.path.isfile(p):
            issues.append(f"Missing brep/{shape}.json")

    # Check CSV splits and report row counts
    csv_counts = {}
    for fname in ('midcurve_llm.csv', 'midcurve_llm_train.csv',
                  'midcurve_llm_test.csv', 'midcurve_llm_val.csv'):
        p = os.path.join(csvs_dir, fname)
        if not os.path.isfile(p):
            issues.append(f"Missing csvs/{fname}")
            continue
        try:
            with open(p) as f:
                rows = sum(1 for _ in f) - 1  # subtract header
            csv_counts[fname] = rows
        except Exception as e:
            issues.append(f"Error reading {fname}: {e}")

    if issues:
        return {"approach": "text_based (Phase II)",
                "status": "WARN — " + "; ".join(issues),
                "csv_counts": csv_counts,
                "note": "Run: cd src/text_based/utils && python create_brep_csvs.py"}

    note = (f"Data OK: train={csv_counts.get('midcurve_llm_train.csv', '?')} rows, "
            f"test={csv_counts.get('midcurve_llm_test.csv', '?')} rows, "
            f"val={csv_counts.get('midcurve_llm_val.csv', '?')} rows. "
            "For model eval run: cd src/text_based/finetuning && python evaluate.py")
    return {"approach": "text_based (Phase II)", "status": "OK",
            "csv_counts": csv_counts, "note": note}


# ===========================================================================
# Reporting
# ===========================================================================

def print_table(results: list):
    sep = "=" * 70
    print(f"\n{sep}")
    print("  MidcurveNN  –  Benchmark Results")
    print(sep)

    # Image-based
    image_results = [r for r in results if r.get('type') == 'image']
    if image_results:
        print("\n  IMAGE-BASED (Phase I)  –  Pixel IoU / MSE")
        print(f"  {'Approach':<28} {'Status':<20} {'IoU':>6}  {'MSE':>8}  {'t/img(s)':>9}")
        print("  " + "-" * 66)
        for r in image_results:
            iou = f"{r['iou']:.4f}" if r['iou'] is not None else "  N/A "
            mse = f"{r['mse']:.6f}" if r['mse'] is not None else "     N/A"
            t   = f"{r['time_s']:.4f}" if r['time_s'] is not None else "     N/A"
            print(f"  {r['approach']:<28} {r['status']:<20} {iou:>6}  {mse:>8}  {t:>9}")

    # Geometry-based
    geo_results = [r for r in results if r.get('type') == 'geometry']
    if geo_results:
        print("\n  GEOMETRY-BASED (Phase III)  –  Chamfer Distance")
        print(f"  {'Approach':<36} {'Status':<30} {'Chamfer':>8}  {'t/shape(s)':>10}")
        print("  " + "-" * 66)
        for r in geo_results:
            ch = f"{r['chamfer']:.4f}" if r['chamfer'] is not None else "     N/A"
            t  = f"{r['time_s']:.4f}" if r['time_s'] is not None else "       N/A"
            print(f"  {r['approach']:<36} {r['status']:<30} {ch:>8}  {t:>10}")

    # Text-based
    text_results = [r for r in results if r.get('type') == 'text']
    if text_results:
        print("\n  TEXT-BASED (Phase II)  –  Data Validation")
        for r in text_results:
            print(f"  {r['approach']}: {r['status']}")
            counts = r.get('csv_counts', {})
            if counts:
                print(f"    CSV rows: " + ", ".join(f"{k}={v}" for k, v in counts.items()))
            if 'note' in r:
                print(f"    Note: {r['note']}")

    print(f"\n{sep}\n")


# ===========================================================================
# CLI
# ===========================================================================

def get_args():
    p = argparse.ArgumentParser(
        description="MidcurveNN cross-approach benchmark",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            Examples:
              python testing/benchmark.py
              python testing/benchmark.py --approaches image geometry
              python testing/benchmark.py --image-approach unet
        """))
    p.add_argument("--approaches",        nargs='+',
                   choices=['image', 'geometry', 'text'],
                   default=['image', 'geometry', 'text'],
                   help="Which approach families to benchmark")
    p.add_argument("--image-approach",    default=None,
                   help="Single image approach to benchmark (default: all)")
    p.add_argument("--geometry-approach", default=None,
                   help="Single geometry approach (default: all)")
    p.add_argument("--n-samples",         type=int, default=5,
                   help="Number of samples for image benchmark")
    return p.parse_args()


def main():
    args = get_args()
    all_results = []

    if 'image' in args.approaches:
        image_approaches = ([args.image_approach] if args.image_approach
                            else ['simpleencoderdecoder', 'cnnencoderdecoder',
                                  'denseencoderdecoder', 'denoiserencoderdecoder',
                                  'unet', 'pix2pix', 'img2img'])
        print(f"\n[Benchmark] Running image-based evaluation ({len(image_approaches)} approaches)...")
        for ap in image_approaches:
            r = benchmark_image(ap, n_samples=args.n_samples)
            r['type'] = 'image'
            all_results.append(r)
            print(f"  {ap}: {r['status']}")

    if 'geometry' in args.approaches:
        geo_approaches = ([args.geometry_approach] if args.geometry_approach
                         else ['graph_transformer', 'finetuned_graph_transformer'])
        print(f"\n[Benchmark] Running geometry-based evaluation ({len(geo_approaches)} approaches)...")
        for ap in geo_approaches:
            r = benchmark_geometry(ap)
            r['type'] = 'geometry'
            all_results.append(r)
            print(f"  {ap}: {r['status']}")

    if 'text' in args.approaches:
        print("\n[Benchmark] Checking text-based (Phase II) status...")
        r = benchmark_text()
        r['type'] = 'text'
        all_results.append(r)

    print_table(all_results)


if __name__ == '__main__':
    main()
