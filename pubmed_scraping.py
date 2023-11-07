from selenium import webdriver
from bs4 import BeautifulSoup

driver = webdriver.Chrome()
base_url = 'https://pubmed.ncbi.nlm.nih.gov/?term=Pain%20management&page={}'

def extract_article_content(article_url): #function for finding the needed data
    driver.get(article_url)
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')

    abstract_content = soup.select_one('div.abstract-content.selected')
    sub_title = soup.select_one('div.sub-title')

    content = ""

    if abstract_content:
        paragraphs = [p.text.strip() for p in abstract_content.find_all('p') if p.text.strip()]   # deleting empy spaces around data we got
        content += "\n".join(paragraphs)
# sometimes the articles are stored in abstract_content and in sub_title, so checking both
    if sub_title:
        content += "\n" + sub_title.text.strip()

    return content if content.strip() else "THERE IS NOT ANY ARTICLE"

titles_and_articles = []

for page_num in range(1, 17561): #adjust the pages number. the total number is 17,560
    page_url = base_url.format(page_num)
    driver.get(page_url)
    content = driver.page_source
    soup = BeautifulSoup(content, 'html.parser')

    title_elements = soup.find_all('a', class_='docsum-title')

    for title_element in title_elements:
        title_text = title_element.text.strip()

        date_element = title_element.find_next('span', class_='docsum-journal-citation short-journal-citation')
        date_string = date_element.text if date_element else ""
        year = date_string.split('. ')[-1].rstrip('.') if date_string else ""

        if year.isnumeric() and int(year) >= 2018: # checking the publication date
            article_url = 'https://pubmed.ncbi.nlm.nih.gov' + title_element.get('href') # getting the article URL for the current title


            article_content = extract_article_content(article_url)

            titles_and_articles.append((title_text, article_content))

with open('pubmed_titles_and_articles.txt', 'w', encoding='utf-8') as file: # appending the sorted data
    for title, article in titles_and_articles:
        file.write(f'The title is: {title}\n')
        file.write(f'The article is: {article}\n\n')

print(f"Extracted {len(titles_and_articles)} titles and articles published after 2018. Data has been written to pubmed_titles_and_articles.txt")
