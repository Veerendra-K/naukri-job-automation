"""
Naukri.com Job Application Automation Script
For: Veerendra K | Target: IT/DevOps/Cloud/Full-Stack roles
Requirements: pip install selenium webdriver-manager openpyxl
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill, Alignment
from datetime import datetime
import time
import random
import os
import logging

# ─────────────────────────────────────────────
#  CONFIGURATION — Edit these before running
# ─────────────────────────────────────────────
CONFIG = {
    "email": "",
    "password": "",

    # Target job titles to search
    "target_titles": [
        "Technical Support Engineer",
        "IT Technician",
        "IT Support Engineer",
        "IT Support Specialist",
        "Technical Specialist",
        "L2 Support Engineer",
        "IT Service Desk",
        "IT Technical Support"
    ],

    # Preferred locations
    "locations": ["Bengaluru", "Bangalore"],

    # Core skills — at least 3 of 5 must appear in JD to apply
"core_skills": [
    "ServiceNow", "ITIL", "Windows", "Troubleshooting", "IT Support"
],
"min_skill_match": 3,

# All skills for broader matching
"all_skills": [
    # ITSM & Frameworks
    "ServiceNow", "ITIL", "Incident Management", "RCA", "Root Cause Analysis",
    "Change Management", "Problem Management", "KB Documentation",

    # Operating Systems
    "Windows 10", "Windows 11", "macOS", "Linux", "Windows Server",
    "Active Directory",

    # Remote & Support Tools
    "LogMeIn", "Bomgar", "Microsoft Remote Desktop", "Webex", "Zoom",
    "Freshdesk", "Jira", "Helpdesk",

    # Networking
    "TCP/IP", "DNS", "DHCP", "VPN", "Network Troubleshooting",

    # Cloud & Virtualisation
    "AWS", "EC2", "IAM", "VMware", "Citrix", "Docker", "Kubernetes",
    "Cloud Infrastructure",

    # Hardware & Deployment
    "OS Imaging", "Device Deployment", "MDM", "ITAM",
    "Asset Management", "Dell", "HP", "Lenovo",

    # Scripting & Dev
    "Python", "Shell Scripting", "SQL", "Git", "Node.js",
    "Automation", "CI/CD",

    # Soft / Role Keywords
    "IT Technician", "IT Support", "Desktop Support", "Service Desk",
    "Technical Support", "L1", "L2", "T2", "T3",
    "Escalation", "SLA", "First Call Resolution", "FCR",
],

    # Application limits
    "max_applications_per_day": 40,
    "search_interval_minutes": 30,

    # Experience filter (years)
    "exp_min": 1,
    "exp_max": 3,

    # Log file for applications
    "log_file": "naukri_application_log.xlsx",
    "run_log": "naukri_run.log",
}

# ─────────────────────────────────────────────
#  LOGGING SETUP
# ─────────────────────────────────────────────
logging.basicConfig(
    filename=CONFIG["run_log"],
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────
#  APPLICATION LOG (Excel)
# ─────────────────────────────────────────────
def init_log_file():
    """Create or load the Excel application log."""
    if os.path.exists(CONFIG["log_file"]):
        return load_workbook(CONFIG["log_file"])

    wb = Workbook()
    ws = wb.active
    ws.title = "Application Log"

    headers = [
        "Date", "Time", "Company Name", "Job Title",
        "Location", "Skills Matched", "Job Link", "Status"
    ]
    header_fill = PatternFill("solid", fgColor="1F4E79")
    header_font = Font(bold=True, color="FFFFFF", name="Arial", size=11)

    for col, h in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=h)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center")

    col_widths = [12, 10, 30, 35, 15, 30, 60, 15]
    for i, w in enumerate(col_widths, 1):
        ws.column_dimensions[ws.cell(1, i).column_letter].width = w

    wb.save(CONFIG["log_file"])
    return wb


def log_application(company, title, location, skills_matched, link, status="Applied"):
    """Append a row to the Excel application log."""
    wb = load_workbook(CONFIG["log_file"])
    ws = wb.active
    now = datetime.now()

    row_data = [
        now.strftime("%Y-%m-%d"),
        now.strftime("%H:%M:%S"),
        company,
        title,
        location,
        ", ".join(skills_matched),
        link,
        status,
    ]

    # Alternate row shading
    next_row = ws.max_row + 1
    fill_color = "D6E4F0" if next_row % 2 == 0 else "FFFFFF"
    row_fill = PatternFill("solid", fgColor=fill_color)

    for col, val in enumerate(row_data, 1):
        cell = ws.cell(row=next_row, column=col, value=val)
        cell.fill = row_fill
        cell.font = Font(name="Arial", size=10)
        cell.alignment = Alignment(horizontal="left")

    wb.save(CONFIG["log_file"])
    logger.info(f"APPLIED → {company} | {title} | {link}")
    print(f"  ✅ Applied: {company} — {title}")


# ─────────────────────────────────────────────
#  BROWSER SETUP
# ─────────────────────────────────────────────
def create_driver():
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    import subprocess

    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    # Force fresh driver download matching your Chrome version
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    driver.execute_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    )
    return driver


# ─────────────────────────────────────────────
#  LOGIN
# ─────────────────────────────────────────────
def login(driver):
    print("🔐 Logging in to Naukri.com...")
    driver.get("https://www.naukri.com/nlogin/login")
    wait = WebDriverWait(driver, 15)

    try:
        # Using exact IDs found from diagnostic
        email_field = wait.until(EC.presence_of_element_located(
            (By.ID, "usernameField")
        ))
        email_field.clear()
        email_field.send_keys(CONFIG["email"])

        pwd_field = driver.find_element(By.ID, "passwordField")
        pwd_field.clear()
        pwd_field.send_keys(CONFIG["password"])

        # Click login button
        login_btn = driver.find_element(
            By.XPATH, "//button[contains(text(),'Login') or @type='submit']"
        )
        login_btn.click()

        time.sleep(4)  # Wait for redirect
        print("✅ Login successful. URL:", driver.current_url)
        logger.info("Login successful.")

    except Exception as e:
        logger.error(f"Login failed: {e}")
        raise RuntimeError(f"Login failed: {e}")


# ─────────────────────────────────────────────
#  SKILL MATCHING
# ─────────────────────────────────────────────
def get_skill_matches(jd_text):
    """Return list of core skills found in the job description."""
    jd_lower = jd_text.lower()
    return [skill for skill in CONFIG["core_skills"] if skill.lower() in jd_lower]


def is_good_match(jd_text):
    """True if at least min_skill_match core skills appear in the JD."""
    return len(get_skill_matches(jd_text)) >= CONFIG["min_skill_match"]



# ─────────────────────────────────────────────
#  QUESTIONNAIRE HANDLER
# ─────────────────────────────────────────────
QUESTIONNAIRE_ANSWERS = {
    # Yes/No fields — mapped to your actual resume skills
    "linux":                    "Yes",
    "windows":                  "Yes",
    "macos":                    "Yes",
    "troubleshooting":          "Yes",
    "itil":                     "Yes",
    "aws":                      "Yes",
    "docker":                   "Yes",
    "servicenow":               "Yes",
    "active directory":         "Yes",
    "vpn":                      "Yes",
    "networking":               "Yes",
    "remote support":           "Yes",
    "hardware support":         "Yes",
    "sql":                      "Yes",
    "python":                   "Yes",
    "vmware":                   "Yes",
    "citrix":                   "Yes",
    "logmein":                  "Yes",
    "bomgar":                   "Yes",
    "jira":                     "Yes",
    "freshdesk":                "Yes",
    "incident management":      "Yes",
    "root cause analysis":      "Yes",
    "asset management":         "Yes",
    "os imaging":               "Yes",
    "shift":                    "Yes",   # rotational / flexible shifts
    "immediate joiner":         "Yes",
    "bangalore":                "Yes",
    "bengaluru":                "Yes",

    # Open-ended fallback — covers most common application questions
    "open_ended": (
        "I have 2+ years of hands-on enterprise IT support experience at Motorola Solutions India, "
        "where I served as the primary L1/L2 helpdesk contact for 500+ enterprise users, resolving "
        "50+ ServiceNow incidents per week across hardware, software, VPN, and network issues while "
        "consistently exceeding SLA targets. My day-to-day work involves remote support via LogMeIn, "
        "Bomgar, and Microsoft Remote Desktop; end-to-end device deployment including OS imaging and "
        "software provisioning for Windows and macOS laptops; Root Cause Analysis on recurring system "
        "issues; and IT Asset Management including hardware lifecycle planning. I also have hands-on "
        "experience with AWS (EC2, IAM), VMware, Citrix, Active Directory, TCP/IP networking, and "
        "Python and Shell scripting for automation. Prior to this, at Thought Frameworks, I supported "
        "a 70+ user engineering environment, managed Jira tickets for bug tracking and change requests, "
        "administered SVN repositories, and worked closely with DevOps and QA teams on CI/CD pipeline "
        "stability. I am currently pursuing my ITIL 4 Foundation certification and actively learning "
        "Docker and Kubernetes. I am an immediate joiner, flexible for rotational shifts including "
        "night shifts, and available for on-site, hybrid, or remote roles in Bengaluru."
    ),
}


def handle_questionnaire(driver):
    """Detect and answer common application questionnaire fields."""
    try:
        questions = driver.find_elements(
            By.CSS_SELECTOR,
            ".chatbot-question, .apply-question, "
            ".application-question, [data-testid='question'], "
            ".jobs-easy-apply-form-element"   # LinkedIn easy apply
        )
        for q in questions:
            q_text = q.text.lower()
            answered = False

            # ── Yes / No radio buttons ────────────────────────────────────
            for keyword, answer in QUESTIONNAIRE_ANSWERS.items():
                if keyword == "open_ended":
                    continue
                if keyword in q_text:
                    try:
                        option = q.find_element(
                            By.XPATH,
                            f".//input[@type='radio']"
                            f"[following-sibling::label"
                            f"[contains(translate(text(),'abcdefghijklmnopqrstuvwxyz',"
                            f"'ABCDEFGHIJKLMNOPQRSTUVWXYZ'),'{answer.upper()}')]]"
                        )
                        driver.execute_script("arguments[0].click();", option)
                        answered = True
                        break
                    except Exception:
                        pass

            # ── Dropdown selects (Yes/No dropdowns) ──────────────────────
            if not answered:
                for keyword, answer in QUESTIONNAIRE_ANSWERS.items():
                    if keyword == "open_ended":
                        continue
                    if keyword in q_text:
                        try:
                            from selenium.webdriver.support.ui import Select
                            select_el = q.find_element(By.TAG_NAME, "select")
                            Select(select_el).select_by_visible_text(answer)
                            answered = True
                            break
                        except Exception:
                            pass

            # ── Years of experience numeric fields ────────────────────────
            if not answered:
                try:
                    num_input = q.find_element(
                        By.XPATH,
                        ".//input[@type='number' or @type='text'"
                        " and contains(@placeholder,'year')]"
                    )
                    if any(k in q_text for k in [
                        "year", "experience", "servicenow", "itil",
                        "windows", "linux", "aws", "support"
                    ]):
                        num_input.clear()
                        num_input.send_keys("2")   # your actual years
                        answered = True
                except Exception:
                    pass

            # ── Open-ended textarea fallback ──────────────────────────────
            if not answered:
                try:
                    textarea = q.find_element(By.TAG_NAME, "textarea")
                    textarea.clear()
                    textarea.send_keys(QUESTIONNAIRE_ANSWERS["open_ended"])
                except Exception:
                    pass

    except Exception as e:
        logger.warning(f"Questionnaire handling issue: {e}")



# ─────────────────────────────────────────────
#  APPLY TO A SINGLE JOB
# ─────────────────────────────────────────────
def apply_to_job(driver, job_url, company, title, location, skills_matched):
    """Navigate to job and attempt to apply."""
    try:
        driver.get(job_url)
        time.sleep(random.uniform(3, 5))
        wait = WebDriverWait(driver, 10)

        # Find apply button — multiple selector attempts
        apply_btn = None
        apply_xpaths = [
            "//button[contains(translate(text(),'abcdefghijklmnopqrstuvwxyz','ABCDEFGHIJKLMNOPQRSTUVWXYZ'),'APPLY')]",
            "//a[contains(translate(text(),'abcdefghijklmnopqrstuvwxyz','ABCDEFGHIJKLMNOPQRSTUVWXYZ'),'APPLY')]",
            "//button[@id='apply-button']",
            "//*[contains(@class,'apply-btn') or contains(@class,'applyBtn')]",
        ]
        for xpath in apply_xpaths:
            try:
                apply_btn = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
                break
            except Exception:
                continue

        if not apply_btn:
            print(f"  ⚠️  No apply button found: {company} — {title}")
            log_application(company, title, location, skills_matched, job_url, "Apply Btn Missing")
            return False

        apply_btn.click()
        time.sleep(random.uniform(2, 3))

        # Handle questionnaire if present
        handle_questionnaire(driver)

        # Submit if needed
        for submit_xpath in [
            "//button[contains(text(),'Submit')]",
            "//button[contains(text(),'Apply Now')]",
            "//button[contains(text(),'Confirm')]",
        ]:
            try:
                btn = driver.find_element(By.XPATH, submit_xpath)
                btn.click()
                time.sleep(1.5)
                break
            except Exception:
                continue

        log_application(company, title, location, skills_matched, job_url, "Applied")
        return True

    except Exception as e:
        logger.error(f"Apply failed at {job_url}: {e}")
        return False


# ─────────────────────────────────────────────
#  SEARCH & COLLECT JOB LISTINGS
# ─────────────────────────────────────────────
def search_jobs(driver, title, location):
    """Search Naukri and return list of (title, company, location, link) tuples."""
    keyword = title.lower().replace(" ", "-")
    loc     = location.lower().replace(" ", "-")
    search_url = (
        f"https://www.naukri.com/{keyword}-jobs-in-{loc}"
        f"?experienceDD={CONFIG['exp_min']}"
    )
    print(f"\n🔍 Searching: {title} in {location}")
    driver.get(search_url)
    time.sleep(random.uniform(4, 6))

    jobs = []
    try:
        # Updated selectors for 2025/2026 Naukri layout
        card_selectors = [
            "article.jobTuple",
            ".cust-job-tuple",
            "div.srp-jobtuple-wrapper",
            "[class*='jobTuple']",
            "[class*='job-tuple']",
            "div.list > article",
        ]
        cards = []
        for sel in card_selectors:
            cards = driver.find_elements(By.CSS_SELECTOR, sel)
            if cards:
                break

        # Fallback: find all job title links directly
        if not cards:
            links = driver.find_elements(
                By.XPATH,
                "//a[contains(@href,'naukri.com/job-listings') or contains(@class,'title')]"
            )
            print(f"  Found {len(links)} job links (fallback mode).")
            for lnk in links:
                href = lnk.get_attribute("href")
                title_text = lnk.text.strip()
                if href and title_text:
                    jobs.append((title_text, "Unknown", location, href))
            return jobs

        print(f"  Found {len(cards)} listings.")
        for card in cards:
            try:
                # Title + link
                link_el = card.find_element(
                    By.XPATH,
                    ".//a[contains(@class,'title') or contains(@class,'jobTitle') or @title]"
                )
                job_link  = link_el.get_attribute("href") or ""
                job_title = link_el.text.strip() or link_el.get_attribute("title") or "Unknown"
            except Exception:
                continue

            try:
                company = card.find_element(
                    By.XPATH,
                    ".//*[contains(@class,'comp-name') or contains(@class,'companyInfo') or contains(@class,'subTitle')]"
                ).text.strip()
            except Exception:
                company = "Unknown"

            try:
                loc_text = card.find_element(
                    By.XPATH,
                    ".//*[contains(@class,'loc') or contains(@class,'location') or contains(@class,'locWdth')]"
                ).text.strip()
            except Exception:
                loc_text = location

            if job_link:
                jobs.append((job_title, company, loc_text, job_link))

    except Exception as e:
        logger.warning(f"Search error for {title} in {location}: {e}")

    return jobs


def extract_job_details(card):
    """Extract title, company, location, link from a job card."""
    try:
        title = card.find_element(By.CSS_SELECTOR, ".title, .jobTitle").text.strip()
    except Exception:
        title = "Unknown Title"
    try:
        company = card.find_element(By.CSS_SELECTOR, ".subTitle, .companyInfo").text.strip()
    except Exception:
        company = "Unknown Company"
    try:
        location = card.find_element(By.CSS_SELECTOR, ".location, .locWdth").text.strip()
    except Exception:
        location = ""
    try:
        link_el = card.find_element(By.CSS_SELECTOR, "a.title, a.jobTitle, a[href*='naukri.com']")
        link = link_el.get_attribute("href")
    except Exception:
        link = ""
    return title, company, location, link


# ─────────────────────────────────────────────
#  FETCH JOB DESCRIPTION
# ─────────────────────────────────────────────
def get_jd_text(driver, job_url):
    """Open job URL in new tab and return full page text as JD."""
    try:
        driver.execute_script("window.open('');")
        driver.switch_to.window(driver.window_handles[-1])
        driver.get(job_url)
        time.sleep(random.uniform(3, 4))

        # Try specific selectors first
        jd_selectors = [
            ".job-desc",
            ".dang-inner-html",
            ".jd-desc",
            ".jobDescriptionText",
            "[class*='job-desc']",
            "[class*='description']",
            "[class*='JDC']",
            ".detail-view",
            "section.styles_job-desc-container__txpYf",
        ]
        text = ""
        for sel in jd_selectors:
            try:
                el = driver.find_element(By.CSS_SELECTOR, sel)
                text = el.text.strip()
                if len(text) > 100:  # Valid JD found
                    break
            except Exception:
                continue

        # Fallback: grab full page body text
        if len(text) < 100:
            text = driver.find_element(By.TAG_NAME, "body").text

        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        return text

    except Exception as e:
        logger.warning(f"JD fetch error for {job_url}: {e}")
        try:
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
        except Exception:
            pass
        return ""


# ─────────────────────────────────────────────
#  MAIN SEARCH + APPLY CYCLE
# ─────────────────────────────────────────────
def run_application_cycle(driver):
    print(f"\n{'='*55}")
    print(f"  🚀 Application Cycle Started — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*55}")

    applied_today = 0
    seen_links = set()

    for title in CONFIG["target_titles"]:
        if applied_today >= CONFIG["max_applications_per_day"]:
            print(f"\n⚠️  Daily limit of {CONFIG['max_applications_per_day']} reached.")
            break

        for location in CONFIG["locations"]:
            if applied_today >= CONFIG["max_applications_per_day"]:
                break

            jobs = search_jobs(driver, title, location)  # Now returns list of tuples

            for (job_title, company, job_loc, link) in jobs:
                if applied_today >= CONFIG["max_applications_per_day"]:
                    break
                if not link or link in seen_links:
                    continue
                seen_links.add(link)

                # Fetch JD and check skill match
                jd_text = get_jd_text(driver, link)
                if not jd_text:
                    print(f"  ⚠️  Empty JD: {company} — {job_title}")
                    continue

                matched = get_skill_matches(jd_text)
                match_count = len(matched)

                if match_count < CONFIG["min_skill_match"]:
                    print(f"  ⏭  Skipped ({match_count}/{CONFIG['min_skill_match']} skills): {company} — {job_title}")
                    continue

                print(f"  🎯 Match ({match_count} skills: {', '.join(matched)}): {company} — {job_title}")

                success = apply_to_job(driver, link, company, job_title, job_loc, matched)
                if success:
                    applied_today += 1

                time.sleep(random.uniform(8, 15))

    print(f"\n✅ Cycle complete. Applied to {applied_today} jobs this cycle.")
    logger.info(f"Cycle complete. Applied: {applied_today}")
    return applied_today





# ─────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────
def main():
    init_log_file()
    print("\n📋 Naukri Job Application Bot — Veerendra K")
    print(f"📍 Locations: {', '.join(CONFIG['locations'])}")
    print(f"🎯 Core Skills Required (≥{CONFIG['min_skill_match']} of 5): {', '.join(CONFIG['core_skills'])}")
    print(f"📊 Max Applications/Day: {CONFIG['max_applications_per_day']}")
    print(f"🔁 Search Interval: every {CONFIG['search_interval_minutes']} minutes\n")

    driver = create_driver()

    try:
        login(driver)
        cycle = 1
        while True:
            print(f"\n📌 Cycle #{cycle}")
            run_application_cycle(driver)
            cycle += 1
            wait_mins = CONFIG["search_interval_minutes"]
            print(f"\n⏳ Waiting {wait_mins} minutes before next cycle...")
            logger.info(f"Sleeping {wait_mins} minutes.")
            time.sleep(wait_mins * 60)

    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user.")
        logger.info("Bot stopped by user (KeyboardInterrupt).")
    except Exception as e:
        logger.critical(f"Unhandled error: {e}")
        print(f"\n❌ Fatal error: {e}")
    finally:
        driver.quit()
        print("🔒 Browser closed. Check naukri_application_log.xlsx for results.")


if __name__ == "__main__":
    main()
