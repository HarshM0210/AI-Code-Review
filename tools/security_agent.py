import json
from .gemini_utils import generate_with_retry, parse_json_safely

SYSTEM_PROMPT = """You are an expert Security Analysis Agent.
Your task is to analyze the provided code and identify security vulnerabilities.
You must return your findings in the exact JSON format requested, without any other text.

Format:
{
    "security_issues":[
        {
            "risk":"<vulnerability name/type>",
            "severity":"<low|medium|high|critical>",
            "recommendation":"<how to fix it>"
        }
    ]
}"""

def analyze(input_json_str: str) -> str:
    """
    Receives JSON containing code, returns JSON containing security issues.
    """
    try:
        input_data = json.loads(input_json_str)
        code = input_data.get("code", "")
        language = input_data.get("language", "Unknown")
    except json.JSONDecodeError:
        return json.dumps({"error": "Invalid input JSON"})
        
    prompt = f"Analyze this {language} code for security issues:\n\n{code}"
    
    try:
        raw_response = generate_with_retry(prompt, system_instruction=SYSTEM_PROMPT)
        result_dict = parse_json_safely(raw_response)
    except Exception as e:
        result_dict = {"error": str(e)}
        
    return json.dumps(result_dict)
