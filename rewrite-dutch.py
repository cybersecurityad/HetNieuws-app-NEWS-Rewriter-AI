import openai
import pymongo
from datetime import datetime, timezone, timedelta
import concurrent.futures
import os
import re
import requests
from google.cloud import storage
import nltk
from nltk.corpus import stopwords
import firebase_admin
from firebase_admin import credentials

def initialize_firebase():
    if not firebase_admin._apps:
        cred = credentials.ApplicationDefault()
        firebase_admin.initialize_app(cred)

# Initialize Firebase at the start of your script
initialize_firebase()

# Use environment variables for configuration
bucket_name = 'hetnieuws-app-427719.appspot.com'
openai.api_key = os.getenv('OPENAI_API_KEY')
mongo_uri = os.getenv('MONGO_URI')

try:
    client = pymongo.MongoClient(mongo_uri)
    db = client["HetNieuws-app"]
    input_collection = db["HetNieuws.Raw"]
    output_collection = db["HetNieuws.RW"]
    print("Successfully connected to MongoDB")
except pymongo.errors.ServerSelectionTimeoutError as err:
    print(f"Error connecting to MongoDB: {err}")
    exit(1)

# Base directory to save the HTML files
base_dir = "/Users/_akira/hacker/automate/circel-sites-vergelijk/hetnieuws-app"

# Download stopwords if not already present
nltk.download('stopwords')

# Load Dutch stopwords
stop_words = set(stopwords.words('dutch'))

# Function to generate rewritten text using OpenAI API
def generate_text(prompt, max_tokens=512):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Herschrijf in een gemakkelijk te lezen zakelijke stijl."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=1.0
        )
        return response.choices[0].message["content"].strip()
    except Exception as e:
        print(f"Error generating text: {e}")
        return prompt  # Fallback to original text if generation fails

# Function to generate an image based on a prompt using DALL-E API
def generate_image(prompt):
    try:
        if len(prompt) > 800:
            prompt = prompt[:800]
        response = openai.Image.create(
            prompt=prompt,
            n=1,
            size="512x512"
        )
        image_url = response['data'][0]['url']
        return image_url
    except Exception as e:
        print(f"Error generating image: {e}")
        return None  # No fallback image URL

# Function to get current timestamp with UTC+02:00 offset
def get_current_timestamp():
    amsterdam_tz = timezone(timedelta(hours=2))
    return datetime.now(amsterdam_tz).strftime('%Y-%m-%d %H:%M:%S')

# Function to create a valid URL slug
def create_url_slug(title):
    title = title.replace("'", "")
    words = [word for word in title.split() if word.lower() not in stop_words and not word.isdigit()]
    important_words = words[:4]
    slug = '-'.join(important_words)
    slug = re.sub(r'[^a-zA-Z0-9-]', ' ', slug).strip()
    slug = re.sub(r'\s+', '-', slug)
    return slug.lower()

def generate_summary(full_text, char_limit=59):
    if len(full_text) <= char_limit:
        return full_text
    else:
        summary = full_text[:char_limit]
        if summary.endswith(' ') and full_text[char_limit:]:
            return summary.rstrip() + '...'
        else:
            return summary.rsplit(' ', 1)[0] + '...'

# Function to get category based on full text
def get_category(full_text):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Classificeer de categorie van de volgende tekst in één woord."},
                {"role": "user", "content": full_text}
            ],
            max_tokens=10
        )
        category = response.choices[0].message["content"].strip().split()[0]
        return category
    except Exception as e:
        print(f"Error getting category: {e}")
        return "Ongecategoriseerd"

# Function to get tags based on full text
def get_tags(full_text):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Genereer drie tags voor de volgende tekst. Houd ze kort — tussen 1 en 3 woorden."},
                {"role": "user", "content": full_text}
            ],
            max_tokens=20
        )
        tags = response.choices[0].message["content"].strip().split(", ")
        return tags[:3]
    except Exception as e:
        print(f"Error getting tags: {e}")
        return ["Tag1", "Tag2", "Tag3"]

# Function to remove original images from the HTML content
def remove_original_images(html_content):
    cleaned_content = re.sub(r'<img[^>]*src="https://images\.cointelegraph\.com/[^>]*>', '', html_content)
    return cleaned_content

# Function to download the image from a URL
def download_image(image_url, local_path):
    try:
        response = requests.get(image_url, stream=True)
        if response.status_code == 200:
            with open(local_path, 'wb') as file:
                for chunk in response.iter_content(1024):
                    file.write(chunk)
            print(f"Image downloaded to {local_path}")
            return local_path
        else:
            print(f"Failed to download image. Status code: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error downloading image: {e}")
        return None

def upload_image_to_firebase(local_image_path, bucket_name, destination_blob_name):
    try:
        if not os.path.exists(local_image_path):
            raise FileNotFoundError(f"The local file was not found at {local_image_path}")

        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)
        blob.upload_from_filename(local_image_path)

        blob.make_public()

        print(f"File {local_image_path} uploaded to {destination_blob_name}.")
        return blob.public_url
    except Exception as e:
        print(f"Error uploading to Firebase Storage: {e}")
        return None

def create_single_article_html(article_data, base_dir):
    title_slug = create_url_slug(article_data['title'])
    category_slug = article_data['category'].lower()
    local_file_path = os.path.join(base_dir, f"category/{category_slug}", f"{title_slug}.html")

    os.makedirs(os.path.dirname(local_file_path), exist_ok=True)
    clean_full_text = remove_original_images(article_data['full_text'])

    with open(local_file_path, 'w') as file:
        file.write(f"""
<!DOCTYPE html>
<html lang="nl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="robots" content="index, follow">
    <meta name="revisit-after" content="3 days">
    <meta name="language" content="Dutch">
    
    <title itemprop="name">"{article_data['summary']}"</title> 
    <link rel="canonical" href="https://hetnieuws.app/category/{category_slug}/{title_slug}.html" />
    
    <title>{article_data['title']}</title>
    <meta name="description" content="{article_data['summary']}">
    <meta name="keywords" content="{', '.join(article_data['tags'])}">

    <meta property="og:title" content="{article_data['title']}">
    <meta property="og:description" content="{article_data['summary']}">
    <meta property="og:image" content="{article_data['image_url']}">
    <meta property="og:url" content="https://hetnieuws.app/category/{category_slug}/{title_slug}.html"/>
    <meta property="og:type" content="article">
    <meta name="twitter:card" content="{article_data['image_url']}">
    <meta name="twitter:title" content="{article_data['title']}">
    <meta name="twitter:description" content="{article_data['summary']}">
    <meta name="twitter:image" content="{article_data['image_url']}">
    
    <meta name="rating" content="General">
    <meta name="author" content="Peter Oldenburger" />
    <meta itemprop="copyrightHolder" content="Peter Oldenburger" /> 
    <meta itemprop="copyrightYear" content="2023" />
    <meta name="distribution" content="Global">
    <meta itemprop="isFamilyFriendly" content="True" />
    <meta name="mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-title" content="HetNieuws.app">
     <meta itemprop="image" content="https://hetnie">
         <meta name="apple-mobile-web-app-title" content="HetNieuws.app">
    <meta itemprop="image" content="https://hetnieuws.app/media/image/hetnieuws-app-logo-white.webp" />
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="default">
    
    <link rel="icon" href="/media/image/favicon.ico" type="image/x-icon">
    
    <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        @media (max-width: 768px) {{
            .main-container {{
                flex-direction: column;
            }}
            .main-content, .sidebar {{
                width: 100%;
            }}
        }}
        body {{
            font-family: 'Poppins', sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f4f4f9;
            font-size: 18px;
            line-height: 1.8;
        }}
        body, .main-container {{
            display: flex;
            flex-direction: column; 
        }}
        body .site-header {{
            width: 100%;
            top: 0;
            position: relative; 
        }}
        header {{
            order: -1; 
        }}
        header {{
            background: #000;
            color: #fff;
            padding: 1rem 0;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        }}
        header h1 {{
            color: #00008B;
            font-weight: bold;
        }}
        h1 {{
            color: #00008B;
            font-size: 55px;
            font-weight: bold;
        }}
        h2 {{
            font-size: 24px;
            font-weight: bold;
        }}
        .navbar {{
            justify-content: center;
        }}
        .navbar-nav .nav-item .nav-link {{
            color: #000;
            font-weight: 500;
        }}
        .navbar-nav .nav-item .nav-link:hover {{
            color: #00008B;
        }}
        .main-container {{
            display: flex;
            flex-direction: row;
            max-width: 1200px;
            margin: 2rem auto;
            padding: 0 1rem;
        }}
        .main-content {{
            flex: 3;
            margin-right: 2rem;
        }}
        .sidebar {{
            flex: 1;
        }}
        .article {{
            background-color: #fff;
            border-radius: 10px;
            padding: 2rem;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            margin-bottom: 2rem;
            display: flex;
            flex-direction: column;
            align-items: center;
        }}
        .article img {{
            width: 50%;
            height: 50%;
            border-radius: 10px;
            border: 5px solid black;
        }}
        .article h2 {{
            color: #000;
            font-weight: bold;
        }}
        .read-more {{
            width: 100%;
            padding: 0.5rem;
            margin-top: 0.5rem;
            border: none;
            border-radius: 5px;
            background-color: #00008B;
            color: white;
            font-weight: bold;
            text-align: center;
            display: inline-block;
            text-decoration: none;
            font-size: 22px;
        }}
        .widget {{
            margin-bottom: 2rem;
            background: #fff;
            padding: 1rem;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        }}
        .widget-title {{
            font-weight: bold;
            margin-bottom: 1rem;
            text-align: center;
        }}
        .search-bar input[type="text"] {{
            width: 100%;
            padding: 0.5rem;
            border: 1px solid #ccc;
            border-radius: 5px;
        }}
        .search-bar button {{
            width: 100%;
            padding: 0.5rem;
            margin-top: 0.5rem;
            border: none;
            border-radius: 5px;
            background-color: #00008B;
            color: white;
            font-weight: bold;
        }}
        .widget_recent_entries ul {{
            list-style-type: none;
            padding-left: 0;
        }}
        .widget_recent_entries ul li {{
            display: flex;
            align-items: center;
            margin-bottom: 0.5rem;
            padding: 0.5rem;
            border: 1px solid #ddd;
            border-radius: 5px;
        }}
        .widget_recent_entries ul li a {{
            color: #1e73be;
            text-decoration: none;
            flex: 1;
            font-size: 14px;
        }}
        .widget_recent_entries ul li img {{
            width: 50%;
            height: auto;
            margin-right: 10px;
            border-radius: 5px;
        }}
        .widget_recent_entries ul li a:hover {{
            text-decoration: none;
            color: #00008B;
        }}
        .navbar .navbar-nav .nav-item {{
            position: relative;
        }}
        .navbar .navbar-nav .nav-item .dropdown-menu {{
            display: none;
            position: absolute;
            top: 100%;
            left: 0;
            background-color: #f9f9f9;
            box-shadow: 0px 8px 16px 0px rgba(0,0,0,0.2);
            z-index: 1;
        }}
        .navbar .navbar-nav .nav-item:hover .dropdown-menu {{
            display: block;
        }}
        .navbar .navbar-nav .dropdown-menu li {{
            padding: 8px 16px;
            text-decoration: none;
            display: block;
        }}
        .navbar .navbar-nav .dropdown-menu li a {{
            color: black;
            text-decoration: none;
        }}
        .navbar .navbar-nav .dropdown-menu li a:hover {{
            background-color: #ddd;
        }}
        .widget_categories ul {{
            list-style-type: none;
            padding-left: 0;
        }}
        .widget_categories ul li {{
            margin-bottom: 0.5rem;
        }}
        .widget_categories ul li a {{
            color: #1e73be;
            text-decoration: none;
        }}
        .widget_categories ul li a:hover {{
            text-decoration: underline;
            color: #00008B;
        }}
        .widget_tags ul {{
            list-style-type: none;
            padding-left: 0;
        }}
        .widget_tags ul li {{
            display: inline-block;
            margin-bottom: 0.5rem;
            margin-right: 0.5rem;
            padding: 0.5rem;
            border: 1px solid #ddd;
            border-radius: 5px;
            background-color: #f4f4f9;
        }}
        .widget_tags ul li a {{
            color: #1e73be;
            text-decoration: none;
            font-size: 14px;
        }}
        .widget_tags ul li a:hover {{
            color: #00008B;
        }}
        .share-options {{
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-top: 1rem;
        }}
        .share-options a {{
            display: inline-block;
            width: 30px;
            height: 30px;
            background-color: #ddd;
            border-radius: 50%;
            display: flex;
            justify-content: center;
            align-items: center;
            text-decoration: none;
            color: #333;
        }}
        .share-options a img {{
            width: 15px;
            height: 15px;
        }}
        .footer {{
            padding: 1rem;
            text-align: center;
            background: #000;
            color: #00008B;
            box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.1);
            margin-top: 2rem;
        }}
        .footer .footer-links a {{
            color: #fff;
            text-decoration: none;
            margin: 0 10px;
        }}
        .footer .footer-links a:hover {{
            color: #00008B;
            text-decoration: underline;
        }}
    </style>
</head>
<body>
    <header class="site-header">
        <img src="https://hetnieuws.app/media/image/hetnieuws-app-logo-white.webp" alt="hetnieuws.app logo" style="width: 3.5%;">
        <a href="http://www.hetnieuws.app" style="text-decoration: none; color: #00008B; font-weight: bold;">H</a>
        <a href="http://www.hetnieuws.app" style="text-decoration: none; color: #ffff;">etNieuws</a>
        <a href="http://www.hetnieuws.app" style="text-decoration: none; color: #00008B; font-weight: bold;">A</a>
        <a href="http://www.hetnieuws.app" style="text-decoration: none; color: #ffff;">pp.com</a>
        <nav class="navbar navbar-expand-lg navbar-light bg-light">
            <ul class="navbar-nav">
                <li class="nav-item"><a class="nav-link" href="/">Home</a></li>
                <li class="nav-item"><a class="nav-link" href="/shopping">Shopping</a></li>
                <li class="nav-item">
                    <a class="nav-link" href="/lifestyle">Lifestyle</a>
                    <ul class="dropdown-menu">
                        <li><a href="/health">Health</a></li>
                        <li><a href="/beauty">Beauty</a></li>
                        <li><a href="/fashion">Fashion</a></li>
                        <li><a href="/food">Food</a></li>
                        <li><a href="/travel">Travel</a></li>
                    </ul>
                </li>
                <li class="nav-item">
                    <a class="nav-link" href="/science">Science</a>
                    <ul class="dropdown-menu">
                        <li><a href="/technology">Technology</a></li>
                        <li><a href="/cryptocurrency">Cryptocurrency</a></li>
                        <li><a href="/blockchain">Blockchain</a></li>
                    </ul>
                </li>
                <li class="nav-item">
                    <a class="nav-link" href="/news">News</a>
                    <ul class="dropdown-menu">
                        <li><a href="/europe">Europe</a></li>
                        <li><a href="/us">United States</a></li>
                        <li><a href="/asia">Asia</a></li>
                        <li><a href="/africa">Africa</a></li>
                        <li><a href="/middle-east">Middle East</a></li>
                        <li><a href="/americas">Americas</a></li>
                    </ul>
                </li>
                <li class="nav-item"><a class="nav-link" href="/marketing">Marketing</a></li>
                <li class="nav-item"><a class="nav-link" href="/entertainment">Entertainment</a></li>
                <li class="nav-item"><a class="nav-link" href="/sport">Sports</a></li>
                <li class="nav-item">
                    <a class="nav-link" href="/about">About</a>
                    <ul class="dropdown-menu">
                        <li><a href="/privacy-policy">Privacy Policy</a></li>
                        <li><a href="/terms-of-service">Terms of Service</a></li>
                        <li><a href="/disclaimer">Disclaimer</a></li>
                        <li><a href="/contact">Contact</a></li>
                    </ul>
                </li>
            </ul>
        </nav>
    </header>
    <div class="main-container">
        <div class="main-content">
            <h1>{article_data['title']}</h1>
            <br>
            <h2>{article_data['summary']}</h2>
            <p>Gepubliceerd: {article_data['timestamp']}</p>
            {f'<h3><img src="{article_data["image_url"]}" alt="{article_data["title"]}"></h3>' if article_data['image_url'] else ''}
            <br>
            <p>Auteur: Peter Oldenburger, HetNieuws.app</p>
            <br>
            <p>{clean_full_text}</p>
        </div>
        <aside class="sidebar">
            <div id="recent-posts-2" class="widget widget_recent_entries">
                <h3 class="widget-title">Recente berichten</h3>
                <ul id="recent-posts-list">
                </ul>
            </div>
            <div id="tag-sidebar" class="widget widget_tags">
                <h3 class="widget-title">Tags</h3>
                <ul>
                </ul>
            </div>
            <div id="categories-2" class="widget widget_categories">
                <h3 class="widget-title">Categorieën</h3>
                <ul>
                    <li><a href="/animals">Dieren</a></li>
                    <li><a href="/athletics">Atletiek</a></li>
                    <li><a href="/automotive">Auto's</a></li>
                    <li><a href="/beauty-products">Schoonheidsproducten</a></li>
                    <li><a href="/corporate">Zakelijk</a></li>
                    <li><a href="/design">Design</a></li>
                    <li><a href="/education">Onderwijs</a></li>
                    <li><a href="/entertainment">Amusement</a></li>
                    <li><a href="/faith">Geloof</a></li>
                    <li><a href="/fashion">Mode</a></li>
                    <li><a href="/finance">Financiën</a></li>
                    <li><a href="/food-drink">Eten & Drinken</a></li>
                    <li><a href="/games">Spellen</a></li>
                    <li><a href="/health">Gezondheid</a></li>
                    <li><a href="/holiday">Vakantie</a></li>
                    <li><a href="/house-enhancement">Huisverbetering</a></li>
                    <li><a href="/jobs">Banen</a></li>
                    <li><a href="/legal">Juridisch</a></li>
                    <li><a href="/marketing">Marketing</a></li>
                    <li><a href="/media">Media</a></li>
                    <li><a href="/news">Nieuws</a></li>
                    <li><a href="/outdoor">Buitenleven</a></li>
                    <li><a href="/presents">Cadeaus</a></li>
                    <li><a href="/production">Productie</a></li>
                    <li><a href="/property">Vastgoed</a></li>
                    <li><a href="/shopping">Winkelen</a></li>
                    <li><a href="/technical">Techniek</a></li>
                </ul>
            </div>
        </aside>
    </div>
    <footer class="footer">
        <div class="footer-links">
            <a href="/privacy-policy">Privacybeleid</a>
            <a href="/cookie-policy">Cookiebeleid</a>
            <a href="/terms-of-service">Gebruiksvoorwaarden</a>
            <a href="/avg">AVG</a>
            <a href="/gpdr">GPDR</a>
            <a href="/disclaimer">Disclaimer</a>
            <br><br>
            <p>&copy; 2024 HetNieuws.app</p>
        </div>
    </footer>
    <script>
        async function loadBlogs() {{
            try {{
                const response = await fetch('https://hetnieuws-app-0261cbb24d44.herokuapp.com/get-blogs');
                const blogs = await response.json();
                const recentPostsList = document.getElementById('recent-posts-list');
                const tagsList = document.getElementById('tag-sidebar').querySelector('ul');

                blogs.forEach(blog => {{
                    const recentPostItem = document.createElement('li');
                    const titleSlug = blog.slug;
                    const category = blog.category.toLowerCase();

                    recentPostItem.innerHTML = `
                        <img src="${{blog.image_url}}" alt="${{blog.title}}" onerror="this.onerror=null;this.remove();">
                        <a href="/category/${{category}}/${{titleSlug}}.html">${{blog.title}}</a>
                    `;
                    recentPostsList.appendChild(recentPostItem);

                    blog.tags.forEach(tag => {{
                        const tagItem = document.createElement('li');
                        tagItem.innerHTML = `<a href="/tags/${{tag.toLowerCase().replace(/\s+/g, '-')}}">${{tag}}</a>`;
                        tagsList.appendChild(tagItem);
                    }});
                }});
            }} catch (error) {{
                console.error('Error fetching blogs:', error);
                alert('Error fetching blogs: ' + error.message);
            }}
        }}
        loadBlogs();
    </script>
</body>
</html>
""")
    print(f"Local HTML file created at: {local_file_path}")
    return local_file_path


def rewrite_article(article, base_dir, bucket_name):
    original_title = article["title"]
    original_body = article["body"]  # Changed from article["full_text"]

    # Generate new title
    rewritten_title = generate_text(original_title, max_tokens=50)
    rewritten_title = rewritten_title[:160]  # Ensure title is within 160 characters

    # Generate new body text in chunks if necessary
    chunk_size = 512
    rewritten_body = ""
    for i in range(0, len(original_body), chunk_size):
        chunk = original_body[i:i + chunk_size]
        rewritten_body_chunk = generate_text(f"Herschrijf in een gemakkelijk te lezen zakelijke stijl:\n\n{chunk}", max_tokens=chunk_size)
        rewritten_body += rewritten_body_chunk + " "
    
    rewritten_body = rewritten_body.strip()

    # Remove original images from the body text
    rewritten_body = remove_original_images(rewritten_body)

    # Generate new image URL based on the rewritten title
    image_url = generate_image(rewritten_title)
    if not image_url:
        image_url = generate_image(rewritten_body)
    if not image_url:
        image_url = None  # No fallback image URL

    if image_url:
        print(f"Generated image URL: {image_url}")
    else:
        print("No image generated.")

    # Download the generated image
    local_image_path = None
    if image_url:
        local_image_path = download_image(image_url, "/tmp/temp_image.png")
        if not local_image_path:
            local_image_path = None

    title_slug = create_url_slug(rewritten_title)

    # Ensure the downloaded image path exists
    if local_image_path and os.path.exists(local_image_path):
        # Rename the image file based on the article title
        renamed_image_path = f"/tmp/{title_slug}.png"
        try:
            os.rename(local_image_path, renamed_image_path)
        except FileNotFoundError as e:
            print(f"Error renaming file: {e}")
            renamed_image_path = local_image_path
    else:
        renamed_image_path = None

    # Upload the renamed image to Firebase Storage
    uploaded_image_url = None
    if renamed_image_path:
        uploaded_image_url = upload_image_to_firebase(renamed_image_path, bucket_name, f"images/{title_slug}.png")

    # Generate summary from rewritten body text
    summary = generate_summary(rewritten_body)

    # Determine category and tags
    category = get_category(rewritten_body)
    tags = get_tags(rewritten_body)

    # Compile the article data
    article_data = {
        "title": rewritten_title,
        "link": article["link"],
        "published": article.get("published", get_current_timestamp()),  # Use current timestamp as default
        "summary": summary,  # Use the generated summary
        "full_text": rewritten_body,  # Note: This field name can be changed as required
        "image_url": uploaded_image_url if uploaded_image_url else None,  # Use the newly generated and uploaded image URL or None
        "timestamp": get_current_timestamp(),  # Add the current timestamp
        "slug": title_slug,  # Use the slug created earlier
        "category": category,  # Add the category
        "tags": tags,  # Add the tags
        "url": f"https://hetnieuws.app/category/{category.lower()}/{title_slug}.html"[:300]  # Add the new generated URL, limited to 300 characters
    }

    # Create and upload the single article HTML file
    public_url = create_and_upload_article_html(article_data, base_dir, bucket_name)

    return article_data, public_url

def create_and_upload_article_html(article_data, base_dir, bucket_name):
    # Create the single article HTML file and save it locally in the specified directory
    local_file_path = create_single_article_html(article_data, base_dir)
    
    if not os.path.exists(local_file_path):
        print(f"Error: The generated HTML file was not found at {local_file_path}")
        return None

    # Generate a valid filename slug from the article title
    title_slug = create_url_slug(article_data['title'])
    category = article_data['category'].lower()
    destination_blob_name = f"category/{category}/{title_slug}.html"
    
    # Upload the HTML file to Firebase Storage
    public_url = upload_image_to_firebase(local_file_path, bucket_name, destination_blob_name)
    
    if public_url:
        print(f"Article HTML uploaded to: {public_url}")
        return public_url
    else:
        print("Failed to upload article HTML to Firebase Storage.")
        return None

def update_index_html(rewritten_articles, base_dir):
    index_html_path = os.path.join(base_dir, "blogx", "index.html")

    # Read the existing index HTML file
    with open(index_html_path, 'r') as file:
        index_html_content = file.read()

    # Define the markers to locate where to insert the articles
    articles_marker_start = "<!-- Articles will be injected here -->"
    articles_marker_end = "<!-- End of Articles -->"
    tags_marker_start = "<!-- Tags will be injected here -->"
    tags_marker_end = "<!-- End of Tags -->"

    # Find the positions of the markers
    start_pos = index_html_content.find(articles_marker_start) + len(articles_marker_start)
    end_pos = index_html_content.find(articles_marker_end)
    tag_start_pos = index_html_content.find(tags_marker_start) + len(tags_marker_start)
    tag_end_pos = index_html_content.find(tags_marker_end)

    # Extract existing articles section
    existing_articles_html = index_html_content[start_pos:end_pos].strip()
    existing_tags_html = index_html_content[tag_start_pos:tag_end_pos].strip()

    # Construct new articles HTML
    new_articles_html = ""
    new_tags_html = ""
    tags_set = set()
    for article in rewritten_articles:
        summary = generate_summary(article['full_text'])  # Generate summary from full_text
        new_articles_html += f"""
            <div class="article">
                <h2>{article['title'][:60]}</h2>
                {"<img src=\"" + article['image_url'] + "\" alt=\"" + article['title'] + "\">" if article['image_url'] else ""}
                <p>{summary}</p>
                <a href="{article['url']}" class="read-more">Lees meer</a>
            </div>
        """
        # Collect tags
        for tag in article['tags']:
            tags_set.add(tag)

    for tag in tags_set:
        new_tags_html += f'<li><a href="/tags/{tag.lower().replace(" ", "-")}">{tag}</a></li>'

    # Update the index HTML content with the new articles and tags
    updated_index_html_content = (
        index_html_content[:start_pos] +
        "\n" + new_articles_html + "\n" +
        index_html_content[end_pos:tag_start_pos] +
        "\n" + new_tags_html + "\n" +
        index_html_content[tag_end_pos:]
    )

    # Write the updated index HTML file
    with open(index_html_path, 'w') as file:
        file.write(updated_index_html_content)

    print("Index HTML updated successfully.")

# Rewrite articles with parallel processing
rewritten_articles = []
with concurrent.futures.ThreadPoolExecutor() as executor:
    # Fetch only the articles that have not been processed yet
    futures = [executor.submit(rewrite_article, article, base_dir, bucket_name) for article in input_collection.find({"processed": {"$ne": True}})]
    for future in concurrent.futures.as_completed(futures):
        result = future.result()
        if result:  # Ensure result is not None
            article_data, uploaded_url = result  # Ensure to unpack correctly
            rewritten_articles.append(article_data)
            # Display the rewritten title and text
            print("\n=== Herschreven artikel ===")
            print(f"Title: {article_data['title']}")
            print(f"Full Text: {article_data['full_text']}\n")
            print(f"Image URL: {article_data['image_url']}\n")
            print(f"Category: {article_data['category']}\n")
            print(f"Tags: {', '.join(article_data['tags'])}\n")
            if uploaded_url:
                print(f"Uploaded HTML URL: {uploaded_url}\n")
                # Mark the original article as processed in the database
                input_collection.update_one({"link": article_data["link"]}, {"$set": {"processed": True}})

# Save rewritten articles to MongoDB
if rewritten_articles:
    output_collection.insert_many(rewritten_articles)

# Update the index HTML file
update_index_html(rewritten_articles, base_dir)

print("Herschreven artikelen zijn opgeslagen in MongoDB en index.html is bijgewerkt.")
