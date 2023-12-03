from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time

class ScrapeReddit():
    def __init__(self):
        options = Options()
        self.driver = webdriver.Chrome(options=options)
        self.postids = []

    def lazy_scroll(self):
        current_height = self.driver.execute_script('return document.body.scrollHeight;')
        while True:
            self.driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
            time.sleep(2)
            new_height = self.driver.execute_script('return document.body.scrollHeight;')
            if new_height == current_height:
                html = self.driver.page_source
                break
            current_height = new_height
        return html

    def scrape_post(self, post_url, output_file, info_file):
        self.driver.get(post_url)
        self.driver.maximize_window()
        time.sleep(5)
        html = self.lazy_scroll()
        parser = BeautifulSoup(html, 'html.parser')

        # Find <div> with class "mb-sm mb-xs px-md xs:px-0"
        div_content = parser.find('div', {'class': 'mb-sm mb-xs px-md xs:px-0'})
        if div_content:
            div_text = div_content.get_text(strip=True)
            if not self.is_content_in_file(info_file, div_text):
                with open(info_file, 'a', encoding='utf-8') as file:
                    file.write(f"Content: {div_text}\n")

        # Find <h1> with id "post-title-t3_tfn5mr"
        h1_content = parser.find('h1', {'id': 'post-title-t3_tfn5mr'})
        if h1_content:
            h1_text = h1_content.get_text(strip=True)
            if not self.is_content_in_file(info_file, h1_text):
                with open(info_file, 'a', encoding='utf-8') as file:
                    file.write(f"Title: {h1_text}\n")

        # Find all divs with id="-post-rtjson-content"
        post_contents = parser.find_all('div', {'id': '-post-rtjson-content'})

        print(f"Total posts: {len(post_contents)}")

        existing_paragraphs = set()  # Set to store existing paragraphs in the output file

        # Read existing paragraphs from the file
        try:
            with open(output_file, 'r', encoding='utf-8') as file:
                for line in file:
                    if line.startswith("Paragraph:"):
                        existing_paragraphs.add(line.lstrip("Paragraph:").strip())
        except FileNotFoundError:
            pass  # File doesn't exist yet

        with open(output_file, 'a', encoding='utf-8') as file:
            for post_content in post_contents:
                # Find all <p> tags within the specified div
                paragraphs = post_content.find_all('p')
                for paragraph in paragraphs:
                    paragraph_text = paragraph.text.strip()
                    if paragraph_text not in existing_paragraphs:
                        file.write(f"Paragraph: {paragraph_text}\n")
                        existing_paragraphs.add(paragraph_text)

    def is_content_in_file(self, file_path, content):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return content in file.read()
        except FileNotFoundError:
            return False

    def destroy(self):
        self.driver.close()

# Example usage
post_url = 'https://www.reddit.com/r/medicine/comments/tfn5mr/how_do_you_deal_with_chronic_pain_patients_who/'
output_file = 'post_comments.txt'
info_file = 'post_info.txt'

scraper = ScrapeReddit()
scraper.scrape_post(post_url, output_file, info_file)
scraper.destroy()
