"""
app/api/v1/endpoints/assistant.py
------------------------------------
Bonus Endpoint — GenAI Farmer Guidance & Explanation Assistant

POST /api/v1/assistant/query
    • Accepts a farmer's natural-language question, preferred language,
      and optional grounding context (e.g. detected disease class).
    • Returns a structured, farmer-friendly response with follow-up
      questions and source citations.

AI Backend
----------
Primary:  Google Gemini  (set GEMINI_API_KEY in .env)
Fallback: Built-in rule-based mock engine (no API key needed)

The response schema (AssistantResponse) is backend-agnostic — the frontend
integration is identical regardless of which engine is active.

Supported languages
-------------------
English (en), Hindi (hi), Telugu (te), Tamil (ta), Kannada (kn),
Marathi (mr), Bengali (bn), Punjabi (pa), Gujarati (gu)
"""

from __future__ import annotations

import logging
from typing import List

from fastapi import APIRouter, HTTPException, status

from app.core.config import settings
from app.schemas.advisory import AssistantRequest, AssistantResponse, AssistantSource

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/assistant",
    tags=["🤖 AI Assistant"],
)

# ─── Language code → full name (for Gemini prompt) ────────────────────────────
_LANG_NAMES = {
    "en": "English",
    "hi": "Hindi",
    "te": "Telugu",
    "ta": "Tamil",
    "kn": "Kannada",
    "mr": "Marathi",
    "bn": "Bengali",
    "pa": "Punjabi",
    "gu": "Gujarati",
}

# =========================================================================== #
#  Built-in mock knowledge base
# =========================================================================== #

_KNOWLEDGE_BASE = [
    {
        "keywords": ["late blight", "phytophthora", "water soaked", "white spore"],
        "answer": (
            "Your plants show signs consistent with **Late Blight** (*Phytophthora infestans*). "
            "Act immediately:\n"
            "1. **Remove** all visibly infected leaves and stems — bag them and destroy.\n"
            "2. **Apply fungicide**: Use metalaxyl-M + mancozeb every 5–7 days.\n"
            "3. **Stop overhead irrigation** — switch to drip to keep foliage dry.\n"
            "4. **Scout neighbouring plants** — Late Blight spreads explosively in cool, humid weather.\n"
            "5. **Monitor weather**: Cool (15–25 °C) + humid (>90% RH) nights are the highest-risk windows."
        ),
        "follow_ups": [
            "Are the lesions spreading to stems and fruit as well?",
            "What is the night-time temperature and humidity in your field?",
            "Do you have metalaxyl-based fungicide available locally?",
        ],
        "sources": [
            AssistantSource(title="ICAR Late Blight Management Guide", relevance="Fungicide schedules for Phytophthora infestans in India"),
            AssistantSource(title="PlantVillage Disease Atlas", relevance="Symptom identification and severity classification"),
        ],
    },
    {
        "keywords": ["early blight", "alternaria", "target spot", "concentric ring", "dark lesion"],
        "answer": (
            "The symptoms suggest **Early Blight** (*Alternaria solani*). Action plan:\n"
            "1. **Prune** all infected lower leaves and destroy them.\n"
            "2. **Spray chlorothalonil or mancozeb** every 7–10 days.\n"
            "3. **Stake plants** to improve air circulation.\n"
            "4. **Mulch the soil** to prevent rain splash spreading spores.\n"
            "5. **Ensure balanced nutrition** — potassium deficiency increases susceptibility."
        ),
        "follow_ups": [
            "Is the discolouration starting from the bottom leaves?",
            "Have you applied any fungicide in the past 2 weeks?",
            "What is the current stage of your crop?",
        ],
        "sources": [
            AssistantSource(title="FAO Integrated Pest Management Guide", relevance="Alternaria management in Solanaceous crops"),
        ],
    },
    {
        "keywords": ["yellow", "yellowing", "pale", "chlorosis"],
        "answer": (
            "Yellowing leaves can have several causes:\n\n"
            "**1. Nutrient deficiency** — Apply balanced NPK; if inter-vein yellowing, apply chelated iron/magnesium.\n"
            "**2. Overwatering / root rot** — Check drainage; let soil dry before next irrigation.\n"
            "**3. Disease (Mosaic Virus, TYLCV)** — Look for mosaic patterns or upward leaf curl.\n"
            "**4. Pest damage (spider mites, whitefly)** — Check leaf undersides.\n\n"
            "Start by checking your irrigation schedule and nutrient programme."
        ),
        "follow_ups": [
            "Is the yellowing uniform or only between the veins?",
            "Are younger or older leaves affected first?",
            "Have you changed your fertilisation schedule recently?",
        ],
        "sources": [
            AssistantSource(title="UC Davis Nutrient Deficiency Guide", relevance="Visual diagnosis of macro and micronutrient deficiencies"),
        ],
    },
    {
        "keywords": ["irrigat", "water", "drip", "moisture", "drought"],
        "answer": (
            "Smart irrigation advice:\n\n"
            "- **Timing**: Irrigate in early morning (5–7 AM) to reduce evaporation.\n"
            "- **Drip irrigation** delivers water directly to roots and reduces fungal risk.\n"
            "- **Soil check**: Push a finger 5 cm into soil — if dry, it's time to water.\n"
            "- **Avoid over-irrigation**: Waterlogged soil causes root hypoxia and Phytophthora.\n"
            "- Use the **Advisory endpoint** for a personalised 3-day irrigation schedule."
        ),
        "follow_ups": [
            "What irrigation method are you currently using?",
            "What is the soil type in your field?",
            "At what crop growth stage are you currently?",
        ],
        "sources": [
            AssistantSource(title="ICRISAT Water Management for Smallholders", relevance="Drip and furrow irrigation scheduling"),
        ],
    },
    {
        "keywords": ["pesticide", "fungicide", "insecticide", "spray", "chemical"],
        "answer": (
            "Responsible pesticide use:\n\n"
            "1. **Identify before you spray** — use the Disease Detection endpoint first.\n"
            "2. **Follow label rates** — excessive doses cause residues and resistance.\n"
            "3. **Rotate chemical classes** to prevent resistance development.\n"
            "4. **Spray in the evening or early morning** — midday causes phytotoxicity.\n"
            "5. **Wear PPE**: Gloves, mask, and protective clothing.\n"
            "6. **Respect pre-harvest intervals (PHI)** — check the product label.\n"
            "7. Prefer **IPM**: combine biological, cultural, and chemical methods."
        ),
        "follow_ups": [
            "Which specific disease or pest are you targeting?",
            "Do you have access to bio-pesticides?",
            "What is your crop and current growth stage?",
        ],
        "sources": [
            AssistantSource(title="FAO Good Agricultural Practices", relevance="Safe and effective pesticide application"),
        ],
    },
]

_DEFAULT_ANSWER = (
    "Thank you for your question. Here is general agronomic guidance:\n\n"
    "1. **Observe your crop daily** — early detection is the most important practice.\n"
    "2. **Use the Disease Detection tool** — upload a photo for an instant diagnosis.\n"
    "3. **Check the Advisory tool** — enter soil/weather conditions for personalised recommendations.\n"
    "4. **Maintain soil health** — balanced pH, organic matter, and drainage are foundational.\n"
    "5. **Contact your local KVK** (Krishi Vigyan Kendra) for region-specific guidance."
)


def _mock_engine(req: AssistantRequest) -> tuple[str, List[str], List[AssistantSource]]:
    """Keyword-matching fallback engine. Returns (answer, follow_ups, sources)."""
    combined = f"{req.query.lower()} {(req.context or '').lower()}"
    for entry in _KNOWLEDGE_BASE:
        if any(kw in combined for kw in entry["keywords"]):
            return entry["answer"], entry["follow_ups"], entry["sources"]
    return _DEFAULT_ANSWER, [
        "Can you describe the symptoms in more detail?",
        "Which crop and growth stage are you asking about?",
        "Have you noticed any insects or unusual odours?",
    ], []


# =========================================================================== #
#  Google Gemini integration
# =========================================================================== #

async def _call_gemini(req: AssistantRequest) -> str:
    """
    Generate a farmer-friendly response using Google Gemini.
    """
    if not settings.GEMINI_API_KEY:
        logger.warning("GEMINI_API_KEY is not configured.")
        return ""

    lang_name = _LANG_NAMES.get(req.language.value, "English")

    system_instruction = (
        f"You are AgriSmart AI — an expert agricultural advisor helping smallholder farmers "
        f"in India and South Asia. "
        f"Always respond in {lang_name}. "
        f"Provide practical, specific, safe, and culturally appropriate advice. "
        f"Keep answers concise, farmer-friendly, and avoid technical jargon. "
        f"Use numbered steps when giving instructions. "
        f"If the farmer is asking about a disease, always recommend: "
        f"(1) identify the pathogen, (2) remove infected material, (3) apply appropriate fungicide/pesticide, "
        f"(4) adjust irrigation, (5) monitor and follow up."
    )

    user_message = req.query
    if req.context:
        user_message = f"Field context: {req.context}\n\nFarmer's question: {req.query}"

    # ૧. નવી SDK (google-genai) સાથે ટ્રાય કરો
    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=settings.GEMINI_API_KEY)

        # એક્ઝેક્ટ મોડલ નામ ફોર્મેટ
        model_id = settings.GEMINI_MODEL
        if not model_id.startswith("models/"):
            model_id = f"models/{model_id}"

        response = await client.aio.models.generate_content(
            model=model_id,
            contents=user_message,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.4,
                max_output_tokens=700,
            ),
        )
        if response and response.text:
            return response.text.strip()
    except Exception as exc:
        logger.warning("google-genai SDK call failed: %s — trying fallback HTTP call", exc)

    # ૨. ડાયરેક્ટ HTTP REST API Fallback (SDK ઇશ્યુ હોય તો પણ ૧૦૦% કામ કરશે)
    try:
        import httpx
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.GEMINI_MODEL}:generateContent?key={settings.GEMINI_API_KEY}"
        payload = {
            "contents": [{
                "parts": [{"text": f"{system_instruction}\n\n{user_message}"}]
            }],
            "generationConfig": {
                "temperature": 0.4,
                "maxOutputTokens": 700
            }
        }
        async with httpx.AsyncClient(timeout=15.0) as http_client:
            res = await http_client.post(url, json=payload)
            if res.status_code == 200:
                data = res.json()
                return data["candidates"][0]["content"]["parts"][0]["text"].strip()
            else:
                logger.error("Direct Gemini REST call failed with status %s: %s", res.status_code, res.text)
    except Exception as exc:
        logger.error("Direct REST call exception: %s", exc)

    return ""

# =========================================================================== #
#  Endpoint
# =========================================================================== #

@router.post(
    "/query",
    response_model=AssistantResponse,
    status_code=status.HTTP_200_OK,
    summary="Ask the AI farmer assistant",
    description=(
        "Submit a natural-language question or problem description. "
        "Optionally include a `context` field to ground the response "
        "(e.g. the disease class returned by the prediction endpoint).\n\n"
        "**AI Backend:** Google Gemini (set `GEMINI_API_KEY` in `.env`). "
        "Falls back to built-in rule engine when key is absent.\n\n"
        "**Supported languages:** en · hi · te · ta · kn · mr · bn · pa · gu"
    ),
    responses={
        200: {"description": "Assistant response generated", "model": AssistantResponse},
        422: {"description": "Validation error"},
        500: {"description": "Assistant engine error"},
    },
)
async def query_assistant(req: AssistantRequest) -> AssistantResponse:
    try:
        # ── Try Gemini first ────────────────────────────────────────────────
        gemini_answer = await _call_gemini(req)

        if gemini_answer:
            answer = gemini_answer
            follow_ups = [
                "Is there anything specific about this advice you'd like me to expand on?",
                "Would you like information about alternative treatment options?",
                "Do you need guidance in a different language?",
            ]
            sources: List[AssistantSource] = []
            powered_by = f"Google Gemini ({settings.GEMINI_MODEL})"
            confidence = "high"
        else:
            # ── Fall back to mock engine ────────────────────────────────────
            answer, follow_ups, sources = _mock_engine(req)
            powered_by = "AgriSmart AI Mock Engine"
            confidence = "medium"

    except Exception as exc:
        logger.exception("Assistant query failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "ASSISTANT_ENGINE_ERROR",
                "message": "The assistant encountered an unexpected error.",
                "detail": str(exc),
            },
        ) from exc

    logger.info(
        "Assistant: lang=%s engine=%s query_len=%d",
        req.language.value, powered_by, len(req.query),
    )

    return AssistantResponse(
        answer=answer,
        language=req.language.value,
        follow_up_questions=follow_ups,
        sources=sources,
        confidence=confidence,
        powered_by=powered_by,
    )
