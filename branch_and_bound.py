"""
Implementasi Branch and Bound untuk Menyelesaikan MINLP secara Lokal
====================================================================
Final Project ET4244 -- Soal 4c
Paper: Price-Based Distributed Offloading for MEC

Script ini mengimplementasikan algoritma Branch and Bound manual untuk menyelesaikan
masalah differentiated pricing (P4') yang merupakan 0-1 Binary Knapsack.

Pada setiap node B&B, relaksasi LP diselesaikan menggunakan:
  - IPOPT (Interior Point Optimizer) -- solver NLP lokal
  - MINOS -- solver NLP lokal

Variabel integer x_k dalam {0,1} direlaksasi menjadi x_k dalam [0,1].
"""

# Load modul AMPL agar IPOPT dan MINOS tersedia
from amplpy import modules
modules.load()

import pyomo.environ as pyo
import time
import sys
from utils import generate_parameters, solve_dp_knapsack, compute_latency, print_parameters


# ═══════════════════════════════════════════════════════════════════════
#  BRANCH AND BOUND -- Algoritma Inti
# ═══════════════════════════════════════════════════════════════════════

class BranchAndBoundNode:
    """Merepresentasikan sebuah node di dalam pohon B&B."""
    def __init__(self, fixed_vars=None):
        self.fixed_vars = fixed_vars if fixed_vars is not None else {}

    def __repr__(self):
        fixed_str = ", ".join(f"x[{k}]={v}" for k, v in self.fixed_vars.items())
        return f"Node({fixed_str})" if fixed_str else "Node(akar)"


def build_relaxation_model(params, fixed_vars):
    """
    Membangun model relaksasi LP untuk masalah binary knapsack pada sebuah node B&B.

    Masalah asli P4':
        max  Σ v_k * x_k        (v_k = m_k * C_k / F_k)
        s.t. Σ w_k * x_k <= F_bar   (w_k = m_k * C_k)
             x_k dalam {0, 1}

    Direlaksasi menjadi:
        x_k dalam [0, 1]  (kontinu)
        Ditambah variabel yang sudah di-fix dari keputusan percabangan (branching).
    """
    K = params['K']
    w = params['w']
    v = params['v']
    F_bar = params['F_bar']

    model = pyo.ConcreteModel()
    model.K_set = pyo.RangeSet(0, K - 1)

    # Variabel Keputusan: x_k dalam [0, 1] (direlaksasi dari biner)
    model.x = pyo.Var(model.K_set, bounds=(0, 1), within=pyo.NonNegativeReals)

    # Fix variabel dari keputusan percabangan
    for idx, val in fixed_vars.items():
        model.x[idx].fix(val)

    # Fungsi Objektif: maksimalkan Σ v_k * x_k
    model.obj = pyo.Objective(
        expr=sum(v[k] * model.x[k] for k in model.K_set),
        sense=pyo.maximize
    )

    # Constraint (Kendala): Σ w_k * x_k <= F_bar
    model.capacity = pyo.Constraint(
        expr=sum(w[k] * model.x[k] for k in model.K_set) <= F_bar
    )

    return model


def solve_relaxation(params, fixed_vars, solver_name='ipopt'):
    """
    Menyelesaikan relaksasi LP pada node B&B menggunakan solver NLP yang ditentukan.

    Parameter
    ----------
    params : dict
        Parameter sistem.
    fixed_vars : dict
        {index: value} untuk variabel yang di-fix dari percabangan.
    solver_name : str
        'ipopt' atau 'minos'.

    Returns
    -------
    tuple
        (nilai_objektif, dict_nilai_x, bool_feasible, iterasi)
    """
    K = params['K']
    w = params['w']
    v = params['v']
    F_bar = params['F_bar']

    # Jika semua variabel sudah di-fix, evaluasi secara langsung (tanpa solver)
    if len(fixed_vars) == K:
        obj_val = sum(v[k] * fixed_vars[k] for k in range(K))
        cap_used = sum(w[k] * fixed_vars[k] for k in range(K))
        if cap_used > F_bar + 1e-6:
            return None, None, False, 0
        return obj_val, dict(fixed_vars), True, 0

    model = build_relaxation_model(params, fixed_vars)

    iterations = 0

    if solver_name == 'ipopt':
        solver = pyo.SolverFactory('ipopt')
        solver.options['print_level'] = 0          # Matikan output
        solver.options['max_iter'] = 3000
        solver.options['tol'] = 1e-8
        result = solver.solve(model, tee=False)
        # Coba ekstrak jumlah iterasi dari log solver
        try:
            iterations = result.solver.statistics.get('iterations', 0)
        except:
            iterations = 0

    elif solver_name == 'minos':
        solver = pyo.SolverFactory('minos')
        result = solver.solve(model, tee=False)

    else:
        raise ValueError(f"Solver tidak dikenal: {solver_name}")

    if result.solver.termination_condition == pyo.TerminationCondition.optimal:
        obj_val = pyo.value(model.obj)
        x_vals = {k: pyo.value(model.x[k]) for k in model.K_set}
        return obj_val, x_vals, True, iterations
    else:
        return None, None, False, 0


def branch_and_bound(params, solver_name='ipopt', verbose=False):
    """
    Branch and Bound Manual untuk Binary Knapsack (Differentiated Pricing).

    Algoritma:
    1. Mulai dengan node akar (semua x_k direlaksasi ke [0,1])
    2. Selesaikan relaksasi LP
    3. Jika semua x_k adalah integer -> periksa apakah menjadi solusi terbaik baru
    4. Jika ada x_k pecahan (fractional) -> branch pada variabel paling pecahan
    5. Prune (pangkas) dengan bound (relaksasi <= solusi integer terbaik) atau jika infeasible
    6. Ulangi sampai stack kosong

    Parameter
    ----------
    params : dict
        Parameter sistem dari generate_parameters().
    solver_name : str
        Solver NLP yang digunakan ('ipopt' atau 'minos').
    verbose : bool
        Cetak informasi detail untuk setiap node.

    Returns
    -------
    dict
        Hasil termasuk nilai optimal, user yang dipilih, dan metrik performa.
    """
    K = params['K']

    best_obj = -float('inf')
    best_x = None
    nodes_explored = 0
    total_iterations = 0
    nodes_pruned_bound = 0
    nodes_pruned_infeasible = 0

    # DFS stack: list dari BranchAndBoundNode
    stack = [BranchAndBoundNode()]

    start_time = time.time()

    while stack:
        node = stack.pop()
        nodes_explored += 1

        if verbose:
            print(f"\n  [Node {nodes_explored}] {node}")

        # Selesaikan relaksasi LP di node ini
        obj_val, x_vals, feasible, iters = solve_relaxation(
            params, node.fixed_vars, solver_name
        )
        total_iterations += iters

        # ── Pruning: Infeasible ──
        if not feasible:
            nodes_pruned_infeasible += 1
            if verbose:
                print(f"    -> Dipangkas (infeasible/tidak layak)")
            continue

        # ── Pruning: Bound ──
        if obj_val <= best_obj + 1e-10:
            nodes_pruned_bound += 1
            if verbose:
                print(f"    -> Dipangkas (bound/batas: {obj_val:.6f} <= {best_obj:.6f})")
            continue

        if verbose:
            print(f"    -> Nilai relaksasi: {obj_val:.6f}")

        # ── Cek Integralitas ──
        fractional_vars = []
        for k in range(K):
            if k not in node.fixed_vars:
                val = x_vals[k]
                if abs(val - round(val)) > 1e-6:
                    fractional_vars.append((k, val))

        if not fractional_vars:
            # Semua integer -> potensi solusi integer terbaik baru
            if obj_val > best_obj:
                best_obj = obj_val
                best_x = {k: int(round(x_vals[k])) for k in range(K)}
                if verbose:
                    selected = [k for k in range(K) if best_x[k] == 1]
                    print(f"    * Solusi integer terbaik baru! Nilai={obj_val:.6f}")
                    print(f"      User yang dipilih: {selected}")
            continue

        # ── Branching (Percabangan) ──
        # Pilih variabel paling pecahan (paling dekat dengan 0.5)
        branch_var, branch_val = min(fractional_vars, key=lambda x: abs(x[1] - 0.5))

        if verbose:
            print(f"    -> Melakukan branch pada x[{branch_var}] = {branch_val:.4f}")

        # Buat node anak (child nodes)
        # Anak kiri: x[branch_var] = 0
        left_fixed = dict(node.fixed_vars)
        left_fixed[branch_var] = 0
        stack.append(BranchAndBoundNode(left_fixed))

        # Anak kanan: x[branch_var] = 1
        right_fixed = dict(node.fixed_vars)
        right_fixed[branch_var] = 1
        stack.append(BranchAndBoundNode(right_fixed))

    elapsed_time = time.time() - start_time

    # ── Menghitung hasil turunan ──
    selected_users = [k for k, val in best_x.items() if val == 1] if best_x else []

    # Harga optimal (Prices)
    prices = {}
    for k in range(K):
        if best_x and best_x[k] == 1:
            prices[k] = 1.0 / params['F'][k]
        else:
            prices[k] = float('inf')

    # Rincian Pendapatan
    revenue_per_user = {}
    for k in range(K):
        if best_x and best_x[k] == 1:
            revenue_per_user[k] = params['v'][k]
        else:
            revenue_per_user[k] = 0.0

    # Rata-rata Latensi
    avg_latency = compute_latency(params, best_x) if best_x else float('inf')

    # Penggunaan Kapasitas
    capacity_used = sum(params['w'][k] * best_x[k] for k in range(K)) if best_x else 0
    capacity_pct = (capacity_used / params['F_bar']) * 100

    return {
        'solver': solver_name,
        'optimal_value': best_obj,
        'optimal_x': best_x,
        'selected_users': selected_users,
        'prices': prices,
        'revenue_per_user': revenue_per_user,
        'avg_latency': avg_latency,
        'nodes_explored': nodes_explored,
        'nodes_pruned_bound': nodes_pruned_bound,
        'nodes_pruned_infeasible': nodes_pruned_infeasible,
        'total_iterations': total_iterations,
        'time': elapsed_time,
        'capacity_used': capacity_used,
        'capacity_pct': capacity_pct
    }


# -----------------------------------------------------------------------
#  TAMPILAN HASIL (RESULT DISPLAY)
# -----------------------------------------------------------------------

def print_results(result, params):
    """Mencetak hasil B&B dengan format rapi."""
    print(f"\n{'-'*70}")
    print(f"  HASIL BRANCH AND BOUND -- Solver: {result['solver'].upper()}")
    print(f"{'-'*70}")

    print(f"\n  +-- Solusi Optimal ------------------------------------+")
    print(f"  | Pendapatan Optimal (objektif):  {result['optimal_value']:.6f}")
    print(f"  | Rata-rata Latensi:              {result['avg_latency']:.6f} detik")
    print(f"  | User Terpilih:                  {result['selected_users']}")
    print(f"  | Kapasitas Terpakai:             {result['capacity_used']:,.0f} / "
          f"{params['F_bar']:,.0f} ({result['capacity_pct']:.1f}%)")
    print(f"  +----------------------------------------------------------+")

    print(f"\n  +-- Metrik Performa ------------------------------------+")
    print(f"  | Waktu Komputasi:                {result['time']:.4f} detik")
    print(f"  | Node Dieksplorasi:              {result['nodes_explored']}")
    print(f"  | Node Dipangkas (bound):         {result['nodes_pruned_bound']}")
    print(f"  | Node Dipangkas (infeasible):    {result['nodes_pruned_infeasible']}")
    print(f"  | Total Iterasi Solver:           {result['total_iterations']}")
    print(f"  +----------------------------------------------------------+")

    print(f"\n  +-- Detail User ---------------------------------------+")
    print(f"  | {'User':>4}  {'x*':>3}  {'mu*(1/F_k)':>12}  {'Revenue':>10}"
          f"  {'m_k(bits)':>10}  {'w_k(cycles)':>12} |")
    print(f"  | {'-'*4}  {'-'*3}  {'-'*12}  {'-'*10}  {'-'*10}  {'-'*12} |")
    K = params['K']
    for k in range(K):
        x_k = result['optimal_x'][k] if result['optimal_x'] else 0
        mu_k = f"{result['prices'][k]:.4e}" if result['prices'][k] != float('inf') else "INF"
        rev_k = result['revenue_per_user'][k]
        print(f"  | {k:4d}  {x_k:3d}  {mu_k:>12}  {rev_k:10.4f}"
              f"  {params['m'][k]:10.0f}  {params['w'][k]:12.0f} |")
    print(f"  +----------------------------------------------------------+")


# -----------------------------------------------------------------------
#  MAIN -- Jalankan B&B dengan IPOPT
# -----------------------------------------------------------------------

def main():
    print("=" * 70)
    print("  SOAL 4c: MENYELESAIKAN MINLP LOKAL -- Branch and Bound + IPOPT")
    print("  Paper: Price-Based Distributed Offloading for MEC")
    print("=" * 70)

    for K in [5, 10]:
        params = generate_parameters(K)
        print_parameters(params)

        # ── Selesaikan dengan B&B + IPOPT ──
        print(f"  Menjalankan Branch and Bound dengan IPOPT (K={K})...")
        result_ipopt = branch_and_bound(params, solver_name='ipopt', verbose=True)
        print_results(result_ipopt, params)

        # ── Verifikasi dengan DP (Ground Truth) ──
        print(f"\n  {'-'*70}")
        print(f"  VERIFIKASI: Dynamic Programming (Kunci Jawaban/Ground Truth)")
        dp_result = solve_dp_knapsack(params)
        print(f"  DP Pendapatan Optimal: {dp_result['optimal_value']:.6f}")
        print(f"  DP User Terpilih:      {dp_result['selected_users']}")
        print(f"  B&B Pendapatan Optimal:{result_ipopt['optimal_value']:.6f}")
        print(f"  B&B User Terpilih:     {result_ipopt['selected_users']}")

        match = abs(result_ipopt['optimal_value'] - dp_result['optimal_value']) < 0.01
        print(f"  Sesuai: {'[OK] YA' if match else '[X] TIDAK'}")
        print(f"  {'-'*70}")


if __name__ == '__main__':
    main()
