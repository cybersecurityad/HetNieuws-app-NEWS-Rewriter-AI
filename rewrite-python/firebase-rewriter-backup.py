import firebase_admin
from firebase_admin import credentials, firestore
from openai import OpenAI
from datetime import datetime, timezone, timedelta
import concurrent.futures
import os
import re
import requests
import time
from google.cloud import storage
import nltk
from nltk.corpus import stopwords

def initialize_firebase():
    """Initialize Firebase Admin SDK"""
    if not firebase_admin._apps:
        import os
        try:
            # First, try to use service account key if it exists
            service_account_path = os.path.join(os.path.dirname(__file__), '..', 'serviceAccountKey.json')
            
            if os.path.exists(service_account_path):
                print("🔑 Using service account key for Firebase authentication")
                cred = credentials.Certificate(service_account_path)
                firebase_admin.initialize_app(cred, {
                    'projectId': 'hetnieuws-app',
                    'storageBucket': 'hetnieuws-app.appspot.com'
                })
            else:
                # Fallback to Application Default Credentials
                print("🔑 Using Application Default Credentials for Firebase authentication")
                cred = credentials.ApplicationDefault()
                firebase_admin.initialize_app(cred, {
                    'projectId': 'hetnieuws-app',
                    'storageBucket': 'hetnieuws-app.appspot.com'
                })
            
            print("✅ Firebase Admin initialized successfully")
        except Exception as e:
            print(f"❌ Failed to initialize Firebase: {e}")
            print("\n🔧 To fix this issue:")
            print("1. Download your service account key from Firebase Console")
            print("2. Save it as 'serviceAccountKey.json' in your project root")
            print("3. Or set up Application Default Credentials: gcloud auth application-default login")
            raise e

# Initialize Firebase
initialize_firebase()
db = firestore.client()

# Use environment variables for configuration
bucket_name = 'hetnieuws-app.appspot.com'

# Initialize AI client with multiple provider support
def get_ai_client():
    """Get AI client based on available API keys (priority order)"""
    
    # 1. Try DeepSeek (cheapest, excellent quality)
    deepseek_api_key = os.getenv('DEEPSEEK_API_KEY')
    if deepseek_api_key:
        print("🧠 Using DeepSeek AI - Cost: ~$0.14 per 1M tokens (excellent value!)")
        return OpenAI(
            api_key=deepseek_api_key,
            base_url="https://api.deepseek.com"
        ), "deepseek-chat"
    
    # 2. Try Groq (free tier)
    groq_api_key = os.getenv('GROQ_API_KEY')
    if groq_api_key:
        print("⚡ Using Groq AI - Cost: Free tier available!")
        return OpenAI(
            api_key=groq_api_key,
            base_url="https://api.groq.com/openai/v1"
        ), "llama3-8b-8192"
    
    # 3. Try Together AI (free credits)
    together_api_key = os.getenv('TOGETHER_API_KEY')
    if together_api_key:
        print("🤝 Using Together AI - Cost: $5 free credits!")
        return OpenAI(
            api_key=together_api_key,
            base_url="https://api.together.xyz"
        ), "meta-llama/Llama-2-7b-chat-hf"
    
    # 4. Try Ollama (local, free)
    try:
        import requests
        # Check if Ollama is running locally
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        if response.status_code == 200:
            print("🏠 Using Ollama (Local AI) - Cost: Free!")
            return OpenAI(
                api_key="ollama",  # Ollama doesn't need a real API key
                base_url="http://localhost:11434/v1"
            ), "llama3"
    except:
        pass
    
    # 5. Fallback to OpenAI (most expensive)
    openai_api_key = os.getenv('OPENAI_API_KEY')
    if openai_api_key:
        print("🔓 Using OpenAI - Cost: $0.50-$2.00 per 1M tokens (expensive)")
        return OpenAI(api_key=openai_api_key), "gpt-3.5-turbo"
    
    # No API keys found
    print("❌ No AI API key found!")
    print("💡 Set up a free/cheap AI provider:")
    print("   • DeepSeek: export DEEPSEEK_API_KEY='your-key'")
    print("   • Groq: export GROQ_API_KEY='your-key'")
    print("   • Together AI: export TOGETHER_API_KEY='your-key'")
    print("   • Or install Ollama locally (completely free)")
    print("   • Run: ./setup-ai-provider.sh for guided setup")
    return None, None

client, model_name = get_ai_client()

print("Successfully connected to Firebase Firestore")

# Base directory to save the HTML files
base_dir = "/Users/_akira/CSAD/websites-new-2025/work-in-progress/hetnieuws-app"

# Download stopwords if not already present
nltk.download('stopwords')

# Load stopwords
stop_words = set(stopwords.words('dutch'))

# Function to generate rewritten text using AI API
def generate_text(prompt, max_tokens=512):
    if not client or not model_name:
        print("⚠️ No AI client available, using original text")
        return prompt
    
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "Herschrijf de tekst in het Nederlands in een gemakkelijk leesbare nieuwsstijl. Gebruik eenvoudige zinnen en heldere taal. Behoud alle belangrijke informatie maar maak het toegankelijker voor een breed publiek."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=1.0
        )
        content = response.choices[0].message.content
        return content.strip() if content else prompt
    except Exception as e:
        print(f"Error generating text: {e}")
        return prompt  # Fallback to original text if generation fails

# Function to generate an image based on a prompt using DALL-E API
def generate_image(prompt):
    """
    Image generation is now isolated in image_generator.py
    This function is kept for backward compatibility but disabled
    """
    print("ℹ️ Image generation is isolated in image_generator.py")
    print("💡 To add images to articles, run: python image_generator.py add-to-existing")
    return None  # No image generation in main rewriter
    
# Function to get current timestamp with UTC+02:00 offset
def get_current_timestamp():
    amsterdam_tz = timezone(timedelta(hours=2))
    return datetime.now(amsterdam_tz).strftime('%Y-%m-%d %H:%M:%S')

# Function to create a valid URL slug
def create_url_slug(title):
    # Remove apostrophes
    title = title.replace("'", "")
    # Split title into words and filter out stopwords
    words = [word for word in title.split() if word.lower() not in stop_words and not word.isdigit()]
    # Select the first three important words
    important_words = words[:4]
    # Join the words with hyphens
    slug = '-'.join(important_words)
    # Replace non-alphanumeric characters (except for hyphens) with spaces
    slug = re.sub(r'[^a-zA-Z0-9-]', ' ', slug).strip()
    # Replace spaces with hyphens
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
    if not client or not model_name:
        print("⚠️ No AI client available, using default category")
        return "Nieuws"
    
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "Classificeer de categorie van de volgende Nederlandse tekst met één woord in het Nederlands. Kies uit: Politiek, Sport, Economie, Gezondheid, Technologie, Cultuur, Onderwijs, Milieu, Internationaal, of Nieuws."},
                {"role": "user", "content": full_text}
            ],
            max_tokens=10
        )
        content = response.choices[0].message.content
        if content:
            category = content.strip().split()[0]  # Take only the first word
            return category
        else:
            return "Nieuws"
    except Exception as e:
        print(f"Error getting category: {e}")
        return "Nieuws"  # Fallback category

# Function to get tags based on full text
def get_tags(full_text):
    if not client or not model_name:
        print("⚠️ No AI client available, using default tags")
        return ["Nederland", "Nieuws", "Actueel"]
    
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "Genereer precies drie Nederlandse tags gescheiden door komma's. Bijvoorbeeld: 'Politiek, Nederland, Verkiezingen'. Gebruik korte woorden van 1-3 woorden elk."},
                {"role": "user", "content": full_text[:200]}  # Limit text to avoid token issues
            ],
            max_tokens=30
        )
        content = response.choices[0].message.content
        if content and ',' in content:
            # Split by comma and clean up
            tags = [tag.strip() for tag in content.split(',')]
            # Filter out empty tags and limit to 3
            tags = [tag for tag in tags if tag and len(tag) > 0][:3]
            return tags if len(tags) == 3 else ["Nederland", "Nieuws", "Actueel"]
        else:
            return ["Nederland", "Nieuws", "Actueel"]
    except Exception as e:
        print(f"Error getting tags: {e}")
        return ["Nederland", "Nieuws", "Actueel"]  # Fallback tags

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

def rewrite_article(article, base_dir, bucket_name):
    """Process and rewrite article using OpenAI and store in Firestore"""
    original_title = article["title"]
    original_body = article.get("body", article.get("full_text", ""))

    # Generate new title
    rewritten_title = generate_text(original_title, max_tokens=50)
    rewritten_title = rewritten_title[:160]  # Ensure title is within 160 characters

    # Generate new body text in chunks if necessary
    chunk_size = 512
    rewritten_body = ""
    for i in range(0, len(original_body), chunk_size):
        chunk = original_body[i:i + chunk_size]
        rewritten_body_chunk = generate_text(f"Herschrijf dit Nederlandse nieuwsartikel in eenvoudige, begrijpelijke taal:\n\n{chunk}", max_tokens=chunk_size)
        rewritten_body += rewritten_body_chunk + " "
    
    rewritten_body = rewritten_body.strip()

    # Remove original images from the body text
    rewritten_body = remove_original_images(rewritten_body)

    # Generate new image URL based on the rewritten title
    image_url = generate_image(rewritten_title)
    if not image_url:
        image_url = generate_image(rewritten_body)
    
    # No image download/upload needed since generate_image returns None
    uploaded_image_url = None
    
    if image_url:
        print(f"Generated image URL: {image_url}")
    else:
        print("ℹ️ No image generated (use image_generator.py separately)")

    # Create URL slug from title
    title_slug = create_url_slug(rewritten_title)

    # Generate summary from rewritten body text
    summary = generate_summary(rewritten_body)

    # Determine category and tags
    category = get_category(rewritten_body)
    tags = get_tags(rewritten_body)

    # Compile the article data
    article_data = {
        "title": rewritten_title,
        "link": article.get("link", ""),
        "published": article.get("published", ""),
        "summary": summary,
        "full_text": rewritten_body,
        "image_url": uploaded_image_url if uploaded_image_url else None,
        "timestamp": get_current_timestamp(),
        "slug": title_slug,
        "category": category,
        "tags": tags,
        "url": f"https://hetnieuws.app/category/{category.lower()}/{title_slug}.html"[:300],
        "processed": True
    }

    # Save to Firestore
    try:
        doc_ref = db.collection('HetNieuws_Rewritten').document()
        doc_ref.set(article_data)
        print(f"Article saved to Firestore with ID: {doc_ref.id}")
        
        # Mark original as processed if it exists
        if article.get("link"):
            # Update the original article to mark as processed
            raw_docs = db.collection('HetNieuws_Raw').where('link', '==', article["link"]).get()
            for doc in raw_docs:
                doc.reference.update({"processed": True})
        
        return article_data, uploaded_image_url
    except Exception as e:
        print(f"Error saving to Firestore: {e}")
        return None, None

def main():
    """Main function to process articles"""
    try:
        # Get all articles from Firestore to check what we have
        raw_collection = db.collection('HetNieuws_Raw')
        all_docs = raw_collection.get()
        
        print(f"Total articles in HetNieuws_Raw: {len(all_docs)}")
        
        # Check processed status and collect unprocessed articles
        processed_count = 0
        unprocessed_articles = []
        
        for doc in all_docs:
            article_data = doc.to_dict()
            if article_data:
                # Skip articles with /video/ in the link or slug
                article_link = article_data.get('link', '')
                article_slug = article_data.get('slug', '')
                article_title = article_data.get('title', '')
                
                if '/video/' in article_link or '/video/' in article_slug:
                    print(f"⏭️ Skipping video article: {article_title[:50]}...")
                    continue
                
                # Skip articles with NU+ in the title (premium content)
                if 'NU+' in article_title:
                    print(f"⏭️ Skipping NU+ premium article: {article_title[:50]}...")
                    continue
                
                # Check if processed field exists and is True
                if article_data.get('processed') == True:
                    processed_count += 1
                else:
                    # Article is not processed (field missing or False)
                    article_data['id'] = doc.id
                    unprocessed_articles.append(article_data)
                    print(f"Found unprocessed article: {article_title[:50]}...")
        
        print(f"Processed articles: {processed_count}")
        print(f"Unprocessed articles: {len(unprocessed_articles)}")
        
        if len(unprocessed_articles) == 0:
            print("No articles to process. All articles are already processed.")
            return
        
        # Process articles one by one to avoid rate limits
        articles_to_process = unprocessed_articles[:3]  # Process 3 at a time
        print(f"Processing {len(articles_to_process)} articles (to avoid rate limits)...")
        
        # Process articles sequentially to avoid rate limits
        rewritten_articles = []
        for i, article in enumerate(articles_to_process):
            print(f"\n🔄 Processing article {i+1}/{len(articles_to_process)}: {article.get('title', 'No title')[:50]}...")
            
            result = rewrite_article(article, base_dir, bucket_name)
            if result:
                article_data, uploaded_url = result
                if article_data:
                    rewritten_articles.append(article_data)
                    print("\n=== Rewritten Article ===")
                    print(f"Title: {article_data['title']}")
                    print(f"Category: {article_data['category']}")
                    print(f"Tags: {', '.join(article_data['tags'])}")
                    if uploaded_url:
                        print(f"Uploaded Image URL: {uploaded_url}")
            
            # Add delay between articles to respect rate limits
            if i < len(articles_to_process) - 1:  # Don't delay after the last article
                print("⏳ Waiting 3 seconds to respect rate limits...")
                time.sleep(3)

        print(f"Successfully processed {len(rewritten_articles)} articles")
        
    except Exception as e:
        print(f"Error in main processing: {e}")

if __name__ == "__main__":
    main()
