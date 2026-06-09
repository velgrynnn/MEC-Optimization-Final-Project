# Ringkasan Hasil Eksperimen: Local vs Global Solver

**Konfigurasi:** K = [10, 15, 20, 25, 30, 35, 40, 45, 50] | Seed = 1 | F_bar = 6×10⁹ | MAX_NODES = 1000

---

## Tabel Ringkasan Per Variasi K

### K = 10 users

| Solver | Objective | Selected Users | Nodes | Solver Calls | Waktu (s) | Gap (%) | Completed |
|--------|-----------|----------------|-------|--------------|-----------|---------|-----------|
| **B&B+IPOPT** | 23.4580 | [1, 9] | 99 | 74 | 7.54 | 0.00 | ✅ |
| **B&B+MINOS** | 23.4580 | [1, 9] | 91 | 68 | 8.76 | 0.00 | ✅ |
| **SCIP** | 23.4580 | [1, 9] | 1 | — | **0.006** | 0.00 | ✅ |
| **Couenne** | 23.4580 | [1, 9] | 0 | — | 0.077 | 0.00 | ✅ |

### K = 15 users

| Solver | Objective | Selected Users | Nodes | Solver Calls | Waktu (s) | Gap (%) | Completed |
|--------|-----------|----------------|-------|--------------|-----------|---------|-----------|
| **B&B+IPOPT** | 30.0549 | [1, 6, 8] | 113 | 76 | 7.20 | 0.00 | ✅ |
| **B&B+MINOS** | 30.0549 | [1, 6, 8] | 63 | 40 | 4.08 | 0.00 | ✅ |
| **SCIP** | 30.0549 | [1, 6, 8] | 1 | — | **0.001** | 0.00 | ✅ |
| **Couenne** | 30.0549 | [1, 6, 8] | 0 | — | 0.069 | 0.00 | ✅ |

### K = 20 users

| Solver | Objective | Selected Users | Nodes | Solver Calls | Waktu (s) | Gap (%) | Completed |
|--------|-----------|----------------|-------|--------------|-----------|---------|-----------|
| **B&B+IPOPT** | 36.3503 | [7, 8, 11, 18] | 257 | 196 | 19.53 | 0.00 | ✅ |
| **B&B+MINOS** | 36.3503 | [7, 8, 11, 18] | 197 | 143 | 16.35 | 0.00 | ✅ |
| **SCIP** | 36.3503 | [7, 8, 11, 18] | 1 | — | **0.014** | 0.00 | ✅ |
| **Couenne** | 36.3503 | [7, 8, 11, 18] | 0 | — | 0.070 | 0.00 | ✅ |

### K = 25 users

| Solver | Objective | Selected Users | Nodes | Solver Calls | Waktu (s) | Gap (%) | Completed |
|--------|-----------|----------------|-------|--------------|-----------|---------|-----------|
| **B&B+IPOPT** | 45.0418 | [8, 11, 18, 22] | 187 | 157 | 15.09 | 0.00 | ✅ |
| **B&B+MINOS** | 45.0418 | [8, 11, 18, 22] | 345 | 269 | 25.91 | 0.00 | ✅ |
| **SCIP** | 45.0418 | [8, 11, 18, 22] | 1 | — | **0.013** | 0.00 | ✅ |
| **Couenne** | 45.0418 | [8, 11, 18, 22] | 0 | — | 0.075 | 0.00 | ✅ |

### K = 30 users

| Solver | Objective | Selected Users | Nodes | Solver Calls | Waktu (s) | Gap (%) | Completed |
|--------|-----------|----------------|-------|--------------|-----------|---------|-----------|
| **B&B+IPOPT** | 42.1028 | [5, 12, 16, 19] | 367 | 328 | 27.03 | 0.00 | ✅ |
| **B&B+MINOS** | 42.1028 | [5, 12, 16, 19] | 537 | 440 | 35.97 | 0.00 | ✅ |
| **SCIP** | 42.1028 | [5, 12, 16, 19] | 1 | — | **0.011** | 0.00 | ✅ |
| **Couenne** | 42.1028 | [5, 12, 16, 19] | 0 | — | 0.064 | 0.00 | ✅ |

### K = 35 users

| Solver | Objective | Selected Users | Nodes | Solver Calls | Waktu (s) | Gap (%) | Completed |
|--------|-----------|----------------|-------|--------------|-----------|---------|-----------|
| **B&B+IPOPT** | 59.9519 | [3, 7, 26, 33] | 631 | 525 | 42.63 | 0.00 | ✅ |
| **B&B+MINOS** | 59.9519 | [3, 7, 26, 33] | 711 | 484 | 42.95 | 0.00 | ✅ |
| **SCIP** | 59.9519 | [3, 7, 26, 33] | 1 | — | **0.001** | 0.00 | ✅ |
| **Couenne** | 59.9519 | [3, 7, 26, 33] | 0 | — | 0.066 | 0.00 | ✅ |

### K = 40 users

| Solver | Objective | Selected Users | Nodes | Solver Calls | Waktu (s) | Gap (%) | Completed |
|--------|-----------|----------------|-------|--------------|-----------|---------|-----------|
| **B&B+IPOPT** | 59.4396 | [20, 34] | 245 | 130 | 10.47 | 0.00 | ✅ |
| **B&B+MINOS** | 59.4396 | [20, 34] | 883 | 706 | **61.54** | 0.00 | ✅ |
| **SCIP** | 59.4396 | [20, 34] | 1 | — | **0.022** | 0.00 | ✅ |
| **Couenne** | 59.4396 | [20, 34] | 0 | — | 0.065 | 0.00 | ✅ |

### K = 45 users

| Solver | Objective | Selected Users | Nodes | Solver Calls | Waktu (s) | Gap (%) | Completed |
|--------|-----------|----------------|-------|--------------|-----------|---------|-----------|
| **B&B+IPOPT** | 56.5662 | [13, 27, 41] | 613 | 398 | 36.23 | 0.00 | ✅ |
| **B&B+MINOS** | 56.5662 | [13, 27, 41] | 485 | 324 | 28.35 | 0.00 | ✅ |
| **SCIP** | 56.5662 | [13, 27, 41] | 1 | — | **0.012** | 0.00 | ✅ |
| **Couenne** | 56.5662 | [13, 27, 41] | 0 | — | 0.090 | 0.00 | ✅ |

### ⚠️ K = 50 users — KASUS MENARIK!

| Solver | Objective | Selected Users | Nodes | Solver Calls | Waktu (s) | Gap (%) | Completed |
|--------|-----------|----------------|-------|--------------|-----------|---------|-----------|
| **B&B+IPOPT** | ❌ 55.3536 | [6, 18, 20, 45] | **1000** | 607 | **52.70** | **7.74** | ❌ **GAGAL** |
| **B&B+MINOS** | 59.4842 | [36, 38] | 111 | 59 | 5.14 | 0.00 | ✅ |
| **SCIP** | 59.4842 | [36, 38] | 1 | — | **0.007** | 0.00 | ✅ |
| **Couenne** | 59.4842 | [36, 38] | 0 | — | 0.068 | 0.00 | ✅ |

> **Analisis K=50:** B&B+IPOPT mencapai batas MAX_NODES (1000 nodes) sebelum menemukan solusi optimal. Solusi yang ditemukan (obj=55.35) **lebih rendah 6.9%** dari optimal (obj=59.48). Ini membuktikan bahwa local solver tidak menjamin konvergensi ke global optimum pada masalah besar. Sementara MINOS berhasil karena *branching pattern* yang berbeda — simplex-based solver memiliki LP relaxation yang lebih tajam sehingga pruning lebih efektif.

---

## Tabel Perbandingan Ringkas (Semua K)

### Waktu Komputasi (detik)

| K | B&B+IPOPT | B&B+MINOS | SCIP | Couenne |
|---|-----------|-----------|------|---------|
| 10 | 7.54 | 8.76 | **0.006** | 0.077 |
| 15 | 7.20 | 4.08 | **0.001** | 0.069 |
| 20 | 19.53 | 16.35 | **0.014** | 0.070 |
| 25 | 15.09 | 25.91 | **0.013** | 0.075 |
| 30 | 27.03 | 35.97 | **0.011** | 0.064 |
| 35 | 42.63 | 42.95 | **0.001** | 0.066 |
| 40 | 10.47 | 61.54 | **0.022** | 0.065 |
| 45 | 36.23 | 28.35 | **0.012** | 0.090 |
| 50 | 52.70 | 5.14 | **0.007** | 0.068 |

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
| 50 | **1000** ⚠️ | 111 | **1** | 0 |

### Optimality Gap (%)

| K | B&B+IPOPT | B&B+MINOS | SCIP | Couenne |
|---|-----------|-----------|------|---------|
| 10–45 | 0.00 | 0.00 | 0.00 | 0.00 |
| **50** | **7.74** ⚠️ | 0.00 | 0.00 | 0.00 |

---

## Temuan Kunci

### 1. SCIP Paling Superior
- SCIP selalu menyelesaikan masalah dalam **1 node** dan waktu **< 0.02 detik** untuk SEMUA variasi K.
- Ini karena teknik **presolve** SCIP mampu mereduksi masalah knapsack linier ini sebelum B&B dimulai.

### 2. Couenne Konsisten Tapi Lebih Lambat dari SCIP
- Couenne juga selalu berhasil (0 branching nodes), tapi **10-70× lebih lambat** dari SCIP (~0.07s vs ~0.01s).
- Couenne menggunakan LP relaxation + linearization cuts, bukan presolve.

### 3. B&B Manual Eksponensial
- Waktu komputasi B&B manual (IPOPT/MINOS) meningkat secara **tidak linear** seiring K bertambah.
- Jumlah nodes yang dieksplorasi bervariasi besar tergantung struktur masalah.

### 4. Kasus K=50: IPOPT Gagal!
- **B&B+IPOPT** mencapai batas 1000 nodes → solusi **sub-optimal** (gap 7.74%).
- **B&B+MINOS** berhasil dengan hanya 111 nodes → solusi **optimal** (gap 0%).
- **Penjelasan**: MINOS (simplex-based) menghasilkan LP relaxation solution yang lebih tajam pada simplex vertex, sehingga bounding lebih efektif dan pruning lebih agresif. IPOPT (interior point) cenderung menghasilkan solusi di interior yang kurang tajam untuk bounding.

### 5. Rasio Kecepatan SCIP vs B&B Manual
| K | SCIP (s) | B&B+IPOPT (s) | Rasio (×lebih cepat) |
|---|----------|---------------|----------------------|
| 10 | 0.006 | 7.54 | **1,257×** |
| 20 | 0.014 | 19.53 | **1,395×** |
| 35 | 0.001 | 42.63 | **35,858×** |
| 50 | 0.007 | 52.70 | **7,529×** |
