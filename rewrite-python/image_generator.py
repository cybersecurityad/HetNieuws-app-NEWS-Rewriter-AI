#!/usr/bin/env python3
"""
Standalone Image Generator for HetNieuws App
Generates images for articles using various AI providers
"""

import os
import sys
import requests
from openai import OpenAI
import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud import storage

def initialize_firebase():
    """Initialize Firebase Admin SDK"""
    if not firebase_admin._apps:
        try:
            service_account_path = os.path.join(os.path.dirname(__file__), '..', 'serviceAccountKey.json')
            
            if os.path.exists(service_account_path):
                print("🔑 Using service account key for Firebase authentication")
                cred = credentials.Certificate(service_account_path)
                firebase_admin.initialize_app(cred, {
                    'projectId': 'hetnieuws-app',
                    'storageBucket': 'hetnieuws-app.appspot.com'
                })
            else:
                print("❌ serviceAccountKey.json not found")
                return False
            
            print("✅ Firebase Admin initialized successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to initialize Firebase: {e}")
            return False

def get_image_ai_client():
    """Get AI client that supports image generation"""
    
    # OpenAI supports image generation
    openai_api_key = os.getenv('OPENAI_API_KEY')
    if openai_api_key:
        print("🎨 Using OpenAI DALL-E for image generation")
        return OpenAI(api_key=openai_api_key), "dall-e-2"
    
    # Stability AI supports image generation
    stability_api_key = os.getenv('STABILITY_API_KEY')
    if stability_api_key:
        print("🎨 Using Stability AI for image generation")
        return "stability", stability_api_key
    
    # Replicate supports image generation
    replicate_api_key = os.getenv('REPLICATE_API_TOKEN')
    if replicate_api_key:
        print("🎨 Using Replicate for image generation")
        return "replicate", replicate_api_key
    
    print("❌ No image generation API key found!")
    print("💡 Available options:")
    print("   • OpenAI: export OPENAI_API_KEY='your-key'")
    print("   • Stability AI: export STABILITY_API_KEY='your-key'")
    print("   • Replicate: export REPLICATE_API_TOKEN='your-key'")
    return None, None

def generate_image_openai(client, prompt):
    """Generate image using OpenAI DALL-E"""
    try:
        if len(prompt) > 800:
            prompt = prompt[:800]
        
        response = client.images.generate(
            prompt=f"Professional news illustration: {prompt}",
            n=1,
            size="512x512"
        )
        
        if response.data and len(response.data) > 0:
            return response.data[0].url
        return None
    except Exception as e:
        print(f"Error generating image with OpenAI: {e}")
        return None

def generate_image_stability(api_key, prompt):
    """Generate image using Stability AI"""
    try:
        import requests
        
        url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"
        
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }
        
        body = {
            "steps": 40,
            "width": 512,
            "height": 512,
            "seed": 0,
            "cfg_scale": 5,
            "samples": 1,
            "text_prompts": [
                {
                    "text": f"Professional news illustration, clean modern style: {prompt}",
                    "weight": 1
                }
            ],
        }
        
        response = requests.post(url, headers=headers, json=body)
        
        if response.status_code == 200:
            data = response.json()
            # Save base64 image and return URL (implementation needed)
            print("Stability AI image generated (base64)")
            return "stability_generated_url"  # Placeholder
        else:
            print(f"Stability AI error: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"Error generating image with Stability AI: {e}")
        return None

def generate_image_replicate(api_token, prompt):
    """Generate image using Replicate"""
    try:
        try:
            import replicate
        except ImportError:
            print("❌ Replicate library not installed. Run: pip install replicate")
            return None
        
        output = replicate.run(
            "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
            input={
                "prompt": f"Professional news illustration, modern clean style: {prompt}",
                "width": 512,
                "height": 512,
                "num_outputs": 1,
                "guidance_scale": 7.5,
                "num_inference_steps": 50
            }
        )
        
        if output and len(output) > 0:
            return output[0]  # Returns URL
        return None
        
    except Exception as e:
        print(f"Error generating image with Replicate: {e}")
        return None

def download_image(image_url, local_path):
    """Download image from URL to local path"""
    try:
        response = requests.get(image_url, stream=True, timeout=30)
        if response.status_code == 200:
            with open(local_path, 'wb') as file:
                for chunk in response.iter_content(1024):
                    file.write(chunk)
            print(f"✅ Image downloaded to {local_path}")
            return local_path
        else:
            print(f"❌ Failed to download image. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error downloading image: {e}")
        return None

def upload_image_to_firebase(local_image_path, bucket_name, destination_blob_name):
    """Upload image to Firebase Storage"""
    try:
        if not os.path.exists(local_image_path):
            raise FileNotFoundError(f"Local file not found: {local_image_path}")
        
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)
        blob.upload_from_filename(local_image_path)
        
        blob.make_public()
        
        print(f"✅ Image uploaded to Firebase: {destination_blob_name}")
        return blob.public_url
    except Exception as e:
        print(f"❌ Error uploading to Firebase Storage: {e}")
        return None

def generate_and_upload_image(title, article_slug, bucket_name='hetnieuws-app.appspot.com'):
    """Generate image and upload to Firebase Storage"""
    
    client, model = get_image_ai_client()
    if not client:
        return None
    
    # Generate image based on title
    print(f"🎨 Generating image for: {title[:50]}...")
    
    if model == "dall-e-2":
        image_url = generate_image_openai(client, title)
    elif client == "stability":
        image_url = generate_image_stability(model, title)
    elif client == "replicate":
        image_url = generate_image_replicate(model, title)
    else:
        print(f"❌ Unknown image generation provider: {client}")
        return None
    
    if not image_url:
        print("❌ Failed to generate image")
        return None
    
    # Download image
    local_path = f"/tmp/{article_slug}.png"
    downloaded_path = download_image(image_url, local_path)
    
    if not downloaded_path:
        return None
    
    # Upload to Firebase
    firebase_path = f"images/{article_slug}.png"
    uploaded_url = upload_image_to_firebase(downloaded_path, bucket_name, firebase_path)
    
    # Cleanup local file
    try:
        os.remove(downloaded_path)
        print(f"🧹 Cleaned up local file: {downloaded_path}")
    except:
        pass
    
    return uploaded_url

def add_images_to_existing_articles():
    """Add images to articles that don't have them"""
    
    if not initialize_firebase():
        return
    
    db = firestore.client()
    
    # Get articles without images from both collections
    collections = ['HetNieuws_Raw', 'HetNieuws_Rewritten']
    
    for collection_name in collections:
        print(f"\n🔍 Checking {collection_name} for articles without images...")
        
        collection_ref = db.collection(collection_name)
        docs = collection_ref.get()
        
        articles_without_images = []
        for doc in docs:
            article = doc.to_dict()
            if article and not article.get('image_url'):
                article['id'] = doc.id
                articles_without_images.append(article)
        
        print(f"📊 Found {len(articles_without_images)} articles without images")
        
        # Process first 3 articles to avoid rate limits
        for i, article in enumerate(articles_without_images[:3]):
            title = article.get('title', 'No title')
            article_slug = article.get('slug', f"article-{article['id']}")
            
            print(f"\n🎨 Processing {i+1}/3: {title[:50]}...")
            
            # Generate and upload image
            image_url = generate_and_upload_image(title, article_slug)
            
            if image_url:
                # Update article with image URL
                doc_ref = collection_ref.document(article['id'])
                doc_ref.update({'image_url': image_url})
                print(f"✅ Updated article with image: {image_url}")
            else:
                print("❌ Failed to generate image for article")
            
            # Rate limiting
            if i < 2:  # Don't sleep after last article
                print("⏳ Waiting 5 seconds...")
                import time
                time.sleep(5)

def main():
    """Main function"""
    print("🎨 HetNieuws Image Generator")
    print("============================")
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "add-to-existing":
            add_images_to_existing_articles()
        else:
            print("Usage: python image_generator.py [add-to-existing]")
    else:
        # Test image generation
        if not initialize_firebase():
            return
        
        test_title = "Breaking News: Important Development in Technology Sector"
        test_slug = "breaking-news-tech"
        
        image_url = generate_and_upload_image(test_title, test_slug)
        
        if image_url:
            print(f"✅ Test image generated: {image_url}")
        else:
            print("❌ Test image generation failed")

if __name__ == "__main__":
    main()
