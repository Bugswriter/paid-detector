from urllib.parse import urlparse
import re
import subprocess
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from flask import Flask, request

def are_domains_similar(url1, url2):
    # Parse the URLs
    parsed_url1 = urlparse(url1)
    parsed_url2 = urlparse(url2)

    # Normalize the domains (remove protocol and convert to lowercase)
    domain1 = parsed_url1.netloc.lower()
    domain2 = parsed_url2.netloc.lower()

    # Check if one domain is a substring of the other
    return domain1 in domain2 or domain2 in domain1

class SiteScraper:
    def scrape_site(self, url):
        html_content = get_html_content(url)

        if html_content is None:
            return f"Skipping {url} due to redirect.\n{'-'*50}"

        cleaned_content = clean_html_content(html_content)
        return f"\n{'-'*50}\nContent {url}:\n{cleaned_content}\n{'-'*50}"

def get_html_content(url):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")  # headless mode 
    prefs = {"profile.managed_default_content_settings.images": 2}  # 2: Block images
    chrome_options.add_experimental_option("prefs", prefs)

    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_page_load_timeout(15)  # Set page load timeout

        original_url = url
        driver.get(url)

        # Check if there was a redirect with a more lenient comparison
        current_url = driver.execute_script("return window.location.href;")
        if not are_domains_similar(original_url, current_url):
            print(f"Redirect detected from {original_url} to {current_url}")
            return None

        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.TAG_NAME, 'body'))
        )

        html_content = driver.page_source
        return html_content
    except Exception as e:
        print(f"Error {e}")
        return None
    finally:
        driver.quit()

def clean_html_content(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')

    # Remove da headers
    for header in soup(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
        header.decompose()

    # Strip HTML tags la
    cleaned_content = ' '.join(soup.stripped_strings)
    return cleaned_content

def paid_detector(url_input):
    scraper = SiteScraper()
    raw_site_data = scraper.scrape_site(url_input)
    if raw_site_data.startswith("Skipping"):
        return "UNPAID"  # Assuming False indicates an unpaid site

    if len(raw_site_data) < 60:
        print("Length reason")
        return "UNPAID"  # Assuming False indicates an unpaid site
        
    string_lines = raw_site_data.splitlines()
    raw_site = " ".join(string_lines)

    prompt = f"I'm providing some raw data which I got from homepage of a website, you need to analyse and tell me, if you think, this website is categorized as some sort of manufacturer of anything physical (for example - screw, fan, industry part, some product)? Answer format should be only - one word - YES or NO (just make your prediction, doesn't matter if it go wrong), also any non english website is NO - raw data ==> {raw_site}"

    if len(prompt) > 3800:
        prompt = prompt[:3800] 

    comm = f"tgpt -q --provider phind \"{prompt}\""
    try:
        output = subprocess.check_output(comm, shell=True, text=True).strip()
    except Exception as e:
        print(f"ERROR -> {e}")

    if 'output' not in locals():
        print("No output from tgpt")
        return f"UNPAID - {url_input}"

    if output == "YES":
        return f"PAID - {url_input}"  # Assuming True indicates a paid site
    if not are_domains_similar(original_url, current_url):
        return False
    elif output == "NO":
        return f"UNPAID - {url_input}"  # Assuming False indicates an unpaid site
    else:
        return False  # Assuming False indicates an unknown status

def detect_url_work(url):
    if re.search(r'\.org\b', url):
        return False
    elif re.search(r'\.gov\b', url):
        return False
    elif re.search(r'\.edu\b', url):
        return False
    else:
        return True
    
app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def main():
    if request.method == "POST":
        url = request.form.get("url")
        
        if not detect_url_work(url):
            return {"result": "UNPAID"}  # Assuming False indicates an unpaid site
        
        result = paid_detector(url).split(' ')[0]
        
        if result:
            return {"result": "PAID"}  # Assuming True indicates a paid site
        else:
            return {"result": "UNPAID"}  # Assuming False indicates an unpaid site
    else:
        return """
        <form action='/' method='POST'>
        <input type='text' name='url' placeholder='Enter Domain'>
        <button>Detect</button>
        </form>
        """

app.run(host="0.0.0.0")
