import os
import httpx
import json
import asyncio
from pathlib import Path
from mcp.server.fastmcp import FastMCP
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Initialize FastMCP server
mcp = FastMCP("GitHub Card Generator")

# Configure Gemini
# Pinning to 2.0-flash to avoid low Gemini 3 quotas in 2026 environment
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")

@mcp.tool()
async def scrape_github(username: str) -> dict:
    """Calls the GitHub REST API to fetch public profile data."""
    async with httpx.AsyncClient() as client:
        # Fetch profile
        headers = {"Accept": "application/vnd.github.v3+json"}
        token = os.getenv("GITHUB_TOKEN")
        if token:
            headers["Authorization"] = f"token {token}"

        profile_res = await client.get(f"https://api.github.com/users/{username}", headers=headers)
        if profile_res.status_code != 200:
            raise Exception(f"GitHub profile not found: {profile_res.status_code}")

        user_data = profile_res.json()

        # Fetch repos
        repos_res = await client.get(f"https://api.github.com/users/{username}/repos?sort=updated&per_page=100", headers=headers)
        repos_data = repos_res.json() if repos_res.status_code == 200 else []

        # Process repos
        sorted_repos = sorted(repos_data, key=lambda x: x.get("stargazers_count", 0), reverse=True)[:6]
        top_6_repos = [{"name": r["name"], "stars": r["stargazers_count"], "language": r["language"]} for r in sorted_repos]
        
        languages = {}
        for r in repos_data:
            lang = r.get("language")
            if lang: languages[lang] = languages.get(lang, 0) + 1
        sorted_langs = sorted(languages.items(), key=lambda x: x[1], reverse=True)[:5]

        return {
            "name": user_data.get("name") or username,
            "bio": user_data.get("bio"),
            "location": user_data.get("location"),
            "public_repos": user_data.get("public_repos"),
            "followers": user_data.get("followers"),
            "avatar_url": user_data.get("avatar_url"),
            "top_6_repos": top_6_repos,
            "languages": [l[0] for l in sorted_langs]
        }

@mcp.tool()
async def analyze_profile(github_data: dict) -> dict:
    """Uses Gemini 2.0 Flash to analyze profile."""
    prompt = f"Analyze GitHub data and return JSON for developer_vibe, top_skills, and card_theme (hacker, builder, researcher, designer, open-source-hero): {json.dumps(github_data)}"
    response = model.generate_content(prompt)
    try:
        text = response.text.strip().replace("```json", "").replace("```", "")
        return json.loads(text)
    except:
        return {"developer_vibe": "A dedicated code craftsman.", "top_skills": github_data["languages"][:3], "card_theme": "builder"}

@mcp.tool()
async def generate_card_html(username: str, github_data: dict, analysis: dict) -> str:
    """Generates the inner HTML component for the card."""
    theme = analysis.get("card_theme", "builder")
    theme_info = {
        "hacker": {"bg": "#0d1117", "text": "#39ff14", "accent": "#238636", "label": "HACKER"},
        "builder": {"bg": "#ffffff", "text": "#24292e", "accent": "#0366d6", "label": "BUILDER"},
        "researcher": {"bg": "#f6f8fa", "text": "#24292e", "accent": "#6f42c1", "label": "RESEARCHER"},
        "designer": {"bg": "#fff5f5", "text": "#d73a49", "accent": "#f9826c", "label": "DESIGNER"},
        "open-source-hero": {"bg": "#f0f9ff", "text": "#005cc5", "accent": "#2188ff", "label": "OSS HERO"}
    }
    c = theme_info.get(theme, theme_info["builder"])
    skills_html = "".join([f'<span style="background:{c["accent"]}; color:white; padding:2px 8px; border-radius:10px; margin-right:4px; font-size:11px; font-weight:600;">{s}</span>' for s in analysis.get("top_skills", [])])

    html = f"""
    <div style="background:{c["bg"]}; color:{c["text"]}; border: 1px solid #e1e4e8; border-radius: 12px; padding: 20px; width: 550px; font-family: sans-serif; box-shadow: 0 8px 24px rgba(0,0,0,0.1); display: flex; gap: 24px;">
        <div style="flex: 1; display: flex; flex-direction: column; align-items: center; text-align: center; border-right: 1px solid #eee; padding-right: 20px;">
            <div style="position: relative; margin-bottom: 12px;">
                <img src="{github_data['avatar_url']}" style="width: 100px; height: 100px; border-radius: 50%; border: 3px solid {c['accent']};">
                <div style="position: absolute; bottom: -5px; right: -5px; background: {c['accent']}; color: white; font-size: 10px; padding: 2px 6px; border-radius: 4px; border: 2px solid {c['bg']}; font-weight:800;">{c['label']}</div>
            </div>
            <h2 style="margin: 0; font-size: 20px;">{github_data['name']}</h2>
            <p style="margin: 2px 0 10px 0; font-size: 14px; opacity: 0.7;">@{username}</p>
            <p style="font-size: 13px; margin-bottom: 12px;">{analysis['developer_vibe']}</p>
            <div style="display: flex; flex-wrap: wrap; justify-content: center; gap: 4px; margin-bottom:12px;">{skills_html}</div>
            <a href="https://github.com/{username}" target="_blank" style="display: inline-block; font-size: 11px; color: {c['accent']}; text-decoration: none; font-weight: 700; border: 1.5px solid {c['accent']}; padding: 5px 10px; border-radius: 6px; text-transform: uppercase;">View Profile &rarr;</a>
        </div>
        <div style="flex: 1.2; display: flex; flex-direction: column; justify-content: center;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 16px; font-size: 13px; background: rgba(0,0,0,0.03); padding: 8px; border-radius: 8px;">
                <div style="text-align: center;"><strong>{github_data['public_repos']}</strong><br><small>Repos</small></div>
                <div style="text-align: center;"><strong>{github_data['followers']}</strong><br><small>Followers</small></div>
                <div style="text-align: center;">📍<br><small>{github_data['location'] or 'Cloud'}</small></div>
            </div>
            <div>
                <h4 style="margin: 0 0 8px 0; font-size: 12px; text-transform: uppercase; color: {c['accent']};">Featured Projects</h4>
                {''.join([f'<div style="margin-bottom: 6px; font-size: 12px; display: flex; justify-content: space-between;"><strong>{r["name"]}</strong><span>⭐ {r["stars"]}</span></div>' for r in github_data['top_6_repos'][:3]])}
            </div>
        </div>
    </div>
    """
    return html

@mcp.tool()
async def save_card(username: str, html: str) -> str:
    """Saves the card as a FULL standalone HTML document."""
    output_dir = Path(__file__).resolve().parent / "static" / "cards"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Wrap in full HTML boilerplate for sharing
    full_html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>{username}'s GitHub Dev Card</title>
        <style>
            body {{
                background-color: #0d1117;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
            }}
        </style>
    </head>
    <body>
        {html}
    </body>
    </html>
    """
    
    file_path = output_dir / f"{username}.html"
    file_path.write_text(full_html, encoding="utf-8")
    return f"/card/{username}"

if __name__ == "__main__":
    mcp.run()
