from selenium import webdriver
from bs4 import BeautifulSoup
import re

base_url = 'https://pubmed.ncbi.nlm.nih.gov/?term=Pain+management+guidelines&page={}'

driver = webdriver.Chrome()

try:
    # Maintain a set to store unique PMIDs or titles
    processed_items = set()

    with open('pubmed_t&a_pain_guidelines.txt', 'a', encoding='utf-8') as title_file, \
            open('pubmed_l_pain_guidelines.txt', 'a', encoding='utf-8') as link_file:

        for page_number in range(1, 4):  # Adjust the range accordingly
            url = base_url.format(page_number)
            driver.get(url)
            driver.implicitly_wait(5)
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            docsums = soup.find_all('div', class_='docsum-content')

            for docsum in docsums:
                no_abstract = docsum.find('span', class_='no-abstract')
                if not no_abstract:
                    pub_date_span = docsum.find('span', class_='docsum-journal-citation')
                    if pub_date_span:
                        pub_date_text = pub_date_span.text
                        match = re.search(r'\b\d{4}\b', pub_date_text)
                        if match and int(match.group()) > 2018:
                            title_elem = docsum.find('a', class_='docsum-title')
                            title = title_elem.text.strip()

                            # Extract PMID
                            pmid_span = docsum.find('span', class_='docsum-pmid')
                            pmid = pmid_span.text.strip() if pmid_span else ''

                            # Check if title or PMID is already processed
                            if title not in processed_items and pmid not in processed_items:
                                # Write title and PMID to the title file
                                title_file.write(f"{title}\n")

                                # Construct URL for the article page
                                article_url = f'https://pubmed.ncbi.nlm.nih.gov/{pmid}/'
                                link_file.write(f"{article_url}\n")

                                driver.get(article_url)
                                driver.implicitly_wait(5)
                                article_source = driver.page_source
                                article_soup = BeautifulSoup(article_source, 'html.parser')

                                # Extract and write article content
                                article_content = article_soup.find('div', class_='abstract-content selected')
                                if article_content:
                                    article_text = article_content.get_text(strip=True)
                                    title_file.write(f"Article:{article_text}\n\n")

                                # Add the title or PMID to the processed set
                                processed_items.add(title)
                                processed_items.add(pmid)

finally:
    driver.quit()
