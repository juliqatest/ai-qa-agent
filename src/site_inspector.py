from playwright.sync_api import sync_playwright
from src.config import MAX_SITE_ELEMENTS, MAX_PAGE_TEXT

def inspeccionar_sitio(base_url, headless=True):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        page = browser.new_page()

        page.goto(
            base_url,
            wait_until="domcontentloaded",
            timeout=30000
        )

        try:
            page.wait_for_load_state(
                "networkidle",
                timeout=5000
            )
        except Exception:
            pass

        elementos = []
        formularios = []

        # Inputs
        for locator in page.locator(
            'input:not([type="checkbox"]):not([type="radio"])'
        ).all():
            input_id = locator.get_attribute("id")

            label = None
            if input_id:
                label_locator = page.locator(f'label[for="{input_id}"]')
                if label_locator.count() > 0:
                    label = label_locator.first.inner_text().strip()

            elementos.append({
                "type": "input",
                "id": input_id,
                "name": locator.get_attribute("name"),
                "input_type": locator.get_attribute("type"),
                "placeholder": locator.get_attribute("placeholder"),
                "aria_label": locator.get_attribute("aria-label"),
                "label": label
            })

        # Textareas
        for locator in page.locator("textarea").all():
            elementos.append({
                "type": "textarea",
                "id": locator.get_attribute("id"),
                "name": locator.get_attribute("name"),
                "placeholder": locator.get_attribute("placeholder"),
                "aria_label": locator.get_attribute("aria-label")
            })

        # Selects
        for locator in page.locator("select").all():
            opciones = []

            for option in locator.locator("option").all():
                opciones.append({
                    "text": option.inner_text().strip(),
                    "value": option.get_attribute("value")
                })

            elementos.append({
                "type": "select",
                "id": locator.get_attribute("id"),
                "name": locator.get_attribute("name"),
                "aria_label": locator.get_attribute("aria-label"),
                "options": opciones[:20]
            })

        # Checkboxes
        for locator in page.locator('input[type="checkbox"]').all():
            elementos.append({
                "type": "checkbox",
                "id": locator.get_attribute("id"),
                "name": locator.get_attribute("name"),
                "value": locator.get_attribute("value"),
                "aria_label": locator.get_attribute("aria-label")
            })

        # Radios
        for locator in page.locator('input[type="radio"]').all():
            elementos.append({
                "type": "radio",
                "id": locator.get_attribute("id"),
                "name": locator.get_attribute("name"),
                "value": locator.get_attribute("value"),
                "aria_label": locator.get_attribute("aria-label")
            })

        # Buttons
        for locator in page.locator("button").all():
            elementos.append({
                "type": "button",
                "text": locator.inner_text().strip(),
                "aria_label": locator.get_attribute("aria-label"),
                "name": locator.get_attribute("name")
            })

        # Links
        for locator in page.locator("a").all():
            elementos.append({
                "type": "link",
                "text": locator.inner_text().strip(),
                "href": locator.get_attribute("href"),
                "aria_label": locator.get_attribute("aria-label")
            })

        # Elementos con roles ARIA relevantes
        roles_interactivos = [
            "button",
            "link",
            "textbox",
            "checkbox",
            "radio",
            "combobox",
            "menuitem",
            "tab"
        ]

        for role in roles_interactivos:
            for locator in page.locator(f'[role="{role}"]').all():
                elementos.append({
                    "type": "aria_role",
                    "role": role,
                    "text": locator.inner_text().strip(),
                    "aria_label": locator.get_attribute("aria-label"),
                    "name": locator.get_attribute("name")
                })

        # Forms
        for index, form in enumerate(page.locator("form").all(), start=1):
            form_data = {
                "index": index,
                "action": form.get_attribute("action"),
                "method": form.get_attribute("method"),
                "inputs": [],
                "buttons": []
            }

            for input_locator in form.locator("input").all():
                form_data["inputs"].append({
                    "name": input_locator.get_attribute("name"),
                    "type": input_locator.get_attribute("type"),
                    "placeholder": input_locator.get_attribute("placeholder"),
                    "aria_label": input_locator.get_attribute("aria-label")
                })

            for button_locator in form.locator("button").all():
                form_data["buttons"].append({
                    "text": button_locator.inner_text().strip(),
                    "type": button_locator.get_attribute("type")
                })
            form_data["textareas"] = []
            form_data["selects"] = []

            for textarea in form.locator("textarea").all():
                form_data["textareas"].append({
                    "name": textarea.get_attribute("name"),
                    "placeholder": textarea.get_attribute("placeholder"),
                    "aria_label": textarea.get_attribute("aria-label")
                })

            for select in form.locator("select").all():
                form_data["selects"].append({
                    "name": select.get_attribute("name"),
                    "aria_label": select.get_attribute("aria-label")
                })

            formularios.append(form_data)

        titulo = page.title()

        body_text = page.locator("body").inner_text()

        browser.close()

        return {
            "url": base_url,
            "title": titulo,
            "elements": elementos[:MAX_SITE_ELEMENTS],
            "forms": formularios,
            "page_text_preview": body_text[:MAX_PAGE_TEXT]
        }
