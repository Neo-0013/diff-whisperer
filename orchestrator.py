import time
import json
import os
from google.api_core import exceptions as google_exceptions
from models import AnalysisResponse
from utils import extract_json_from_text
from config import MODEL_31B, MODEL_26B

class ReasoningOrchestrator:
    """Handles the multi-stage reasoning pipeline and LLM orchestration."""
    
    def __init__(self, client):
        self.client = client

    def generate_with_retry(self, model_name, system_prompt, user_prompt, retries=5, mime_type="application/json"):
        """Generates content with universal exponential backoff retry logic."""
        for i in range(retries):
            try:
                return self.client.models.generate_content(
                    model=model_name,
                    config={
                        "system_instruction": system_prompt,
                        "response_mime_type": mime_type
                    },
                    contents=user_prompt
                )
            except Exception as e:
                error_str = str(e).upper()
                is_transient = any(code in error_str for code in ["500", "503", "429", "INTERNAL", "OVERLOADED"])
                
                if is_transient and i < retries - 1:
                    wait_time = (2 ** i) + 3
                    time.sleep(wait_time)
                else:
                    raise e

    def run_standard_pipeline(self, model_to_use, persona, diff_text):
        """Runs a single-stage narrative generation."""
        user_prompt = f"Analyze this git diff and return a JSON object. Ensure the JSON strictly follows the schema with 'story', 'risks' (each with category, description, level), and 'improvements'.\n\n<git_diff>\n{diff_text}\n</git_diff>"
        response = self.generate_with_retry(model_to_use, persona["system_prompt"], user_prompt)
        data = extract_json_from_text(response.text)
        return AnalysisResponse(**data).model_dump()

    def run_deep_pipeline(self, model_to_use, persona, diff_text, progress_callback=None):
        """Runs the multi-stage reasoning pipeline (Extraction -> Audit -> Synthesis)."""
        
        # Stage 1: Technical Extraction
        if progress_callback: progress_callback("[Stage 1/3] Extracting technical essence...")
        extract_prompt = "You are a technical analyst. Summarize the following git diff precisely. Focus on modified functions, logic changes, and dependencies."
        extraction_resp = self.generate_with_retry(model_to_use, extract_prompt, f"<git_diff>\n{diff_text}\n</git_diff>", mime_type="text/plain")
        tech_summary = extraction_resp.text
        time.sleep(1) 
        
        # Stage 2: Security & Risk Critique
        if progress_callback: progress_callback("[Stage 2/3] Auditing for risks & blind spots...")
        critique_prompt = """You are a security and architecture auditor. Analyze the technical summary and original diff for risks. 
        Return a JSON object with a 'risks' list (each item: {category, description, level})."""
        critique_user_prompt = f"Technical Summary: {tech_summary}\n\nOriginal Diff:\n<git_diff>\n{diff_text}\n</git_diff>"
        critique_resp = self.generate_with_retry(model_to_use, critique_prompt, critique_user_prompt)
        risks_data = extract_json_from_text(critique_resp.text)
        time.sleep(1)
        
        # Stage 3: Persona-Based Synthesis
        if progress_callback: progress_callback(f"[Stage 3/3] {persona['name']} is synthesizing the story...")
        synthesis_prompt = f"{persona['system_prompt']}\nUsing the technical summary and risk assessment, synthesize a final narrative and suggestions. Return JSON with 'story' and 'improvements' (list)."
        synthesis_user_prompt = f"Technical Summary: {tech_summary}\n\nRisk Assessment: {json.dumps(risks_data.get('risks', []))}"
        synthesis_resp = self.generate_with_retry(model_to_use, synthesis_prompt, synthesis_user_prompt)
        synthesis_data = extract_json_from_text(synthesis_resp.text)
        
        final_data = {
            "story": synthesis_data.get("story", "No story generated."),
            "risks": risks_data.get("risks", []),
            "improvements": synthesis_data.get("improvements", [])
        }
        return AnalysisResponse(**final_data).model_dump()

    def run_fallback_pipeline(self, persona, diff_text):
        """Emergency fallback to 26B model if 31B fails."""
        fallback_model = os.getenv("GEMMA_MODEL_26B", MODEL_26B)
        fallback_prompt = f"Analyze this git diff and return a JSON object with 'story', 'risks', and 'improvements'.\n\n<git_diff>\n{diff_text}\n</git_diff>"
        response = self.generate_with_retry(fallback_model, persona["system_prompt"], fallback_prompt)
        data = extract_json_from_text(response.text)
        return AnalysisResponse(**data).model_dump()
