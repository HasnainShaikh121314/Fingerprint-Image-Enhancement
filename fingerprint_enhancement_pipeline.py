import os
from pathlib import Path
import os
from PIL import Image, ImageDraw, ImageFilter, ImageOps
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
import cv2
import numpy as np
import pyfing as pf

ADAPTIVE_BLOCK_SIZE = 21
ADAPTIVE_C = 2
OVAL_WIDTH_RATIO = 0.84
OVAL_HEIGHT_RATIO = 0.92
CARBON_GRAY = 55
SOFTEN_RADIUS = 0.6
INPUT_DIR = "sample"
OUTPUT_DIR = "output"
SCANNER_OUTPUT_DIR = os.path.join(
    OUTPUT_DIR,
    "scanner_style"
)
SCANNER_500DPI_OUTPUT_DIR = os.path.join(
    OUTPUT_DIR,
    "scanner_style_500dpi"
)
os.makedirs(SCANNER_OUTPUT_DIR, exist_ok=True)
os.makedirs(SCANNER_500DPI_OUTPUT_DIR, exist_ok=True)

# ── 500 DPI conversion constants ──────────────────────────────────────────────
TARGET_RIDGE_SPACING_PX = 9.65   # pixels/ridge at true 500 DPI

# pyfing frequency_estimation returns cycles/pixel, typical range 0.05–0.15
# → spacing = 1/freq, typical range ~6.7–20 px/ridge
RIDGE_SPACING_MIN_PX = 4.0   # sanity lower bound
RIDGE_SPACING_MAX_PX = 25.0  # sanity upper bound


def get_median_ridge_spacing(frequencies, seg_mask):
    """
    pyfing frequency_estimation returns ridge spacing in px/ridge directly.
    No inversion needed. Typical range: 5–20 px/ridge.
    """
    valid = (
        (seg_mask > 0) &
        np.isfinite(frequencies) &
        (frequencies > 0)
    )

    if not np.any(valid):
        return None

    spacing = frequencies[valid].astype(float)  # no 1/x

    clamped = spacing[
        (spacing >= RIDGE_SPACING_MIN_PX) &
        (spacing <= RIDGE_SPACING_MAX_PX)
    ]

    if len(clamped) == 0:
        return None

    return float(np.median(clamped))
def convert_to_500dpi(img_array, ridge_spacing_px):
    """
    Resize image so ridge spacing matches 500 DPI.
    """
    scale = TARGET_RIDGE_SPACING_PX / ridge_spacing_px

    h, w = img_array.shape[:2]

    new_w = max(1, int(round(w * scale)))
    new_h = max(1, int(round(h * scale)))

    return cv2.resize(
        img_array,
        (new_w, new_h),
        interpolation=cv2.INTER_CUBIC
    )
def create_scanner_style(enhanced, seg_mask):
    pil_img = Image.fromarray(enhanced)
    flipped = ImageOps.mirror(pil_img)
    flipped_arr = np.array(flipped)
    binary_arr = cv2.adaptiveThreshold(
        flipped_arr,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        ADAPTIVE_BLOCK_SIZE,
        -ADAPTIVE_C
    )
    binary = Image.fromarray(binary_arr)
    w, h = binary.size
    oval_w = int(w * OVAL_WIDTH_RATIO)
    oval_h = int(h * OVAL_HEIGHT_RATIO)
    left = (w - oval_w) // 2
    top = (h - oval_h) // 2
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).ellipse(
        [left, top, left + oval_w, top + oval_h],
        fill=255
    )
    carbon = binary.point(
        lambda p: CARBON_GRAY if p == 0 else 255
    )
    carbon = carbon.filter(
        ImageFilter.GaussianBlur(
            SOFTEN_RADIUS
        )
    )
    result = Image.new("L", (w, h), 255)
    result.paste(
        carbon,
        (0, 0),
        mask
    )
    return np.array(result)

def preprocess(img):
    if len(img.shape) == 3:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(
        clipLimit=2.0,
        tileGridSize=(8, 8)
    )
    img = clahe.apply(img)
    return img

def enhance_fingerprint(img):
    img = preprocess(img)
    # segmentation
    mask = pf.fingerprint_segmentation(img)
    # orientation estimation
    orientations = pf.orientation_field_estimation(
        img,
        mask
    )
    # frequency estimation
    frequencies = pf.frequency_estimation(
        img,
        orientations,
        mask
    )
    # enhancement
    enhanced = pf.fingerprint_enhancement(
        img,
        orientations,
        frequencies,
        mask,
        method="GBFEN"
    )
    # convert white ridges -> black ridges
    # enhanced = cv2.bitwise_not(enhanced)
    enhanced = cv2.normalize(
        enhanced,
        None,
        0,
        255,
        cv2.NORM_MINMAX
    )
    return enhanced.astype(np.uint8), mask, frequencies

def process_folder():
    image_files = []
    for ext in ("*.jpg", "*.jpeg", "*.png",
                "*.JPG", "*.JPEG", "*.PNG"):
        image_files.extend(
            Path(INPUT_DIR).glob(ext)
        )
    print(f"Found {len(image_files)} images")
    for file in image_files:
        print(f"Processing: {file.name}")
        img = cv2.imread(
            str(file),
            cv2.IMREAD_GRAYSCALE
        )
        if img is None:
            print(f"Cannot read {file}")
            continue
        enhanced, mask, frequencies = enhance_fingerprint(img)
        scanner_style = create_scanner_style(
            enhanced,
            mask
        )

        scanner_output = os.path.join(
            SCANNER_OUTPUT_DIR,
            file.stem + "_scanner_style.png"
        )
        cv2.imwrite(
            scanner_output,
            scanner_style
        )

        # ── proper 500 DPI conversion ──────────────────────────────────────
        ridge_spacing = get_median_ridge_spacing(
            frequencies,
            mask
        )

        if ridge_spacing is None:
            print(f"  Skipping 500dpi for {file.name}: no valid ridge frequency")
        else:
            scale = TARGET_RIDGE_SPACING_PX / ridge_spacing
            img_500dpi = convert_to_500dpi(scanner_style, ridge_spacing)

            Image.fromarray(img_500dpi).save(
                os.path.join(
                    SCANNER_500DPI_OUTPUT_DIR,
                    file.stem + "_scanner_style_500dpi.png"
                ),
                dpi=(500, 500)
            )

            print(
                f"  ridge_spacing={ridge_spacing:.2f}px/ridge "   # should be ~6–20
                f"→ scale={scale:.3f} "                            # should be ~0.5–2.0
                f"→ output={img_500dpi.shape[1]}x{img_500dpi.shape[0]}px @500dpi"
            )
    print("Done")

if __name__ == "__main__":
    process_folder()