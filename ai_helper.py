"""ai_helper.py — Gemini AI integration for PawPal+"""

import logging
from google import generativeai as genai

logging.basicConfig(filename="pawpal.log", level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(message)s")

BLOCKED_TERMS = ["harm", "kill", "hurt", "abuse", "neglect"]
MODEL_FALLBACKS = [
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-1.5-flash-latest",
    "gemini-1.5-flash-8b",
    "gemini-1.5-pro-latest",
]


def _discover_supported_model(preferred: str | None = None) -> str | None:
    """Pick a model that supports generateContent for the current API key."""
    try:
        available: list[str] = []
        for m in genai.list_models():
            methods = getattr(m, "supported_generation_methods", []) or []
            if "generateContent" not in methods:
                continue
            name = getattr(m, "name", "")
            if name.startswith("models/"):
                name = name.split("/", 1)[1]
            if name:
                available.append(name)

        if not available:
            return preferred

        if preferred and preferred in available:
            return preferred

        for candidate in MODEL_FALLBACKS:
            if candidate in available:
                return candidate

        flash_models = [m for m in available if "flash" in m]
        if flash_models:
            return flash_models[0]

        return available[0]
    except Exception as e:
        logging.warning("Model discovery failed, using fallback list: %s", e)
        return preferred

def validate_input(title: str, duration: int) -> tuple[bool, str]:
    """Guardrail: block unsafe or malformed task inputs."""
    if not title or len(title.strip()) < 2:
        return False, "Task title too short."
    if any(bad in title.lower() for bad in BLOCKED_TERMS):
        return False, "Task title contains a disallowed term."
    if not (1 <= duration <= 480):
        return False, "Duration must be 1–480 minutes."
    logging.info("GUARDRAIL PASSED: task='%s' duration=%d", title, duration)
    return True, "ok"

def _ask_gemini(api_key: str, prompt: str) -> str:
    genai.configure(api_key=api_key)
    preferred = _discover_supported_model(preferred="gemini-2.5-flash")

    candidates: list[str] = []
    for candidate in [preferred, *MODEL_FALLBACKS]:
        if candidate and candidate not in candidates:
            candidates.append(candidate)

    last_error: Exception | None = None
    for model_name in candidates:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            logging.info("Gemini call succeeded using model=%s", model_name)
            return response.text
        except Exception as e:
            last_error = e
            logging.warning("Gemini model attempt failed for model=%s error=%s", model_name, e)
            continue

    logging.error("Gemini error after trying models %s: %s", candidates, last_error)
    return f"Error: {last_error}"

def get_schedule_advice(api_key: str, pet_name: str, species: str, tasks: list[dict]) -> str:
    task_list = "\n".join(
        f"- {t['title']} ({t['duration_minutes']} min, {t['priority']} priority, {t['time']})"
        for t in tasks
    )
    prompt = (
        f"I have a {species} named {pet_name}. Today's care tasks:\n{task_list}\n\n"
        "In 3-4 sentences, recommend the best order for these tasks and briefly explain why. Be practical."
    )
    return _ask_gemini(api_key, prompt)

def check_welfare(api_key: str, pet_name: str, species: str, tasks: list[dict]) -> str:
    task_list = "\n".join(f"- {t['title']}" for t in tasks)
    prompt = (
        f"Care tasks planned for {pet_name}, a {species}:\n{task_list}\n\n"
        "In 2-3 sentences, flag any animal welfare concerns or missing essential care. Be direct."
    )
    return _ask_gemini(api_key, prompt)
