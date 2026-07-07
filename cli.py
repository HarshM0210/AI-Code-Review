import argparse
import sys
import os
from pipeline import run_pipeline

def main():
    parser = argparse.ArgumentParser(description="AI Code Review Team - CLI Utility")
    parser.add_argument("file", help="Path to the file to review")
    parser.add_argument("-l", "--language", help="Programming language of the code (default: auto-detect from extension)")
    args = parser.parse_args()

    if not os.path.exists(args.file):
        print(f"Error: File not found at {args.file}", file=sys.stderr)
        sys.exit(1)

    try:
        with open(args.file, "r", encoding="utf-8") as f:
            code_content = f.read()
    except Exception as e:
        print(f"Error: Failed to read file {args.file}: {e}", file=sys.stderr)
        sys.exit(1)

    # Determine language
    language = args.language
    if not language:
        ext = os.path.splitext(args.file)[1].lower()
        ext_map = {
            ".py": "Python",
            ".java": "Java",
            ".cpp": "C++",
            ".cc": "C++",
            ".c": "C++",
            ".h": "C++",
            ".js": "JavaScript",
            ".ts": "TypeScript",
        }
        language = ext_map.get(ext, "Python")

    print(f"Reviewing {args.file} as {language} code...")
    
    try:
        results = run_pipeline(code_content, language)
        report_path = results.get("report_path")
        if report_path and os.path.exists(report_path):
            print(f"\nReview complete! Consolidating findings...")
            print(f"Full report generated at: {report_path}")
            
            # Print a clean summary to the terminal
            doc_report = results.get("documentation", {})
            print("\n" + "="*50)
            print("             AI Code Review Summary             ")
            print("="*50)
            print(f"Overall Code Quality Score: {doc_report.get('code_quality_score', 'N/A')}/10")
            print(f"Summary: {doc_report.get('summary', 'No summary generated.')}")
            
            bugs = results.get("bug_report", {}).get("bugs", [])
            print(f"\nBugs Detected: {len(bugs)}")
            for b in bugs:
                print(f"  - [Line {b.get('line')}] ({b.get('severity', '').upper()}): {b.get('description')}")
                
            sec = results.get("security_report", {}).get("security_issues", [])
            print(f"\nSecurity Issues: {len(sec)}")
            for s in sec:
                print(f"  - [{s.get('severity', '').upper()}] {s.get('risk')}: {s.get('recommendation')}")
                
            perf = results.get("performance_report", {}).get("performance", [])
            print(f"\nPerformance Bottlenecks: {len(perf)}")
            for p in perf:
                print(f"  - [{p.get('impact', '').upper()} Impact] {p.get('issue')}: {p.get('optimization')}")
            print("="*50)
        else:
            print("Error: Pipeline finished but report file was not generated.", file=sys.stderr)
            sys.exit(1)
    except Exception as e:
        print(f"Error during code review: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
