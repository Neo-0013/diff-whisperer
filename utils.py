import re
import json

def extract_json_from_text(text: str) -> dict:
    """
    Strips markdown code blocks and extracts the first valid JSON object found in the text.
    """
    # Try to find content between ```json and ```
    json_block_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if json_block_match:
        text = json_block_match.group(1)
    
    # Alternatively, find the first '{' and the last '}'
    start_index = text.find('{')
    end_index = text.rfind('}')
    
    if start_index != -1 and end_index != -1:
        json_str = text[start_index:end_index+1]
        # Clean trailing commas inside arrays and objects
        json_str = re.sub(r',\s*([\]}])', r'\1', json_str)
        # Fix invalid JSON escape sequences (unescaped backslashes)
        json_str = re.sub(r'\\(?!["\\/bfnrt]|u[0-9a-fA-F]{4})', r'\\\\', json_str)
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            pass
            
    # If all else fails, try loading the whole string
    try:
        cleaned_text = re.sub(r',\s*([\]}])', r'\1', text)
        cleaned_text = re.sub(r'\\(?!["\\/bfnrt]|u[0-9a-fA-F]{4})', r'\\\\', cleaned_text)
        return json.loads(cleaned_text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to extract valid JSON from LLM response: {e}\nResponse text: {text[:200]}...")


