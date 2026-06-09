"""
Perbandingan Hasil Branch and Bound: IPOPT vs MINOS
===================================================
Final Project ET4244 -- Soal 4c
Paper: Price-Based Distributed Offloading for MEC

Menjalankan algoritma B&B dengan kedua solver NLP lokal dan menghasilkan tabel perbandingan.
"""

# Load modul AMPL agar IPOPT dan MINOS tersedia
from amplpy import modules
modules.load()

import sys
import json
import numpy as np
from utils import generate_parameters, solve_dp_knapsack, compute_latency, print_parameters
from branch_and_bound import branch_and_bound, print_results


def run_comparison(K_values=[5, 10], seed=42):
    """
    Menjalankan Branch and Bound dengan IPOPT dan MINOS untuk setiap nilai K,
    kemudian membandingkan hasilnya.
    """
    all_results = {}

    for K in K_values:
        print(f"\n{'='*70}")
        print(f"  K = {K} USER")
        print(f"{'='*70}")

        params = generate_parameters(K, seed=seed)
        print_parameters(params)

        # DP Ground Truth (Kunci Jawaban Absolut)
        dp_result = solve_dp_knapsack(params)
        dp_latency = compute_latency(params, dp_result['optimal_x'])
        print(f"  DP Ground Truth:")
        print(f"    Pendapatan: {dp_result['optimal_value']:.6f}")
        print(f"    Terpilih:   {dp_result['selected_users']}")
        print(f"    Latensi:    {dp_latency:.6f} s")

        results_for_K = {'dp': dp_result, 'dp_latency': dp_latency}

        # === IPOPT ===
        print(f"\n  [1/2] Menjalankan B&B dengan IPOPT...")
        try:
            result_ipopt = branch_and_bound(params, solver_name='ipopt', verbose=False)
            print_results(result_ipopt, params)
            results_for_K['ipopt'] = result_ipopt
        except Exception as e:
            print(f"  IPOPT Error: {e}")
            results_for_K['ipopt'] = None

        # === MINOS ===
        print(f"\n  [2/2] Menjalankan B&B dengan MINOS...")
        try:
            result_minos = branch_and_bound(params, solver_name='minos', verbose=False)
            print_results(result_minos, params)
            results_for_K['minos'] = result_minos
        except Exception as e:
            print(f"  MINOS Error: {e}")
            results_for_K['minos'] = None

        all_results[K] = results_for_K

    return all_results


def print_comparison_table(all_results):
    """Mencetak tabel perbandingan berdampingan (side-by-side) antara IPOPT vs MINOS."""
    print(f"\n{'='*90}")
    print(f"  TABEL PERBANDINGAN: IPOPT vs MINOS (Branch and Bound)")
    print(f"{'='*90}")

    for K, results in all_results.items():
        print(f"\n  K = {K} user")
        print(f"  {'-'*80}")

        dp = results['dp']
        ipopt = results.get('ipopt')
        minos = results.get('minos')

        header = f"  {'Metrik':<35} {'DP (Asli)':>15} {'IPOPT':>15} {'MINOS':>15}"
        print(header)
        print(f"  {'-'*35} {'-'*15} {'-'*15} {'-'*15}")

        # Pendapatan Optimal
        dp_rev = f"{dp['optimal_value']:.6f}"
        ip_rev = f"{ipopt['optimal_value']:.6f}" if ipopt else "N/A"
        mi_rev = f"{minos['optimal_value']:.6f}" if minos else "N/A"
        print(f"  {'Pendapatan Optimal (Objektif)':<35} {dp_rev:>15} {ip_rev:>15} {mi_rev:>15}")

        # Rata-rata Latensi
        dp_lat = f"{results['dp_latency']:.6f}"
        ip_lat = f"{ipopt['avg_latency']:.6f}" if ipopt else "N/A"
        mi_lat = f"{minos['avg_latency']:.6f}" if minos else "N/A"
        print(f"  {'Rata-rata Latensi (detik)':<35} {dp_lat:>15} {ip_lat:>15} {mi_lat:>15}")

        # User yang dipilih
        dp_sel = str(dp['selected_users'])
        ip_sel = str(ipopt['selected_users']) if ipopt else "N/A"
        mi_sel = str(minos['selected_users']) if minos else "N/A"
        print(f"  {'User Terpilih':<35} {dp_sel:>15} {ip_sel:>15} {mi_sel:>15}")

        # Waktu Komputasi
        dp_time = "N/A"
        ip_time = f"{ipopt['time']:.4f}" if ipopt else "N/A"
        mi_time = f"{minos['time']:.4f}" if minos else "N/A"
        print(f"  {'Waktu Komputasi (detik)':<35} {dp_time:>15} {ip_time:>15} {mi_time:>15}")

        # Node Dieksplorasi
        ip_nodes = str(ipopt['nodes_explored']) if ipopt else "N/A"
        mi_nodes = str(minos['nodes_explored']) if minos else "N/A"
        print(f"  {'Node Dieksplorasi':<35} {'N/A':>15} {ip_nodes:>15} {mi_nodes:>15}")

        # Node Dipangkas (Bound)
        ip_pbound = str(ipopt['nodes_pruned_bound']) if ipopt else "N/A"
        mi_pbound = str(minos['nodes_pruned_bound']) if minos else "N/A"
        print(f"  {'Node Dipangkas (Bound)':<35} {'N/A':>15} {ip_pbound:>15} {mi_pbound:>15}")

        # Node Dipangkas (Infeasible)
        ip_pinf = str(ipopt['nodes_pruned_infeasible']) if ipopt else "N/A"
        mi_pinf = str(minos['nodes_pruned_infeasible']) if minos else "N/A"
        print(f"  {'Node Dipangkas (Infeasible)':<35} {'N/A':>15} {ip_pinf:>15} {mi_pinf:>15}")

        # Penggunaan Kapasitas
        ip_cap = f"{ipopt['capacity_pct']:.1f}%" if ipopt else "N/A"
        mi_cap = f"{minos['capacity_pct']:.1f}%" if minos else "N/A"
        print(f"  {'Penggunaan Kapasitas':<35} {'N/A':>15} {ip_cap:>15} {mi_cap:>15}")

        # Cek kesesuaian dengan DP
        if ipopt:
            ip_match = abs(ipopt['optimal_value'] - dp['optimal_value']) < 0.01
            print(f"\n  IPOPT sesuai dengan DP: {'[OK] YA' if ip_match else '[X] TIDAK'}")
        if minos:
            mi_match = abs(minos['optimal_value'] - dp['optimal_value']) < 0.01
            print(f"  MINOS sesuai dengan DP: {'[OK] YA' if mi_match else '[X] TIDAK'}")

        print(f"  {'-'*80}")

    # Perbandingan Kompleksitas Big-O
    print(f"\n{'='*90}")
    print(f"  ANALISIS KOMPLEKSITAS BIG-O")
    print(f"{'='*90}")
    print(f"  {'Metode':<30} {'Kompleksitas Waktu':<25} {'Kompleksitas Ruang':<20}")
    print(f"  {'-'*30} {'-'*25} {'-'*20}")
    print(f"  {'Branch & Bound (B&B)':<30} {'O(2^K * T_solver)':<25} {'O(K)':<20}")
    print(f"  {'  - IPOPT per node':<30} {'O(n^3) per iterasi':<25} {'O(n^2)':<20}")
    print(f"  {'  - MINOS per node':<30} {'O(n^2) per iterasi':<25} {'O(n^2)':<20}")
    print(f"  {'DP (Ground Truth)':<30} {'O(K * F_bar/delta)':<25} {'O(K * F_bar/delta)':<20}")
    print(f"\n  Catatan:")
    print(f"  - K = jumlah user")
    print(f"  - n = jumlah variabel (= K untuk masalah ini)")
    print(f"  - T_solver = waktu untuk satu kali run NLP (LP relaksasi)")
    print(f"  - IPOPT menggunakan metode Interior Point: kubik per iterasi")
    print(f"  - MINOS menggunakan Simplex + Reduced Gradient: kuadratik per iterasi")
    print(f"  - Skenario terburuk B&B adalah eksponensial, namun pruning mempercepat praktiknya")
    print(f"  - DP bersifat pseudo-polynomial, sangat bergantung pada nilai kapasitas F_bar")


if __name__ == '__main__':
    results = run_comparison(K_values=[5, 10])
    print_comparison_table(results)
