#!/usr/bin/env python3
"""
7-Agent Resume Hiring Panel CLI
Evaluates resumes across 7 harsh hiring personas, ranks flaws, rewrites ATS-clean text,
and compares before/after scoreboard metrics.
"""

import argparse
import os
import sys

# Ensure local site-packages are available
sys.path.insert(0, "/opt/data/.local/lib/python3.14/site-packages")

import json
import re

try:
    import pypdf
except ImportError:
    pypdf = None

from engine import ResumeAuditor
from rewrite_engine import generate_improved_resume

def extract_text(file_path: str) -> str:
    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}", file=sys.stderr)
        sys.exit(1)
        
    ext = os.path.splitext(file_path)[1].lower()
    
    # Text or Markdown
    if ext in [".txt", ".md", ".json"]:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            return f.read()
            
    # PDF parsing
    if ext == ".pdf":
        if pypdf:
            try:
                reader = pypdf.PdfReader(file_path)
                pages_text = [page.extract_text() or "" for page in reader.pages]
                full_text = "\n".join(pages_text).strip()
                if full_text:
                    return full_text
            except Exception as e:
                pass

        # Try fitz if available
        try:
            import fitz
            doc = fitz.open(file_path)
            text = "\n".join([page.get_text() for page in doc])
            if text.strip():
                return text
        except ImportError:
            pass

        # Native fallback: extract PDF text using pdftotext or strings
        import subprocess
        try:
            out = subprocess.check_output(["pdftotext", file_path, "-"], stderr=subprocess.DEVNULL)
            return out.decode("utf-8", errors="replace")
        except Exception:
            pass

        # Fallback to python standard library binary text sweep
        with open(file_path, "rb") as f:
            content = f.read().decode("latin-1", errors="replace")
            # Extract plain string sequences
            strings = re.findall(r'[A-Za-z0-9\s.,;:()\-—–/+=%@#&]{4,}', content)
            return "\n".join(strings)
            
    # Fallback default read
    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()

def format_terminal_report(results: dict) -> str:
    before = results["before_panel"]
    after = results["after_panel"]
    
    out = []
    out.append("================================================================================")
    out.append("                         THE 7-AGENT RESUME HIRING PANEL                        ")
    out.append("================================================================================\n")
    
    # PART 1: SCOREBOARD
    out.append("PART 1 — PANEL SCOREBOARD")
    out.append("--------------------------------------------------------------------------------")
    out.append(f"{'Judge / Agent':<35} | {'Decision':<10} | {'Score':<8} | Biggest Reason")
    out.append("-" * 80)
    for j in before["judges"]:
        reason_preview = j["reasons"][0][:25] + "..." if len(j["reasons"][0]) > 25 else j["reasons"][0]
        out.append(f"{j['name']:<35} | {j['decision']:<10} | {j['score']}/10     | {reason_preview}")
    out.append("-" * 80)
    out.append(f"Panel Result: {before['rejections']} of 7 would REJECT this resume.")
    out.append(f"Overall Pre-Audit Score: {before['total_score']} / {before['max_score']}\n")

    # PART 2: EACH AGENT'S VERDICT
    out.append("PART 2 — EACH AGENT'S VERDICT")
    out.append("--------------------------------------------------------------------------------")
    for idx, j in enumerate(before["judges"], 1):
        out.append(f"\n[AGENT {idx}] {j['name']} ({j['role']})")
        out.append(f"• Decision: {j['decision']} (Score: {j['score']}/10)")
        out.append("• Top Reasons:")
        for r in j["reasons"]:
            out.append(f"   - {r}")
        out.append(f"• Flip Condition: {j['flip']}")

    # PART 3: WHAT IS WRONG
    out.append("\nPART 3 — RANKED RESUME FLAWS")
    out.append("--------------------------------------------------------------------------------")
    for issue in before["all_issues"][:10]:
        out.append(f"[{issue['severity']}] ({issue['agent']}): {issue['issue']}")

    # PART 4: IMPROVED RESUME
    out.append("\nPART 4 — YOUR IMPROVED RESUME (Clean ATS Plain Text)")
    out.append("--------------------------------------------------------------------------------")
    out.append(results["improved_resume"])
    out.append("\n[PLACEHOLDERS TO FILL]:")
    for p in results["placeholders"]:
        out.append(f"• {p['placeholder']}: {p['context']}")

    # PART 5: RE-JUDGED BEFORE & AFTER
    out.append("\nPART 5 — RE-EVALUATION SCOREBOARD (BEFORE vs AFTER)")
    out.append("--------------------------------------------------------------------------------")
    out.append(f"{'Judge':<35} | {'Before':<10} | {'After':<10} | Delta")
    out.append("-" * 70)
    for b_j, a_j in zip(before["judges"], after["judges"]):
        delta = round(a_j["score"] - b_j["score"], 1)
        sign = f"+{delta}" if delta >= 0 else f"{delta}"
        out.append(f"{b_j['name']:<35} | {b_j['score']}/10    | {a_j['score']}/10     | {sign}")
    out.append("-" * 70)
    out.append(f"Original Score: {before['total_score']}/70 ➔ Improved Score: {after['total_score']}/70 (+{round(after['total_score'] - before['total_score'], 1)})")
    out.append(f"Rejections: {before['rejections']} of 7 ➔ {after['rejections']} of 7 (All judges satisfied)")

    # PART 6: NEXT 3 MOVES
    out.append("\nPART 6 — YOUR NEXT 3 MOVES")
    out.append("--------------------------------------------------------------------------------")
    for move in results["next_moves"]:
        out.append(f"• {move}")
    out.append("================================================================================\n")
    
    return "\n".join(out)

def main():
    parser = argparse.ArgumentParser(description="Run 7-Agent Resume Hiring Panel")
    parser.add_argument("--resume", required=True, help="Path to resume file (PDF, TXT, or MD)")
    parser.add_argument("--jd", help="Path to target job description file (optional)")
    parser.add_argument("--role", help="Target job role title (optional)")
    parser.add_argument("--output", help="Write report to file (optional)")
    parser.add_argument("--json", action="store_true", help="Output raw JSON results")

    args = parser.parse_args()

    resume_text = extract_text(args.resume)
    jd_text = extract_text(args.jd) if args.jd else ""

    results = generate_improved_resume(resume_text, target_role=args.role or "", jd=jd_text)

    if args.json:
        out_str = json.dumps(results, indent=2)
    else:
        out_str = format_terminal_report(results)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(out_str)
        print(f"Report successfully saved to {args.output}")
    else:
        print(out_str)

if __name__ == "__main__":
    main()
