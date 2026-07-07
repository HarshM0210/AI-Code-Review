import os
from datetime import datetime

REPORT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "reports")

def generate_markdown_report(
    code_hash: str, 
    bug_report: dict, 
    security_report: dict, 
    performance_report: dict, 
    documentation: dict
) -> str:
    """
    Generates a consolidated Markdown report from all agent outputs.
    Returns the absolute path to the generated report file.
    """
    if not os.path.exists(REPORT_DIR):
        os.makedirs(REPORT_DIR, exist_ok=True)
        
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_filename = f"review_report_{code_hash}_{timestamp}.md"
    report_path = os.path.join(REPORT_DIR, report_filename)
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# AI Code Review Report\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # Overview & Documentation
        f.write("## 1. Overview\n")
        if "error" in documentation:
            f.write(f"**Error analyzing documentation:** {documentation['error']}\n\n")
        else:
            f.write(f"**Summary:** {documentation.get('summary', 'N/A')}\n\n")
            f.write(f"**Code Quality Score:** {documentation.get('code_quality_score', 'N/A')}/10\n\n")
        
        # Bug Detection
        f.write("## 2. Bug Detection\n")
        if "error" in bug_report:
            f.write(f"**Error during bug analysis:** {bug_report['error']}\n\n")
        else:
            bugs = bug_report.get("bugs", [])
            if not bugs:
                f.write("No bugs detected.\n\n")
            else:
                for b in bugs:
                    f.write(f"- **Line {b.get('line', 'N/A')}** [{str(b.get('severity', '')).upper()}]: {b.get('description', '')}\n")
                    f.write(f"  - *Fix:* {b.get('fix', '')}\n")
                f.write("\n")
            
        # Security Analysis
        f.write("## 3. Security Analysis\n")
        if "error" in security_report:
            f.write(f"**Error during security analysis:** {security_report['error']}\n\n")
        else:
            security_issues = security_report.get("security_issues", [])
            if not security_issues:
                f.write("No security issues detected.\n\n")
            else:
                for s in security_issues:
                    f.write(f"- **{s.get('risk', 'Issue')}** [{str(s.get('severity', '')).upper()}]: {s.get('recommendation', '')}\n")
                f.write("\n")
            
        # Performance Analysis
        f.write("## 4. Performance Analysis\n")
        if "error" in performance_report:
            f.write(f"**Error during performance analysis:** {performance_report['error']}\n\n")
        else:
            performance = performance_report.get("performance", [])
            if not performance:
                f.write("No performance issues detected.\n\n")
            else:
                for p in performance:
                    f.write(f"- **Issue:** {p.get('issue', '')} [{str(p.get('impact', '')).upper()} Impact]\n")
                    f.write(f"  - *Optimization:* {p.get('optimization', '')}\n")
                f.write("\n")
            
        # Best Practices
        f.write("## 5. Best Practices & Documentation Suggestions\n")
        if "error" not in documentation:
            best_practices = documentation.get("best_practices", [])
            if best_practices:
                f.write("### Best Practices\n")
                for bp in best_practices:
                    f.write(f"- {bp}\n")
                f.write("\n")
                
            docs = documentation.get("documentation", [])
            if docs:
                f.write("### Documentation Suggestions\n")
                for d in docs:
                    f.write(f"- {d}\n")
                
    return report_path
