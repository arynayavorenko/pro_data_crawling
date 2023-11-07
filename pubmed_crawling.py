import threading
from selenium import webdriver
from bs4 import BeautifulSoup

driver = webdriver.Chrome()
base_url = 'https://pubmed.ncbi.nlm.nih.gov/?term=Pain%20management&page={}'

def extract_article_content(article_url): # getting the data from the both sections
    driver.get(article_url)
    page_source = driver.page_source
    return page_source

article_links = []

# Function for a single page scrape
def scrape_page(page_num):
    page_url = base_url.format(page_num)
    driver.get(page_url)
    content = driver.page_source
    soup = BeautifulSoup(content, 'html.parser')

    # Find all elements with class 'docsum-title' (titles)
    title_elements = soup.find_all('a', class_='docsum-title')

    for title_element in title_elements:
        # Get the article URL for the current title
        article_url = 'https://pubmed.ncbi.nlm.nih.gov' + title_element.get('href')

        article_links.append(article_url)

num_pages = 17560 # setting to the total number of pages you want to scrape

num_threads = 5 # setting number of threads


threads = []

pages_per_thread = num_pages // num_threads

for i in range(num_threads): # adding multithreading to crawling prosses
    start_page = i * pages_per_thread + 1
    end_page = (i + 1) * pages_per_thread if i < num_threads - 1 else num_pages
    thread = threading.Thread(target=lambda: [scrape_page(page) for page in range(start_page, end_page + 1)])
    threads.append(thread)
    thread.start()

for thread in threads:
    thread.join()

with open('pubmed_links.txt', 'w', encoding='utf-8') as file: # appending the data to file
    for link in article_links:
        file.write(f'{link}\n')

print(f"Extracted {len(article_links)} article links. Data has been written to pubmed_links.txt")
