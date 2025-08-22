# app/helpers.py

def _generate_about_section(team):
    return {
        "heading": team.get("about_heading", "About Us"),
        "text": team.get("about_text", "About text placeholder."),
        "players": team.get("players", []),
        "cta": team.get("cta_label", "Join Us"),
    }

def _generate_impact_stats(team):
    return team.get("impact_stats", [{"label": "Players Enrolled", "value": 16}])

def _generate_challenge_section(team, impact_stats):
    return {
        "heading": team.get("challenge_heading", "The Challenge"),
        "text": team.get("challenge_text", "Our challenge is..."),
        "metrics": impact_stats,
    }

def _generate_mission_section(team, impact_stats):
    return {
        "heading": team.get("mission_heading", "Our Mission"),
        "text": team.get("mission_text", "Mission text."),
        "stats": impact_stats,
    }

def _prepare_stats(team, raised, goal, percent_raised):
    return {
        "raised": raised,
        "goal": goal,
        "percent": percent_raised,
    }

