from playwright.sync_api import sync_playwright, expect

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto("https://www.saucedemo.com/")
    
    page.fill("#user-name", "standard_user")
    page.fill("#password", "wrong_password")
    page.click("#login-button")
    
    expect(page).to_have_url("https://www.saucedemo.com/inventory.html")
    expect(page.locator(".inventory_list")).to_be_visible()
    
    browser.close()
