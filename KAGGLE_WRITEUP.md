# Kaggle AI Agents Capstone Submission Writeup

## Title & Subtitle
* **Title**: AI Code Review Team: Coordinated Multi-Agent Software Quality & Analysis Assistant
* **Subtitle**: An intelligent developer productivity assistant that orchestrates specialized AI agents to automate bug detection, security audits, performance profiling, and documentation compilation.

## Track Selection
* **Track**: Concierge Agents (Developer tools and productivity workflow enhancement)

---

## 🔍 Problem Statement
Manual code reviews are an essential part of the modern software development lifecycle (SDLC), yet they present significant friction points:
1. **High Overhead & Delay**: Waiting for senior developers to review code introduces bottlenecks and slows down shipping velocity.
2. **Cognitive Fatigue & Human Oversight**: Reviewing large diffs is mentally taxing. Security flaws, subtle bugs, and edge cases are frequently overlooked during manual checks.
3. **Inconsistent Review Quality**: Review comments vary heavily based on a reviewer's expertise, fatigue, or focus areas (e.g., a reviewer might focus on logical bugs but miss security vulnerabilities or optimization opportunities).
4. **Lack of Instant Feedback**: Developers often have to wait hours or days for review feedback, forcing them to switch context multiple times.

---

## 💡 Solution
The **AI Code Review Team** is a developer concierge system that acts as a virtual panel of senior software engineers checking code in parallel. When a developer submits a code file, the system routes it to specialized, independent AI agents:
1. **Bug Detector**: Evaluates code correctness and logic.
2. **Security Analyst**: Identifies vulnerabilities, insecure imports, and credential exposure.
3. **Performance Profiler**: Spots expensive operations and optimization opportunities.
4. **Documentation Architect**: Reviews styling, generates summaries, and highlights missing docstrings.

The system compiles their parallel JSON reviews into a single consolidated, executive-level Markdown report. By offering both an **interactive Web UI** for manual reviews and a **CLI Skill** for developer scripts, it provides instant, comprehensive feedback on demand.

---

## Architecture

The application is built on a **Worker-Coordinator Agent Pattern** to ensure high cohesion, low coupling, and easy extensibility.

### 1. Architectural Diagram

```
                 +-----------------------+
                 |   Developer Input     |
                 | (Web Dashboard / CLI) |
                 +-----------+-----------+
                             |
                             v
                 +-----------------------+
                 |   Coordinator Agent   | <--- MD5 Cache Hashing
                 |     (pipeline.py)     |
                 +-----------+-----------+
                             |
         +-------------------+-------------------+
         |                   |                   |
         v                   v                   v
 +---------------+   +---------------+   +---------------+
 |   Bug Agent   |   | SecurityAgent |   |  Perf Agent   | ... (Doc Agent)
 | (bug_agent.py)|   | (sec_agent.py)|   |(perf_agent.py)|
 +-------+-------+   +-------+-------+   +-------+-------+
         |                   |                   |
         +-------------------+-------------------+
                             |
                             v (Structured JSONs)
                 +-----------------------+
                 |   Report Generator    |
                 | (report_generator.py) |
                 +-----------+-----------+
                             |
                             v
                 +-----------------------+
                 |  Consolidated Report  |
                 |    (Markdown File)    |
                 +-----------------------+
```

### 2. Core Components
* **Coordinator Agent (`pipeline.py`)**: Computes an MD5 hash of the input code and language. It queries the cache layer; if there is a cache miss, it triggers the specialized agents sequentially, parses their individual JSON outputs, and forwards them to the report generator.
* **Specialized Agent Workers (`tools/*_agent.py`)**: Each agent possesses a narrow, specialized system instruction prompting the LLM to analyze the code from a single perspective (e.g., security only) and output structured JSON matching a strict schema.
* **LLM Engine Wrapper (`tools/gemini_utils.py`)**: Encapsulates Gemini API communication using the new `google-genai` SDK, applying a robust retries utility with exponential backoff to handle rate limits or API errors gracefully.
* **Cache System (`tools/cache_utils.py`)**: Hashes the combination of language and code to read/write local review cache files, optimizing API costs and speeding up review iteration.
* **Report Writer (`tools/report_generator.py`)**: Combines the structured data into a professional markdown template, calculating a weighted code quality score and outputting a timestamped report file.

---

## Technical Implementation & Course Concepts

This capstone project implements **four** core concepts taught in the **Kaggle AI Agents: Intensive Vibe Coding** course:

### 1. Multi-Agent Systems (ADK Pattern)
Instead of relying on a single monolithic prompt to handle bugs, security, performance, and documentation simultaneously, which leads to prompt dilution, missed checks, and high context rot—the system implements the ADK worker-coordinator pattern. Each agent has its own isolated prompt and JSON output schema. The coordinator acts as the workflow engine, sequencing execution and managing data flow.

### 2. Security and Safe Practices
The codebase incorporates secure software practices:
* **Secrets Isolation**: API keys are handled using environment variables loaded via `python-dotenv`. A robust `.gitignore` ensures that local `.env` keys, reports, and run caches are never committed to version control.
* **Dedicated Audit**: A specialized `Security Agent` is dedicated strictly to auditing the submitted code for OWASP top 10 vulnerabilities, insecure defaults, and exposed keys.
* **Safe JSON Extraction**: A utility parsing function strips markdown wrappers (` ```json ` blocks) and uses standard JSON loading to guarantee program stability.

### 3. Agent Skills (CLI Utility)
The project demonstrates the **Agent Skills (CLI)** concept by providing a terminal script (`cli.py`). The script acts as a command-line skill, enabling developers to run code reviews directly from shell commands. It supports file path arguments, auto-detects programming languages via file extensions, runs the multi-agent pipeline, prints a concise stdout summary, and returns the path to the detailed generated markdown report. This CLI integration allows the reviewer to be called by other automated agents or git hook scripts.

### 4. Deployability
The design cleanly separates the frontend view (`app.py` using Streamlit) from the underlying pipeline engine (`pipeline.py`). Since the pipeline relies on standard JSON exchanges and local directory storage, it can be deployed seamlessly to any host environment. The web application is fully prepared for local execution, Streamlit Community Cloud hosting, or dockerization for Google Cloud Run.

---

## Verification and Validation
To verify the application, we run the tool against its own codebase.
1. **CLI Execution Test**:
   ```bash
   python cli.py cli.py
   ```
   **Output Summary**:
   - The CLI successfully detects the code as Python.
   - It runs the 4 agents, showing cache hits or generating calls.
   - It outputs a consolidated Markdown report under `reports/review_report_*.md`.
   - It prints a clean summary to standard output, detailing the overall quality score (9/10), summarizing the code, and confirming that no bugs or security issues were detected.

2. **Web Dashboard Execution Test**:
   - Running `streamlit run app.py` launches the UI correctly.
   - Pasting a faulty code snippet (e.g., Python code with syntax errors or hardcoded API keys) successfully triggers error tags, warning boxes, and score reductions.
   - A download button is rendered, allowing the user to download the generated markdown file.

---

## Future Work
1. **GitHub Actions / Git Hooks**: Create a pre-commit hook that runs `cli.py` locally, preventing buggy or insecure code from being committed. Combine this with a GitHub Action to post code reviews directly as Pull Request comments.
2. **Exposing an MCP Server**: Implement the Model Context Protocol (MCP) to expose this multi-agent code reviewer as a tool that other agents (such as Antigravity or Cursor agents) can call dynamically inside their workspace.
3. **Repository-Level Context**: Upgrade the coordinator to inspect full directory structures, building a repository dependency map to perform codebase-wide impact reviews instead of single-file analyses.
