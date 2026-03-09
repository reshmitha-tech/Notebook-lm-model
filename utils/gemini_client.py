"""
gemini_client.py - Handles all interactions with the Google Gemini API.
"""
import json
import re
import google.generativeai as genai
import os


def _clean_json_response(text: str) -> str:
    """Strip markdown code fences from Gemini JSON responses."""
    text = text.strip()
    # Remove ```json ... ``` or ``` ... ``` fences
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"\s*```$", "", text, flags=re.MULTILINE)
    return text.strip()


def configure_gemini(api_key: str):
    """Configure the Gemini SDK with an API key."""
    genai.configure(api_key=api_key)


def analyze_pdf_content(text: str, api_key: str) -> dict:
    """
    Send extracted PDF text to Gemini and get structured learning content.
    
    Returns a dict with:
      - summary (str): 6-sentence paragraph summary
      - key_concepts (list): 5 objects {term, definition}
      - mcqs (list): 5 objects {question, options[4], answer}
      - subject_tags (list): subject labels e.g. ["Mathematics", "Physics"]
      - is_stem (bool): True if Math/Science detected
      - manim_snippet (str|null): Manim Python code for formulas if STEM
    """
    configure_gemini(api_key)
    model = genai.GenerativeModel("gemini-flash-latest")

    # Truncate very long texts to avoid token limit
    truncated_text = text[:12000] if len(text) > 12000 else text

    prompt = f"""You are an expert educational AI. Analyze the following document text and return a structured JSON response.

DOCUMENT TEXT:
{truncated_text}

Return ONLY valid JSON (no markdown, no code fences) with this exact structure:
{{
  "summary": "A comprehensive 6-sentence summary of the document covering the main topic, key arguments, important details, conclusions, and real-world significance.",
  "key_concepts": [
    {{"term": "Concept Name", "definition": "Clear 1-2 sentence definition or explanation"}},
    {{"term": "Concept Name", "definition": "Clear 1-2 sentence definition or explanation"}},
    {{"term": "Concept Name", "definition": "Clear 1-2 sentence definition or explanation"}},
    {{"term": "Concept Name", "definition": "Clear 1-2 sentence definition or explanation"}},
    {{"term": "Concept Name", "definition": "Clear 1-2 sentence definition or explanation"}}
  ],
  "mcqs": [
    {{
      "question": "Question text here?",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "answer": "Option A"
    }},
    {{
      "question": "Question text here?",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "answer": "Option B"
    }},
    {{
      "question": "Question text here?",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "answer": "Option C"
    }},
    {{
      "question": "Question text here?",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "answer": "Option D"
    }},
    {{
      "question": "Question text here?",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "answer": "Option A"
    }}
  ],
  "subject_tags": ["Tag1", "Tag2", "Tag3"],
  "is_stem": false,
  "manim_snippet": null
}}

CRITICAL RULES:
1. If the document contains Mathematics, Physics, Chemistry, or Engineering formulas, set is_stem to true and provide a valid Manim Python code snippet in manim_snippet that animates 2-3 key formulas from the document.
2. For non-STEM subjects, set is_stem to false and manim_snippet to null.
3. Make MCQ options realistic and plausible, with exactly one correct answer matching the "answer" field.
4. Subject tags should be concise single words or short phrases (e.g., "Machine Learning", "Biology", "History").
5. Return ONLY the JSON object, nothing else.
"""

    import time
    for attempt in range(3):
        try:
            response = model.generate_content(prompt)
            break
        except Exception as e:
            if "429" in str(e) or "503" in str(e):
                time.sleep(2 ** attempt)  # Simple backoff
                continue
            raise e
    else:
        raise RuntimeError("Gemini quota exceeded after retries. Please wait a minute and try again.")

    raw = response.text
    cleaned = _clean_json_response(raw)
    
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        # Try to extract JSON from the response
        json_match = re.search(r'\{.*\}', cleaned, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group())
        else:
            raise ValueError(f"Could not parse Gemini JSON response: {cleaned[:500]}")
    
    return data


def chat_with_context(question: str, document_text: str, history: list, api_key: str) -> str:
    """
    Answer a user question in the context of the uploaded document.
    
    Args:
        question: User's question
        document_text: The extracted PDF text for context
        history: List of {"role": "user"|"model", "parts": [str]} dicts
        api_key: Gemini API key
    
    Returns:
        AI response string
    """
    configure_gemini(api_key)
    model = genai.GenerativeModel(
        "gemini-flash-latest",
        system_instruction=(
            "You are an expert educational AI assistant. You have access to a document provided by the user. "
            "Answer questions based on the document content. Be concise, accurate, and cite relevant parts when possible. "
            "If the answer is not in the document, say so clearly."
        )
    )

    # Build conversation with document context injected at the start
    context_message = f"[DOCUMENT CONTEXT]\n{document_text[:8000]}\n[END CONTEXT]\n\nUser's question: {question}"
    
    if not history:
        # Fresh conversation
        response = model.generate_content(context_message)
    else:
        # Continue conversation
        chat = model.start_chat(history=history)
        response = chat.send_message(f"Referring to the same document: {question}")

    return response.text
