import re
from engine import ResumeAuditor

def generate_improved_resume(raw_text: str, target_role: str = "", jd: str = "") -> dict:
    auditor = ResumeAuditor(raw_text, target_role=target_role, job_description=jd)
    before_panel = auditor.run_full_panel()
    
    # Extract candidate name and contacts
    lines = [l.strip() for l in raw_text.split("\n") if l.strip()]
    name = lines[0] if lines else "CANDIDATE NAME"
    # Clean markdown if present
    name = re.sub(r'^[#*_\s]+|[#*_\s]+$', '', name)
    
    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', raw_text)
    email = email_match.group(0) if email_match else "[ADD EMAIL]"
    
    phone_match = re.search(r'\+?\d[\d\s-]{8,14}\d', raw_text)
    phone = phone_match.group(0).strip() if phone_match else "[ADD PHONE]"
    
    links = []
    if "github.com" in raw_text.lower():
        gh = re.search(r'(https?://)?github\.com/[a-zA-Z0-9_-]+', raw_text, re.I)
        if gh: links.append(gh.group(0))
    if "linkedin.com" in raw_text.lower():
        li = re.search(r'(https?://)?linkedin\.com/in/[a-zA-Z0-9_-]+', raw_text, re.I)
        if li: links.append(li.group(0))
    if "primuez.in" in raw_text.lower():
        links.append("primuez.in")

    role_title = target_role or "AI Systems & Full-Stack Engineer"
    
    # Compose improved resume
    improved_text = f"""{name.upper()}
{role_title} | {phone} | {email} | {' | '.join(links) if links else '[ADD GITHUB / LINKEDIN]'}

==================================================
PROFESSIONAL SUMMARY
==================================================
Results-driven {role_title} with proven expertise engineering, testing, and deploying production systems. Specializes in end-to-end workflow automation, autonomous agent frameworks, and high-availability API architectures that reduce operational latency by [ADD 85]% and maintain [ADD 99.9]% uptime. Combines deep full-stack technical rigor with commercial awareness to translate technical features into direct business ROI.

==================================================
TECHNICAL SKILLS & COMPETENCIES
==================================================
• Systems & Architecture: Autonomous AI Agents, RAG Pipelines, Multi-Agent Orchestration, Microservices, Production Git Workflows
• Cloud & Infrastructure: Docker, Linux VPS Administration, Reverse Proxies (Traefik/Nginx), CI/CD Automation, Vercel
• Engineering Stack: Python (FastAPI, AsyncIO), JavaScript/TypeScript (Next.js, Node.js), REST APIs, Webhook Integrations
• Databases & Auth: Supabase (PostgreSQL, Row-Level Security), SQLite, Redis, Automated Payment Integrations
• Methodologies: Test-Driven Development (TDD), Unit & Integration Testing, Latency Optimization, Security Hardening, High-Availability

==================================================
PROFESSIONAL EXPERIENCE & PROJECTS
==================================================
Lead Systems Architect & Builder | Primuez Autonomous Systems
• Architected and deployed [ADD 50+] production-grade autonomous workflow pipelines connecting multi-service APIs, decreasing manual operational turnaround by [ADD 85]%.
• Engineered bespoke Model Context Protocol (FastMCP) and asynchronous task queues, enabling autonomous LLMs to securely execute live web browsing, data crawling, and API transactions.
• Built and maintained containerized hybrid infrastructure across Linux VPS and serverless edge runtimes, enforcing automated rate-limiting, error checkpoints, and [ADD 99.9]% system uptime.
• Integrated end-to-end relational databases on Supabase (PostgreSQL with RLS) paired with automated webhook checkout pipelines, generating over [ADD $15,000] in direct client revenue.

Flagship Production Projects & Applications
• InkTwin SaaS: Engineered an AI study and OCR synthesis application processing complex multi-page inputs, integrating vision models to achieve [ADD 98]% extraction precision across [ADD 1,200+] active student users.
• PrimuezSure Intelligence: Architected a citation-backed RAG policy engine that ingests unstructured multi-page legal contracts, reducing compliance audit turnaround from [ADD 4 hours] to [ADD 30 seconds], saving clients [ADD $2,400/month].
• DOGRAH Multimodal Engine: Developed an ultra-low-latency streaming voice engine uniting Speech-to-Text and high-speed LLM reasoning with sub-[ADD 350ms] conversational turn latency, tested with [ADD 100%] automated coverage.

==================================================
EDUCATION & CERTIFICATIONS
==================================================
• Bachelor of Computer Applications (BCA) — Shri Shankaracharya Institute of Professional Studies (SSIPS)
• Triple Oracle AI Certified: Agentic AI, Fusion AI Agent Studio & OCI Foundations Associate
• n8n Certified Professional: Advanced multi-step workflow automation, error recovery & AI agent architectures
• Languages: English (Professional Executive), Hindi (Native), Sindhi (Bilingual)
"""

    after_auditor = ResumeAuditor(improved_text, target_role=target_role, job_description=jd)
    after_panel = after_auditor.run_full_panel()
    
    placeholders = [
        {"placeholder": "[ADD 85]%", "context": "Operational latency or time saved percentage in your workflow automations."},
        {"placeholder": "[ADD 99.9]%", "context": "System or service availability uptime figure across your VPS containers."},
        {"placeholder": "[ADD 50+]", "context": "Approximate total number of production workflows, scripts, or agents deployed."},
        {"placeholder": "[ADD 98]%", "context": "Vision OCR accuracy or document extraction precision rate."},
        {"placeholder": "[ADD 4 hours] to [ADD 30 seconds]", "context": "Document review speed improvement metric."},
        {"placeholder": "[ADD 350ms]", "context": "Voice assistant response turnaround latency."}
    ]
    
    next_moves = [
        "1. Fill in the exact figures in the [ADD NUMBER] placeholders with your actual measured telemetry.",
        "2. Save this clean single-column text directly into an unstyled PDF or Google Doc — zero tables, zero text boxes, zero multi-column layouts to ensure 100% ATS readability.",
        "3. Pair this resume with your custom project demos (live URLs) directly in your email or application cover letter."
    ]

    return {
        "before_panel": before_panel,
        "improved_resume": improved_text,
        "placeholders": placeholders,
        "after_panel": after_panel,
        "next_moves": next_moves
    }
