from playwright.sync_api import sync_playwright, expect

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    # Abrir la página de práctica
    page.goto("https://www.saucedemo.com/")

    # Completar usuario y contraseña
    page.fill("#user-name", "standard_user")
    page.fill("#password", "secret_sauce")

    # Hacer login
    page.click("#login-button")

    # Verificar que ingresamos correctamente
    expect(page).to_have_url("https://www.saucedemo.com/inventory.html")

    print("✅ TEST PASÓ: Login exitoso")

    browser.close()
