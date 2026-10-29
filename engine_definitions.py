import re

JUDGE_PROMPTS = {
    "agent_1_ats": {
        "id": "agent_1_ats",
        "name": "The Robot Gatekeeper (ATS)",
        "role": "Automated Applicant Tracking System",
        "avatar": "🤖",
        "perspective": "Checks layout parsability, missing target keywords, non-standard section headers, and unparsable tables/columns.",
        "eval_fn": "eval_ats"
    },
    "agent_2_hiring_manager": {
        "id": "agent_2_hiring_manager",
        "name": "The Hiring Manager",
        "role": "Role Owner & Technical Director",
        "avatar": "👔",
        "perspective": "Has 30 seconds. Checks top-third clarity, impact & scale vs mere job duties, and flags fluff or job-hopping.",
        "eval_fn": "eval_hiring_manager"
    },
    "agent_3_recruiter": {
        "id": "agent_3_recruiter",
        "name": "The Recruiter",
        "role": "Talent Acquisition Screener",
        "avatar": "📋",
        "perspective": "Screens 200 resumes/day. Checks page length, visual scanability, typos, date consistency, and clean grammar.",
        "eval_fn": "eval_recruiter"
    },
    "agent_4_competitor": {
        "id": "agent_4_competitor",
        "name": "Another Applicant (Competition)",
        "role": "Top-Tier Peer Candidate",
        "avatar": "⚔️",
        "perspective": "Applying for the same seat with superior metrics, clearer impact numbers, and less generic corporate phrasing.",
        "eval_fn": "eval_competitor"
    },
    "agent_5_team_lead": {
        "id": "agent_5_team_lead",
        "name": "The Team Manager (Future Boss)",
        "role": "Direct Engineering / Functional Lead",
        "avatar": "🛠️",
        "perspective": "Cares about day-to-day work: real hands-on tools, architecture ownership, test discipline, and 90-day execution velocity.",
        "eval_fn": "eval_team_lead"
    },
    "agent_6_ceo": {
        "id": "agent_6_ceo",
        "name": "The CEO / Founder",
        "role": "Executive Leadership",
        "avatar": "💼",
        "perspective": "Has 10 seconds. Demands bottom-line business ROI: revenue generated, costs slashed, speed-to-market, and user scale.",
        "eval_fn": "eval_ceo"
    },
    "agent_7_domain_expert": {
        "id": "agent_7_domain_expert",
        "name": "The Domain Expert",
        "role": "Principal Architect / Senior Specialist",
        "avatar": "🔬",
        "perspective": "Hunts buzzwords lacking technical substantiation, outdated methodologies, exaggerated claims, and missing industry rigor.",
        "eval_fn": "eval_domain_expert"
    }
}
