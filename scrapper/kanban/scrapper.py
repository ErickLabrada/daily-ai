import os
import asyncio
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv()
url = os.getenv('KANBAN_BOARD_URL')

#async def scrape_kanban():
#    async with async_playwright() as p:
#        # Load the saved session
#        browser = await p.chromium.launch(headless=True)
#        context = await browser.new_context(storage_state="auth_state.json")
#        page = await context.new_page()
#        
#        await page.goto(url)
#        
#        # Wait for the board to load
#        await page.wait_for_selector(".kanban-card")
#
#        columns=["TO DO", "Pending", "In process", "Ready", "QA pending","QA process","Integration queue", "Done"]
#
#
#        for state in columns:
#            column_selector = f".kanban-board[data-id='{state}']"
#
#        await browser.close()
#       return tasks

async def get_my_tasks(user_id="206"):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(storage_state="auth_state.json")
        page = await context.new_page()
        
        await page.goto(os.getenv('KANBAN_BOARD_URL'))
        
        # Wait for the board to actually render cards
        await page.wait_for_selector(".kanban-item", timeout=20000)

        # Logic to extract ONLY your cards across ALL columns
        my_tasks = await page.eval_on_selector_all(
            ".kanban-item", 
            """
            (elements, myId) => {
                return elements
                    .filter(el => {
                        // Get all collaborator inputs in this specific card
                        const collabs = Array.from(el.querySelectorAll('input[name="id_colaboradores[]"]'));
                        // Keep the card if your ID is found in any of them
                        return collabs.some(input => input.value === myId);
                    })
                    .map(el => {
                        // Find the parent column to determine the "State"
                        const board = el.closest('.kanban-board');
                        const state = board ? board.getAttribute('data-id') : 'Unknown';

                        return {
                            folio: el.querySelector('input[name="folio"]')?.value || 'N/A',
                            title: el.querySelector('input[name="title"]')?.value || 'No Title',
                            state: state,
                            id: el.getAttribute('data-eid') || el.getAttribute('data-id_subtarea')
                        };
                    });
            }
            """,
            user_id # Passing the Python variable into the browser context
        )
        
        await browser.close()
        print(my_tasks)
        return my_tasks