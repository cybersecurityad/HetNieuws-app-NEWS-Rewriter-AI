import feedparser
import pymongo
import os
import time
import json
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# Set up Selenium
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--no-sandbox')

# Set up ChromeDriver path
chrome_driver_path = '/opt/homebrew/bin/chromedriver'  # Default Homebrew path for ChromeDriver
service = Service(chrome_driver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

def fetch_article_details_with_selenium(link):
    try:
        driver.get(link)
        time.sleep(3)  # Wait for the page to load
        page_source = driver.page_source
        return page_source
    except Exception as e:
        print(f"Failed to fetch article details from {link}. Exception: {e}")
        return "Full text not found."

def extract_generic_article_body(html_content):
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        article_body = soup.find('div', class_='post-content')  # Adjust the selector based on the website
        full_text = article_body.get_text(separator='\n').strip() if article_body else "Full text not found."
        print("Generic article body extracted.")
        return full_text
    except Exception as e:
        print(f"Error extracting article details: {e}")
        return "Full text not found."

def extract_nu_nl_article_body(html_content):
    try:
        start_token = '"articleBody":"'
        end_token = ',"wordCount":'

        start_index = html_content.find(start_token)
        end_index = html_content.find(end_token, start_index)

        if start_index != -1 and end_index != -1:
            start_index += len(start_token)
            full_text = html_content[start_index:end_index].replace('\\n', '\n').replace('\\"', '"')
            print("NU.nl article body extracted.")
            return full_text
        else:
            print("Failed to locate NU.nl article body using tokens.")
            return "Full text not found."
    except Exception as e:
        print(f"Error extracting NU.nl article details: {e}")
        return "Full text not found."

def extract_articles(rss_url, num_articles=5, is_nu_nl=False):
    feed = feedparser.parse(rss_url)
    articles = []
    print(f"Parsed RSS feed from {rss_url}")

    for entry in feed.entries[:num_articles]:
        title = entry.title
        link = entry.link
        print(f"Processing article: {title} - {link}")
        article = {"title": title, "link": link, "timestamp": datetime.now()}

        if is_nu_nl:
            page_source = fetch_article_details_with_selenium(link)
            full_text = extract_nu_nl_article_body(page_source)
        else:
            page_source = fetch_article_details_with_selenium(link)
            full_text = extract_generic_article_body(page_source)
        
        article["body"] = full_text
        articles.append(article)

    return articles

def display_menu():
    print("---------------------------------------------------")
    print("Welkom bij het RSS Artikelen Extractor")
    print("---------------------------------------------------")
    print("Menu:\n")
    print("1. Voer RSS-URL in")
    print("2. Voer categorie in")
    print("3. Voer aantal artikelen in")
    print("4. Extract Artikelen")
    print("5. Toon Artikelen")
    print("6. Geef een overzicht van de RSS kanalen")
    print("7. Extract Artikelen van NU.nl")
    print("8. Verwerk NU.nl artikelen uit MongoDB")
    print("9. Exit")

def get_user_choice():
    choice = input("Maak een keuze (1-9): ")
    return choice

def set_rss():
    rss_url = input("Voer RSS-feed URL in: ")
    print(f"RSS URL set to {rss_url}")
    return rss_url

def set_category():
    category = input("Voer categorie in: ")
    print(f"Categorie set to {category}")
    return category

def set_num_articles():
    num_articles = input("Voer aantal artikelen in: ")
    print(f"Aantal artikelen set to {num_articles}")
    return int(num_articles)

def show_articles(articles):
    for article in articles:
        print(f"Title: {article['title']}")
        print(f"Body: {article['body'][:200]}...")  # Showing only first 200 characters for brevity
        print("-" * 50)

def save_articles_to_mongodb(articles, collection):
    try:
        if articles:
            collection.insert_many(articles)
            print("Artikelen succesvol opgeslagen in MongoDB.")
        else:
            print("Geen artikelen om op te slaan.")
    except Exception as e:
        print(f"Fout bij het opslaan van artikelen in MongoDB: {e}")

def show_rss_feeds():
    print("Overzicht van de RSS kanalen:\n")
    for source, categories in RSS_FEEDS.items():
        print(f"{source}:")
        for category, url in categories.items():
            print(f"  {category}: {url}")
        print()

def process_nu_nl_articles(db):
    raw_collection = db["HetNieuws.Raw"]
    full_collection = db["HetNieuws.Full"]
    
    articles = raw_collection.find({"link": {"$regex": "nu.nl"}})
    for article in articles:
        link = article["link"]
        print(f"Processing NU.nl article from {link}")
        page_source = fetch_article_details_with_selenium(link)
        full_text = extract_nu_nl_article_body(page_source)
        full_article = {
            "title": article["title"],
            "link": article["link"],
            "body": full_text,
            "timestamp": article["timestamp"]
        }
        try:
            full_collection.insert_one(full_article)
            print(f"Saved full article from {link} to MongoDB.")
        except pymongo.errors.PyMongoError as e:
            print(f"Failed to save full article from {link} to MongoDB. Error: {e}")

# RSS NL
RSS_FEEDS = {
    "NOS Nieuws": {
        "Algemeen nieuws": "https://feeds.nos.nl/nosnieuwsalgemeen",
        "Binnenland": "https://feeds.nos.nl/nosnieuwsbinnenland",
        "Buitenland": "https://feeds.nos.nl/nosnieuwsbuitenland",
        "Economie": "https://feeds.nos.nl/nosnieuwseconomie",
        "Politiek": "https://feeds.nos.nl/nosnieuwspolitiek",
        "Sport": "https://feeds.nos.nl/nossportalgemeen",
    },
    "NU.nl": {
        "Algemeen nieuws": "https://www.nu.nl/rss/Algemeen",
        "Binnenland": "https://www.nu.nl/rss/Binnenland",
        "Buitenland": "https://www.nu.nl/rss/Buitenland",
        "Economie": "https://www.nu.nl/rss/Economie",
        "Sport": "https://www.nu.nl/rss/Sport",
        "Tech": "https://www.nu.nl/rss/Tech",
        "Opmerkelijk": "https://www.nu.nl/rss/Opmerkelijk",
    },
    "De Telegraaf": {
        "Algemeen nieuws": "https://www.telegraaf.nl/nieuws/rss",
        "Financieel": "https://www.telegraaf.nl/financieel/rss",
        "Sport": "https://www.telegraaf.nl/sport/rss",
        "Privé": "https://www.telegraaf.nl/entertainment/rss",
        "Lifestyle": "https://www.telegraaf.nl/lifestyle/rss",
        "Vrouw": "https://www.telegraaf.nl/vrouw/rss",
    },
    "AD.nl (Algemeen Dagblad)": {
        "Algemeen nieuws": "https://www.ad.nl/rss.xml",
        "Binnenland": "https://www.ad.nl/binnenland/rss.xml",
        "Buitenland": "https://www.ad.nl/buitenland/rss.xml",
        "Economie": "https://www.ad.nl/economie/rss.xml",
        "Sport": "https://www.ad.nl/sport/rss.xml",
        "Show": "https://www.ad.nl/show/rss.xml",
    },
    "Trouw": {
        "Algemeen nieuws": "https://www.trouw.nl/rss.xml",
        "Binnenland": "https://www.trouw.nl/binnenland/rss.xml",
        "Buitenland": "https://www.trouw.nl/buitenland/rss.xml",
        "Economie": "https://www.trouw.nl/economie/rss.xml",
        "Sport": "https://www.trouw.nl/sport/rss.xml",
    },
    "Volkskrant": {
        "Binnenland": "https://www.volkskrant.nl/binnenland/rss.xml",
        "Buitenland": "https://www.volkskrant.nl/buitenland/rss.xml",
        "Economie": "https://www.volkskrant.nl/economie/rss.xml",
        "Sport": "https://www.volkskrant.nl/sport/rss.xml",
    }
}

def main():
    # Use environment variables for configuration
    mongo_uri = os.getenv('MONGO_URI')

    try:
        client = pymongo.MongoClient(mongo_uri)
        db = client["HetNieuws-app"]
        raw_collection = db["HetNieuws.Raw"]
        print("Successfully connected to MongoDB")
    except pymongo.errors.ServerSelectionTimeoutError as err:
        print(f"Error connecting to MongoDB: {err}")
        exit(1)

    rss_url = None
    category = None
    num_articles = 5
    articles = []

    while True:
        display_menu()
        choice = get_user_choice()

        if choice == '1':
            rss_url = set_rss()
        elif choice == '2':
            category = set_category()
            if category in RSS_FEEDS["NU.nl"]:
                rss_url = RSS_FEEDS["NU.nl"][category]
                print(f"RSS URL set to {rss_url} for category {category}")
            else:
                print("Categorie niet gevonden in NU.nl feeds.")
        elif choice == '3':
            num_articles = set_num_articles()
        elif choice == '4':
            if rss_url:
                print(f"Extracting {num_articles} articles from {rss_url}")
                articles = extract_articles(rss_url, num_articles=num_articles)
                save_articles_to_mongodb(articles, raw_collection)
            else:
                print("Voer eerst een RSS-URL in of kies een categorie.")
        elif choice == '5':
            if articles:
                show_articles(articles)
            else:
                print("Er zijn geen artikelen om te tonen.")
        elif choice == '6':
            show_rss_feeds()
        elif choice == '7':
            if category:
                nu_nl_url = RSS_FEEDS["NU.nl"].get(category, RSS_FEEDS["NU.nl"]["Algemeen nieuws"])
            else:
                nu_nl_url = RSS_FEEDS["NU.nl"]["Algemeen nieuws"]
            print(f"Extracting {num_articles} articles from NU.nl category {category or 'Algemeen nieuws'}")
            articles = extract_articles(nu_nl_url, num_articles=num_articles, is_nu_nl=True)
            save_articles_to_mongodb(articles, raw_collection)
        elif choice == '8':
            process_nu_nl_articles(db)
        elif choice == '9':
            print("Het programma wordt afgesloten.")
            break
        else:
            print("Ongeldige keuze. Probeer het opnieuw.")

    # Close the Selenium driver
    driver.quit()

if __name__ == "__main__":
    main()