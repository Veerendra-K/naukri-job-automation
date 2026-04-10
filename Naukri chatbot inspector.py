"""
Naukri Chatbot DOM Inspector
============================
Run this script, click Apply on any Naukri job that shows
the chatbot questionnaire panel, then press ENTER in this
terminal. It will print the EXACT DOM structure of the panel
so we can build correct selectors.

Usage:
  py naukri_chatbot_inspector.py
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import json

# ── CONFIG ──────────────────────────────────────────────────
EMAIL    = "veerendrasagar.k48@gmail.com"
PASSWORD = "MyDream#2324"

# Paste any Naukri job URL that you know shows the chatbot panel
JOB_URL = "https://www.naukri.com/job-listings-it-support-engineer-quess-corp-bengaluru-1-to-6-years-270326500617"

# ── BROWSER ─────────────────────────────────────────────────
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)
driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()), options=options
)

def login():
    driver.get("https://www.naukri.com/nlogin/login")
    time.sleep(3)
    driver.find_element(By.ID, "usernameField").send_keys(EMAIL)
    driver.find_element(By.ID, "passwordField").send_keys(PASSWORD)
    driver.find_element(
        By.XPATH, "//button[contains(text(),'Login') or @type='submit']"
    ).click()
    time.sleep(4)
    print(f"Logged in. URL: {driver.current_url}")

def dump_element(el, indent=0):
    """Print tag, classes, text snippet of an element."""
    try:
        tag     = el.tag_name
        classes = el.get_attribute("class") or ""
        id_attr = el.get_attribute("id") or ""
        text    = el.text.strip()[:60].replace("\n", " ")
        role    = el.get_attribute("role") or ""
        typ     = el.get_attribute("type") or ""
        prefix  = "  " * indent
        parts   = [f"{prefix}<{tag}"]
        if id_attr:   parts.append(f" id='{id_attr}'")
        if classes:   parts.append(f" class='{classes[:80]}'")
        if typ:       parts.append(f" type='{typ}'")
        if role:      parts.append(f" role='{role}'")
        if text:      parts.append(f"> {text!r}")
        else:         parts.append(">")
        print("".join(parts))
    except Exception:
        pass

def inspect_panel():
    print("\n" + "="*60)
    print("INSPECTING PAGE DOM FOR CHATBOT PANEL")
    print("="*60)

    # 1. Print current URL
    print(f"\nCurrent URL: {driver.current_url}")

    # 2. Find ALL elements with class names containing common keywords
    keywords = [
        "chatbot", "chat", "bot", "apply", "widget",
        "panel", "question", "questionnaire", "modal",
        "popup", "drawer", "sidebar", "overlay",
        "recruiter", "ssrc", "apply-chatbot",
    ]

    print("\n── Scanning all elements with relevant class names ──")
    found_elements = {}
    all_els = driver.find_elements(By.XPATH, "//*[@class]")
    for el in all_els:
        try:
            if not el.is_displayed():
                continue
            cls = (el.get_attribute("class") or "").lower()
            for kw in keywords:
                if kw in cls:
                    tag = el.tag_name
                    key = f"{tag}.{cls[:60]}"
                    if key not in found_elements:
                        found_elements[key] = el
                        break
        except Exception:
            pass

    print(f"Found {len(found_elements)} unique visible elements with relevant classes:\n")
    for key, el in list(found_elements.items())[:30]:
        dump_element(el, indent=1)

    # 3. Find all visible inputs/radios/textareas
    print("\n── All visible INPUT elements ──")
    inputs = driver.find_elements(By.XPATH, "//input[not(@type='hidden')]")
    for inp in inputs:
        try:
            if inp.is_displayed():
                dump_element(inp, indent=1)
        except Exception:
            pass

    # 4. Find all visible radio buttons specifically
    print("\n── All visible RADIO buttons ──")
    radios = driver.find_elements(By.XPATH, "//input[@type='radio']")
    for r in radios:
        try:
            if r.is_displayed():
                # Print radio + its parent label text
                parent_text = driver.execute_script(
                    "return arguments[0].closest('label,li,div') ? "
                    "arguments[0].closest('label,li,div').textContent.trim() : '';",
                    r
                )
                print(f"    RADIO: value='{r.get_attribute('value')}' "
                      f"label='{parent_text[:50]}'")
        except Exception:
            pass

    # 5. Find all visible buttons
    print("\n── All visible BUTTON elements ──")
    btns = driver.find_elements(By.TAG_NAME, "button")
    for btn in btns:
        try:
            if btn.is_displayed() and btn.text.strip():
                cls = btn.get_attribute("class") or ""
                print(f"    BUTTON text='{btn.text.strip()}' "
                      f"class='{cls[:60]}'")
        except Exception:
            pass

    # 6. Try to find question text using XPath text search
    print("\n── Elements containing question keywords ──")
    q_keywords = [
        "notice period", "how many years", "experience",
        "current ctc", "expected ctc", "residing", "city",
        "monitoring", "it support"
    ]
    for kw in q_keywords:
        try:
            els = driver.find_elements(
                By.XPATH, f"//*[contains(translate(text(),"
                f"'ABCDEFGHIJKLMNOPQRSTUVWXYZ',"
                f"'abcdefghijklmnopqrstuvwxyz'),'{kw}')]"
            )
            for el in els:
                try:
                    if el.is_displayed() and el.text.strip():
                        cls = el.get_attribute("class") or ""
                        print(f"  [{kw}] <{el.tag_name} class='{cls[:50]}'>"
                              f" {el.text.strip()[:80]!r}")
                except Exception:
                    pass
        except Exception:
            pass

    # 7. Print full outer HTML of the first chatbot-looking container
    print("\n── Outer HTML of first chatbot container ──")
    for sel in [
        "[class*='chatbot']", "[class*='applyWidget']",
        "[class*='apply-widget']", "[class*='ssrc']",
        "[class*='recruiter']", "[class*='bot']",
    ]:
        try:
            els = driver.find_elements(By.CSS_SELECTOR, sel)
            for el in els:
                if el.is_displayed() and len(el.text.strip()) > 10:
                    html = driver.execute_script(
                        "return arguments[0].outerHTML;", el
                    )
                    print(f"\nSelector: {sel}")
                    print(f"Text content: {el.text.strip()[:200]!r}")
                    print(f"Outer HTML (first 800 chars):\n{html[:800]}")
                    break
        except Exception:
            pass

    print("\n" + "="*60)
    print("INSPECTION COMPLETE")
    print("="*60)


try:
    print("Step 1: Logging in...")
    login()

    print(f"\nStep 2: Opening job URL...")
    driver.get(JOB_URL)
    time.sleep(4)

    print("\nStep 3: Looking for Apply button...")
    T = "translate(text(),'abcdefghijklmnopqrstuvwxyz','ABCDEFGHIJKLMNOPQRSTUVWXYZ')"
    apply_btn = None
    for xpath in [
        f"//button[contains({T},'APPLY')]",
        f"//a[contains({T},'APPLY')]",
        "//button[@id='apply-button']",
    ]:
        try:
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            apply_btn = WebDriverWait(driver, 8).until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            )
            print(f"  Found Apply button: {apply_btn.text!r}")
            break
        except Exception:
            continue

    if apply_btn:
        apply_btn.click()
        print("  Clicked Apply — waiting 4s for chatbot panel...")
        time.sleep(4)
        inspect_panel()
    else:
        print("  Apply button not found — inspecting current page anyway")
        inspect_panel()

    input("\n\n>>> Chatbot panel should now be visible in browser.\n"
          ">>> Press ENTER to inspect again after panel loads fully: ")
    inspect_panel()

finally:
    input("\n>>> Press ENTER to close browser...")
    driver.quit()