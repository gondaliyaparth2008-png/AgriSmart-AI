"""
app/services/labels.py
-----------------------
Official hackathon class list for AgriSmart AI crop disease detection.

This module is the single source of truth for:
  • CLASS_NAMES   — ordered list matching the model's output layer indices
  • DISEASE_INFO  — per-class metadata: display name, crop, severity,
                    description, and precautionary guidance

Design
------
The model's output is a probability vector of length len(CLASS_NAMES).
argmax → index → CLASS_NAMES[index] → DISEASE_INFO lookup.

Adding a new class
------------------
1. Append the class key to CLASS_NAMES at the correct index.
2. Add a matching entry to DISEASE_INFO with the required keys.
   Required keys: display_name, crop, is_healthy, severity, description, precautions
"""

from __future__ import annotations

from typing import Dict, List, Any

# =========================================================================== #
#  Ordered class list
#  Index order MUST match the model's output layer.
# =========================================================================== #

CLASS_NAMES: List[str] = [
    # ── Tomato (5 classes) ──────────────────────────────────────────────────
    "Tomato Early Blight",
    "Tomato Late Blight",
    "Tomato Leaf Mould",
    "Tomato Bacterial Spot",
    "Tomato Healthy",
    # ── Potato (3 classes) ──────────────────────────────────────────────────
    "Potato Early Blight",
    "Potato Late Blight",
    "Potato Healthy",
    # ── Corn / Maize (3 classes) ────────────────────────────────────────────
    "Corn Common Rust",
    "Corn Grey Leaf Spot",
    "Corn Healthy",
    # ── Apple (3 classes) ───────────────────────────────────────────────────
    "Apple Scab",
    "Apple Black Rot",
    "Apple Healthy",
    # ── Grape (2 classes) ───────────────────────────────────────────────────
    "Grape Black Rot",
    "Grape Healthy",
    # ── Bell Pepper (2 classes) ─────────────────────────────────────────────
    "Bell Pepper Bacterial Spot",
    "Bell Pepper Healthy",
]

NUM_CLASSES: int = len(CLASS_NAMES)   # 18


# =========================================================================== #
#  Disease metadata + precautionary guidance
# =========================================================================== #

DISEASE_INFO: Dict[str, Dict[str, Any]] = {

    # ── Tomato ─────────────────────────────────────────────────────────────

    "Tomato Early Blight": {
        "display_name": "Tomato Early Blight",
        "crop": "Tomato",
        "is_healthy": False,
        "severity": "Moderate",
        "description": (
            "Early blight (Alternaria solani) causes dark, concentric-ring 'target' lesions "
            "on lower leaves. It progresses upward and reduces photosynthesis, shrinking fruit yield."
        ),
        "precautions": [
            "Remove and destroy infected lower leaves immediately — do not compost.",
            "Spray chlorothalonil or mancozeb fungicide every 7–10 days.",
            "Avoid overhead irrigation; switch to drip to keep foliage dry.",
            "Stake plants and prune suckers to improve canopy air circulation.",
            "Apply balanced potassium fertiliser — deficiency increases susceptibility.",
        ],
    },

    "Tomato Late Blight": {
        "display_name": "Tomato Late Blight",
        "crop": "Tomato",
        "is_healthy": False,
        "severity": "High",
        "description": (
            "Late blight (Phytophthora infestans) is the most destructive tomato disease. "
            "Water-soaked lesions with white sporulation expand rapidly in cool, moist weather "
            "and can destroy an entire field within days if untreated."
        ),
        "precautions": [
            "Remove and bag all visibly infected plants immediately — do not compost.",
            "Apply metalaxyl-M + mancozeb fungicide every 5–7 days as a preventive.",
            "Stop overhead irrigation — evening watering keeps leaves wet overnight.",
            "Monitor weather: cool (15–25 °C) + humid (>90 % RH) nights = highest risk window.",
            "Hill soil around stems to prevent spore wash-down to tubers.",
        ],
    },

    "Tomato Leaf Mould": {
        "display_name": "Tomato Leaf Mould",
        "crop": "Tomato",
        "is_healthy": False,
        "severity": "Moderate",
        "description": (
            "Leaf mould (Passalora fulva) creates pale yellow patches on upper leaf surfaces "
            "and olive-green velvety mould below. Primarily a greenhouse problem driven by "
            "high humidity; causes premature defoliation."
        ),
        "precautions": [
            "Reduce greenhouse humidity below 85 % — improve ventilation immediately.",
            "Remove all visibly infected leaves and bag them carefully.",
            "Apply difenoconazole or copper-based fungicide every 10 days.",
            "Avoid over-crowding plants — maintain 40–50 cm between stems.",
            "Water at the base only and avoid wetting foliage during watering.",
        ],
    },

    "Tomato Bacterial Spot": {
        "display_name": "Tomato Bacterial Spot",
        "crop": "Tomato",
        "is_healthy": False,
        "severity": "Moderate",
        "description": (
            "Bacterial spot (Xanthomonas spp.) causes water-soaked leaf lesions with yellow halos "
            "and rough, scabby blemishes on fruit, significantly reducing marketability."
        ),
        "precautions": [
            "Apply copper-based bactericide weekly from transplanting through fruit set.",
            "Use certified, pathogen-free transplants — never save seed from infected plants.",
            "Avoid working in wet fields; bacteria spread on wet tools and clothing.",
            "Switch from overhead to drip irrigation to minimise leaf wetness.",
            "Rotate crops — avoid planting tomato or pepper in the same plot for 2 seasons.",
        ],
    },

    "Tomato Healthy": {
        "display_name": "Tomato Healthy",
        "crop": "Tomato",
        "is_healthy": True,
        "severity": "None",
        "description": "No disease detected. Tomato plant appears vigorous and healthy.",
        "precautions": [
            "Continue preventive copper + mancozeb spray rotation as a calendar programme.",
            "Inspect lower leaves weekly from fruiting stage onward for early signs of blight.",
            "Maintain consistent soil moisture — fluctuations cause blossom-drop and fruit crack.",
        ],
    },

    # ── Potato ─────────────────────────────────────────────────────────────

    "Potato Early Blight": {
        "display_name": "Potato Early Blight",
        "crop": "Potato",
        "is_healthy": False,
        "severity": "Moderate",
        "description": (
            "Early blight (Alternaria solani) produces concentric-ring 'target' lesions on "
            "lower leaves, progressing upward. Defoliation reduces tuber size and storability."
        ),
        "precautions": [
            "Remove and destroy all early-infected lower foliage immediately.",
            "Apply chlorothalonil every 7–10 days from first symptoms through haulm death.",
            "Maintain adequate potassium — well-nourished plants tolerate early blight better.",
            "Use certified disease-free seed tubers each season.",
            "Hill soil around stems to protect developing tubers.",
        ],
    },

    "Potato Late Blight": {
        "display_name": "Potato Late Blight",
        "crop": "Potato",
        "is_healthy": False,
        "severity": "High",
        "description": (
            "Potato late blight (Phytophthora infestans) can wipe out an entire crop in days. "
            "Grey-green, water-soaked lesions appear on leaves; white sporulation is visible on "
            "undersides in humid conditions. Tubers rot in storage."
        ),
        "precautions": [
            "Begin preventive metalaxyl + mancozeb sprays before disease onset; repeat every 5–7 days.",
            "Hill up soil aggressively — prevents spore wash-down from foliage to tubers.",
            "Cut and remove haulm 2 weeks before harvest to protect tubers.",
            "Never irrigate in the evening — wet foliage overnight is the highest infection risk.",
            "Store only fully dry, undamaged tubers in cool, well-ventilated conditions.",
        ],
    },

    "Potato Healthy": {
        "display_name": "Potato Healthy",
        "crop": "Potato",
        "is_healthy": True,
        "severity": "None",
        "description": "No disease detected. Potato crop appears healthy.",
        "precautions": [
            "Scout fields twice weekly from V6 stage — early detection prevents epidemic spread.",
            "Ensure adequate drainage — waterlogged soils invite Phytophthora.",
            "Check seed stock for Colorado beetle egg masses before planting.",
        ],
    },

    # ── Corn ───────────────────────────────────────────────────────────────

    "Corn Common Rust": {
        "display_name": "Corn Common Rust",
        "crop": "Corn",
        "is_healthy": False,
        "severity": "Moderate",
        "description": (
            "Common rust (Puccinia sorghi) produces brick-red pustules on both leaf surfaces. "
            "Cool, wet weather accelerates spread; heavy infection reduces grain fill."
        ),
        "precautions": [
            "Plant early in the season to escape peak rust pressure.",
            "Apply triazole or strobilurin fungicide at early infection detection.",
            "Scout fields twice weekly from V6 stage — early action prevents epidemic spread.",
            "Select rust-resistant hybrid varieties for future seasons.",
            "Avoid dense planting — good canopy airflow slows spore spread.",
        ],
    },

    "Corn Grey Leaf Spot": {
        "display_name": "Corn Grey Leaf Spot",
        "crop": "Corn",
        "is_healthy": False,
        "severity": "High",
        "description": (
            "Grey leaf spot (Cercospora zeae-maydis) creates long, rectangular tan-to-grey lesions "
            "parallel to leaf veins. Severe infections cause premature senescence and major yield loss."
        ),
        "precautions": [
            "Select corn hybrids with published GLS resistance ratings.",
            "Rotate away from corn for at least one full season to reduce soil inoculum.",
            "Apply strobilurin fungicide at VT/R1 (tassel/silking) stage when disease pressure is high.",
            "Avoid minimum-till fields with heavy corn residue — residue harbours overwintering spores.",
            "Ensure adequate nitrogen — stressed plants are far more susceptible.",
        ],
    },

    "Corn Healthy": {
        "display_name": "Corn Healthy",
        "crop": "Corn",
        "is_healthy": True,
        "severity": "None",
        "description": "No disease detected. Corn crop is in good health.",
        "precautions": [
            "Maintain balanced potassium fertility — it enhances tolerance to foliar diseases.",
            "Monitor weekly for fall armyworm frass at the whorl stage.",
            "Scout for aphid colonies which can transmit Barley Yellow Dwarf Virus.",
        ],
    },

    # ── Apple ──────────────────────────────────────────────────────────────

    "Apple Scab": {
        "display_name": "Apple Scab",
        "crop": "Apple",
        "is_healthy": False,
        "severity": "Moderate",
        "description": (
            "Apple scab (Venturia inaequalis) produces olive-green to brown lesions on leaves "
            "and fruit. Infected fruit loses market value; heavy leaf infection weakens the tree."
        ),
        "precautions": [
            "Apply captan or myclobutanil fungicide at bud-break and every 7–10 days during wet weather.",
            "Rake and destroy all fallen leaf litter in autumn to eliminate overwintering spores.",
            "Prune crowded branches to reduce canopy humidity.",
            "Plant scab-resistant apple varieties for new orchards.",
            "Avoid wetting foliage with overhead irrigation — use drip or micro-sprinklers.",
        ],
    },

    "Apple Black Rot": {
        "display_name": "Apple Black Rot",
        "crop": "Apple",
        "is_healthy": False,
        "severity": "High",
        "description": (
            "Black rot (Botryosphaeria obtusa) causes circular, browning lesions on fruit "
            "that enlarge until the apple mummifies. Cankers form on bark, weakening limbs "
            "and providing inoculum for seasons ahead."
        ),
        "precautions": [
            "Collect and destroy all mummified fruit on and under the tree before spring.",
            "Prune cankers 15 cm below visible margins and sterilise tools between each cut.",
            "Apply copper hydroxide at dormant and green-tip stages.",
            "Remove dead wood promptly — it is the primary inoculum reservoir.",
            "Thin fruit clusters to a single fruit to reduce disease spread within clusters.",
        ],
    },

    "Apple Healthy": {
        "display_name": "Apple Healthy",
        "crop": "Apple",
        "is_healthy": True,
        "severity": "None",
        "description": "No disease detected. Apple tree is in good health.",
        "precautions": [
            "Continue preventive fungicide calendar through the growing season.",
            "Monitor for fire blight during bloom — avoid overhead irrigation at flowering.",
            "Apply balanced NPK fertiliser per seasonal recommendations.",
        ],
    },

    # ── Grape ──────────────────────────────────────────────────────────────

    "Grape Black Rot": {
        "display_name": "Grape Black Rot",
        "crop": "Grape",
        "is_healthy": False,
        "severity": "High",
        "description": (
            "Grape black rot (Guignardia bidwellii) causes brown lesions with dark borders on "
            "leaves and mummifies berries into hard black 'raisins' that overwinter spores "
            "and re-infect the following season."
        ),
        "precautions": [
            "Collect and destroy all mummified berries before budbreak.",
            "Spray mancozeb or myclobutanil from budbreak through veraison every 7–14 days.",
            "Train vines to ensure good air circulation throughout the canopy.",
            "Remove infected shoot tips and leaves promptly.",
            "Apply lime sulphur at dormant stage to reduce overwintering inoculum.",
        ],
    },

    "Grape Healthy": {
        "display_name": "Grape Healthy",
        "crop": "Grape",
        "is_healthy": True,
        "severity": "None",
        "description": "No disease detected. Grapevine is in excellent health.",
        "precautions": [
            "Continue calendar copper / sulphur preventive spray programme.",
            "Monitor canopy density — over-vigour promotes disease-friendly micro-climates.",
            "Scout for grape berry moth and mealybug during the growing season.",
        ],
    },

    # ── Bell Pepper ────────────────────────────────────────────────────────

    "Bell Pepper Bacterial Spot": {
        "display_name": "Bell Pepper Bacterial Spot",
        "crop": "Bell Pepper",
        "is_healthy": False,
        "severity": "Moderate",
        "description": (
            "Bacterial spot (Xanthomonas campestris pv. vesicatoria) causes water-soaked spots "
            "on leaves and fruit that turn brown and scabby, reducing yield and market quality."
        ),
        "precautions": [
            "Tank-mix copper + mancozeb and apply weekly from transplant through fruit set.",
            "Use certified disease-free transplants — never save seed from infected plants.",
            "Avoid working in wet fields — bacteria spread on wet tools and clothing.",
            "Switch from overhead to drip irrigation to minimise leaf wetness.",
            "Rotate with non-Solanaceous crops for at least 2 seasons.",
        ],
    },

    "Bell Pepper Healthy": {
        "display_name": "Bell Pepper Healthy",
        "crop": "Bell Pepper",
        "is_healthy": True,
        "severity": "None",
        "description": "No disease detected. Bell pepper plant is in good health.",
        "precautions": [
            "Mulch around plants to conserve moisture and suppress weeds.",
            "Scout weekly for aphids — they vector CMV and PVY viruses.",
            "Ensure consistent soil moisture — stress triggers blossom drop.",
        ],
    },
}

# =========================================================================== #
#  Convenience helpers
# =========================================================================== #

def get_class_name(index: int) -> str:
    """
    Return the class name for a given model output index.
    Falls back to 'Tomato Healthy' if index is out of range.
    """
    if 0 <= index < len(CLASS_NAMES):
        return CLASS_NAMES[index]
    return "Tomato Healthy"


def get_disease_info(class_name: str) -> Dict[str, Any]:
    """
    Return metadata for a given class name.
    Falls back to 'Tomato Healthy' metadata if class is unknown.
    """
    return DISEASE_INFO.get(class_name, DISEASE_INFO["Tomato Healthy"])


def is_healthy_class(class_name: str) -> bool:
    """Return True if the class represents a healthy plant."""
    return DISEASE_INFO.get(class_name, {}).get("is_healthy", False)
