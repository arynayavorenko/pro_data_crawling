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

    def get_posts(self, subreddit_url, output_file_titles, output_file_articles, output_file_links):
        self.driver.get(subreddit_url)
        self.driver.maximize_window()
        time.sleep(5)
        html = self.lazy_scroll()
        parser = BeautifulSoup(html, 'html.parser')

        post_titles = parser.find_all('div', {'class': 'font-bold text-neutral-content-strong m-0 text-18 mb-2xs xs:mb-xs'})
        post_articles = parser.find_all('div', {'class': 'text-neutral-content md max-h-[337px] overflow-hidden text-12 xs:text-14'})
        post_links = parser.find_all('a', {'class': 'absolute inset-0'})

        print(f"Total posts: {len(post_titles)}")

        with open(output_file_titles, 'a', encoding='utf-8') as file_titles, \
             open(output_file_articles, 'a', encoding='utf-8') as file_articles, \
             open(output_file_links, 'a', encoding='utf-8') as file_links:

            for post_title, post_article, post_link in zip(post_titles, post_articles, post_links):
                title_text = post_title.text.strip()
                article_text = post_article.text.strip()
                link_text = post_link['href']

                file_titles.write(f"Title: {title_text}\n")
                file_articles.write(f"Article: {article_text}\n\n")
                file_links.write(f"Link: {link_text}\n")

    def destroy(self):
        self.driver.close()

# Example usage
subreddit_url = 'https://www.reddit.com/r/AskDocs/'
output_file_titles = 'titles.txt'
output_file_articles = 'articles.txt'
output_file_links = 'links.txt'

scraper = ScrapeReddit()
scraper.get_posts(subreddit_url, output_file_titles, output_file_articles, output_file_links)
scraper.destroy()
