import json
from tools import bug_agent, security_agent, performance_agent, documentation_agent, report_generator, cache_utils

def run_agent(agent_name: str, agent_module, code: str, language: str, code_hash: str) -> dict:
    """
    Executes a specific agent on the code, using cache if available.
    """
    # The cache hash now represents both code and language
    cached = cache_utils.get_cached_result(agent_name, code_hash)
    if cached is not None:
        return cached
        
    input_json = json.dumps({"code": code, "language": language})
    result_str = agent_module.analyze(input_json)
    
    try:
        result = json.loads(result_str)
    except json.JSONDecodeError:
        result = {"error": f"Invalid output from {agent_name} agent."}
        
    cache_utils.set_cached_result(agent_name, code_hash, result)
    return result

def run_pipeline(code: str, language: str = "Python") -> dict:
    """
    Orchestrates the entire AI Code Review pipeline.
    Returns a dictionary containing all individual reports and the final report path.
    """
    # Hash includes language to prevent cross-language cache collision on identical text
    code_hash = cache_utils.get_code_hash(f"{language}_{code}")
    
    # Run all agents sequentially
    bug_report = run_agent("bug", bug_agent, code, language, code_hash)
    security_report = run_agent("security", security_agent, code, language, code_hash)
    performance_report = run_agent("performance", performance_agent, code, language, code_hash)
    documentation = run_agent("documentation", documentation_agent, code, language, code_hash)
    
    # Compile the final physical report
    report_path = report_generator.generate_markdown_report(
        code_hash=code_hash, 
        bug_report=bug_report, 
        security_report=security_report, 
        performance_report=performance_report, 
        documentation=documentation
    )
    
    return {
        "bug_report": bug_report,
        "security_report": security_report,
        "performance_report": performance_report,
        "documentation": documentation,
        "report_path": report_path
    }
