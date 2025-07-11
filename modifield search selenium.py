from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options  # Correct import
from selenium.webdriver.common.by import By
from urllib.parse import urlparse, urljoin
import time

class WebCrawler:
    def __init__(self, start_url):
        self.visited = set()
        self.queue = [start_url]
        self.domain = "eb360.hitachi-ebworx.com"
        self.max_depth = 3  # Safety limit
        self.delay = 0.1  # Seconds between requests
        self.file = 'crawler_results.txt'
        self.matching_urls = []  # List to store URLs containing the string 🔥

        # Initialize file
        with open(self.file, 'w', encoding='utf-8') as f:
            f.write(f"Starting crawl of: {start_url}\n\n")

        # Setup Selenium WebDriver
        self.options = Options()
        self.options.headless = True
        self.driver = webdriver.Chrome(service=Service("C:/Users/andrewhernando/Documents/extra/chromedriver-win64/chromedriver.exe"), options=self.options)  # Correct path to chromedriver

    def _same_domain(self, url):
        return urlparse(url).netloc == self.domain

    def _save_result(self, content):
        with open(self.file, 'a', encoding='utf-8') as f:
            f.write(content + '\n')

    def crawl(self):
        try:
            while self.queue:
                url = self.queue.pop(0)
                
                if url in self.visited:
                    continue
                
                if len(self.visited) >= 1000:  # Absolute safety limit
                    self._save_result("\nSAFETY LIMIT REACHED (1000 URLs)")
                    return

                try:
                    # Polite crawling delay
                    time.sleep(self.delay)

                    # Load the page using Selenium
                    self.driver.get(url)

                    # Allow time for JavaScript to load the page
                    time.sleep(2)  # Adjust as needed

                    self._save_result(f"Visited: {url}")
                    print(f"Crawling: {url}")

                    # Check for the string 🔥 in the page content
                    if "Yee Yan Shuen" in self.driver.page_source:
                        self.matching_urls.append(url)
                        self._save_result(f"String 🔥 found in: {url}")

                    # Extract links from the page
                    links = self.driver.find_elements(By.TAG_NAME, "a")
                    for link in links:
                        href = link.get_attribute("href")
                        if href:
                            # Join the URL with the base URL if it's a relative link
                            absolute_url = urljoin(url, href)
                            print(f"Found link: {absolute_url}")

                            # Check if the URL is new, belongs to the same domain, and is valid
                            if (absolute_url not in self.visited and 
                                absolute_url.startswith('http') and 
                                self._same_domain(absolute_url)):
                                self.queue.append(absolute_url)
                                self._save_result(f"Found: {absolute_url}")

                    self.visited.add(url)

                except Exception as e:
                    self._save_result(f"Error on {url}: {str(e)}")
                    continue

        except KeyboardInterrupt:
            self._save_result("\nCrawl interrupted by user")
            print("\nCrawl saved before exit")

        finally:
            self.driver.quit()

        # Save matching URLs to file
        with open(self.file, 'a', encoding='utf-8') as f:
            f.write("\nURLs containing the string 🔥:\n")
            for matching_url in self.matching_urls:
                f.write(matching_url + '\n')

# Usage (start with initial URL)
crawler = WebCrawler("https://eb360.hitachi-ebworx.com/")
crawler.crawl()
