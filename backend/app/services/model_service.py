"""
app/services/model_service.py
------------------------------
Image classification inference wrapper for AgriSmart AI.

Public API
----------
    predict(image_bytes: bytes) -> DiseasePredictionResponse

Inference routing
-----------------
1. If MODEL_PATH is set in .env AND the file exists:
   → Real inference via the appropriate backend (ONNX / PyTorch / Keras)
2. If MODEL_PATH is set BUT the file is missing:
   → Logs a warning and falls back to mock (server never crashes)
3. If MODEL_PATH is empty:
   → Mock mode (deterministic, hash-based; perfect for frontend testing)

Real model backends (auto-detected by file extension)
------------------------------------------------------
  .onnx  — ONNX Runtime   (pip install onnxruntime)
  .pt / .pth — PyTorch    (pip install torch torchvision)
  .h5    — TF/Keras       (pip install tensorflow)

PlantVillage classes
--------------------
38 classes across 14 crop species — the standard benchmark dataset.
"""

from __future__ import annotations

import hashlib
import logging
import os
import random
import time
from io import BytesIO
from typing import Any, Dict, List, Optional, Tuple

from PIL import Image, UnidentifiedImageError

from app.core.config import settings
from app.schemas.disease import (
    AlternativePrediction,
    DiseasePredictionResponse,
    PrecautionItem,
)

logger = logging.getLogger(__name__)

# =========================================================================== #
#  Module-level model handles (loaded once at first inference call)
# =========================================================================== #

_onnx_session: Optional[Any] = None   # onnxruntime.InferenceSession
_torch_model:  Optional[Any] = None   # torch.nn.Module
_keras_model:  Optional[Any] = None   # tf.keras.Model
_INFERENCE_BACKEND: str = "none"       # "onnx" | "torch" | "keras" | "mock"


def _load_model() -> str:
    """
    Lazily load the model at first call and cache it in the module globals.

    Returns the backend name: "onnx", "torch", "keras", or "mock".
    """
    global _onnx_session, _torch_model, _keras_model, _INFERENCE_BACKEND

    if _INFERENCE_BACKEND != "none":
        return _INFERENCE_BACKEND  # already loaded

    model_path = settings.MODEL_PATH

    if not model_path:
        logger.warning(
            "⚠  MODEL_PATH is not set in .env — using mock predictions."
        )
        _INFERENCE_BACKEND = "mock"
        return _INFERENCE_BACKEND

    if not os.path.isfile(model_path):
        logger.warning(
            "⚠  Model file not found at '%s' — using mock predictions.", model_path
        )
        _INFERENCE_BACKEND = "mock"
        return _INFERENCE_BACKEND

    ext = os.path.splitext(model_path)[1].lower()

    if ext == ".onnx":
        try:
            import onnxruntime as ort  # type: ignore
            _onnx_session = ort.InferenceSession(
                model_path,
                providers=["CUDAExecutionProvider", "CPUExecutionProvider"],
            )
            _INFERENCE_BACKEND = "onnx"
            logger.info("✅ ONNX model loaded from '%s'", model_path)
        except ImportError:
            logger.error(
                "onnxruntime is not installed. Run: pip install onnxruntime. "
                "Falling back to mock."
            )
            _INFERENCE_BACKEND = "mock"

    elif ext in (".pt", ".pth"):
        try:
            import torch  # type: ignore
            _torch_model = torch.load(model_path, map_location="cpu")
            _torch_model.eval()
            _INFERENCE_BACKEND = "torch"
            logger.info("✅ PyTorch model loaded from '%s'", model_path)
        except ImportError:
            logger.error(
                "torch is not installed. Run: pip install torch torchvision. "
                "Falling back to mock."
            )
            _INFERENCE_BACKEND = "mock"

    elif ext == ".h5":
        try:
            import tensorflow as tf  # type: ignore
            _keras_model = tf.keras.models.load_model(model_path)
            _INFERENCE_BACKEND = "keras"
            logger.info("✅ Keras model loaded from '%s'", model_path)
        except ImportError:
            logger.error(
                "tensorflow is not installed. Run: pip install tensorflow. "
                "Falling back to mock."
            )
            _INFERENCE_BACKEND = "mock"

    else:
        logger.warning(
            "Unknown model file extension '%s'. Supported: .onnx, .pt, .pth, .h5. "
            "Falling back to mock.",
            ext,
        )
        _INFERENCE_BACKEND = "mock"

    return _INFERENCE_BACKEND

# =========================================================================== #
#  PlantVillage 38-class taxonomy with rich metadata
# =========================================================================== #

DISEASE_CATALOGUE: Dict[str, Dict[str, Any]] = {
    # ── Apple ──────────────────────────────────────────────────────────────
    "Apple___Apple_scab": {
        "display_name": "Apple Scab",
        "crop": "Apple",
        "severity": "Moderate",
        "description": (
            "Apple scab is caused by Venturia inaequalis fungus. "
            "It produces olive-green to brown lesions on leaves, fruit, and young shoots, "
            "reducing marketability and weakening the tree."
        ),
        "precautions": [
            ("Apply preventive fungicide", "Use captan or myclobutanil at bud-break and repeat every 7–10 days during wet weather."),
            ("Remove fallen leaves", "Rake and destroy leaf litter in autumn to eliminate overwintering spores."),
            ("Improve air circulation", "Prune crowded branches to reduce humidity within the canopy."),
        ],
    },
    "Apple___Black_rot": {
        "display_name": "Black Rot",
        "crop": "Apple",
        "severity": "High",
        "description": (
            "Black rot (Botryosphaeria obtusa) causes circular, brown lesions on fruit "
            "that enlarge to mummify the apple. Cankers form on bark, weakening limbs."
        ),
        "precautions": [
            ("Remove mummified fruit", "Collect and destroy all shrivelled fruit on and under the tree before spring."),
            ("Prune cankers", "Cut 15 cm below visible canker margin and sterilise tools between cuts."),
            ("Apply copper fungicide", "Spray copper hydroxide at dormant and green-tip stages."),
        ],
    },
    "Apple___Cedar_apple_rust": {
        "display_name": "Cedar Apple Rust",
        "crop": "Apple",
        "severity": "Moderate",
        "description": (
            "Cedar apple rust (Gymnosporangium juniperi-virginianae) causes orange-yellow "
            "spots on leaves and distorted fruit. Requires both cedar/juniper and apple hosts."
        ),
        "precautions": [
            ("Remove nearby juniper galls", "Cut and bag orange gelatinous galls on junipers before spring rains."),
            ("Apply myclobutanil", "Spray at pink-bud stage and repeat every 7 days during infection periods."),
            ("Plant resistant varieties", "Consider scab- and rust-resistant apple rootstock for new plantings."),
        ],
    },
    "Apple___healthy": {
        "display_name": "Healthy Apple",
        "crop": "Apple",
        "severity": "None",
        "description": "No disease detected. The apple plant appears healthy.",
        "precautions": [
            ("Maintain fertilisation schedule", "Apply balanced NPK fertiliser per seasonal recommendations."),
            ("Monitor regularly", "Inspect foliage weekly for early signs of pest or disease pressure."),
        ],
    },
    # ── Blueberry ──────────────────────────────────────────────────────────
    "Blueberry___healthy": {
        "display_name": "Healthy Blueberry",
        "crop": "Blueberry",
        "severity": "None",
        "description": "No disease detected. Blueberry plant appears vigorous and healthy.",
        "precautions": [
            ("Maintain soil acidity", "Keep soil pH between 4.5–5.5 using sulphur amendments if needed."),
            ("Mulch roots", "Apply 10 cm of pine-bark mulch to retain moisture and suppress weeds."),
        ],
    },
    # ── Cherry ─────────────────────────────────────────────────────────────
    "Cherry_(including_sour)___Powdery_mildew": {
        "display_name": "Powdery Mildew",
        "crop": "Cherry",
        "severity": "Moderate",
        "description": (
            "Powdery mildew (Podosphaera clandestina) appears as white powdery coating on "
            "leaves and shoots, causing distortion and premature leaf drop."
        ),
        "precautions": [
            ("Apply sulphur-based fungicide", "Spray wettable sulphur at first sign and repeat every 10 days."),
            ("Thin the canopy", "Remove water sprouts to improve air movement and reduce humidity."),
            ("Avoid excess nitrogen", "High nitrogen promotes succulent growth — a preferred target for mildew."),
        ],
    },
    "Cherry_(including_sour)___healthy": {
        "display_name": "Healthy Cherry",
        "crop": "Cherry",
        "severity": "None",
        "description": "No disease detected. Cherry plant is in good health.",
        "precautions": [
            ("Prune after harvest", "Thin the canopy post-harvest to prepare for next season."),
            ("Monitor for brown rot", "Check fruit closely during ripening — brown rot can establish rapidly."),
        ],
    },
    # ── Corn / Maize ───────────────────────────────────────────────────────
    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot": {
        "display_name": "Gray Leaf Spot",
        "crop": "Corn",
        "severity": "High",
        "description": (
            "Gray leaf spot (Cercospora zeae-maydis) creates rectangular, grey to tan lesions "
            "parallel to leaf veins. Severe infections cause premature senescence and yield loss."
        ),
        "precautions": [
            ("Use resistant hybrids", "Select corn hybrids with published GLS resistance ratings."),
            ("Rotate crops", "Rotate away from corn for at least one season to reduce inoculum."),
            ("Apply strobilurin fungicide", "Spray at VT/R1 stage if disease pressure is high."),
        ],
    },
    "Corn_(maize)___Common_rust_": {
        "display_name": "Common Rust",
        "crop": "Corn",
        "severity": "Moderate",
        "description": (
            "Common rust (Puccinia sorghi) produces brick-red pustules on both leaf surfaces. "
            "Cool, wet weather accelerates its spread."
        ),
        "precautions": [
            ("Plant early", "Early-season planting allows the crop to escape peak rust pressure."),
            ("Apply foliar fungicide", "Triazole or strobilurin fungicides at early infection signs."),
            ("Scout fields regularly", "Walk fields twice weekly from V6 stage to identify early outbreak."),
        ],
    },
    "Corn_(maize)___Northern_Leaf_Blight": {
        "display_name": "Northern Leaf Blight",
        "crop": "Corn",
        "severity": "High",
        "description": (
            "Northern leaf blight (Exserohilum turcicum) causes long, cigar-shaped grey-green "
            "lesions on lower leaves, progressing upward. Major yield robber in warm, humid seasons."
        ),
        "precautions": [
            ("Rotate crops", "Avoid planting corn after corn in the same field."),
            ("Apply fungicide at silking", "Propiconazole or azoxystrobin at VT stage is most effective."),
            ("Select resistant varieties", "Modern hybrids carry Ht genes — check seed catalogues."),
        ],
    },
    "Corn_(maize)___healthy": {
        "display_name": "Healthy Corn",
        "crop": "Corn",
        "severity": "None",
        "description": "No disease detected. Corn crop appears healthy.",
        "precautions": [
            ("Maintain balanced fertility", "Ensure adequate potassium — it enhances disease tolerance."),
            ("Monitor for insects", "Watch for fall armyworm frass at whorl stage."),
        ],
    },
    # ── Grape ──────────────────────────────────────────────────────────────
    "Grape___Black_rot": {
        "display_name": "Grape Black Rot",
        "crop": "Grape",
        "severity": "High",
        "description": (
            "Grape black rot (Guignardia bidwellii) causes brown leaf lesions with black borders "
            "and mummifies berries into hard, black 'raisins' that overwinter spores."
        ),
        "precautions": [
            ("Remove mummified berries", "Collect and destroy all mummified fruit before budbreak."),
            ("Apply mancozeb", "Spray from budbreak through veraison every 7–14 days."),
            ("Train vines properly", "Ensure good air circulation to reduce canopy humidity."),
        ],
    },
    "Grape___Esca_(Black_Measles)": {
        "display_name": "Esca (Black Measles)",
        "crop": "Grape",
        "severity": "High",
        "description": (
            "Esca is a complex trunk disease caused by multiple wood-decay fungi. "
            "It produces inter-vein chlorosis and necrosis (tiger-stripe pattern) on leaves "
            "and internal wood decay, eventually killing the vine."
        ),
        "precautions": [
            ("Protect pruning wounds", "Apply wound sealant or fungicide paste immediately after cuts."),
            ("Remove and burn infected wood", "Cut out all visibly diseased canes and disinfect tools."),
            ("Delay pruning", "Prune during dry weather to reduce infection window."),
        ],
    },
    "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)": {
        "display_name": "Leaf Blight",
        "crop": "Grape",
        "severity": "Moderate",
        "description": (
            "Isariopsis leaf spot creates angular, brown lesions with yellow halos on grape leaves, "
            "causing premature defoliation and reducing photosynthesis."
        ),
        "precautions": [
            ("Apply copper fungicide", "Spray Bordeaux mixture at 7–10 day intervals during wet periods."),
            ("Improve drainage", "Waterlogged roots predispose vines — ensure field drainage is adequate."),
            ("Thin foliage", "Remove leaves around clusters to improve spray penetration."),
        ],
    },
    "Grape___healthy": {
        "display_name": "Healthy Grape",
        "crop": "Grape",
        "severity": "None",
        "description": "No disease detected. Grapevine is in excellent health.",
        "precautions": [
            ("Maintain fungicide programme", "Continue calendar-based copper / sulphur sprays as preventive."),
            ("Monitor canopy density", "Avoid over-vigour — it promotes disease-friendly micro-climates."),
        ],
    },
    # ── Orange ─────────────────────────────────────────────────────────────
    "Orange___Haunglongbing_(Citrus_greening)": {
        "display_name": "Huanglongbing (Citrus Greening)",
        "crop": "Orange",
        "severity": "High",
        "description": (
            "HLB (caused by Candidatus Liberibacter spp.) is the most destructive citrus disease "
            "globally. It causes asymmetric yellowing (blotchy mottle), small lopsided bitter fruit, "
            "and eventually tree death. Spread by the Asian citrus psyllid insect."
        ),
        "precautions": [
            ("Control psyllid vector", "Apply systemic insecticide (imidacloprid) to control psyllid populations."),
            ("Remove infected trees", "Infected trees are incurable — remove and chip or burn promptly."),
            ("Use certified disease-free nursery stock", "Never plant trees without phytosanitary certificate."),
        ],
    },
    # ── Peach ──────────────────────────────────────────────────────────────
    "Peach___Bacterial_spot": {
        "display_name": "Bacterial Spot",
        "crop": "Peach",
        "severity": "Moderate",
        "description": (
            "Peach bacterial spot (Xanthomonas arboricola pv. pruni) causes water-soaked, "
            "angular lesions on leaves that turn brown and fall out, and pitted, cracked "
            "fruit that loses market value."
        ),
        "precautions": [
            ("Apply copper bactericide", "Spray copper hydroxide at shuck-split and repeat weekly."),
            ("Plant resistant varieties", "Choose bacterial-spot-resistant peach cultivars."),
            ("Avoid wound injury", "Hail and wind-driven rain create entry points — consider windbreaks."),
        ],
    },
    "Peach___healthy": {
        "display_name": "Healthy Peach",
        "crop": "Peach",
        "severity": "None",
        "description": "No disease detected. Peach tree is in good health.",
        "precautions": [
            ("Continue preventive copper sprays", "Apply copper fungicide at dormant and pink-bud stages."),
            ("Thin fruit early", "Thin to 15–20 cm spacing to encourage large, marketable fruit."),
        ],
    },
    # ── Pepper ─────────────────────────────────────────────────────────────
    "Pepper,_bell___Bacterial_spot": {
        "display_name": "Bacterial Spot",
        "crop": "Pepper (Bell)",
        "severity": "Moderate",
        "description": (
            "Bacterial spot (Xanthomonas campestris pv. vesicatoria) causes water-soaked spots "
            "on leaves and fruit that turn brown and scabby, significantly reducing yield."
        ),
        "precautions": [
            ("Use copper + mancozeb tank mix", "Weekly applications from transplant through fruit set."),
            ("Use disease-free transplants", "Always source certified pathogen-tested seedlings."),
            ("Avoid overhead irrigation", "Overhead water splash spreads bacteria — use drip irrigation."),
        ],
    },
    "Pepper,_bell___healthy": {
        "display_name": "Healthy Pepper",
        "crop": "Pepper (Bell)",
        "severity": "None",
        "description": "No disease detected. Bell pepper plant appears healthy.",
        "precautions": [
            ("Mulch to conserve moisture", "Use straw mulch to maintain uniform soil moisture."),
            ("Scout for aphids", "Aphids vector pepper viruses — control early with neem oil."),
        ],
    },
    # ── Potato ─────────────────────────────────────────────────────────────
    "Potato___Early_blight": {
        "display_name": "Early Blight",
        "crop": "Potato",
        "severity": "Moderate",
        "description": (
            "Early blight (Alternaria solani) produces concentric-ring 'target' lesions on lower "
            "leaves, progressing upward. Defoliation reduces tuber size and storability."
        ),
        "precautions": [
            ("Remove lower infected leaves", "Prune and destroy earliest affected foliage promptly."),
            ("Apply chlorothalonil", "Spray every 7–10 days from first symptoms through haulm senescence."),
            ("Maintain crop vigour", "Well-fertilised plants tolerate early blight better — apply adequate potassium."),
        ],
    },
    "Potato___Late_blight": {
        "display_name": "Late Blight",
        "crop": "Potato",
        "severity": "High",
        "description": (
            "Late blight (Phytophthora infestans) is the most devastating potato disease. "
            "Water-soaked lesions with white sporulation expand rapidly in cool, moist conditions "
            "and can destroy an entire field within days."
        ),
        "precautions": [
            ("Apply metalaxyl + mancozeb", "Begin preventive sprays before disease onset; repeat every 5–7 days."),
            ("Hill up soil around stems", "Hilling prevents spore wash-down from foliage to tubers."),
            ("Remove infected haulm", "Cut and remove foliage 2 weeks before harvest to protect tubers."),
            ("Avoid overhead irrigation at night", "Wet foliage overnight dramatically increases infection risk."),
        ],
    },
    "Potato___healthy": {
        "display_name": "Healthy Potato",
        "crop": "Potato",
        "severity": "None",
        "description": "No disease detected. Potato crop appears healthy.",
        "precautions": [
            ("Scout for Colorado beetle", "Hand-pick egg masses and apply spinosad if populations build."),
            ("Ensure adequate drainage", "Waterlogged soils encourage Phytophthora — check drainage channels."),
        ],
    },
    # ── Raspberry ──────────────────────────────────────────────────────────
    "Raspberry___healthy": {
        "display_name": "Healthy Raspberry",
        "crop": "Raspberry",
        "severity": "None",
        "description": "No disease detected. Raspberry canes are healthy.",
        "precautions": [
            ("Prune floricanes after harvest", "Remove spent canes at ground level to reduce disease inoculum."),
            ("Tie up new canes", "Training primocanes improves airflow and reduces fungal pressure."),
        ],
    },
    # ── Soybean ────────────────────────────────────────────────────────────
    "Soybean___healthy": {
        "display_name": "Healthy Soybean",
        "crop": "Soybean",
        "severity": "None",
        "description": "No disease detected. Soybean crop is in good health.",
        "precautions": [
            ("Inoculate with Bradyrhizobium", "Ensure seed inoculation for optimal nitrogen fixation."),
            ("Monitor for soybean aphid", "Check undersides of leaves weekly from V2 stage."),
        ],
    },
    # ── Squash ─────────────────────────────────────────────────────────────
    "Squash___Powdery_mildew": {
        "display_name": "Powdery Mildew",
        "crop": "Squash",
        "severity": "Moderate",
        "description": (
            "Powdery mildew on squash (Podosphaera xanthii / Erysiphe cichoracearum) produces "
            "white powder on leaf surfaces, causing premature death of older leaves."
        ),
        "precautions": [
            ("Apply potassium bicarbonate", "Spray organic-approved potassium bicarbonate every 7 days."),
            ("Remove severely infected leaves", "Cut and bag leaves with >50 % coverage promptly."),
            ("Plant resistant varieties", "Select modern squash varieties with bred-in mildew resistance."),
        ],
    },
    # ── Strawberry ─────────────────────────────────────────────────────────
    "Strawberry___Leaf_scorch": {
        "display_name": "Leaf Scorch",
        "crop": "Strawberry",
        "severity": "Moderate",
        "description": (
            "Strawberry leaf scorch (Diplocarpon earlianum) causes small, irregular purple spots "
            "that merge and give leaves a scorched appearance, reducing plant vigour."
        ),
        "precautions": [
            ("Remove old leaves after renovation", "Mow and remove foliage after harvest to eliminate inoculum."),
            ("Apply captan fungicide", "Begin sprays at first bloom and repeat every 10 days."),
            ("Use certified planting material", "Always start with virus-indexed, disease-tested transplants."),
        ],
    },
    "Strawberry___healthy": {
        "display_name": "Healthy Strawberry",
        "crop": "Strawberry",
        "severity": "None",
        "description": "No disease detected. Strawberry plant is in good health.",
        "precautions": [
            ("Renovate beds after harvest", "Mow foliage, thin plants, and fertilise to rejuvenate beds."),
            ("Monitor for spider mites", "Check leaf undersides in hot, dry weather — apply miticides if needed."),
        ],
    },
    # ── Tomato ─────────────────────────────────────────────────────────────
    "Tomato___Bacterial_spot": {
        "display_name": "Bacterial Spot",
        "crop": "Tomato",
        "severity": "Moderate",
        "description": (
            "Bacterial spot (Xanthomonas spp.) creates water-soaked leaf lesions with yellow halos "
            "and rough, scabby blemishes on fruit, reducing both yield and marketability."
        ),
        "precautions": [
            ("Apply copper bactericide", "Start copper sprays at transplanting and repeat every 5–7 days during wet weather."),
            ("Avoid working in wet fields", "Bacteria spread on wet tools and clothing — delay field operations after rain."),
            ("Use drip irrigation", "Minimise leaf wetness by switching from overhead to drip systems."),
        ],
    },
    "Tomato___Early_blight": {
        "display_name": "Early Blight",
        "crop": "Tomato",
        "severity": "Moderate",
        "description": (
            "Tomato early blight (Alternaria solani) produces dark, concentric-ring lesions on "
            "older leaves, causing defoliation from the bottom up and reducing fruit quality."
        ),
        "precautions": [
            ("Remove affected lower leaves", "Prune and dispose of all infected foliage immediately."),
            ("Apply chlorothalonil or mancozeb", "Spray every 7 days, ensuring full coverage of the lower canopy."),
            ("Stake and prune for airflow", "Keep plants staked and pruned to lateral shoots to improve air movement."),
        ],
    },
    "Tomato___Late_blight": {
        "display_name": "Late Blight",
        "crop": "Tomato",
        "severity": "High",
        "description": (
            "Late blight (Phytophthora infestans) causes rapidly expanding water-soaked lesions "
            "with white sporulation on leaf undersides and brown rotting of stem and fruit. "
            "It spreads explosively in cool, humid conditions."
        ),
        "precautions": [
            ("Remove and destroy infected plants", "Bag and remove visibly infected plants — do not compost."),
            ("Apply metalaxyl-M + mancozeb", "Spray every 5–7 days as a preventive from first-risk weather onward."),
            ("Avoid overhead irrigation", "Evening watering keeps leaves wet overnight — an ideal infection window."),
            ("Monitor weather forecasts", "Blight-friendly weather (15–25 °C, >90 % RH, leaf wetness >10 h) demands immediate action."),
        ],
    },
    "Tomato___Leaf_Mold": {
        "display_name": "Leaf Mold",
        "crop": "Tomato",
        "severity": "Moderate",
        "description": (
            "Leaf mold (Passalora fulva / Cladosporium fulvum) causes pale yellow patches on "
            "upper leaf surfaces and olive-green velvety mould on lower surfaces. "
            "Primarily a greenhouse problem due to high humidity."
        ),
        "precautions": [
            ("Reduce humidity", "Ensure adequate ventilation — target greenhouse RH below 85 %."),
            ("Apply difenoconazole", "Spray every 10 days from first symptom appearance."),
            ("Remove infected leaves", "Carefully bag and remove all visibly infected leaves."),
        ],
    },
    "Tomato___Septoria_leaf_spot": {
        "display_name": "Septoria Leaf Spot",
        "crop": "Tomato",
        "severity": "Moderate",
        "description": (
            "Septoria leaf spot (Septoria lycopersici) causes small, circular spots with dark borders "
            "and grey centres on lower leaves. It progresses upward, stripping the plant of its foliage."
        ),
        "precautions": [
            ("Remove and destroy affected leaves", "Prune infected foliage below the disease front."),
            ("Apply mancozeb or copper fungicide", "Weekly preventive sprays during wet, warm periods."),
            ("Mulch the soil surface", "Mulch prevents rain splash from transferring soil-borne spores to lower leaves."),
        ],
    },
    "Tomato___Spider_mites Two-spotted_spider_mite": {
        "display_name": "Spider Mites (Two-spotted)",
        "crop": "Tomato",
        "severity": "Moderate",
        "description": (
            "Two-spotted spider mites (Tetranychus urticae) cause stippled, bronzed leaves "
            "with fine webbing on undersides. They thrive in hot, dry conditions and "
            "can reach damaging levels very rapidly."
        ),
        "precautions": [
            ("Apply miticide or insecticidal soap", "Spray undersides of leaves thoroughly — rotate miticides to prevent resistance."),
            ("Increase irrigation frequency", "Mites prefer dry conditions — keeping soil and air moist reduces outbreak severity."),
            ("Release predatory mites", "Phytoseiulus persimilis is an effective biological control agent."),
        ],
    },
    "Tomato___Target_Spot": {
        "display_name": "Target Spot",
        "crop": "Tomato",
        "severity": "Moderate",
        "description": (
            "Target spot (Corynespora cassiicola) produces large, concentric-ring lesions on leaves, "
            "stems, and fruit, causing premature defoliation and fruit blemishes."
        ),
        "precautions": [
            ("Apply tebuconazole", "Fungicide application at first detection, repeated every 10 days."),
            ("Improve canopy airflow", "Stake and prune to ensure leaves dry rapidly after rain."),
            ("Practice crop rotation", "Avoid successive tomato crops in the same field."),
        ],
    },
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus": {
        "display_name": "Yellow Leaf Curl Virus (TYLCV)",
        "crop": "Tomato",
        "severity": "High",
        "description": (
            "TYLCV is a begomovirus spread by whiteflies. "
            "Infected plants show upward leaf curling, yellowing, and severe stunting. "
            "There is no cure — prevention and vector control are critical."
        ),
        "precautions": [
            ("Control whitefly vector", "Apply systemic neonicotinoids at transplanting; use yellow sticky traps to monitor."),
            ("Remove infected plants", "Infected plants cannot be cured — remove and bag them immediately."),
            ("Use resistant varieties", "Plant TYLCV-resistant tomato hybrids where available."),
            ("Use insect-proof screens in nurseries", "Prevent vector entry during seedling production."),
        ],
    },
    "Tomato___Tomato_mosaic_virus": {
        "display_name": "Tomato Mosaic Virus (ToMV)",
        "crop": "Tomato",
        "severity": "High",
        "description": (
            "Tomato mosaic virus causes light/dark green mosaic patterning on leaves, "
            "leaf distortion, and fruit bronzing. It spreads mechanically via contaminated "
            "tools, hands, and clothing — and survives in dried plant material for years."
        ),
        "precautions": [
            ("Sanitise all tools", "Dip tools in 1 % sodium hypochlorite (bleach) or 70 % ethanol between plants."),
            ("Wash hands thoroughly", "Wash with soap before and during field work, especially after handling infected plants."),
            ("Remove and destroy infected plants", "No chemical cure exists — physical removal is the only option."),
            ("Use resistant varieties", "Modern tomato hybrids carry Tm-2² gene conferring ToMV resistance."),
        ],
    },
    "Tomato___healthy": {
        "display_name": "Healthy Tomato",
        "crop": "Tomato",
        "severity": "None",
        "description": "No disease detected. Tomato plant appears vigorous and healthy.",
        "precautions": [
            ("Continue preventive spray programme", "Maintain a calendar copper + mancozeb rotation as a preventive."),
            ("Monitor for early blight onset", "Inspect lower leaves weekly from fruiting stage onward."),
        ],
    },
}

# Ordered list of all class keys (for stable random sampling)
ALL_CLASSES: List[str] = list(DISEASE_CATALOGUE.keys())


# =========================================================================== #
#  Image pre-processing helper
# =========================================================================== #


def _preprocess_image(image_bytes: bytes) -> Image.Image:
    """
    Decode raw bytes into a PIL Image and resize to model input dimensions.

    Raises:
        ValueError: If the bytes cannot be decoded as a valid image.
    """
    try:
        img = Image.open(BytesIO(image_bytes)).convert("RGB")
    except UnidentifiedImageError as exc:
        raise ValueError(f"Cannot decode image bytes: {exc}") from exc

    target = settings.MODEL_INPUT_SIZE
    img = img.resize((target, target), Image.LANCZOS)
    return img


# =========================================================================== #
#  Mock inference
# =========================================================================== #


def _mock_inference(image_bytes: bytes) -> Tuple[str, float, List[Tuple[str, float]]]:
    """
    Deterministic mock inference.

    Uses a hash of the image bytes so that the SAME image always returns
    the SAME class — useful for repeatable frontend integration testing.

    Returns:
        (top_class_key, confidence, [(alt_class_key, alt_confidence), ...])
    """
    # Hash → deterministic index into ALL_CLASSES
    digest = hashlib.md5(image_bytes).hexdigest()  # noqa: S324  (not crypto, safe here)
    seed = int(digest, 16)
    rng = random.Random(seed)

    top_index = rng.randint(0, len(ALL_CLASSES) - 1)
    top_class = ALL_CLASSES[top_index]

    # Confidence: skewed high to simulate a trained model
    confidence = round(rng.uniform(0.72, 0.97), 3)

    # Generate 2 plausible alternatives (different classes, lower confidence)
    remaining = [c for i, c in enumerate(ALL_CLASSES) if i != top_index]
    alt_classes = rng.sample(remaining, k=2)
    leftover = 1.0 - confidence
    alt1_conf = round(rng.uniform(0.01, leftover * 0.7), 3)
    alt2_conf = round(leftover - alt1_conf, 3)
    alternatives = [(alt_classes[0], alt1_conf), (alt_classes[1], alt2_conf)]

    return top_class, confidence, alternatives


# =========================================================================== #
#  Real inference  (dispatches to loaded backend)
# =========================================================================== #


def _real_inference(
    img: Image.Image,
) -> Tuple[str, float, List[Tuple[str, float]]]:
    """
    Run inference through whichever backend was loaded by _load_model().

    Returns
    -------
    (top_class_key, confidence, [(alt_class_key, alt_confidence), ...])
    """
    import numpy as np  # type: ignore  # optional dep — only imported when real model used

    target = settings.MODEL_INPUT_SIZE
    img_resized = img.resize((target, target), Image.LANCZOS)

    # ── ONNX Runtime ────────────────────────────────────────────────────────
    if _INFERENCE_BACKEND == "onnx" and _onnx_session is not None:
        x = np.array(img_resized, dtype=np.float32)[None] / 255.0  # (1, H, W, 3)
        input_name = _onnx_session.get_inputs()[0].name
        preds = _onnx_session.run(None, {input_name: x})[0][0]      # (num_classes,)

    # ── PyTorch ─────────────────────────────────────────────────────────────
    elif _INFERENCE_BACKEND == "torch" and _torch_model is not None:
        import torch  # type: ignore
        from torchvision import transforms  # type: ignore
        tfm = transforms.Compose([
            transforms.Resize((target, target)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
        ])
        x = tfm(img_resized).unsqueeze(0)  # (1, 3, H, W)
        with torch.no_grad():
            logits = _torch_model(x)
            preds = torch.softmax(logits, dim=1)[0].cpu().numpy()  # (num_classes,)

    # ── Keras / TensorFlow ──────────────────────────────────────────────────
    elif _INFERENCE_BACKEND == "keras" and _keras_model is not None:
        x = np.array(img_resized, dtype=np.float32)[None] / 255.0  # (1, H, W, 3)
        preds = _keras_model.predict(x, verbose=0)[0]              # (num_classes,)

    else:
        raise RuntimeError(
            f"_real_inference called but _INFERENCE_BACKEND={_INFERENCE_BACKEND!r}"
        )

    # ── Map probabilities → class labels ────────────────────────────────────
    top_idx = int(np.argmax(preds))
    top_class = ALL_CLASSES[top_idx] if top_idx < len(ALL_CLASSES) else "Tomato___healthy"
    confidence = float(preds[top_idx])

    # Top-2 alternatives
    sorted_indices = np.argsort(preds)[::-1]  # descending
    alt_indices = [i for i in sorted_indices if i != top_idx][:2]
    alternatives = [
        (ALL_CLASSES[i] if i < len(ALL_CLASSES) else "Tomato___healthy", float(preds[i]))
        for i in alt_indices
    ]

    return top_class, confidence, alternatives


# =========================================================================== #
#  Public API
# =========================================================================== #


def predict(image_bytes: bytes) -> DiseasePredictionResponse:
    """
    Classify a plant leaf image and return a rich prediction response.

    Parameters
    ----------
    image_bytes : bytes
        Raw bytes of the uploaded image file.

    Returns
    -------
    DiseasePredictionResponse
        Full prediction with class, confidence, precautions, and metadata.

    Raises
    ------
    ValueError
        If the image bytes cannot be decoded as a valid image.
    """
    t_start = time.perf_counter()

    # 1. Pre-process
    img = _preprocess_image(image_bytes)

    # 2. Determine backend (lazy-loads model on first call)
    backend = _load_model()
    use_mock = backend == "mock"

    if use_mock:
        top_class, confidence, raw_alternatives = _mock_inference(image_bytes)
        model_version = "mock-v1.0"
    else:
        top_class, confidence, raw_alternatives = _real_inference(img)
        model_version = f"{backend}-v{settings.APP_VERSION}"

    # 3. Apply confidence threshold
    if confidence < settings.CONFIDENCE_THRESHOLD:
        top_class = "Tomato___healthy"  # fallback to a safe, known class
        confidence = 0.0

    # 4. Build response from catalogue
    meta = DISEASE_CATALOGUE.get(top_class, DISEASE_CATALOGUE["Tomato___healthy"])

    precautions = [
        PrecautionItem(step=i + 1, action=action, detail=detail)
        for i, (action, detail) in enumerate(meta["precautions"])
    ]

    alternatives = [
        AlternativePrediction(class_name=cls, confidence=conf)
        for cls, conf in raw_alternatives
    ] if raw_alternatives else None

    t_end = time.perf_counter()

    return DiseasePredictionResponse(
        class_name=top_class,
        confidence=confidence,
        severity=meta["severity"],
        is_healthy=(meta["severity"] == "None"),
        display_name=meta["display_name"],
        crop_name=meta["crop"],
        description=meta["description"],
        precautions=precautions,
        alternatives=alternatives,
        model_version=model_version,
        processing_time_ms=round((t_end - t_start) * 1000, 2),
    )
