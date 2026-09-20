# Fingerprint Scanner-Style Conversion Pipeline

## Overview

This project converts raw fingerprint images into scanner-style fingerprint images using PyFing enhancement techniques.

The pipeline:

* Enhances fingerprint ridge structures using PyFing GBFEN.
* Generates scanner-style fingerprint images.
* Produces 500 DPI PNG versions.
* Processes all images in a folder automatically.

The output is intended for:

* AFIS evaluation
* NFIQ quality assessment
* Fingerprint visualization
* Contactless fingerprint enhancement workflows

---

# Features

* Batch image processing
* Automatic fingerprint enhancement
* Orientation field estimation
* Ridge frequency estimation
* GBFEN fingerprint enhancement
* Scanner-style fingerprint rendering
* Carbon-gray ridge appearance
* Oval fingerprint card formatting
* 500 DPI PNG export

---

# Installation

Create environment:

```bash
conda create -n fingenhan python=3.10 -y
conda activate fingenhan
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# Project Structure

```text
project/
│
├── fingerprint_enhancement_pipeline.py
│
├── sample/
│   ├── image1.jpg
│   ├── image2.png
│   └── ...
│
└── output/
    │
    ├── scanner_style/
    │   ├── image1_scanner_style.png
    │   ├── image2_scanner_style.png
    │   └── ...
    │
    └── scanner_style_500dpi/
        ├── image1_scanner_style_500dpi.png
        ├── image2_scanner_style_500dpi.png
        └── ...
```

---

# Input

Place fingerprint images inside:

```text
sample/
```

Supported formats:

```text
.jpg
.jpeg
.png
.JPG
.JPEG
.PNG
```

---

# Processing Pipeline

## 1. Preprocessing

The image is converted to grayscale and enhanced using CLAHE.

```text
Raw Image
    ↓
Grayscale
    ↓
CLAHE
```

---

## 2. PyFing Enhancement

PyFing performs:

```text
Fingerprint Segmentation
        ↓
Orientation Field Estimation
        ↓
Frequency Estimation
        ↓
GBFEN Enhancement
```

Methods used:

```python
pf.fingerprint_segmentation()
pf.orientation_field_estimation()
pf.frequency_estimation()
pf.fingerprint_enhancement(method="GBFEN")
```

---

## 3. Scanner-Style Conversion

The enhanced image is transformed into a scanner-like fingerprint.

```text
GBFEN Output
      ↓
Horizontal Mirror
      ↓
Adaptive Threshold
      ↓
Carbon Gray Ridge Rendering
      ↓
Gaussian Blur
      ↓
Oval Fingerprint Layout
      ↓
Scanner Style Output
```

---

# Output Files

## Scanner Style Image

```text
output/scanner_style/
```

Example:

```text
right-index_scanner_style.png
```

---

## Scanner Style 500 DPI Image

```text
output/scanner_style_500dpi/
```

Example:

```text
right-index_scanner_style_500dpi.png
```

---

# Configuration Parameters

## Adaptive Threshold

```python
ADAPTIVE_BLOCK_SIZE = 21
ADAPTIVE_C = 2
```

Controls local thresholding sensitivity.

---

## Oval Layout

```python
OVAL_WIDTH_RATIO = 0.84
OVAL_HEIGHT_RATIO = 0.92
```

Controls the size of the oval fingerprint area.

---

## Ridge Appearance

```python
CARBON_GRAY = 55
SOFTEN_RADIUS = 0.6
```

* CARBON_GRAY controls ridge darkness.
* SOFTEN_RADIUS controls ridge smoothing.

---

# Running

Run:

```bash
python pipeline.py
```

Example:

```text
Found 6 images
Processing: right-index.png
Processing: user1.jpg
Processing: user2.png
Done
```

---

# Output Resolution

The pipeline exports an additional image with:

```text
500 DPI metadata
```

using:

```python
dpi=(500, 500)
```

This adds DPI information to the PNG file but does not resample image dimensions.

---

# Dependencies

* Python 3.10+
* PyFing
* TensorFlow
* OpenCV
* Pillow
* NumPy

---

# Use Cases

* AFIS preprocessing
* NFIQ quality evaluation
* Contactless fingerprint enhancement
* Fingerprint visualization
* Biometric research
* Fingerprint image normalization

---
