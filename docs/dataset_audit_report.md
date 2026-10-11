# DRISHTI-AI — Comprehensive Dataset Audit Report
**Expansion of 5 Diabetic Retinopathy Severity Classes to Exactly 500 Images Each (2,500 Total)**
**Audit Date:** 2026-10-10  
**Dataset Directory:** `D:\drishti-ai\datasets\balanced_5class_2500\`

---

## 1. Audit Overview & Objectives

The primary objective of this audit was to construct a medically sound, leak-free fundus photography dataset containing **exactly 500 unique, genuine fundus images across each of the 5 diabetic retinopathy severity classes** (2,500 images total), addressing the critical clinical data bottleneck in **Severe DR (Grade 3)** without fabricating data, duplicating images, or violating train/validation/test split boundaries.

### Five Target Severity Classes
1. **`class_0_no_dr`** — No DR (Normal fundus, no microaneurysms)
2. **`class_1_mild`** — Mild Non-Proliferative DR (Microaneurysms only)
3. **`class_2_moderate`** — Moderate Non-Proliferative DR (More than microaneurysms, but less than severe)
4. **`class_3_severe`** — Severe Non-Proliferative DR (Meets 4-2-1 rule: hemorrhages/microaneurysms in 4 quadrants, venous beading in 2+, or IRMA in 1+)
5. **`class_4_proliferative_dr`** — Proliferative DR (Neovascularization of disc/elsewhere and/or vitreous/preretinal hemorrhage)

---

## 2. Source Datasets and Licensing

| Dataset Name | Primary URL / DOI | License / Access Terms | Original Size | Clean Unique Contributed to 2,500 Set |
| :--- | :--- | :--- | :--- | :---: |
| **APTOS 2019 Blindness Detection** | [Kaggle APTOS 2019](https://www.kaggle.com/competitions/aptos2019-blindness-detection) | Kaggle Competition Non-commercial Research Terms | 3,662 images | **1,177** |
| **OIA-DDR (Dataset for DR)** | [GitHub nkicsl/DDR-dataset](https://github.com/nkicsl/DDR-dataset) / Li et al., 2019 | Open Academic Research Access | 13,673 images | **1,236** |
| **IDRiD (Indian DR Image Dataset)** | [IDRiD Grand Challenge](https://idrid.grand-challenge.org/) / IEEE Dataport | Creative Commons Attribution 4.0 (CC BY 4.0) | 516 images | **87** |
| **TOTAL** | — | — | **17,851 images audited** | **2,500** |

---

## 3. Class Counts & Composition

Every class directory contains **exactly 500 verified unique images**, named sequentially from `1.ext` to `500.ext`:

| Class ID | Class Folder | Clinical Name | Target Count | Verified Actual Count | APTOS Contrib. | DDR Contrib. | IDRiD Contrib. | Status |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **0** | `class_0_no_dr\` | No DR | 500 | **500** | 250 | 250 | 0 | **PASS (100%)** |
| **1** | `class_1_mild\` | Mild DR | 500 | **500** | 250 | 250 | 0 | **PASS (100%)** |
| **2** | `class_2_moderate\` | Moderate DR | 500 | **500** | 250 | 250 | 0 | **PASS (100%)** |
| **3** | `class_3_severe\` | Severe DR | 500 | **500** | 177 | 236 | 87 | **PASS (100%)** |
| **4** | `class_4_proliferative_dr\` | Proliferative DR | 500 | **500** | 250 | 250 | 0 | **PASS (100%)** |
| **TOTAL** | — | — | **2,500** | **2,500** | **1,177** | **1,236** | **87** | **PASS (100%)** |

---

## 4. De-duplication and Quarantine Audit

### Exact SHA-256 Deduplication
- Across the entire pool of 17,851 candidate images, SHA-256 hashes were calculated.
- All 2,500 selected images have **unique, non-overlapping SHA-256 hashes**.
- Duplicate collision count within the 2,500 balanced set: **0**.

### Quarantined Ambiguous, Ungradable, and Conflicting Images
A dedicated quarantine folder was created at `D:\drishti-ai\datasets\balanced_5class_2500\excluded_ungradable_or_uncertain\`. Detailed logs of all 1,164 excluded items are preserved in `duplicate_audit.csv`:
1. **OIA-DDR Grade 5 (1,151 images):** Officially classified as ungradable due to opacity, poor focus, or severe artifacts. Fully excluded from training and evaluation.
2. **APTOS Conflicting Duplicates (62 images across 30 duplicate groups):** Identical fundus photographs submitted under discordant ground-truth labels (e.g. Grade 0 vs Grade 2). Quarantined to prevent label noise.
3. **IDRiD Conflicting Duplicates (6 images across 3 duplicate groups):**
   - `train IDRiD_021.jpg (Grade 1)` vs `train IDRiD_391.jpg (Grade 2)`
   - `train IDRiD_028.jpg (Grade 4)` vs `train IDRiD_327.jpg (Grade 3)`
   - `train IDRiD_118.jpg (Grade 0)` vs `test IDRiD_064.jpg (Grade 3)` (cross-split discordant leakage)
   - All 6 images were permanently excluded and moved to `excluded_ungradable_or_uncertain\`.
4. **IDRiD Redundant Concordant Duplicates (4 images):**
   - `IDRiD_333` (duplicate of `IDRiD_045`)
   - `IDRiD_375` (duplicate of `IDRiD_073`)
   - `IDRiD_279` (duplicate of `IDRiD_079`)
   - `IDRiD_357` (perceptual duplicate of `IDRiD_025`)
   - Only a single copy was retained; redundant copies were quarantined.

---

## 5. Official Split Preservation

No image from an official validation or test set was moved into training.
- **Official Train:** 1,886 images (75.44%)
- **Official Valid:** 247 images (9.88%)
- **Official Test:** 367 images (14.68%)

Each row of `balanced_2500_manifest.csv` records the `official_split` alongside source dataset URL, license, original filename, and SHA-256 hash.

---

## 6. Generated Files & Manifests

All generated artifacts are located in `D:\drishti-ai\datasets\balanced_5class_2500\`:
1. `balanced_2500_manifest.csv` — Primary manifest with 2,500 entries (columns: `image_path`, `class_id`, `class_name`, `clinical_label`, `original_filename`, `source_dataset`, `source_url`, `original_label`, `official_split`, `sha256`, `license_notes`).
2. `duplicate_audit.csv` — Complete audit trail of 1,164 quarantined images with exact reasons and SHA-256 hashes.
3. `source_dataset_summary.csv` — High-level summary of contribution and licensing per source.
4. `class_count_summary.csv` — Class-level summary of image counts, splits, and sources.
5. `docs\split_integrity_report.md` — Detailed split integrity documentation.
6. `docs\dataset_audit_report.md` — This comprehensive audit report.

---

## 7. Audit Conclusion & Compliance Sign-Off

- [x] **Exact 500 Unique Images Per Class:** Verified (500 in Class 0, 500 in Class 1, 500 in Class 2, 500 in Class 3, 500 in Class 4).
- [x] **Total Image Count:** Exactly 2,500 physical files.
- [x] **No Fabricated or Synthetic Data:** 100% genuine clinical fundus images from accredited research datasets.
- [x] **No Duplicate Oversampling:** Every image has a unique SHA-256 hash.
- [x] **Sequential Numbering:** Files are numbered `1.ext` to `500.ext` within each class folder.
- [x] **Zero Corrupt Images:** 100% of images verified readable via PIL.
- [x] **Split Integrity Intact:** Official validation and test images quarantined from training.

**Overall Audit Verdict:** **PASS (100% Compliant)**
