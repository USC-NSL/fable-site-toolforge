import mysql.connector
import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import unquote, quote


def fetch_original_text(article_url, search_url):
    try:
        response = requests.get(article_url, timeout=30)
        soup = BeautifulSoup(response.text, "html.parser")

        citations = soup.find_all("cite", class_="citation web cs1")
        search_url_clean = unquote(search_url).lower()

        for citation in citations:
            links = citation.find_all("a", class_="external text")

            for link in links:
                href = link.get("href", "").lower()
                if search_url_clean in href or href in search_url_clean:
                    print('-' * 25)
                    print(f"{href}")
                    print(f"{search_url_clean}")
                    print('-' * 25)
                    link_text = link.text.strip('"')
                    if link_text and link_text != "Archived":
                        return link_text

        print(f"Debug - URL not found in citations. Searching for: {search_url}")
        print("Found citations:", len(citations))
        return None

    except Exception as e:
        print(f"Error fetching original text: {e}")
        return None


def fetch_page_text(url):
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        return soup.title.string if soup.title else None
    except Exception as e:
        print(f"Error fetching page: {e}")
        return None


def test_run():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="fable",
        database="s55570__fable",
    )
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, article, link, alias FROM aliases WHERE feedbackSelection = 'Incorrect' LIMIT 5"
    )
    rows = cursor.fetchall()

    print("Testing with Incorrect feedback rows:")
    print("-" * 50)

    sleep_time = 1

    for row in rows:
        id, article_url, link, alias = row

        print(f"\nProcessing row {id}:")
        print(f"Article URL: {article_url}")
        print(f"Link: {link}")
        print(f"Alias: {alias}")

        link_title = fetch_original_text(article_url, link)
        print(f"Found link title: {link_title}")
        time.sleep(sleep_time)

        alias_title = fetch_page_text(alias)
        print(f"Found alias title: {alias_title}")
        time.sleep(sleep_time)

        print("-" * 50)

    cursor.close()
    conn.close()


def update_run():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="fable",
        database="s55570__fable",
    )
    cursor = conn.cursor()

    cursor.execute("SELECT id, article, link, alias FROM aliases")
    rows = cursor.fetchall()

    print(f"Processing {len(rows)} rows...")
    print("-" * 50)

    sleep_time = 1

    for row in rows:
        id, article_url, link, alias = row

        print(f"\nProcessing row {id}:")
        print(f"Article URL: {article_url}")
        print(f"Link: {link}")
        print(f"Alias: {alias}")

        link_title = fetch_original_text(article_url, link)
        print(f"Found link title: {link_title}")
        time.sleep(sleep_time)

        alias_title = fetch_page_text(alias)
        print(f"Found alias title: {alias_title}")
        time.sleep(sleep_time)

        if link_title is not None or alias_title is not None:
            try:
                cursor.execute(
                    "UPDATE aliases SET link_title = %s, alias_title = %s WHERE id = %s",
                    (link_title, alias_title, id),
                )
                conn.commit()
                print(f"Updated row {id} with titles")
            except Exception as e:
                print(f"Error updating row {id}: {e}")
        else:
            print(f"Skipping row {id} - no titles found")

        print("-" * 50)

    cursor.close()
    conn.close()


if __name__ == "__main__":
    update_run()
