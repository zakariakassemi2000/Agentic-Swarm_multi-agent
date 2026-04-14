"""
Synapse Studio V2 Ultra – Scoring Engine
Extracts numeric scores from Critic output and computes composite quality.
"""
import re
from core.state import ProjectScore


def _extract_score(text: str, keywords: list[str]) -> float:
    """Try to find a numeric score (e.g. '7/10', 'Score: 8', '9 out of 10') near keywords."""
    for kw in keywords:
        pattern = rf"{re.escape(kw)}[^\d]{{0,40}}(\d+(?:\.\d+)?)\s*(?:/\s*10)?"
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            val = float(m.group(1))
            return min(val, 10.0)
    # Fallback: find any X/10 pattern
    m = re.search(r"(\d+(?:\.\d+)?)\s*/\s*10", text)
    if m:
        return min(float(m.group(1)), 10.0)
    return 0.0


def parse_scores_from_critic(critic_text: str) -> ProjectScore:
    """Parse a ProjectScore from raw Critic agent output."""
    s = ProjectScore(
        technical_complexity = _extract_score(critic_text, ["technical", "complexity", "tech"]),
        scalability          = _extract_score(critic_text, ["scalab", "scale"]),
        innovation           = _extract_score(critic_text, ["innovat", "creativity", "creative"]),
        business_value       = _extract_score(critic_text, ["business", "revenue", "market", "roi"]),
        code_quality         = _extract_score(critic_text, ["code quality", "code", "quality", "clean"]),
    )
    # If none were parsed, estimate from overall sentiment
    if s.technical_complexity == 0 and s.scalability == 0:
        # rough estimate: count positive vs negative words
        pos = len(re.findall(r"\b(good|great|excellent|solid|strong|well)\b", critic_text, re.I))
        neg = len(re.findall(r"\b(bad|poor|weak|miss|lack|fail|issue|problem)\b", critic_text, re.I))
        base = 5.0 + min(pos, 5) * 0.5 - min(neg, 5) * 0.5
        s.technical_complexity = s.scalability = s.innovation = s.business_value = s.code_quality = round(base, 1)

    s.compute_overall()
    return s


def score_summary(score: ProjectScore) -> str:
    bar = lambda v: "█" * int(v) + "░" * (10 - int(v))
    return (
        f"🔬 Technical  [{bar(score.technical_complexity)}] {score.technical_complexity}/10\n"
        f"📈 Scalability [{bar(score.scalability)}] {score.scalability}/10\n"
        f"💡 Innovation  [{bar(score.innovation)}] {score.innovation}/10\n"
        f"💼 Business    [{bar(score.business_value)}] {score.business_value}/10\n"
        f"🧹 Code Quality[{bar(score.code_quality)}] {score.code_quality}/10\n"
        f"⭐ OVERALL     [{bar(score.overall)}] {score.overall}/10"
    )
