# DRISHTI-AI — Split Integrity and Provenance Report
**Balanced 5-Class Dataset (2,500 Images)**
**Generated:** 2026-10-10  
**Target Directory:** `D:\drishti-ai\datasets\balanced_5class_2500\`

---

## 1. Executive Summary

This report provides an audit of the split integrity, provenance, and data leakage safeguards for the newly constructed balanced multi-source fundus dataset containing **exactly 500 verified unique fundus images in each of the 5 diabetic retinopathy severity classes** (total: **2,500 images**).

### Key Audit Metrics
- **Total Unique Images:** 2,500
- **Total Classes:** 5 (exactly 500 images per class)
- **Data Sources:** 3 open research datasets (APTOS-2019, OIA-DDR, IDRiD)
- **Exact Duplicate Collisions:** 0 (all 2,500 images possess distinct SHA-256 hashes)
- **Cross-Split Leakage:** 0 (official train, validation, and test splits strictly preserved)

---

## 2. Official Split Distribution per Class

Every image in the balanced dataset retains its official benchmark assignment. No official validation or test image has been moved into training.

| Class ID | Class Name | Clinical Severity | Total Images | Official Train | Official Valid | Official Test | Split Integrity Status |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **0** | `class_0_no_dr` | No DR | 500 | 390 (78.0%) | 46 (9.2%) | 64 (12.8%) | VERIFIED |
| **1** | `class_1_mild` | Mild DR | 500 | 374 (74.8%) | 53 (10.6%) | 73 (14.6%) | VERIFIED |
| **2** | `class_2_moderate` | Moderate DR | 500 | 371 (74.2%) | 54 (10.8%) | 75 (15.0%) | VERIFIED |
| **3** | `class_3_severe` | Severe DR | 500 | 366 (73.2%) | 47 (9.4%) | 87 (17.4%) | VERIFIED |
| **4** | `class_4_proliferative_dr` | Proliferative DR | 500 | 385 (77.0%) | 47 (9.4%) | 68 (13.6%) | VERIFIED |
| **TOTAL** | **All 5 Classes** | — | **2,500** | **1,886 (75.4%)** | **247 (9.9%)** | **367 (14.7%)** | **ZERO LEAKAGE** |

---

## 3. Provenance and Source Dataset Breakdown

To achieve a balanced representation of 500 genuine images per severity class, the dataset integrates three peer-reviewed, publicly available datasets:

| Source Dataset | Source Organization / URL | License & Terms | Grading Standard | Total Images | Class 0 | Class 1 | Class 2 | Class 3 | Class 4 |
| :--- | :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **APTOS-2019** | Aravind Eye Hospital / Kaggle | Competition Research Use (CC BY-NC 4.0) | ICDR 5-scale (0–4) | 1,177 | 250 | 250 | 250 | 177 | 250 |
| **OIA-DDR** | NKICSL / Li et al., 2019 | Academic Research Open Access | ICDR 5-scale (0–4) | 1,236 | 250 | 250 | 250 | 236 | 250 |
| **IDRiD** | IEEE Dataport / Grand Challenge | CC BY 4.0 International | ICDR 5-scale (0–4) | 87 | 0 | 0 | 0 | 87 | 0 |
| **TOTAL** | — | — | — | **2,500** | **500** | **500** | **500** | **500** | **500** |

### Severe DR (Class 3) Provenance
Severe NPDR is clinically underrepresented across all medical screening archives due to the rapid progression of ischemic retinopathy directly to neovascularization (Class 4).
- Neither APTOS (177 unique clean Grade 3) nor DDR (236 unique clean Grade 3) alone possessed 500 images.
- Combined, APTOS and DDR contributed 413 genuine Severe DR images.
- The remaining deficit of 87 genuine images was sourced from the official IDRiD Disease Grading dataset (which contains 89 verified non-conflicting Grade 3 images).
- This achieves **exactly 500 genuine Severe DR images** with 0 synthetic samples and 0 oversampled duplicates.

---

## 4. Leakage Prevention and Cross-Dataset Audits

1. **Exact-Duplicate Elimination (SHA-256):**
   - SHA-256 was computed across all raw and candidate images across APTOS (3,662), DDR (13,673), and IDRiD (516).
   - Within IDRiD, 6 duplicate groups were audited. 3 groups had conflicting clinical severity grades (e.g., `train IDRiD_118 (Grade 0)` vs `test IDRiD_064 (Grade 3)`). All discordant images were excluded and quarantined.
   - 0 exact SHA-256 matches exist between any pair of images in the 2,500 balanced set.
2. **Perceptual Duplicate Audit (pHash / dHash):**
   - 64-bit difference hashes were computed across the candidate pools.
   - Near-zero perceptual duplicate pairs within IDRiD (such as `IDRiD_025` and `IDRiD_357`) were resolved by excluding redundant copies.
   - Cross-dataset perceptual distance checks confirmed zero cross-dataset image collisions.
3. **Split Separation Rules:**
   - Official splits are recorded in `balanced_2500_manifest.csv` under `official_split`.
   - Training pipelines must use `official_split == 'train'` for parameter optimization.
   - `official_split == 'valid'` and `official_split == 'test'` must remain quarantined from model weight updates.

---

## 5. Verification Sign-Off

- **Class Folder Check:** All 5 class directories (`class_0_no_dr`, `class_1_mild`, `class_2_moderate`, `class_3_severe`, `class_4_proliferative_dr`) contain **exactly 500 files**.
- **Sequential Numbering:** Files are numbered `1.ext` to `500.ext` within each class folder.
- **Image Integrity:** Every image was opened and verified by PIL `Image.verify()`. Zero corrupted files.
- **Manifest Synchrony:** The 2,500 rows in `balanced_2500_manifest.csv` correspond 1:1 with the physical disk files and their SHA-256 hashes.
