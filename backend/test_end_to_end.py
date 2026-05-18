import asyncio
import os
import json
from mcp_server import scrape_github, analyze_profile, generate_card_html

async def test_end_to_end():
    username = "torvalds"
    print(f"--- Starting test for {username} ---")
    
    try:
        # 1. scrape_github
        print(f"1. Calling scrape_github('{username}')...")
        github_data = await scrape_github(username)
        print("Success: Data scraped.")
        
        # 2. analyze_profile
        print("2. Calling analyze_profile()...")
        analysis = await analyze_profile(github_data)
        print("Success: Profile analyzed.")
        
        # 3. generate_card_html
        print("3. Calling generate_card_html()...")
        html = await generate_card_html(username, github_data, analysis)
        print("Success: HTML generated.")
        
        # 4. Print results
        print("\n--- TEST RESULTS ---")
        print(f"Card Theme: {analysis.get('card_theme')}")
        print(f"Developer Vibe: {analysis.get('developer_vibe')}")
        print("--- END TEST ---")
        
    except Exception as e:
        print(f"\n!!! TEST FAILED !!!")
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_end_to_end())
