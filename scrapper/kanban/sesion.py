import asyncio
from playwright.async_api import async_playwright
from dotenv import load_dotenv

import os
from playwright.async_api import async_playwright

async def auto_login(auth_path: str = "auth_state.json"):
    async with async_playwright() as p:
        # Run headless=True once you confirm it works
        browser = await p.chromium.launch(headless=True) 
        context = await browser.new_context()
        page = await context.new_page()

        print("Authenticating via .env credentials...")
        await page.goto(os.getenv('KANBAN_LOGIN_URL'))

        # Fill the login form
        # Note: You'll need to find the correct selectors for your app
        await page.fill("input[name='email']", os.getenv('KANBAN_USER'))
        await page.fill("input[name='password']", os.getenv('KANBAN_PASS'))
        
        # Click the submit button
        await page.click("button[type='submit']")

        # Wait for the dashboard to confirm successful login
        try:
            await page.wait_for_selector(".menu-title", timeout=15000)
            await context.storage_state(path=auth_path)
            print("Auth state refreshed and saved.")
        except Exception as e:
            print(f"Login failed: {e}")
            # Screenshot for debugging if it's running headlessly
            await page.screenshot(path="login_error.png")
        
        await browser.close()

load_dotenv()
asyncio.run(auto_login())
