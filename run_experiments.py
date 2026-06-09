# -*- coding: utf-8 -*-
"""
================================================================
EKSPERIMEN PERBANDINGAN: Local Solver vs Global Solver
Final Project ET4244 -- Soal 4a/4c
Paper: Price-Based Distributed Offloading for MEC

Menjalankan eksperimen dengan 7 variasi jumlah user K
untuk membandingkan:
  - Local Solver:  B&B + IPOPT, B&B + MINOS
  - Global Solver: SCIP, Couenne
================================================================

INSTRUKSI GOOGLE COLAB:
Jalankan cell-cell berikut sebelum menjalankan script ini:

    !pip install -q pyomo amplpy pyscipopt
    !python -m amplpy.modules install coin -q
    !python -m amplpy.modules install minos -q

Kemudian jalankan script ini:
    %run run_experiments.py

Atau copy-paste ke cell Colab.
================================================================
"""

import numpy as np
import pandas as pd
import time
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# KONFIGURASI EKSPERIMEN
# ============================================================

# 9 variasi jumlah user sesuai dengan paper:
# K = 10, 15, 20, 25, 30, 35, 40, 45, 50
# Catatan: Untuk K > 25, B&B manual kemungkinan besar akan 
# mencapai batas MAX_NODES (10.000) karena kompleksitas O(2^K).
K_VALUES = [10, 15, 20, 25, 30, 35, 40, 45, 50]

SEED = 1  # Sama dengan kode Colab asli
F_BAR = 6e9

# Toleransi numerik
INTEGER_TOL = 1e-6
BOUND_TOL = 1e-7
MAX_NODES = 2_000  # Dinaikkan menjadi 2000 agar K=50 bisa converge

# Direktori log
import os
LOG_DIR = "solver_logs"
os.makedirs(LOG_DIR, exist_ok=True)

# Parameter sistem sesuai paper
B = 1e6
N0_dBm_per_Hz = -174
h_dB_min = -50
h_dB_max = -30
F_choices_GHz = np.arange(0.1, 1.1, 0.1)
C_min = 500
C_max = 1500
R_min_KB = 100
R_max_KB = 500
p_k_val = 0.1
P_B_k_val = 1.0
alpha_k_val = 0.2
f_C = 100e9

# ============================================================
# IMPORT SOLVER MODULES
# ============================================================

import pyomo.environ as pyo

try:
    from amplpy import modules
    AMPL_AVAILABLE = True
except ImportError:
    AMPL_AVAILABLE = False
    print("WARNING: amplpy not available. IPOPT/MINOS/Couenne won't work.")

try:
    # pyrefly: ignore [missing-import]
    from pyscipopt import Model as SCIPModel, quicksum
    SCIP_AVAILABLE = True
except ImportError:
    SCIP_AVAILABLE = False
    print("WARNING: pyscipopt not available. SCIP won't work.")

try:
    from IPython.display import display
except ImportError:
    display = print


# ============================================================
# 1. GENERATE PARAMETERS
# ============================================================

def generate_params(K, seed=SEED):
    """Generate parameter sistem untuk K user dengan seed tertentu."""
    np.random.seed(seed)

    h_dB = np.random.uniform(h_dB_min, h_dB_max, K)
    h_linear = 10 ** (h_dB / 10)

    F_GHz = np.random.choice(F_choices_GHz, K)
    F = F_GHz * 1e9

    C = np.random.uniform(C_min, C_max, K)

    R_KB = np.random.uniform(R_min_KB, R_max_KB, K)
    R_bits = R_KB * 1024 * 8

    N0_W = 10 ** ((N0_dBm_per_Hz - 30) / 10)
    B_k = B / K

    r_u = B_k * np.log2(1 + (p_k_val * h_linear) / (N0_W * B_k))
    r_d = B_k * np.log2(1 + (P_B_k_val * h_linear) / (N0_W * B_k))

    beta = (1 / r_u) + (C / f_C) + (alpha_k_val / r_d)
    m = (C * R_bits) / (C + F * beta)

    w = m * C
    v = (m * C) / F

    return {
        'K': K, 'F_GHz': F_GHz, 'F': F, 'C': C, 'R_bits': R_bits,
        'h_dB': h_dB, 'r_u': r_u, 'r_d': r_d, 'beta': beta,
        'm': m, 'w': w, 'v': v, 'F_bar': F_BAR
    }


# ============================================================
# 2. LATENCY CALCULATION
# ============================================================

def compute_latency(params, x_star):
    """Hitung rata-rata latensi untuk solusi binary x_star."""
    x = np.array(x_star, dtype=float)
    m = params['m']
    C = params['C']
    F = params['F']
    R_bits = params['R_bits']
    r_u = params['r_u']
    r_d = params['r_d']

    l_star = x * m
    t_loc = ((R_bits - l_star) * C) / F
    t_off = (l_star / r_u) + ((l_star * C) / f_C) + ((alpha_k_val * l_star) / r_d)
    t_total = np.maximum(t_loc, t_off)
    t_only_local = (R_bits * C) / F

    return {
        'avg_latency': float(np.mean(t_total)),
        'avg_local_only': float(np.mean(t_only_local)),
        'reduction': float(np.mean(t_only_local) - np.mean(t_total))
    }


# ============================================================
# 3. LOCAL SOLVER: MANUAL B&B
# ============================================================

def get_solver(solver_name):
    if AMPL_AVAILABLE:
        try:
            exe = modules.find(solver_name)
            return pyo.SolverFactory(solver_name, executable=exe, solve_io="nl")
        except Exception:
            pass
    return pyo.SolverFactory(solver_name)


def solve_relaxed_node(params, fixed_vars, solver_name="ipopt"):
    """Solve satu relaxed B&B node."""
    K = params['K']
    w = params['w']
    v = params['v']
    F_bar = params['F_bar']
    users = range(K)

    # Check capacity violation
    fixed_cap = sum(float(w[k]) * fixed_vars[k] for k in fixed_vars)
    if fixed_cap > float(F_bar) + 1e-6:
        return {"status": "infeasible"}

    # All fixed → evaluate directly
    if len(fixed_vars) == K:
        x_f = np.zeros(K)
        for k in range(K):
            x_f[k] = fixed_vars[k]
        return {
            "status": "ok",
            "x_relaxed": x_f,
            "relaxed_ub": float(np.sum(v * x_f)),
            "called_solver": False
        }

    # Build and solve relaxation
    model = pyo.ConcreteModel()
    model.K_set = pyo.RangeSet(0, K - 1)
    model.x = pyo.Var(model.K_set, bounds=(0, 1))

    for k, val in fixed_vars.items():
        model.x[k].fix(val)

    model.obj = pyo.Objective(
        expr=-sum(float(v[k]) * model.x[k] for k in users),
        sense=pyo.minimize
    )
    model.capacity = pyo.Constraint(
        expr=sum(float(w[k]) * model.x[k] for k in users) <= float(F_bar)
    )

    solver = get_solver(solver_name)
    try:
        result = solver.solve(model, tee=False)
    except Exception:
        return {"status": "solver_error"}

    term = str(result.solver.termination_condition).lower()
    if "infeasible" in term:
        return {"status": "infeasible"}

    try:
        x_rel = np.array([pyo.value(model.x[k]) for k in users], dtype=float)
        ub = float(-pyo.value(model.obj))
    except Exception:
        return {"status": "no_solution"}

    return {
        "status": "ok",
        "x_relaxed": x_rel,
        "relaxed_ub": ub,
        "called_solver": True
    }


def manual_branch_and_bound(params, solver_name="ipopt"):
    """Manual B&B untuk binary knapsack."""
    K = params['K']
    v = params['v']
    w = params['w']
    F_bar = params['F_bar']

    start = time.perf_counter()

    best_obj = -np.inf
    best_x = None
    stack = [{}]  # DFS stack
    nodes_solved = 0
    nodes_pruned = 0
    solver_calls = 0
    root_ub = None

    while stack:
        if nodes_solved >= MAX_NODES:
            break

        fixed = stack.pop()
        nodes_solved += 1

        res = solve_relaxed_node(params, fixed, solver_name)

        if res.get("called_solver", False):
            solver_calls += 1

        if res["status"] != "ok":
            nodes_pruned += 1
            continue

        x_rel = res["x_relaxed"]
        ub = res["relaxed_ub"]

        if root_ub is None:
            root_ub = ub

        # Bound pruning
        if ub <= best_obj + BOUND_TOL:
            nodes_pruned += 1
            continue

        # Check integrality
        is_int = np.all(np.abs(x_rel - np.round(x_rel)) <= INTEGER_TOL)

        if is_int:
            x_int = np.round(x_rel).astype(int)
            obj = float(np.sum(v * x_int))
            cap = float(np.sum(w * x_int))
            if cap <= F_bar + 1e-5 and obj > best_obj:
                best_obj = obj
                best_x = x_int
            nodes_pruned += 1
            continue

        # Branch on most fractional variable
        best_k = None
        best_score = -1
        for k in range(K):
            if k in fixed:
                continue
            dist = min(abs(x_rel[k]), abs(1 - x_rel[k]))
            if dist > INTEGER_TOL:
                score = 1 - abs(x_rel[k] - 0.5)
                if score > best_score:
                    best_score = score
                    best_k = k

        if best_k is None:
            nodes_pruned += 1
            continue

        # Create children
        left = dict(fixed)
        left[best_k] = 0
        right = dict(fixed)
        right[best_k] = 1
        stack.append(left)
        stack.append(right)

    elapsed = time.perf_counter() - start
    completed = (len(stack) == 0)

    if best_x is not None:
        selected = [k + 1 for k in range(K) if best_x[k] == 1]
        lat = compute_latency(params, best_x)
        gap = 0.0 if completed else (root_ub - best_obj if root_ub else None)
    else:
        selected = []
        lat = {'avg_latency': None, 'avg_local_only': None, 'reduction': None}
        gap = None

    return {
        'solver': f"B&B+{solver_name.upper()}",
        'objective': best_obj if best_x is not None else None,
        'x_star': best_x.tolist() if best_x is not None else None,
        'selected': selected,
        'nodes': nodes_solved,
        'nodes_pruned': nodes_pruned,
        'solver_calls': solver_calls,
        'time': elapsed,
        'root_ub': root_ub,
        'gap': gap,
        'gap_pct': (gap / root_ub * 100) if (gap and root_ub) else 0.0,
        'completed': completed,
        **lat
    }


# ============================================================
# 4. GLOBAL SOLVER: SCIP
# ============================================================

def solve_scip(params):
    """Solve dengan SCIP global solver, simpan log per K."""
    if not SCIP_AVAILABLE:
        return None

    K = params['K']
    v = params['v']
    w = params['w']
    F_bar = params['F_bar']
    users = range(K)

    model = SCIPModel("SCIP_Knapsack")

    # Simpan log ke file per K
    log_file = os.path.join(LOG_DIR, f"scip_K{K}.log")
    model.setLogfile(log_file)
    model.hideOutput(True)  # Tetap hide di console

    x = {}
    for k in users:
        x[k] = model.addVar(vtype="B", name=f"x_{k+1}")

    model.setObjective(quicksum(float(v[k]) * x[k] for k in users), "maximize")
    model.addCons(quicksum(float(w[k]) * x[k] for k in users) <= float(F_bar))

    start = time.perf_counter()
    model.optimize()
    elapsed = time.perf_counter() - start

    if model.getStatus() != "optimal":
        return None

    x_star = np.array([int(round(model.getVal(x[k]))) for k in users])
    selected = [k + 1 for k in users if x_star[k] == 1]
    lat = compute_latency(params, x_star)

    return {
        'solver': 'SCIP',
        'objective': model.getObjVal(),
        'x_star': x_star.tolist(),
        'selected': selected,
        'nodes': model.getNNodes(),
        'nodes_pruned': None,
        'solver_calls': None,
        'time': elapsed,
        'scip_time': model.getSolvingTime(),
        'root_ub': None,
        'gap': model.getGap(),
        'gap_pct': model.getGap() * 100,
        'completed': True,
        'log_file': log_file,
        **lat
    }


# ============================================================
# 5. GLOBAL SOLVER: COUENNE
# ============================================================

def solve_couenne(params):
    """Solve dengan Couenne global solver, simpan log per K."""
    if not AMPL_AVAILABLE:
        return None

    K = params['K']
    v = params['v']
    w = params['w']
    F_bar = params['F_bar']
    users = range(K)

    model = pyo.ConcreteModel()
    model.K_set = pyo.RangeSet(0, K - 1)
    model.x = pyo.Var(model.K_set, domain=pyo.Binary)

    model.obj = pyo.Objective(
        expr=sum(float(v[k]) * model.x[k] for k in users),
        sense=pyo.maximize
    )
    model.capacity = pyo.Constraint(
        expr=sum(float(w[k]) * model.x[k] for k in users) <= float(F_bar)
    )

    # Simpan log ke file per K
    log_file = os.path.join(LOG_DIR, f"couenne_K{K}.log")

    try:
        couenne_solver = pyo.SolverFactory(
            "couennenl",
            executable=modules.find("couenne"),
            solve_io="nl"
        )
        start = time.perf_counter()
        result = couenne_solver.solve(model, tee=False, logfile=log_file)
        elapsed = time.perf_counter() - start
    except Exception as e:
        print(f"  Couenne error: {e}")
        return None

    term = str(result.solver.termination_condition).lower()
    if "infeasible" in term:
        return None

    try:
        x_star = np.array([int(round(pyo.value(model.x[k]))) for k in users])
    except Exception:
        return None

    selected = [k + 1 for k in users if x_star[k] == 1]
    lat = compute_latency(params, x_star)

    return {
        'solver': 'Couenne',
        'objective': float(pyo.value(model.obj)),
        'x_star': x_star.tolist(),
        'selected': selected,
        'nodes': 0,
        'nodes_pruned': None,
        'solver_calls': None,
        'time': elapsed,
        'root_ub': None,
        'gap': 0.0,
        'gap_pct': 0.0,
        'completed': True,
        'log_file': log_file,
        **lat
    }


# ============================================================
# 6. MAIN EXPERIMENT LOOP
# ============================================================

def run_all_experiments():
    """Jalankan semua eksperimen dan kumpulkan hasilnya."""

    all_rows = []

    for K in K_VALUES:
        print(f"\n{'='*70}")
        print(f"  K = {K} users")
        print(f"{'='*70}")

        params = generate_params(K, seed=SEED)

        total_weight = sum(params['w'])
        feasible_all = total_weight <= F_BAR
        print(f"  Total weight: {total_weight:,.0f}")
        print(f"  F_bar:        {F_BAR:,.0f}")
        print(f"  All feasible: {feasible_all}")

        # --- Local Solvers ---
        for solver_name in ["ipopt", "minos"]:
            print(f"\n  Running B&B + {solver_name.upper()}...", end=" ")
            try:
                res = manual_branch_and_bound(params, solver_name)
                print(f"[OK] obj={res['objective']:.4f}, "
                      f"nodes={res['nodes']}, time={res['time']:.4f}s")
                res['K'] = K
                all_rows.append(res)
            except Exception as e:
                print(f"[FAIL] Error: {e}")

        # --- SCIP ---
        print(f"\n  Running SCIP...", end=" ")
        try:
            res = solve_scip(params)
            if res:
                print(f"[OK] obj={res['objective']:.4f}, "
                      f"nodes={res['nodes']}, time={res['time']:.4f}s")
                res['K'] = K
                all_rows.append(res)
            else:
                print("[FAIL] No solution")
        except Exception as e:
            print(f"[FAIL] Error: {e}")

        # --- Couenne ---
        print(f"  Running Couenne...", end=" ")
        try:
            res = solve_couenne(params)
            if res:
                print(f"[OK] obj={res['objective']:.4f}, time={res['time']:.4f}s")
                res['K'] = K
                all_rows.append(res)
            else:
                print("[FAIL] No solution")
        except Exception as e:
            print(f"[FAIL] Error: {e}")

    return all_rows


# ============================================================
# 7. FORMAT AND DISPLAY RESULTS
# ============================================================

def format_results(all_rows):
    """Format hasil ke DataFrame dan tampilkan."""

    df = pd.DataFrame(all_rows)

    # Pilih kolom untuk tabel ringkasan
    display_cols = [
        'K', 'solver', 'objective', 'selected', 'nodes',
        'solver_calls', 'time', 'gap_pct',
        'avg_latency', 'avg_local_only', 'reduction', 'completed'
    ]
    existing_cols = [c for c in display_cols if c in df.columns]

    summary = df[existing_cols].copy()
    summary = summary.rename(columns={
        'K': 'Users (K)',
        'solver': 'Solver',
        'objective': 'Optimal Obj',
        'selected': 'Selected Users',
        'nodes': 'B&B Nodes',
        'solver_calls': 'Solver Calls',
        'time': 'Time (s)',
        'gap_pct': 'Gap (%)',
        'avg_latency': 'Avg Latency (s)',
        'avg_local_only': 'Local Only (s)',
        'reduction': 'Lat. Reduction (s)',
        'completed': 'Completed?'
    })

    print(f"\n{'='*90}")
    print(f"  TABEL RINGKASAN EKSPERIMEN")
    print(f"{'='*90}")
    display(summary)

    # Per-K comparison table
    print(f"\n{'='*90}")
    print(f"  PERBANDINGAN PER VARIASI K")
    print(f"{'='*90}")

    for K in K_VALUES:
        subset = df[df['K'] == K]
        if len(subset) == 0:
            continue

        print(f"\n  K = {K}")
        print(f"  {'-'*80}")
        print(f"  {'Solver':<20} {'Objective':>12} {'Nodes':>8} {'Time (s)':>10} "
              f"{'Gap (%)':>8} {'Latency':>10} {'Selected':>20}")
        print(f"  {'-'*20} {'-'*12} {'-'*8} {'-'*10} {'-'*8} {'-'*10} {'-'*20}")

        for _, row in subset.iterrows():
            obj_str = f"{row['objective']:.4f}" if row['objective'] else "N/A"
            nodes_str = str(row['nodes']) if row['nodes'] is not None else "N/A"
            time_str = f"{row['time']:.4f}"
            gap_str = f"{row['gap_pct']:.2f}" if row['gap_pct'] is not None else "N/A"
            lat_str = f"{row['avg_latency']:.4f}" if row['avg_latency'] else "N/A"
            sel_str = str(row['selected'])

            print(f"  {row['solver']:<20} {obj_str:>12} {nodes_str:>8} {time_str:>10} "
                  f"{gap_str:>8} {lat_str:>10} {sel_str:>20}")

    return df


# ============================================================
# 8. SAVE RESULTS
# ============================================================

def save_results(df):
    """Simpan hasil ke CSV."""
    filename = "experiment_results.csv"
    save_cols = [
        'K', 'solver', 'objective', 'selected', 'nodes',
        'nodes_pruned', 'solver_calls', 'time', 'root_ub',
        'gap', 'gap_pct', 'avg_latency', 'avg_local_only',
        'reduction', 'completed'
    ]
    existing = [c for c in save_cols if c in df.columns]
    df[existing].to_csv(filename, index=False)
    print(f"\n[OK] Hasil disimpan ke: {filename}")

    # Download otomatis di Colab
    try:
        # pyrefly: ignore [missing-import]
        from google.colab import files
        files.download(filename)
    except ImportError:
        pass

    return filename


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    print("="*70)
    print("  EKSPERIMEN PERBANDINGAN LOCAL vs GLOBAL SOLVER")
    print("  Final Project ET4244 - MEC Pricing Optimization")
    print("="*70)
    print(f"\n  Variasi K: {K_VALUES}")
    print(f"  Seed: {SEED}")
    print(f"  F_bar: {F_BAR:.2e}")

    all_rows = run_all_experiments()
    df = format_results(all_rows)
    save_results(df)

    print(f"\n{'='*70}")
    print(f"  EKSPERIMEN SELESAI!")
    print(f"  Total runs: {len(all_rows)}")
    print(f"{'='*70}")
