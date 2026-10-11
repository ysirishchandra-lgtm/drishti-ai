# DRISHTI-AI — DDR Dataset Audit & Class Balancing Report

**Author:** Dataset Preparation Assistant (for Rudra — AI/ML Lead)  
**Date:** 2026-10-09  
**Dataset:** OIA-DDR (Dataset of Diabetic Retinopathy)  
**Official Source:** `https://github.com/nkicsl/DDR-dataset`  
**Base Directory:** `D:\drishti-ai\datasets\ddr\`  

---

## 1. Executive Summary

The official **DDR dataset** (13,673 raw annotated retinal fundus images) has been acquired from its official Google Drive source, reconstructed from 10 split archives (`DDR-dataset.zip.001` to `.010`), verified via CRC32, extracted to `_staging\`, deduplicated via cryptographic SHA-256 byte hashing, and organized into:

1. **`cleaned_all/`**: All **13,573 unique, verified images** (duplicates deduplicated, Grade 5 ungradables quarantined) physically separated into five diagnosis-grade folders and an ungradable quarantine folder.
2. **`balanced/`**: An **exact class-balanced dataset** where each of the five diagnosis classes contains **exactly 236 unique images** (total: **1,180 images**), sequentially numbered `1.jpg` to `236.jpg` in each class folder, sampled using reproducible seed `42`.

---

## 2. Acquisition & Archive Metrics

| Item | Details / Value | Status |
| :--- | :--- | :---: |
| **Official Repository** | `https://github.com/nkicsl/DDR-dataset` | Verified |
| **Download Chunks** | 10 split archives (`DDR-dataset.zip.001` through `.010`) | 100% Downloaded |
| **Combined Archive** | `DDR-dataset.zip` (14.10 GB / 15,147,025,972 bytes) | Assembled |
| **Archive CRC Check** | `testzip()` across 18,249 entries | **0 Errors (Passed)** |
| **Extracted Raw Images** | 13,673 images across `train/`, `valid/`, and `test/` | Complete |
| **Annotation Files** | `train.txt` (6,835), `valid.txt` (2,733), `test.txt` (4,105) | 13,673 rows matched |

---

## 3. Label Definitions & Diagnostic Mapping

DDR adopts the International Clinical Diabetic Retinopathy (ICDR) scale:

| DDR Label | Clinical Diagnosis | Class Folder | Action / Category |
| :---: | :--- | :--- | :--- |
| **0** | No Diabetic Retinopathy | `class_0_no_dr` | Eligible for 5-class DR model |
| **1** | Mild NPDR | `class_1_mild` | Eligible for 5-class DR model |
| **2** | Moderate NPDR | `class_2_moderate` | Eligible for 5-class DR model |
| **3** | Severe NPDR | `class_3_severe` | Eligible for 5-class DR model (Minority class) |
| **4** | Proliferative DR | `class_4_proliferative_dr` | Eligible for 5-class DR model |
| **5** | Ungradable (poor image quality) | `unresolved_labels` | Quarantined (cannot train on ungradables) |

---

## 4. SHA-256 Deduplication Audit

Every image was hashed using cryptographic SHA-256 byte hashing:
- **Total Raw Annotated Images**: `13,673`
- **Total Unique Cryptographic Hashes**: **`13,573`**
- **Duplicate Groups Detected**: **`97 groups`** (involving 197 image files)
- **Concordant Duplicates**: **`97 groups`** (100% have identical diagnostic labels!)
- **Conflicting Label Groups**: **`0 groups`** (Zero inter-rater conflicts in DDR!)
- **Deduplication Policy**: For each duplicate group, exactly 1 verified copy was retained in `cleaned_all/`, and redundant copies were recorded in `duplicate_audit.csv`.

---

## 5. Physical Dataset Organizations & Verified Counts

### A. Comprehensive Cleaned Dataset (`D:\drishti-ai\datasets\ddr\cleaned_all\`)
Contains all unique, verified images with original filenames:

| Folder | Diagnosis Category | Verified Unique Image Count |
| :--- | :--- | :---: |
| `class_0_no_dr/` | Grade 0 — No DR | **6,166** |
| `class_1_mild/` | Grade 1 — Mild DR | **630** |
| `class_2_moderate/` | Grade 2 — Moderate DR | **4,477** |
| `class_3_severe/` | Grade 3 — Severe DR | **236** |
| `class_4_proliferative_dr/` | Grade 4 — Proliferative DR | **913** |
| `unresolved_labels/` | Grade 5 — Ungradable Images | **1,151** |
| **Total in `cleaned_all/`** | | **13,573 unique images** |

---

### B. Exact Class-Balanced Dataset (`D:\drishti-ai\datasets\ddr\balanced\`)
To ensure perfectly equal class balance without synthetic oversampling, target per class was set to the minimum eligible class count (**Grade 3: 236 images**). Images were sampled using documented random `seed = 42` and sequentially numbered **`1.jpg` to `236.jpg`** in each class folder:

| Folder | Diagnosis Category | Image Count | Numbering Sequence |
| :--- | :--- | :---: | :--- |
| `class_0_no_dr/` | Grade 0 — No DR | **236** | `1.jpg` to `236.jpg` |
| `class_1_mild/` | Grade 1 — Mild DR | **236** | `1.jpg` to `236.jpg` |
| `class_2_moderate/` | Grade 2 — Moderate DR | **236** | `1.jpg` to `236.jpg` |
| `class_3_severe/` | Grade 3 — Severe DR | **236** | `1.jpg` to `236.jpg` |
| `class_4_proliferative_dr/` | Grade 4 — Proliferative DR | **236** | `1.jpg` to `236.jpg` |
| **Total Balanced Images** | | **1,180** | **Exactly 236 per class** |

- **Zero Duplicates**: Every single image in `balanced/` has a unique SHA-256 hash.
- **Traceability**: `balanced_manifest.csv` maps each numbered file (`1.jpg`, `2.jpg`, etc.) back to its original DDR filename, split, and hash.
- **Images Remaining Outside Balanced Subset**: **11,242 images** remain safe in `cleaned_all/` for additional training or validation.

---

## 6. Generated Manifests

1. 📄 `datasets\ddr\dataset_manifest.csv`: Full manifest of all 13,573 unique images with source paths, destination paths, diagnosis grades, and status.
2. 📄 `datasets\ddr\duplicate_audit.csv`: Detailed log of the 97 duplicate groups (197 files) and removal/retention decisions.
3. 📄 `datasets\ddr\balanced_manifest.csv`: Mapping of the 1,180 balanced images showing `numbered_filename`, original `image_name`, diagnosis, and class folder.
