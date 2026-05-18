import os
import asyncio
from dotenv import load_dotenv
import google.generativeai as genai
from mcp_server import scrape_github, analyze_profile, generate_card_html, save_card

# Load environment variables
load_dotenv()

class GitHubDevCardAgent:
    def __init__(self, model_name="gemini-1.5-flash"):
        self.model_name = model_name
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

        # System instruction for the agent
        self.system_instruction = (
            "You are a GitHub profile analyst and dev card generator. "
            "When a user gives you a GitHub username, you ALWAYS follow this exact sequence: "
            "1. Call scrape_github\n"
            "2. Call analyze_profile with the result\n"
            "3. Call generate_card_html with the username, github data, and analysis\n"
            "4. Call save_card with the username and html\n"
            "Never skip steps. Be enthusiastic about developers' work. "
            "If the profile is private or doesn't exist, say so clearly."
        )

        self.model = genai.GenerativeModel(
            model_name=self.model_name,
            system_instruction=self.system_instruction
        )

    async def generate_card(self, username: str) -> dict:
        """
        Orchestrates the card generation by following the required sequence.
        """
        try:
            # Step 1: Scrape
            print(f"[{username}] Agent Step 1: Scraping GitHub...")
            github_data = await scrape_github(username)

            # Step 2: Analyze
            print(f"[{username}] Agent Step 2: Analyzing profile...")
            analysis = await analyze_profile(github_data)

            # Step 3: Generate
            print(f"[{username}] Agent Step 3: Generating HTML...")
            html = await generate_card_html(username, github_data, analysis)

            # Step 4: Save
            print(f"[{username}] Agent Step 4: Saving card...")
            saved_path = await save_card(username, html)

            return {
                "status": "success",
                "username": username,
                "card_url": saved_path,
                "card_html": html,
                "analysis": analysis
            }

        except Exception as e:
            error_msg = str(e)
            print(f"[{username}] Agent Error: {error_msg}")
            if "404" in error_msg or "not found" in error_msg.lower():
                return {"status": "error", "message": f"The profile '{username}' does not exist or is private."}
            return {"status": "error", "message": error_msg}

# Export the agent instance
github_card_agent = GitHubDevCardAgent()
