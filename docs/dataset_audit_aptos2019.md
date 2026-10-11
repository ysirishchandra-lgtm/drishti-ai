# DRISHTI-AI — APTOS 2019 Dataset Audit & Pre-Training Readiness Report

**Author:** Dataset Preparation Assistant (for Rudra — AI/ML Lead)  
**Date:** 2026-10-09  
**Dataset:** APTOS 2019 Blindness Detection (Official Kaggle Competition Data)  
**Location:** `D:\drishti-ai\datasets\aptos2019\`  

---

## 1. Executive Summary

The official APTOS 2019 Blindness Detection training dataset has been acquired, verified for file integrity, selectively extracted, and audited. All **3,662 labelled retinal fundus photographs** match `train.csv` with **zero missing files** and **zero corrupted images**.

A clinical data integrity audit was conducted, discovering **123 duplicate image groups** (251 images), of which **30 groups possess conflicting diagnostic labels**. This report specifies the exact distribution and provides critical recommendations for Rudra to build a reproducible, leakage-free train/validation split.

---

## 2. File Verification & Storage Metrics

| Check | Expected | Actual Verified | Status |
| :--- | :--- | :--- | :--- |
| **Archive Download** | `aptos2019-blindness-detection.zip` | `10,215,289,875` bytes (~9.51 GB) | Verified (100% byte match) |
| **Archive CRC Test** | 0 CRC errors | 0 CRC errors (`testzip()` passed) | Pass |
| **Metadata File** | `train.csv` | 54,948 bytes (3,662 rows) | Verified |
| **Training Images** | 3,662 PNGs | 3,662 PNGs in `train_images/` | Extracted & Verified |
| **Test Images (Unlabelled)** | 1,928 images | 0 extracted (strictly skipped) | Excluded |
| **Git Exclusion** | `datasets/` in `.gitignore` | `git check-ignore` confirms 100% ignored | Secured |

---

## 3. Clinical Label Distribution & Class Imbalance

Mapped from `train.csv` (Columns: `id_code`, `diagnosis`):

| Grade | Clinical Category | Count | Percentage | Medical Implication & Strategy |
| :---: | :--- | :---: | :---: | :--- |
| **0** | **No DR** | 1,805 | 49.29% | Majority negative class (healthy retina). |
| **1** | **Mild DR** | 370 | 10.10% | Microaneurysms only. Subtle lesions; high risk of misclassification with Grade 0. |
| **2** | **Moderate DR** | 999 | 27.28% | Hemorrhages, microaneurysms, hard exudates, cotton wool spots. |
| **3** | **Severe DR** | 193 | 5.27% | 4-2-1 rule met. Significant risk of rapid progression. High class rarity. |
| **4** | **Proliferative DR** | 295 | 8.06% | Neovascularization and/or vitreous hemorrhage. Critical urgency. |
| **Total** | | **3,662** | **100.00%** | |

### Clinical Insights for Rudra:
- **Severe Class Imbalance**: Severe (3) and Proliferative (4) DR account for only **13.33%** of the entire dataset.
- **Training Strategy**: Must use class-weighted loss (e.g., Weighted Cross-Entropy or Focal Loss) and stratified sampling.

---

## 4. Image Quality & Dimension Analysis

All 3,662 images were verified using PIL (`Image.verify()`). **0 corrupted images detected.**

Retinal cameras in the APTOS dataset come from multiple clinical sites in rural India with varying sensors and resolutions:

| Resolution (Width x Height) | Image Count | Percentage | Aspect Ratio |
| :--- | :---: | :---: | :--- |
| `1050 x 1050` | 974 | 26.6% | 1:1 (Square crop) |
| `2416 x 1736` | 638 | 17.4% | ~1.39:1 |
| `2588 x 1958` | 533 | 14.6% | ~1.32:1 |
| `3216 x 2136` | 410 | 11.2% | ~1.51:1 |
| `2048 x 1536` | 351 | 9.6% | 4:3 |
| *Other resolutions (30+ variations)* | 756 | 20.6% | Varied |

### Recommendation for Preprocessing Pipeline:
1. Circular cropping / black border removal (Ben Graham's preprocessing).
2. Standardized resizing to `512 x 512` or `384 x 384` for EfficientNet / ConvNeXt backbones.
3. Aspect-ratio preserving pad or center crop to prevent distorting circular optic discs and maculae.

---

## 5. Critical Finding: Duplicate Images & Inter-Rater Conflict

MD5 hash analysis identified duplicate fundus photographs across different patient IDs:
- **Total Duplicate Groups**: **123 groups** (involving 251 images).
- **Concordant Duplicates**: **93 groups** share the exact same diagnosis label.
- **Discordant / Conflicting Duplicates**: **30 groups** have **conflicting diagnostic labels**!

### Notable Conflict Examples:
- `['0ac436400db4', 'fda39982a810']`: Exact same image; one labeled **Grade 2 (Moderate)**, the other **Grade 3 (Severe)**.
- `['1c9c583c10bf', 'ea15a290eb96']`: Exact same image; one labeled **Grade 0 (No DR)**, the other **Grade 1 (Mild DR)**.
- `['3ee4841936ef', '7005be54cab1']`: Exact same image; one labeled **Grade 1 (Mild DR)**, the other **Grade 4 (Proliferative DR)**.

### Action Required Before Model Split:
1. **Prevent Data Leakage**: Duplicate images MUST NOT be split across training and validation sets. Both images in a pair must stay in the same split or one must be dropped.
2. **Resolve Conflicting Labels**: For the 30 discordant groups, Rudra can choose:
   - *Option A (Clinical Safety)*: Take the more severe grade (conservative referral).
   - *Option B (Cleanliness)*: Drop the 30 ambiguous groups (~60 images) from training.

---

## 6. Phase 4: Dataset Readiness Verdict

**VERDICT: READY FOR SPLIT AND PREPROCESSING (CONDITIONAL ON DEDUPLICATION)**

The dataset is locally intact, 100% readable, and Git-protected. Rudra can proceed to generate a stratified, deduplicated 80/10/10 or 80/20 train/validation split.

---

## 7. Phase 6: Final Manifest Verification & Physical Class-Wise Segregation

### 7.1 Verification Checklist
- **Check 1: Manifest & Audit File Presence**: PASS (`dataset_manifest.csv`, `duplicates_audit.csv`, class manifests).
- **Check 2: ID Completeness**: PASS (3,662/3,662 IDs match, 0 missing, 0 unexpected).
- **Check 3: Duplicate Group Leakage**: PASS (0% cross-split leakage; 100% of duplicate groups belong to a single split).
- **Check 4: Split Non-Overlap & Union**: PASS (Train: 2,932, Val: 369, Test: 361 = 3,662).
- **Check 5: Clean Evaluation Manifest**: PASS (`dataset_manifest_clean_eval.csv` isolates 62 conflicting images).
- **Check 6: Byte Integrity**: PASS (3,662/3,662 copied files verified identical to source images).

### 7.2 Physical Class-Wise Image Directory (`datasets/aptos2019/classwise_images/`)
- `class_0_no_dr/`: 1,801 images
- `class_1_mild/`: 360 images
- `class_2_moderate/`: 976 images
- `class_3_severe/`: 180 images
- `class_4_proliferative_dr/`: 283 images
- `unresolved_conflicting_labels/`: 62 images (Quarantined discordant ground truth)
- **Total Physical Images Placed**: 3,662 (Originals in `train_images/` preserved 100%).

