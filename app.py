import streamlit as st
import os
from pipeline import run_pipeline

# Configure the Streamlit page
st.set_page_config(page_title="AI Code Review Team", layout="wide")

# Header Section
st.title("AI Code Review Team 🚀")
st.subheader("Multi-Agent Software Engineering Assistant")
st.markdown("---")

# Main Interface
col1, col2 = st.columns([3, 1])

with col1:
    st.markdown("### Source Code")
    code_input = st.text_area("Paste your code here for review:", height=400, label_visibility="collapsed")
    
with col2:
    st.markdown("### Settings")
    language = st.selectbox("Programming Language", ["Python", "Java", "C++", "JavaScript"])
    
    st.markdown("<br>", unsafe_allow_html=True)
    review_button = st.button("Review Code", type="primary", use_container_width=True)

# Process Review
if review_button:
    if not code_input.strip():
        st.warning("Please enter some code to review.")
    else:
        with st.spinner(f"The AI Team is reviewing your {language} code..."):
            try:
                # Call pipeline (No AI logic resides here)
                results = run_pipeline(code_input, language)
                
                st.success("Code Review Complete!")
                
                st.markdown("---")
                
                # Top-level metrics
                if "error" in results["documentation"]:
                    st.error(f"Error checking code quality: {results['documentation']['error']}")
                else:
                    score = results["documentation"].get("code_quality_score", "N/A")
                    st.metric(label="Overall Code Quality Score", value=f"{score} / 10")
                
                # Create tabs for structured reports
                tab_bug, tab_sec, tab_perf, tab_doc = st.tabs([
                    "🐛 Bug Report", 
                    "🔒 Security Analysis", 
                    "⚡ Performance Analysis", 
                    "📝 Documentation & Quality"
                ])
                
                with tab_bug:
                    if "error" in results["bug_report"]:
                        st.error(f"Failed to analyze bugs: {results['bug_report']['error']}")
                    else:
                        bugs = results["bug_report"].get("bugs", [])
                        if not bugs:
                            st.success("No bugs detected! Great job.")
                        else:
                            for b in bugs:
                                st.error(f"**Line {b.get('line', 'N/A')} [{str(b.get('severity')).upper()}]**: {b.get('description')}")
                                st.markdown(f"> *Suggested Fix:* {b.get('fix')}")
                                
                with tab_sec:
                    if "error" in results["security_report"]:
                        st.error(f"Failed to analyze security: {results['security_report']['error']}")
                    else:
                        security = results["security_report"].get("security_issues", [])
                        if not security:
                            st.success("No security issues detected! Safe and secure.")
                        else:
                            for s in security:
                                st.warning(f"**{s.get('risk')} [{str(s.get('severity')).upper()}]**: {s.get('recommendation')}")
                                
                with tab_perf:
                    if "error" in results["performance_report"]:
                        st.error(f"Failed to analyze performance: {results['performance_report']['error']}")
                    else:
                        performance = results["performance_report"].get("performance", [])
                        if not performance:
                            st.success("No obvious performance bottlenecks detected!")
                        else:
                            for p in performance:
                                st.info(f"**Issue**: {p.get('issue')} [{str(p.get('impact')).upper()} Impact]")
                                st.markdown(f"> *Optimization:* {p.get('optimization')}")
                                
                with tab_doc:
                    if "error" in results["documentation"]:
                        st.error(f"Failed to fetch documentation suggestions: {results['documentation']['error']}")
                    else:
                        summary = results["documentation"].get("summary", "")
                        if summary:
                            st.markdown(f"**Code Summary:** {summary}")
                            
                        st.markdown("#### Best Practices")
                        bps = results["documentation"].get("best_practices", [])
                        if bps:
                            for bp in bps:
                                st.markdown(f"- {bp}")
                        else:
                            st.markdown("_No specific best practices suggested._")
                            
                        st.markdown("#### Documentation Suggestions")
                        docs = results["documentation"].get("documentation", [])
                        if docs:
                            for d in docs:
                                st.markdown(f"- {d}")
                        else:
                            st.markdown("_Code seems well-documented._")
                
                st.markdown("---")
                
                # Download Report Button
                report_path = results.get("report_path")
                if report_path and os.path.exists(report_path):
                    with open(report_path, "r", encoding="utf-8") as f:
                        md_data = f.read()
                        
                    st.download_button(
                        label="📄 Download Full Review Report",
                        data=md_data,
                        file_name=os.path.basename(report_path),
                        mime="text/markdown",
                        type="primary"
                    )
                    
            except Exception as e:
                st.error(f"An unexpected error occurred during execution: {str(e)}")
