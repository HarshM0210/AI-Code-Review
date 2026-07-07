import json
from .gemini_utils import generate_with_retry, parse_json_safely

SYSTEM_PROMPT = """You are an expert Documentation and Code Quality Agent.
Your task is to analyze the provided code, summarize it, score its quality, and suggest best practices and documentation improvements.
You must return your findings in the exact JSON format requested, without any other text.

Format:
{
    "summary":"<brief summary of what the code does>",
    "code_quality_score":"<score out of 10 as string>",
    "best_practices":["<practice 1>", "<practice 2>"],
    "documentation":["<doc suggestion 1>", "<doc suggestion 2>"]
}"""

def analyze(input_json_str: str) -> str:
    """
    Receives JSON containing code, returns JSON containing documentation analysis.
    """
    try:
        input_data = json.loads(input_json_str)
        code = input_data.get("code", "")
        language = input_data.get("language", "Unknown")
    except json.JSONDecodeError:
        return json.dumps({"error": "Invalid input JSON"})
        
    prompt = f"Analyze this {language} code for documentation and quality:\n\n{code}"
    
    try:
        raw_response = generate_with_retry(prompt, system_instruction=SYSTEM_PROMPT)
        result_dict = parse_json_safely(raw_response)
    except Exception as e:
        result_dict = {"error": str(e)}
        
    return json.dumps(result_dict)
