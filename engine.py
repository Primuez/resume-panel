import re
import math

class ResumeAuditor:
    def __init__(self, resume_text: str, target_role: str = "", job_description: str = ""):
        self.text = resume_text.strip()
        self.target_role = target_role.strip() or "Software Engineer / Tech Builder"
        self.jd = job_description.strip()
        self.lines = [line.strip() for line in self.text.split("\n") if line.strip()]

    def extract_metrics(self):
        # Look for numbers, percentages, dollar/rupee signs, multipliers
        metrics_pattern = re.compile(r'(\d+[\d,]*%|\$\d+[\d,]*|₹\d+[\d,]*|\d+x|\d+\+?\s*(users|clients|repos|stars|requests|queries|prs|endpoints|models|hours|days|seconds|ms))', re.I)
        return metrics_pattern.findall(self.text)

    def extract_action_verbs(self):
        strong_verbs = {
            "architected", "engineered", "built", "deployed", "orchestrated", "automated",
            "developed", "scaled", "reduced", "increased", "optimized", "implemented",
            "designed", "streamlined", "accelerated", "cut", "saved", "integrated", "monetized"
        }
        words = set(re.findall(r'\b[a-zA-Z]+\b', self.text.lower()))
        return words.intersection(strong_verbs)

    def extract_weak_phrases(self):
        weak_patterns = [
            (r'responsible for', 'Passively states duties ("responsible for") instead of leading with active impact verbs.'),
            (r'worked on', 'Vague phrasing ("worked on") obscures your individual ownership and contribution.'),
            (r'helped with|assisted with', 'Shows secondary role ("helped with") without defining what you specifically built or owned.'),
            (r'hard working|team player|fast learner|self-motivated', 'Subjective soft-skill buzzwords without empirical proof or metrics.'),
            (r'duties include', 'Reads like a job description rather than an achievements record.')
        ]
        found = []
        for pattern, explanation in weak_patterns:
            matches = re.finditer(pattern, self.text, re.I)
            for m in matches:
                # Find the surrounding line
                snippet = self.get_surrounding_line(m.start())
                found.append({"pattern": pattern, "explanation": explanation, "quote": snippet})
        return found

    def get_surrounding_line(self, char_idx):
        start = self.text.rfind('\n', 0, char_idx)
        end = self.text.find('\n', char_idx)
        if start == -1: start = 0
        if end == -1: end = len(self.text)
        return self.text[start:end].strip()

    def audit_agent_1_ats(self):
        # Robot Gatekeeper: ATS
        reasons = []
        score = 8.5
        keywords_missing = []
        
        # Check standard headers
        standard_headers = ["summary", "experience", "skills", "projects", "education"]
        text_lower = self.text.lower()
        missing_headers = [h for h in standard_headers if h not in text_lower]
        
        if missing_headers:
            score -= 1.5 * len(missing_headers)
            reasons.append(f"Missing standard ATS section headers: {', '.join(missing_headers).title()}.")

        # Check keyword overlap if JD provided
        if self.jd:
            jd_words = set(re.findall(r'\b[a-zA-Z]{4,}\b', self.jd.lower()))
            resume_words = set(re.findall(r'\b[a-zA-Z]{4,}\b', text_lower))
            tech_keywords = [w for w in jd_words if w in {"python", "react", "docker", "fastapi", "typescript", "cloud", "api", "database", "sql", "testing", "ci/cd", "automation"}]
            missing_tech = [w for w in tech_keywords if w not in resume_words]
            if missing_tech:
                score -= 1.0
                reasons.append(f"Missing high-frequency job description keywords: {', '.join(missing_tech[:5])}.")
        else:
            # Check core baseline tech keywords
            expected = ["git", "api", "test", "production"]
            missing_exp = [w for w in expected if w not in text_lower]
            if missing_exp:
                score -= 0.5 * len(missing_exp)
                reasons.append(f"Essential engineering keyword signals omitted: {', '.join(missing_exp)}.")

        # Check contact info presence
        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', self.text)
        phone_match = re.search(r'\+?\d[\d\s-]{8,14}\d', self.text)
        if not email_match or not phone_match:
            score -= 2.0
            reasons.append("Contact header lacks clean email or standardized international telephone format.")

        score = max(2.0, min(10.0, score))
        decision = "PASS" if score >= 7.0 else "REJECT"
        flip = "Standardize all section headers (Summary, Experience, Projects, Skills) and ensure exact JD keyword alignment."
        return {
            "id": "agent_1_ats",
            "name": "The Robot Gatekeeper (ATS)",
            "role": "Automated Parsing Engine",
            "decision": decision,
            "score": round(score, 1),
            "reasons": reasons[:3] or ["Headers and layout meet machine parsability standards."],
            "flip": flip
        }

    def audit_agent_2_hiring_manager(self):
        # Hiring Manager: 30-sec scan, impact vs duties, top third
        reasons = []
        score = 8.0
        
        # Check top third
        top_third = "\n".join(self.lines[:max(5, len(self.lines)//3)]).lower()
        if "summary" not in top_third and "architect" not in top_third and "developer" not in top_third and "engineer" not in top_third:
            score -= 2.0
            reasons.append("Top-third lacks an immediate identity anchor: unclear title, seniority level, or primary stack in the first 5 lines.")

        # Check metrics frequency
        metrics = self.extract_metrics()
        if len(metrics) < 3:
            score -= 2.5
            reasons.append("Bullets report passive duties rather than quantifiable business impact: missing percentages, throughput, or dollar ROI.")

        weak = self.extract_weak_phrases()
        if weak:
            score -= 1.5
            reasons.append(f'Contains passive phrases like "{weak[0]["pattern"]}" instead of high-agency execution metrics.')

        score = max(2.0, min(10.0, score))
        decision = "INTERVIEW" if score >= 7.0 else "REJECT"
        flip = "Rewrite top 3 bullets into: [Strong Action Verb] + [Specific Problem Solved] + [Quantified % or Scale Metric]."
        return {
            "id": "agent_2_hiring_manager",
            "name": "The Hiring Manager",
            "role": "Role Owner & Technical Director",
            "decision": decision,
            "score": round(score, 1),
            "reasons": reasons[:3] or ["Demonstrates clear technical ownership and senior delivery velocity."],
            "flip": flip
        }

    def audit_agent_3_recruiter(self):
        # Recruiter: 200/day, page length, consistency, formatting
        reasons = []
        score = 8.5
        line_count = len(self.lines)
        if line_count > 100:
            score -= 2.0
            reasons.append(f"Resume is excessively long ({line_count} lines); screening attention decays after 50-60 lines for junior/mid profiles.")
        elif line_count < 25:
            score -= 2.0
            reasons.append("Resume is too sparse (< 25 lines); lacks sufficient project depth or technical verification.")

        # Typos / capitalization
        if "github.com" not in self.text.lower() and "linkedin.com" not in self.text.lower():
            score -= 1.5
            reasons.append("Missing live professional profile links (GitHub / LinkedIn) for immediate identity verification.")

        score = max(2.0, min(10.0, score))
        decision = "PASS" if score >= 7.0 else "REJECT"
        flip = "Format into clean, crisp 1-page sections with hyperlinked GitHub, LinkedIn, and personal portfolio URLs."
        return {
            "id": "agent_3_recruiter",
            "name": "The Recruiter",
            "role": "High-Volume Talent Screener",
            "decision": decision,
            "score": round(score, 1),
            "reasons": reasons[:3] or ["Scannable hierarchy with verified links and clean chronological order."],
            "flip": flip
        }

    def audit_agent_4_competitor(self):
        # Competition: "Here's why they'd pick me over you"
        reasons = []
        score = 7.0
        metrics = self.extract_metrics()
        
        if len(metrics) < 4:
            score -= 2.0
            reasons.append("I have concrete production scale numbers (e.g. 'handled 10M daily requests, 99.9% uptime'), while your metrics are unquantified.")

        if "ci/cd" not in self.text.lower() and "docker" not in self.text.lower() and "test" not in self.text.lower():
            score -= 1.5
            reasons.append("My resume proves automated testing and CI/CD pipelines; yours only claims feature implementation.")

        score = max(2.0, min(10.0, score))
        decision = "PASS" if score >= 7.0 else "REJECT"
        flip = "Inject explicit comparative engineering scale: database query optimization ms, test coverage %, and container deployment pipelines."
        return {
            "id": "agent_4_competitor",
            "name": "Another Applicant (Competition)",
            "role": "Top-Tier Peer Candidate",
            "decision": decision,
            "score": round(score, 1),
            "reasons": reasons[:3] or ["Competitive technical depth that matches or exceeds market benchmarks."],
            "flip": flip
        }

    def audit_agent_5_team_lead(self):
        # Team Manager: Hands-on skills, tools, 90-day delivery
        reasons = []
        score = 8.0
        
        has_tools = any(t in self.text.lower() for t in ["python", "typescript", "docker", "postgres", "supabase", "git", "linux"])
        if not has_tools:
            score -= 3.0
            reasons.append("Lacks concrete modern backend/infrastructure tooling stack; difficult to assess day-one engineering autonomy.")

        if "test" not in self.text.lower():
            score -= 1.5
            reasons.append("No mention of automated unit testing, integration tests, or TDD discipline—signals potential production code fragility.")

        score = max(2.0, min(10.0, score))
        decision = "PASS" if score >= 7.0 else "REJECT"
        flip = "Showcase test suites, error handling, and concrete microservice/containerized architecture patterns."
        return {
            "id": "agent_5_team_lead",
            "name": "The Team Manager (Future Boss)",
            "role": "Engineering Lead",
            "decision": decision,
            "score": round(score, 1),
            "reasons": reasons[:3] or ["Strong operational stack with proven architectural autonomy."],
            "flip": flip
        }

    def audit_agent_6_ceo(self):
        # CEO / Founder: 10 seconds. Bottom-line business ROI: revenue, growth, costs, time saved
        reasons = []
        score = 7.5
        
        business_terms = ["revenue", "saved", "reduced", "growth", "monetiz", "clients", "users", "cost", "conversion"]
        found_biz = [b for b in business_terms if b in self.text.lower()]
        
        if len(found_biz) < 2:
            score -= 2.5
            reasons.append('Fails the "So What?" test: describes lines of code and tools without translating technical work into revenue, retained margins, or hours saved.')

        score = max(2.0, min(10.0, score))
        decision = "PASS" if score >= 7.0 else "REJECT"
        flip = "Tie every major engineering build to executive outcomes: 'reduced operational overhead by X%', 'saved Y engineering hours/month'."
        return {
            "id": "agent_6_ceo",
            "name": "The CEO / Founder",
            "role": "Executive Leadership",
            "decision": decision,
            "score": round(score, 1),
            "reasons": reasons[:3] or ["Direct connection between engineering pipelines and bottom-line commercial impact."],
            "flip": flip
        }

    def audit_agent_7_domain_expert(self):
        # Domain Expert: Buzzwords without proof, exaggerated claims, technical depth
        reasons = []
        score = 8.0
        
        buzzwords = ["ai-driven", "synergy", "cutting-edge", "game-changing", "revolutionary", "visionary"]
        found_buzz = [b for b in buzzwords if b in self.text.lower()]
        if found_buzz:
            score -= 1.5
            reasons.append(f"Flagged marketing fluff buzzwords without architectural mechanics: {', '.join(found_buzz)}.")

        # Depth check: look for architectural frameworks
        arch_signals = ["mcp", "rag", "docker", "redis", "postgresql", "fastapi", "asyncio", "reverse proxy", "schema"]
        found_arch = [a for a in arch_signals if a in self.text.lower()]
        if len(found_arch) < 2:
            score -= 1.5
            reasons.append("Superficial framework listing: claims AI engineering but omits specific architectural plumbing (RAG, vector stores, caching, RPCs).")

        score = max(2.0, min(10.0, score))
        decision = "PASS" if score >= 7.0 else "REJECT"
        flip = "Replace generic buzzwords with explicit architectural protocols, data schemas, and latency benchmarks."
        return {
            "id": "agent_7_domain_expert",
            "name": "The Domain Expert",
            "role": "Principal Systems Architect",
            "decision": decision,
            "score": round(score, 1),
            "reasons": reasons[:3] or ["High credibility, verified credentials, and rigorous systems architecture."],
            "flip": flip
        }

    def run_full_panel(self):
        judges = [
            self.audit_agent_1_ats(),
            self.audit_agent_2_hiring_manager(),
            self.audit_agent_3_recruiter(),
            self.audit_agent_4_competitor(),
            self.audit_agent_5_team_lead(),
            self.audit_agent_6_ceo(),
            self.audit_agent_7_domain_expert()
        ]
        total_score = sum(j["score"] for j in judges)
        rejections = sum(1 for j in judges if j["decision"] == "REJECT")
        
        # Combine mistakes
        all_reasons = []
        for j in judges:
            for r in j["reasons"]:
                if "meets" not in r.lower() and "matches" not in r.lower() and "strong" not in r.lower() and "high credibility" not in r.lower():
                    all_reasons.append({
                        "agent": j["name"],
                        "issue": r,
                        "severity": "CRITICAL" if j["score"] < 6.0 else ("IMPORTANT" if j["score"] < 7.5 else "POLISH")
                    })

        return {
            "judges": judges,
            "total_score": round(total_score, 1),
            "max_score": 70,
            "rejections": rejections,
            "verdict": "UNREJECTABLE" if rejections == 0 else f"{rejections} of 7 judges would REJECT this resume",
            "all_issues": all_reasons
        }
