import firebase_admin
from firebase_admin import credentials, firestore
import openai
from datetime import datetime, timezone, timedelta
import concurrent.futures
import os
import re
import requests
from google.cloud import storage
import nltk
from nltk.corpus import stopwords

def initialize_firebase():
    """Initialize Firebase Admin SDK"""
    if not firebase_admin._apps:
        import os
        try:
            # First, try to use service account key if it exists
            service_account_path = os.path.join(os.path.dirname(__file__), 'serviceAccountKey.json')
            
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
openai.api_key = os.getenv('OPENAI_API_KEY')

print("Successfully connected to Firebase Firestore")

# Base directory to save the HTML files
base_dir = "/Users/_akira/CSAD/websites-new-2025/work-in-progress/hetnieuws-app"

# Download stopwords if not already present
nltk.download('stopwords')

# Load stopwords
stop_words = set(stopwords.words('dutch'))

# Function to generate rewritten text using OpenAI API
def generate_text(prompt, max_tokens=512):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Rewrite in Easy to Read Business Style."},
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
        return "https://via.placeholder.com/400"  # Fallback to a default image URL
    
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
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Classify the category of the following text with one word."},
                {"role": "user", "content": full_text}
            ],
            max_tokens=10
        )
        category = response.choices[0].message["content"].strip().split()[0]  # Take only the first word
        return category
    except Exception as e:
        print(f"Error getting category: {e}")
        return "Uncategorized"  # Fallback category

# Function to get tags based on full text
def get_tags(full_text):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Generate three tags for the following text. Keep them short — between 1 and 3 words."},
                {"role": "user", "content": full_text}
            ],
            max_tokens=20
        )
        tags = response.choices[0].message["content"].strip().split(", ")
        return tags[:3]  # Limit to three tags
    except Exception as e:
        print(f"Error getting tags: {e}")
        return ["Tag1", "Tag2", "Tag3"]  # Fallback tags

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
        rewritten_body_chunk = generate_text(f"Rewrite in Easy to Read Business Style:\n\n{chunk}", max_tokens=chunk_size)
        rewritten_body += rewritten_body_chunk + " "
    
    rewritten_body = rewritten_body.strip()

    # Remove original images from the body text
    rewritten_body = remove_original_images(rewritten_body)

    # Generate new image URL based on the rewritten title
    image_url = generate_image(rewritten_title)
    if not image_url:
        image_url = generate_image(rewritten_body)
    if not image_url:
        image_url = None

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
        doc_ref = db.collection('HetNieuws.RW').document()
        doc_ref.set(article_data)
        print(f"Article saved to Firestore with ID: {doc_ref.id}")
        
        # Mark original as processed if it exists
        if article.get("link"):
            # Update the original article to mark as processed
            raw_docs = db.collection('HetNieuws.Raw').where('link', '==', article["link"]).get()
            for doc in raw_docs:
                doc.reference.update({"processed": True})
        
        return article_data, uploaded_image_url
    except Exception as e:
        print(f"Error saving to Firestore: {e}")
        return None, None

def main():
    """Main function to process articles"""
    try:
        # Get unprocessed articles from Firestore
        raw_collection = db.collection('HetNieuws.Raw')
        unprocessed_docs = raw_collection.where('processed', '!=', True).get()
        
        articles = []
        for doc in unprocessed_docs:
            article_data = doc.to_dict()
            article_data['id'] = doc.id
            articles.append(article_data)
        
        print(f"Found {len(articles)} unprocessed articles")
        
        # Process articles with parallel processing
        rewritten_articles = []
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(rewrite_article, article, base_dir, bucket_name) for article in articles]
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
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

        print(f"Successfully processed {len(rewritten_articles)} articles")
        
    except Exception as e:
        print(f"Error in main processing: {e}")

if __name__ == "__main__":
    main()
