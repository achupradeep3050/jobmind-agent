# LinkedIn Outreach Agent — generates personalized connection request messages.
# Uses the contacto.md framework from career-ops.

FROM_LINK = """You are a LinkedIn outreach specialist. Generate connection request messages.
Given a company, role, and contact type (recruiter/hiring manager/peer), generate a short message.
Max 300 characters. Be specific and direct — no corporate speak."""

CONTACT_TEMPLATES = {
    "recruiter": (
        "Sentence 1 (Fit): Direct match — role, experience, availability\n"
        "Sentence 2 (Proof): Key metric or achievement relevant to their search\n"
        "Sentence 3 (CTA): Share CV if aligned"
    ),
    "hiring_manager": (
        "Sentence 1 (Hook): Specific challenge the team faces (from JD/news/blog)\n"
        "Sentence 2 (Proof): Quantified achievement showing solved similar problem\n"
        "Sentence 3 (CTA): Ask how team is approaching the challenge"
    ),
    "peer": (
        "Sentence 1 (Interest): Reference specific work — blog, talk, open-source\n"
        "Sentence 2 (Connection): Something you're doing in same space\n"
        "Sentence 3 (CTA): Swap notes on shared problem space"
    ),
}