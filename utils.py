"""
Fungsi Utilitas untuk Optimasi Harga MEC - Final Project ET4244
Paper: Price-Based Distributed Offloading for Mobile-Edge Computing
       with Computation Capacity Constraints

Menghasilkan parameter sistem sesuai spesifikasi di Bagian IV pada paper.
"""

import numpy as np


def generate_parameters(K, seed=42):
    """
    Menghasilkan parameter sistem mengikuti setup simulasi pada paper (Bagian IV).

    Parameter
    ----------
    K : int
        Jumlah user.
    seed : int
        Random seed agar hasil dapat direproduksi.

    Returns
    -------
    dict
        Dictionary berisi semua parameter sistem dan nilai turunannya.
    """
    np.random.seed(seed)

    # ── Parameter Sistem ──
    B = 1e6                          # Total bandwidth: 1 MHz
    N0_dBm = -174                    # Noise PSD dalam dBm/Hz
    N0 = 10**((N0_dBm - 30) / 10)   # Konversi ke W/Hz

    # ── Parameter User ──
    # Channel gain h_k: seragam (uniform) di [-50, -30] dB → konversi ke linear
    h_dB = np.random.uniform(-50, -30, K)
    h = 10**(h_dB / 10)

    # Frekuensi CPU lokal F_k: dipilih dari {0.1, 0.2, ..., 1.0} GHz → cycles/s
    F_choices = np.arange(0.1, 1.1, 0.1) * 1e9
    F = np.random.choice(F_choices, K)

    # Siklus CPU per bit C_k: seragam di [500, 1500] cycles/bit
    C = np.random.uniform(500, 1500, K)

    # Ukuran data R_k: seragam di [100, 500] KB → konversi ke bit
    R = np.random.uniform(100, 500, K) * 1024 * 8

    # Daya pancar Uplink / Downlink
    p_k = 0.1 * np.ones(K)      # Daya uplink: 0.1 W
    P_B = 1.0 * np.ones(K)      # Daya downlink dari BS: 1 W

    # ── Parameter Edge Cloud ──
    F_bar = 6e9                  # Kapasitas komputasi: 6×10^9 cycles/slot
    alpha = 0.2 * np.ones(K)    # Rasio output/input
    f_C = 100e9                  # Kecepatan CPU Cloud: 100 GHz

    # ── Kuantitas Turunan ──
    B_k = B / K                  # Bandwidth per user

    # Kecepatan transmisi uplink untuk user k
    r_up = B_k * np.log2(1 + p_k * h / (N0 * B_k))

    # Kecepatan transmisi downlink untuk user k
    r_down = B_k * np.log2(1 + P_B * h / (N0 * B_k))

    # Koefisien delay offloading: Beta_k = 1/r_up_k + C_k/f_C + alpha_k/r_down_k
    beta = 1.0 / r_up + C / f_C + alpha / r_down

    # Ukuran offloading seimbang (balanced offloading amount) m_k = C_k * R_k / (C_k + F_k * beta_k)
    m = (C * R) / (C + F * beta)

    # Bobot dan Nilai untuk Knapsack
    w = m * C               # bobot (weight): m_k * C_k (siklus CPU yang dikonsumsi)
    v = m * C / F            # nilai (value):  m_k * C_k / F_k (pendapatan/revenue)

    return {
        'K': K, 'B': B, 'N0': N0, 'h': h, 'h_dB': h_dB,
        'F': F, 'C': C, 'R': R,
        'p_k': p_k, 'P_B': P_B,
        'F_bar': F_bar, 'alpha': alpha, 'f_C': f_C,
        'B_k': B_k, 'r_up': r_up, 'r_down': r_down,
        'beta': beta, 'm': m, 'w': w, 'v': v
    }


def solve_dp_knapsack(params):
    """
    Menyelesaikan masalah Differentiated Pricing menggunakan Dynamic Programming
    (seperti dijelaskan di paper). Digunakan sebagai referensi / Ground Truth.

    Returns
    -------
    dict
        optimal_value, optimal_x, selected_users
    """
    K = params['K']
    w = params['w']
    v = params['v']
    F_bar = params['F_bar']

    # Diskritisasi: gunakan granularitas delta untuk mengubah bobot menjadi integer
    delta = 1e3  # 1000 siklus per unit
    w_int = np.ceil(w / delta).astype(int)
    F_int = int(np.floor(F_bar / delta))

    # Tabel DP: dp[f] = revenue maksimum menggunakan kapasitas f
    dp = np.zeros(F_int + 1)
    # Menyimpan keputusan untuk proses backtracking
    decision = np.zeros((K, F_int + 1), dtype=int)

    for k in range(K):
        # Menyusuri kapasitas secara terbalik (reverse) untuk menghindari penggunaan item berulang
        for f in range(F_int, -1, -1):
            if w_int[k] <= f and dp[f - w_int[k]] + v[k] > dp[f]:
                dp[f] = dp[f - w_int[k]] + v[k]
                decision[k][f] = 1

    # Backtrack untuk menemukan user mana saja yang terpilih
    x_opt = np.zeros(K, dtype=int)
    f = F_int
    for k in range(K - 1, -1, -1):
        if decision[k][f] == 1:
            x_opt[k] = 1
            f -= w_int[k]

    return {
        'optimal_value': dp[F_int],
        'optimal_x': {k: int(x_opt[k]) for k in range(K)},
        'selected_users': [k for k in range(K) if x_opt[k] == 1]
    }


def compute_latency(params, x_opt):
    """
    Menghitung rata-rata latensi berdasarkan pemilihan optimal x*.

    Parameter
    ----------
    params : dict
        Parameter sistem dari generate_parameters().
    x_opt : dict
        Pemilihan user yang optimal {k: 0 atau 1}.

    Returns
    -------
    float
        Rata-rata latensi di seluruh user.
    """
    K = params['K']
    m = params['m']
    C = params['C']
    R = params['R']
    F = params['F']
    r_up = params['r_up']
    r_down = params['r_down']
    f_C = params['f_C']
    alpha = params['alpha']

    latencies = []
    for k in range(K):
        ell_k = m[k] * x_opt[k]  # bit yang di-offload

        # Waktu komputasi lokal
        t_loc = (R[k] - ell_k) * C[k] / F[k]

        # Waktu offloading (uplink + eksekusi cloud + downlink)
        if ell_k > 0:
            t_up = ell_k / r_up[k]
            t_cloud = ell_k * C[k] / (f_C / K)
            t_down = alpha[k] * ell_k / r_down[k]
            t_off = t_up + t_cloud + t_down
        else:
            t_off = 0.0

        t_k = max(t_loc, t_off)
        latencies.append(t_k)

    return np.mean(latencies)


def print_parameters(params):
    """Mencetak parameter yang telah digenerate ke layar dengan format rapi."""
    K = params['K']
    print(f"\n{'='*70}")
    print(f"  Parameter Sistem (K = {K} User)")
    print(f"{'='*70}")
    print(f"  Bandwidth B = {params['B']/1e6:.1f} MHz")
    print(f"  Noise PSD N0 = -174 dBm/Hz")
    print(f"  Kapasitas Cloud F_bar = {params['F_bar']:.2e} cycles/slot")
    print(f"  Kecepatan CPU Cloud f_C = {params['f_C']/1e9:.0f} GHz")
    print(f"  Bandwidth per user B_k = {params['B_k']/1e3:.2f} kHz")
    print(f"\n  {'User':>4}  {'F_k(GHz)':>8}  {'C_k':>8}  {'R_k(KB)':>8}"
          f"  {'h_k(dB)':>8}  {'m_k':>10}  {'w_k':>12}  {'v_k':>10}")
    print(f"  {'-'*4}  {'-'*8}  {'-'*8}  {'-'*8}  {'-'*8}"
          f"  {'-'*10}  {'-'*12}  {'-'*10}")
    for k in range(K):
        print(f"  {k:4d}  {params['F'][k]/1e9:8.1f}  {params['C'][k]:8.1f}"
              f"  {params['R'][k]/(1024*8):8.1f}  {params['h_dB'][k]:8.2f}"
              f"  {params['m'][k]:10.0f}  {params['w'][k]:12.0f}"
              f"  {params['v'][k]:10.4f}")
    print(f"\n  Total bobot knapsack (semua user): {sum(params['w']):,.0f}")
    print(f"  Kapasitas Cloud F_bar:             {params['F_bar']:,.0f}")
    print(f"  Feasible (semua offload)?          "
          f"{'Ya' if sum(params['w']) <= params['F_bar'] else 'Tidak'}")
    print()
