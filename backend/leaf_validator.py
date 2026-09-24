"""
leaf_validator.py - GreenScan 2.0 Phase 1: Hierarchical Image Validation

Determines whether an uploaded image is a valid tomato leaf image before
allowing it to proceed to disease classification.

Architecture:
    Image -> LeafValidator -> VALID_TOMATO_LEAF / NOT_TOMATO_LEAF / LOW_QUALITY_IMAGE
                                    |
                           Disease Classifier (only if VALID)

Design Decision:
    Uses a heuristic approach combining existing leaf_segmenter.py output
    (leaf pixel coverage %) with the image_enhancer.py quality check, rather
    than training a separate binary classifier. This avoids needing additional
    training data and leverages already-validated components.

    Thresholds are configurable via config.py / environment variables.
"""

import logging
import numpy as np
from typing import Optional

logger = logging.getLogger("greenscan.leaf_validator")

# Validation Status Constants
VALID_TOMATO_LEAF = "VALID_TOMATO_LEAF"
NOT_TOMATO_LEAF = "NOT_TOMATO_LEAF"
LOW_QUALITY_IMAGE = "LOW_QUALITY_IMAGE"


def validate_leaf_image(
    leaf_pixels: int,
    total_pixels: int,
    quality_info: dict,
    confidence=None,
    min_leaf_coverage_pct: float = 10.0,
    min_leaf_pixels: int = 1000,
    min_confidence=None,
) -> dict:
    """
    Validates whether an image qualifies as a valid tomato leaf image.

    This is the first gate in the hierarchical prediction pipeline.
    If validation fails, the system returns immediately without running
    disease classification, Grad-CAM, or GSA.

    Args:
        leaf_pixels:           Number of pixels identified as leaf/plant material
                               by leaf_segmenter.py.
        total_pixels:          Total image pixels (height x width).
        quality_info:          Dict returned by image_enhancer.check_image_quality().
                               Must contain 'passed' (bool) and 'reasons' (list).
        confidence:            Optional model confidence score [0.0, 1.0].
        min_leaf_coverage_pct: Minimum % of image that must be leaf material.
        min_leaf_pixels:       Absolute minimum leaf pixel floor.
        min_confidence:        Optional confidence threshold.

    Returns:
        dict with validation_status, is_valid, leaf_coverage_pct, message, user_guidance, etc.
    """
    if total_pixels <= 0:
        total_pixels = 224 * 224

    leaf_coverage_pct = float((leaf_pixels / total_pixels) * 100.0)
    leaf_coverage_pct = round(leaf_coverage_pct, 2)

    quality_passed = quality_info.get("passed", True)
    quality_reasons = quality_info.get("reasons", [])

    # Gate 1: Image Quality
    if not quality_passed:
        reason_str = "; ".join(quality_reasons) if quality_reasons else "Poor image quality detected."
        logger.info(f"[LeafValidator] LOW_QUALITY_IMAGE: {reason_str}")
        return {
            "validation_status": LOW_QUALITY_IMAGE,
            "is_valid": False,
            "leaf_coverage_pct": leaf_coverage_pct,
            "leaf_pixels": leaf_pixels,
            "total_pixels": total_pixels,
            "quality_passed": False,
            "quality_reasons": quality_reasons,
            "message": (
                "The image quality is insufficient for reliable analysis. "
                "Please capture a clearer image under good lighting."
            ),
            "user_guidance": (
                "Tips for a better scan: "
                "Ensure adequate lighting (natural daylight works best). "
                "Hold the camera steady to avoid blur. "
                "Position the leaf to fill most of the frame. "
                "Avoid strong shadows or direct flash glare."
            ),
            "confidence_warning": False,
        }

    # Gate 2: Leaf Coverage
    below_pixel_floor = leaf_pixels < min_leaf_pixels
    below_coverage_pct = leaf_coverage_pct < min_leaf_coverage_pct
    confidence_confirms_invalid = (
        confidence is not None
        and min_confidence is not None
        and confidence < min_confidence
        and leaf_coverage_pct < (min_leaf_coverage_pct * 2)
    )

    if below_pixel_floor or below_coverage_pct or confidence_confirms_invalid:
        logger.info(
            f"[LeafValidator] NOT_TOMATO_LEAF: coverage={leaf_coverage_pct:.1f}% "
            f"(min={min_leaf_coverage_pct}%), pixels={leaf_pixels} (min={min_leaf_pixels})"
        )
        return {
            "validation_status": NOT_TOMATO_LEAF,
            "is_valid": False,
            "leaf_coverage_pct": leaf_coverage_pct,
            "leaf_pixels": leaf_pixels,
            "total_pixels": total_pixels,
            "quality_passed": True,
            "quality_reasons": [],
            "message": (
                "This image does not appear to contain a valid tomato leaf. "
                "Please upload a clear, close-up image of a single tomato leaf."
            ),
            "user_guidance": (
                "Tips for a valid leaf scan: "
                "The tomato leaf should fill most of the image frame. "
                "Scan one leaf at a time, not an entire plant from a distance. "
                "Use a plain or simple background if possible. "
                "Ensure the leaf is fully visible with no major obstructions."
            ),
            "confidence_warning": False,
        }

    # Gate 3: Soft Confidence Warning
    confidence_warning = (
        confidence is not None
        and confidence < 0.75
    )

    logger.info(
        f"[LeafValidator] VALID_TOMATO_LEAF: coverage={leaf_coverage_pct:.1f}%, pixels={leaf_pixels}"
    )

    return {
        "validation_status": VALID_TOMATO_LEAF,
        "is_valid": True,
        "leaf_coverage_pct": leaf_coverage_pct,
        "leaf_pixels": leaf_pixels,
        "total_pixels": total_pixels,
        "quality_passed": True,
        "quality_reasons": [],
        "message": None,
        "user_guidance": None,
        "confidence_warning": confidence_warning,
    }


def get_validation_user_message(validation_result: dict) -> str:
    """Returns a clean farmer-friendly message for the given validation result."""
    status = validation_result.get("validation_status", VALID_TOMATO_LEAF)
    if status == NOT_TOMATO_LEAF:
        return (
            "This does not appear to be a valid tomato leaf image. "
            "Please upload a clear, close-up photo of a single tomato leaf."
        )
    elif status == LOW_QUALITY_IMAGE:
        reasons = validation_result.get("quality_reasons", [])
        reason_text = f" ({reasons[0]})" if reasons else ""
        return (
            f"Image quality is too low for reliable analysis{reason_text}. "
            "Please capture a clearer image under good lighting with the leaf in focus."
        )
    return ""
