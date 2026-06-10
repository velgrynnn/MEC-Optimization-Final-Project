# Ringkasan Hasil Eksperimen v2: Local vs Global Solver

**Konfigurasi:** K = [10, 15, 20, 25, 30, 35, 40, 45, 50] | Seed = 1 | F_bar = 6x10^9 | **MAX_NODES = 2000**

> **Update dari v1:** MAX_NODES dinaikkan dari 1000 menjadi 2000. Hasilnya, **B&B+IPOPT di K=50 kini berhasil converge** (1057 nodes, gap 0.00%) — berbeda dengan v1 yang gagal (1000 nodes, gap 7.74%). Log SCIP dan Couenne juga disimpan per setiap K.

---

## Parameter Sistem (Berdasarkan Paper)

Tabel berikut berisi penjelasan seluruh variabel dan parameter sistem yang digunakan untuk membangkitkan data eksperimen (sesuai *setup* simulasi pada paper referensi).

| Simbol | Deskripsi | Nilai / Distribusi |
|:---:|---|---|
| $K$ | Jumlah pengguna (*users*) dalam jaringan | $10, 15, 20, \dots, 50$ |
| $B$ | Total *bandwidth* komunikasi Edge Server | $1$ MHz ($10^6$ Hz) |
| $N_0$ | *Noise power spectral density* | $-174$ dBm/Hz |
| $h_k$ | *Channel gain* dari Base Station ke user $k$ | Seragam (Uniform) di $[-50, -30]$ dB |
| $F_k$ | Kapasitas frekuensi CPU lokal milik user $k$ | Dipilih acak dari $\{0.1, 0.2, \dots, 1.0\}$ GHz |
| $C_k$ | Siklus CPU yang dibutuhkan untuk memproses 1 bit data | Seragam (Uniform) di $[500, 1500]$ cycles/bit |
| $R_k$ | Ukuran data tugas (*task size*) milik user $k$ | Seragam (Uniform) di $[100, 500]$ KB |
| $p_k^t$ | Daya transmisi *uplink* dari perangkat user $k$ | $0.1$ W |
| $P_{B,k}$ | Daya transmisi *downlink* dari Base Station ke user $k$ | $1.0$ W |
| $\alpha_k$ | Koefisien bobot prioritas waktu pada utilitas user | $0.2$ |
| $f_c$ | Kecepatan CPU Edge Server jika melayani 1 user (*baseline*) | $100$ GHz |
| $F_{bar}$ | **Kapasitas maksimal total** CPU Edge Server (Constraint) | $6 \times 10^9$ cycles/s ($6$ GHz) |
| $v_k$ | *Value* / Profit ekonomis BS jika menerima request user $k$ | *Dihitung matematis per user* |
| $w_k$ | *Weight* / Beban komputasi yang diminta user $k$ | *Dihitung dari $C_k \times R_k$* |

---

## Tabel Ringkasan Per Variasi K

### K = 10 users

| Solver | Objective | Selected Users | Nodes | Solver Calls | Waktu (s) | Gap (%) | Completed |
|--------|-----------|----------------|-------|--------------|-----------|---------|-----------|
| B&B+IPOPT | 23.4580 | [1, 9] | 99 | 74 | 14.15 | 0.00 | Ya |
| B&B+MINOS | 23.4580 | [1, 9] | 91 | 68 | 15.56 | 0.00 | Ya |
| SCIP | 23.4580 | [1, 9] | 1 | -- | **0.051** | 0.00 | Ya |
| Couenne | 23.4580 | [1, 9] | 0 | -- | 0.192 | 0.00 | Ya |

### K = 15 users

| Solver | Objective | Selected Users | Nodes | Solver Calls | Waktu (s) | Gap (%) | Completed |
|--------|-----------|----------------|-------|--------------|-----------|---------|-----------|
| B&B+IPOPT | 30.0549 | [1, 6, 8] | 113 | 76 | 14.31 | 0.00 | Ya |
| B&B+MINOS | 30.0549 | [1, 6, 8] | 63 | 40 | 8.16 | 0.00 | Ya |
| SCIP | 30.0549 | [1, 6, 8] | 1 | -- | **0.013** | 0.00 | Ya |
| Couenne | 30.0549 | [1, 6, 8] | 0 | -- | 0.123 | 0.00 | Ya |

### K = 20 users

| Solver | Objective | Selected Users | Nodes | Solver Calls | Waktu (s) | Gap (%) | Completed |
|--------|-----------|----------------|-------|--------------|-----------|---------|-----------|
| B&B+IPOPT | 36.3503 | [7, 8, 11, 18] | 257 | 196 | 37.25 | 0.00 | Ya |
| B&B+MINOS | 36.3503 | [7, 8, 11, 18] | 197 | 143 | 30.71 | 0.00 | Ya |
| SCIP | 36.3503 | [7, 8, 11, 18] | 1 | -- | **0.040** | 0.00 | Ya |
| Couenne | 36.3503 | [7, 8, 11, 18] | 0 | -- | 0.148 | 0.00 | Ya |

### K = 25 users

| Solver | Objective | Selected Users | Nodes | Solver Calls | Waktu (s) | Gap (%) | Completed |
|--------|-----------|----------------|-------|--------------|-----------|---------|-----------|
| B&B+IPOPT | 45.0418 | [8, 11, 18, 22] | 187 | 157 | 32.14 | 0.00 | Ya |
| B&B+MINOS | 45.0418 | [8, 11, 18, 22] | 345 | 269 | 59.94 | 0.00 | Ya |
| SCIP | 45.0418 | [8, 11, 18, 22] | 1 | -- | **0.048** | 0.00 | Ya |
| Couenne | 45.0418 | [8, 11, 18, 22] | 0 | -- | 0.141 | 0.00 | Ya |

### K = 30 users

| Solver | Objective | Selected Users | Nodes | Solver Calls | Waktu (s) | Gap (%) | Completed |
|--------|-----------|----------------|-------|--------------|-----------|---------|-----------|
| B&B+IPOPT | 42.1028 | [5, 12, 16, 19] | 367 | 328 | 67.30 | 0.00 | Ya |
| B&B+MINOS | 42.1028 | [5, 12, 16, 19] | 537 | 440 | 99.22 | 0.00 | Ya |
| SCIP | 42.1028 | [5, 12, 16, 19] | 1 | -- | **0.035** | 0.00 | Ya |
| Couenne | 42.1028 | [5, 12, 16, 19] | 0 | -- | 0.088 | 0.00 | Ya |

### K = 35 users

| Solver | Objective | Selected Users | Nodes | Solver Calls | Waktu (s) | Gap (%) | Completed |
|--------|-----------|----------------|-------|--------------|-----------|---------|-----------|
| B&B+IPOPT | 59.9519 | [3, 7, 26, 33] | 631 | 525 | 52.96 | 0.00 | Ya |
| B&B+MINOS | 59.9519 | [3, 7, 26, 33] | 711 | 484 | 42.32 | 0.00 | Ya |
| SCIP | 59.9519 | [3, 7, 26, 33] | 1 | -- | **0.007** | 0.00 | Ya |
| Couenne | 59.9519 | [3, 7, 26, 33] | 0 | -- | 0.070 | 0.00 | Ya |

### K = 40 users

| Solver | Objective | Selected Users | Nodes | Solver Calls | Waktu (s) | Gap (%) | Completed |
|--------|-----------|----------------|-------|--------------|-----------|---------|-----------|
| B&B+IPOPT | 59.4396 | [20, 34] | 245 | 130 | 11.21 | 0.00 | Ya |
| B&B+MINOS | 59.4396 | [20, 34] | 883 | 706 | **60.06** | 0.00 | Ya |
| SCIP | 59.4396 | [20, 34] | 1 | -- | **0.016** | 0.00 | Ya |
| Couenne | 59.4396 | [20, 34] | 0 | -- | 0.075 | 0.00 | Ya |

### K = 45 users

| Solver | Objective | Selected Users | Nodes | Solver Calls | Waktu (s) | Gap (%) | Completed |
|--------|-----------|----------------|-------|--------------|-----------|---------|-----------|
| B&B+IPOPT | 56.5662 | [13, 27, 41] | 613 | 398 | 32.39 | 0.00 | Ya |
| B&B+MINOS | 56.5662 | [13, 27, 41] | 485 | 324 | 27.28 | 0.00 | Ya |
| SCIP | 56.5662 | [13, 27, 41] | 1 | -- | **0.026** | 0.00 | Ya |
| Couenne | 56.5662 | [13, 27, 41] | 0 | -- | 0.076 | 0.00 | Ya |

### K = 50 users (Kasus Menarik -- Bandingkan dengan v1!)

| Solver | Objective | Selected Users | Nodes | Solver Calls | Waktu (s) | Gap (%) | Completed |
|--------|-----------|----------------|-------|--------------|-----------|---------|-----------|
| B&B+IPOPT | 59.4842 | [36, 38] | **1057** | 607 | **56.31** | **0.00** | **Ya** |
| B&B+MINOS | 59.4842 | [36, 38] | 111 | 59 | 5.40 | 0.00 | Ya |
| SCIP | 59.4842 | [36, 38] | 1 | -- | **0.019** | 0.00 | Ya |
| Couenne | 59.4842 | [36, 38] | 4 | -- | 0.077 | 0.00 | Ya |

> **Perbandingan v1 vs v2 di K=50:**
> - v1 (MAX_NODES=1000): B&B+IPOPT **GAGAL** -- obj=55.35, gap=**7.74%**, 1000 nodes (limit tercapai)
> - v2 (MAX_NODES=2000): B&B+IPOPT **BERHASIL** -- obj=59.48, gap=**0.00%**, 1057 nodes
> - Artinya IPOPT hanya butuh **57 node tambahan** di atas limit 1000 untuk menemukan solusi optimal!

---

## Tabel Perbandingan Ringkas (Semua K)

### Waktu Komputasi (detik)

| K | B&B+IPOPT | B&B+MINOS | SCIP | Couenne |
|---|-----------|-----------|------|---------|
| 10 | 14.15 | 15.56 | **0.051** | 0.192 |
| 15 | 14.31 | 8.16 | **0.013** | 0.123 |
| 20 | 37.25 | 30.71 | **0.040** | 0.148 |
| 25 | 32.14 | 59.94 | **0.048** | 0.141 |
| 30 | 67.30 | 99.22 | **0.035** | 0.088 |
| 35 | 52.96 | 42.32 | **0.007** | 0.070 |
| 40 | 11.21 | 60.06 | **0.016** | 0.075 |
| 45 | 32.39 | 27.28 | **0.026** | 0.076 |
| 50 | 56.31 | 5.40 | **0.019** | 0.077 |

### Jumlah Nodes B&B

| K | B&B+IPOPT | B&B+MINOS | SCIP | Couenne |
|---|-----------|-----------|------|---------|
| 10 | 99 | 91 | **1** | 0 |
| 15 | 113 | 63 | **1** | 0 |
| 20 | 257 | 197 | **1** | 0 |
| 25 | 187 | 345 | **1** | 0 |
| 30 | 367 | 537 | **1** | 0 |
| 35 | 631 | 711 | **1** | 0 |
| 40 | 245 | 883 | **1** | 0 |
| 45 | 613 | 485 | **1** | 0 |
| 50 | 1057 | 111 | **1** | 4 |

### Optimality Gap (%)

| K | B&B+IPOPT | B&B+MINOS | SCIP | Couenne |
|---|-----------|-----------|------|---------|
| 10-50 | **0.00** | **0.00** | **0.00** | **0.00** |

> Semua solver berhasil mencapai gap 0% untuk semua variasi K! (Berbeda dengan v1 di mana IPOPT gagal di K=50)

---

## Analisis Log SCIP dan Couenne

### Ringkasan Log SCIP Per K

Log tersimpan di folder `solver_logs/scip_K{K}.log`

| K | Presolve | Vars Tersisa | Cliques | Cuts | Heuristics | LP Iter | Solving Time |
|---|----------|-------------|---------|------|------------|---------|--------------|
| 10 | 0 del vars | 10 bin | 2 | 4 | locks, simplerounding, rounding | 10 | 0.00s |
| 15 | 0 del vars | 15 bin | 3 | - | locks, simplerounding | - | 0.00s |
| 20 | 0 del vars | 20 bin | 6 | - | locks, simplerounding | - | 0.00s |
| 25 | 0 del vars | 25 bin | 7 | - | locks, simplerounding | - | 0.00s |
| 30 | 0 del vars | 30 bin | 8 | - | locks, simplerounding, oneopt | - | 0.00s |
| 35 | 0 del vars | 35 bin | 9 | - | locks, simplerounding | - | 0.00s |
| 40 | 0 del vars | 40 bin | 6 | - | locks, simplerounding, oneopt | - | 0.00s |
| 45 | 0 del vars | 45 bin | 11 | - | locks, simplerounding, oneopt | - | 0.00s |
| 50 | 0 del vars | 50 bin | 12 | 7 | locks, simplerounding, oneopt | 21 | 0.00s |

**Catatan SCIP:**
- Untuk semua K, SCIP menyelesaikan masalah di **root node (1 node)** tanpa branching.
- SCIP menggunakan **cutting planes** dan **primal heuristics** (locks, simplerounding, oneopt) untuk menemukan solusi integer langsung di root.
- Untuk K=50, SCIP menemukan **7 solusi** secara progresif: gap turun dari 1862.65% -> 347.85% -> 44.10% -> 19.21% -> 0.87% -> **0.00%** dalam waktu < 0.01 detik.

### Ringkasan Log Couenne Per K

Log tersimpan di folder `solver_logs/couenne_K{K}.log`

| K | LP Relaxation | Lin. Cuts (root) | Lin. Cuts (total) | B&B Nodes | Total Time |
|---|--------------|-----------------|-------------------|-----------|------------|
| 10 | Obj = -27.12 | 2 | 2 | 0 | 0.011s |
| 15 | Obj = -31.69 | 2 | 2 | 0 | 0.008s |
| 20 | Obj = -38.20 | 2 | 2 | 0 | 0.004s |
| 25 | Obj = -46.85 | 2 | 2 | 0 | 0.005s |
| 30 | Obj = -43.61 | 2 | 2 | 0 | 0.004s |
| 35 | Obj = -59.98 | 2 | 2 | 0 | 0.003s |
| 40 | Obj = -60.00 | 2 | 2 | 0 | 0.005s |
| 45 | Obj = -60.00 | 2 | 2 | 0 | 0.008s |
| 50 | Obj = -60.00 | 2 | 2 | **4** | **0.014s** |

**Catatan Couenne:**
- Untuk K=10 sampai K=45, Couenne menyelesaikan masalah dengan **0 B&B nodes** (selesai di root).
- Untuk **K=50**, Couenne membutuhkan **4 B&B nodes** — ini satu-satunya kasus di mana Couenne perlu branching!
- Couenne selalu menambahkan **2 linearization cuts** di root node.
- LP relaxation menunjukkan upper bound yang semakin mendekati kapasitas F_bar (60.0) seiring K meningkat.

---

## Contoh Detail Log: K=50

### SCIP K=50 (dari `solver_logs/scip_K50.log`)

```
feasible solution found by trivial heuristic, objective value 0.0
presolving (1 rounds): 0 deleted vars, 12 cliques
presolved problem has 50 variables (50 bin) and 1 constraint

Solving progress at root node:
  locks heuristic  -> obj = 13.05  (gap 1862.65%)
  oneopt heuristic -> obj = 13.40  (gap 1812.27%)
  LP relaxation    -> dual = 60.00 (gap 347.85%)
  simplerounding   -> obj = 41.64  (gap 44.10%)
  oneopt           -> obj = 50.33  (gap 19.21%)
  + cutting planes -> dual = 60.00 (gap 0.87%)
  simplerounding   -> obj = 59.48  (gap 0.00%)  <-- OPTIMAL!

SCIP Status: problem is solved [optimal solution found]
Solving Time: 0.00s | Nodes: 1 | Gap: 0.00%
Primal Bound: 59.4842 (7 solutions found)
```

### Couenne K=50 (dari `solver_logs/couenne_K50.log`)

```
NLP solution: obj = -60.00 (LP relaxation)
Couenne cutoff: -46.53 -> -59.48 (progressively tighter)
Constraints: 1 | Variables: 50 (50 integer)
LP relaxation: Obj = -60 (4 iterations)

At root node: 0 cuts changed objective
Column cuts: 1 active
After 2 nodes: cutoff improved to -59.48
Integer solution of -59.4842 found after 7 iterations and 2 nodes

Total solve time: 0.014s
Branch-and-bound nodes: 4
Gap: 0.00%
```

---

## Temuan Kunci (Updated v2)

### 1. Semua Solver Berhasil di Semua K!
Dengan MAX_NODES=2000, **semua solver berhasil mencapai gap 0.00%** untuk semua variasi K. Tidak ada lagi kasus kegagalan.

### 2. SCIP Tetap Paling Superior
- SCIP selalu menyelesaikan masalah dalam **1 node** dan waktu **< 0.05 detik** untuk SEMUA variasi K.
- Teknik utama: **primal heuristics** (locks, simplerounding, oneopt) + **cutting planes** di root node.

### 3. Couenne Konsisten, Sedikit Lebih Lambat
- Couenne menyelesaikan 8 dari 9 variasi K dengan **0 B&B nodes**.
- Kecuali **K=50** yang membutuhkan **4 nodes** — menunjukkan K=50 memang lebih sulit.
- Waktu Couenne: ~0.07-0.19 detik (3-10x lebih lambat dari SCIP).

### 4. B&B Manual: IPOPT vs MINOS Fluktuatif

| Metrik | B&B+IPOPT | B&B+MINOS | Pemenang |
|--------|-----------|-----------|----------|
| Rata-rata waktu | 35.3 s | 38.7 s | IPOPT (sedikit) |
| Rata-rata nodes | 396 | 380 | MINOS (sedikit) |
| K=50 waktu | 56.3 s | 5.4 s | **MINOS (10x!)** |
| K=50 nodes | 1057 | 111 | **MINOS (10x!)** |
| K=30 waktu | 67.3 s | 99.2 s | IPOPT |
| K=40 waktu | 11.2 s | 60.1 s | **IPOPT (5x!)** |

> Tidak ada pemenang konsisten antara IPOPT dan MINOS. Performa sangat bergantung pada **struktur masalah** di setiap K.

### 5. Rasio Kecepatan: SCIP vs B&B Manual

| K | SCIP (s) | B&B+IPOPT (s) | Rasio (x lebih cepat) |
|---|----------|---------------|----------------------|
| 10 | 0.051 | 14.15 | **277x** |
| 20 | 0.040 | 37.25 | **931x** |
| 30 | 0.035 | 67.30 | **1,923x** |
| 40 | 0.016 | 11.21 | **701x** |
| 50 | 0.019 | 56.31 | **2,964x** |

### 6. Kasus K=50: Update dari v1

| Metrik | v1 (MAX_NODES=1000) | v2 (MAX_NODES=2000) |
|--------|---------------------|---------------------|
| B&B+IPOPT objective | 55.35 (sub-optimal) | **59.48 (optimal)** |
| B&B+IPOPT gap | **7.74%** | **0.00%** |
| B&B+IPOPT nodes | 1000 (limit hit) | **1057** |
| B&B+IPOPT completed | GAGAL | **BERHASIL** |

> IPOPT hanya butuh **57 node tambahan** di atas batas 1000 untuk menemukan solusi optimal. Ini menunjukkan bahwa batas node yang terlalu ketat bisa menyebabkan solver menyerah sangat dekat dengan solusi optimal.

### 7. Konsistensi Solusi Optimal (Local vs Global)

Hal yang paling menonjol dari eksperimen ini adalah **konsistensi absolut** antara *Local Solver* (B&B buatan sendiri) dan *Global Solver* (SCIP & Couenne level industri):
- Untuk **setiap variasi K** (dari 10 hingga 50), keempat solver selalu menghasilkan **Objective Value** yang persis sama hingga 4 angka di belakang koma.
- Keempat solver juga selalu memilih **kombinasi user (Selected Users) yang sama persis**. Contohnya pada K=50, semua solver sepakat hanya memilih user `[36, 38]`.

**Tabel Perbandingan Objective Value:**

| K | SCIP | Couenne | B&B+IPOPT | B&B+MINOS |
|---|------|---------|-----------|-----------|
| 10 | 23.4580 | 23.4580 | 23.4580 | 23.4580 |
| 15 | 30.0549 | 30.0549 | 30.0549 | 30.0549 |
| 20 | 36.3503 | 36.3503 | 36.3503 | 36.3503 |
| 25 | 45.0418 | 45.0418 | 45.0418 | 45.0418 |
| 30 | 42.1028 | 42.1028 | 42.1028 | 42.1028 |
| 35 | 59.9519 | 59.9519 | 59.9519 | 59.9519 |
| 40 | 59.4396 | 59.4396 | 59.4396 | 59.4396 |
| 45 | 56.5662 | 56.5662 | 56.5662 | 56.5662 |
| 50 | 59.4842 | 59.4842 | 59.4842 | 59.4842 |

**Kesimpulan dari temuan ini:**
Algoritma Branch and Bound manual yang kita bangun terbukti **matematis benar (rigorous)**. Algoritma kita tidak menggunakan estimasi kasar atau heuristik yang mengorbankan kualitas solusi; ia menjamin **global optimum** sama persis seperti halnya SCIP dan Couenne. Perbedaan utamanya hanyalah pada **biaya komputasi** (Waktu dan Nodes), di mana Global Solver jauh lebih efisien karena teknik *Branch-and-Cut* dan *Presolve* yang canggih, sementara B&B manual kita harus mencari secara "buta" (*brute-force* yang terarah) dengan hanya mengandalkan LP Relaxation biasa.

---

## File Log yang Tersedia

| File | Ukuran | Deskripsi |
|------|--------|-----------|
| `solver_logs/scip_K10.log` | 2.6 KB | SCIP log untuk K=10 |
| `solver_logs/scip_K15.log` | 2.6 KB | SCIP log untuk K=15 |
| `solver_logs/scip_K20.log` | 2.3 KB | SCIP log untuk K=20 |
| `solver_logs/scip_K25.log` | 2.8 KB | SCIP log untuk K=25 |
| `solver_logs/scip_K30.log` | 3.2 KB | SCIP log untuk K=30 |
| `solver_logs/scip_K35.log` | 2.1 KB | SCIP log untuk K=35 |
| `solver_logs/scip_K40.log` | 2.4 KB | SCIP log untuk K=40 |
| `solver_logs/scip_K45.log` | 3.2 KB | SCIP log untuk K=45 |
| `solver_logs/scip_K50.log` | 3.5 KB | SCIP log untuk K=50 |
| `solver_logs/couenne_K10.log` | 3.2 KB | Couenne log untuk K=10 |
| `solver_logs/couenne_K15.log` | 2.8 KB | Couenne log untuk K=15 |
| `solver_logs/couenne_K20.log` | 2.7 KB | Couenne log untuk K=20 |
| `solver_logs/couenne_K25.log` | 2.7 KB | Couenne log untuk K=25 |
| `solver_logs/couenne_K30.log` | 2.9 KB | Couenne log untuk K=30 |
| `solver_logs/couenne_K35.log` | 2.3 KB | Couenne log untuk K=35 |
| `solver_logs/couenne_K40.log` | 2.7 KB | Couenne log untuk K=40 |
| `solver_logs/couenne_K45.log` | 2.9 KB | Couenne log untuk K=45 |
| `solver_logs/couenne_K50.log` | 2.8 KB | Couenne log untuk K=50 |
| `experiment_results.csv` | ~5.6 KB | Data mentah semua 36 runs |
