#!/usr/bin/env python3
"""
Advanced Firebase News Rewriter
Enhanced with menu system and multiple language/style options
"""

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
import sys
import json

# Global configuration variables
config = {
    'rewrite_style': 'Normal',
    'target_language': 'Dutch',
    'collection_name': 'HetNieuws_Rewritten',
    'add_html_formatting': True,
    'max_title_length': 160,
    'num_tags': 3,
    'batch_size': 3
}

# Available options
REWRITE_STYLES = {
    '1': 'Technical',
    '2': 'Normal', 
    '3': 'Easy'
}

LANGUAGES = {
    '1': 'Dutch',
    '2': 'English',
    '3': 'German'
}

# Language mappings for AI prompts
LANGUAGE_PROMPTS = {
    'Dutch': {
        'rewrite': "Herschrijf de volgende Nederlandse tekst in het Nederlands",
        'category': "Classificeer de categorie van de volgende Nederlandse tekst met één woord in het Nederlands. Kies uit: Politiek, Sport, Economie, Gezondheid, Technologie, Cultuur, Onderwijs, Milieu, Internationaal, of Nieuws.",
        'tags': "Genereer precies drie Nederlandse tags gescheiden door komma's. Bijvoorbeeld: 'Politiek, Nederland, Verkiezingen'. Gebruik korte woorden van 1-3 woorden elk.",
        'title': "Maak een pakkende Nederlandse titel van maximaal 160 karakters voor de volgende tekst:"
    },
    'English': {
        'rewrite': "Rewrite the following text in English",
        'category': "Classify the category of the following text with one word in English. Choose from: Politics, Sports, Economy, Health, Technology, Culture, Education, Environment, International, or News.",
        'tags': "Generate exactly three English tags separated by commas. Example: 'Politics, Elections, Government'. Use short words of 1-3 words each.",
        'title': "Create a compelling English title of maximum 160 characters for the following text:"
    },
    'German': {
        'rewrite': "Schreibe den folgenden Text auf Deutsch um",
        'category': "Klassifiziere die Kategorie des folgenden Textes mit einem Wort auf Deutsch. Wähle aus: Politik, Sport, Wirtschaft, Gesundheit, Technologie, Kultur, Bildung, Umwelt, International oder Nachrichten.",
        'tags': "Generiere genau drei deutsche Tags getrennt durch Kommas. Beispiel: 'Politik, Deutschland, Wahlen'. Verwende kurze Wörter von 1-3 Wörtern.",
        'title': "Erstelle einen ansprechenden deutschen Titel von maximal 160 Zeichen für den folgenden Text:"
    }
}

STYLE_MODIFIERS = {
    'Technical': {
        'Dutch': "in een technische en gedetailleerde stijl met vakjargon en precisieterminologie",
        'English': "in a technical and detailed style with professional jargon and precision terminology",
        'German': "in einem technischen und detaillierten Stil mit Fachsprache und präziser Terminologie"
    },
    'Normal': {
        'Dutch': "in een duidelijke en toegankelijke stijl voor het algemene publiek",
        'English': "in a clear and accessible style for the general public",
        'German': "in einem klaren und zugänglichen Stil für die Allgemeinheit"
    },
    'Easy': {
        'Dutch': "in een eenvoudige stijl die iedereen kan begrijpen, vermijd moeilijke woorden en gebruik korte zinnen",
        'English': "in a simple style that everyone can understand, avoid difficult words and use short sentences",
        'German': "in einem einfachen Stil, den jeder verstehen kann, vermeide schwierige Wörter und verwende kurze Sätze"
    }
}

def initialize_firebase():
    """Initialize Firebase Admin SDK"""
    if not firebase_admin._apps:
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
            raise e

def initialize_ai_client():
    """Initialize AI client based on available providers"""
    # Check for Groq first (free tier)
    groq_api_key = os.getenv('GROQ_API_KEY')
    if groq_api_key:
        try:
            from groq import Groq
            client = Groq(api_key=groq_api_key)
            model_name = "llama-3.1-8b-instant"  # Updated to current model
            print("⚡ Using Groq AI - Cost: Free tier available!")
            return client, model_name
        except ImportError:
            print("⚠️ Groq library not installed. Install with: pip install groq")
    
    # Fallback to OpenAI
    openai_api_key = os.getenv('OPENAI_API_KEY')
    if openai_api_key:
        try:
            client = OpenAI(api_key=openai_api_key)
            model_name = "gpt-3.5-turbo"
            print("🤖 Using OpenAI API - Cost: Pay per use")
            return client, model_name
        except ImportError:
            print("⚠️ OpenAI library not installed. Install with: pip install openai")
    
    print("❌ No AI provider configured. Please set GROQ_API_KEY or OPENAI_API_KEY environment variable")
    return None, None

def display_main_menu():
    """Display the main menu"""
    print("\n" + "="*60)
    print("🚀 ADVANCED FIREBASE NEWS REWRITER")
    print("="*60)
    print(f"📝 Current Settings:")
    print(f"   • Rewrite Style: {config['rewrite_style']}")
    print(f"   • Target Language: {config['target_language']}")
    print(f"   • Collection: {config['collection_name']}")
    print(f"   • HTML Formatting: {'Yes' if config['add_html_formatting'] else 'No'}")
    print(f"   • Max Title Length: {config['max_title_length']} chars")
    print(f"   • Number of Tags: {config['num_tags']}")
    print(f"   • Batch Size: {config['batch_size']}")
    print("\n📋 Main Menu:")
    print("A. Configure Rewrite Style")
    print("B. Configure Target Language") 
    print("C. Configure Database Settings")
    print("D. Start Rewriting Process")
    print("E. View Current Configuration")
    print("F. Reset to Defaults")
    print("G. Exit")
    print("-"*60)

def configure_rewrite_style():
    """Configure rewrite style menu"""
    print("\n📝 Configure Rewrite Style:")
    print("1. Technical - Detailed with professional terminology")
    print("2. Normal - Clear and accessible for general public")
    print("3. Easy - Simple language, easy to understand")
    
    choice = input("\nSelect style (1-3): ").strip()
    if choice in REWRITE_STYLES:
        config['rewrite_style'] = REWRITE_STYLES[choice]
        print(f"✅ Rewrite style set to: {config['rewrite_style']}")
    else:
        print("❌ Invalid choice. Style unchanged.")

def configure_target_language():
    """Configure target language menu"""
    print("\n🌍 Configure Target Language:")
    print("1. Dutch - Nederlandse taal")
    print("2. English - English language")
    print("3. German - Deutsche Sprache")
    
    choice = input("\nSelect language (1-3): ").strip()
    if choice in LANGUAGES:
        config['target_language'] = LANGUAGES[choice]
        print(f"✅ Target language set to: {config['target_language']}")
    else:
        print("❌ Invalid choice. Language unchanged.")

def configure_database_settings():
    """Configure database settings menu"""
    print("\n💾 Configure Database Settings:")
    print("1. Toggle HTML Formatting (H2, H3, P tags)")
    print("2. Set Max Title Length")
    print("3. Set Number of Tags")
    print("4. Set Batch Size")
    print("5. Set Collection Name")
    print("6. Back to Main Menu")
    
    choice = input("\nSelect option (1-6): ").strip()
    
    if choice == '1':
        config['add_html_formatting'] = not config['add_html_formatting']
        print(f"✅ HTML formatting: {'Enabled' if config['add_html_formatting'] else 'Disabled'}")
    
    elif choice == '2':
        try:
            length = int(input(f"Enter max title length (current: {config['max_title_length']}): "))
            if 50 <= length <= 300:
                config['max_title_length'] = length
                print(f"✅ Max title length set to: {length}")
            else:
                print("❌ Length must be between 50 and 300 characters")
        except ValueError:
            print("❌ Invalid number")
    
    elif choice == '3':
        try:
            num_tags = int(input(f"Enter number of tags (1-5, current: {config['num_tags']}): "))
            if 1 <= num_tags <= 5:
                config['num_tags'] = num_tags
                print(f"✅ Number of tags set to: {num_tags}")
            else:
                print("❌ Number of tags must be between 1 and 5")
        except ValueError:
            print("❌ Invalid number")
    
    elif choice == '4':
        try:
            batch_size = int(input(f"Enter batch size (1-10, current: {config['batch_size']}): "))
            if 1 <= batch_size <= 10:
                config['batch_size'] = batch_size
                print(f"✅ Batch size set to: {batch_size}")
            else:
                print("❌ Batch size must be between 1 and 10")
        except ValueError:
            print("❌ Invalid number")
    
    elif choice == '5':
        collection = input(f"Enter collection name (current: {config['collection_name']}): ").strip()
        if collection:
            config['collection_name'] = collection
            print(f"✅ Collection name set to: {collection}")
        else:
            print("❌ Collection name cannot be empty")
    
    elif choice == '6':
        return
    else:
        print("❌ Invalid choice")

def view_configuration():
    """Display current configuration"""
    print("\n⚙️ Current Configuration:")
    print("-"*40)
    for key, value in config.items():
        print(f"{key.replace('_', ' ').title()}: {value}")
    print("-"*40)

def reset_to_defaults():
    """Reset configuration to defaults"""
    global config
    config = {
        'rewrite_style': 'Normal',
        'target_language': 'Dutch',
        'collection_name': 'HetNieuws_Rewritten',
        'add_html_formatting': True,
        'max_title_length': 160,
        'num_tags': 3,
        'batch_size': 3
    }
    print("✅ Configuration reset to defaults")

def add_html_formatting(text):
    """Add HTML formatting to text with H2, H3, and P tags"""
    if not config['add_html_formatting']:
        return text
    
    # Split text into paragraphs
    paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
    
    if not paragraphs:
        return text
    
    formatted_text = []
    
    for i, paragraph in enumerate(paragraphs):
        # First paragraph as H2 (main heading)
        if i == 0 and len(paragraph) < 100:
            formatted_text.append(f"<h2>{paragraph}</h2>")
        # Every 3rd paragraph as H3 (subheading) if it's short
        elif i % 3 == 0 and len(paragraph) < 80:
            formatted_text.append(f"<h3>{paragraph}</h3>")
        else:
            formatted_text.append(f"<p>{paragraph}</p>")
        
        # Add spacious line breaks between chunks
        if i > 0 and i % 2 == 0:
            formatted_text.append("")
    
    return "\n\n".join(formatted_text)

def generate_optimized_title(full_text, client, model_name):
    """Generate an optimized title from full text"""
    lang_prompts = LANGUAGE_PROMPTS[config['target_language']]
    
    try:
        # Use first 500 characters for title generation
        text_sample = full_text[:500] + "..." if len(full_text) > 500 else full_text
        
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": f"{lang_prompts['title']} Maximaal {config['max_title_length']} karakters."},
                {"role": "user", "content": text_sample}
            ],
            max_tokens=50
        )
        
        title = response.choices[0].message.content.strip()
        
        # Ensure title doesn't exceed max length
        if len(title) > config['max_title_length']:
            title = title[:config['max_title_length']-3] + "..."
        
        return title
    except Exception as e:
        print(f"Error generating title: {e}")
        # Fallback: create title from first sentence
        first_sentence = full_text.split('.')[0]
        if len(first_sentence) > config['max_title_length']:
            return first_sentence[:config['max_title_length']-3] + "..."
        return first_sentence

def rewrite_article_content(full_text, client, model_name):
    """Rewrite article content with current style and language"""
    lang_prompts = LANGUAGE_PROMPTS[config['target_language']]
    style_modifier = STYLE_MODIFIERS[config['rewrite_style']][config['target_language']]
    
    try:
        system_prompt = f"{lang_prompts['rewrite']} {style_modifier}. Behoud de belangrijkste informatie en feiten."
        
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": full_text}
            ],
            max_tokens=2000
        )
        
        rewritten_text = response.choices[0].message.content
        return add_html_formatting(rewritten_text)
    except Exception as e:
        print(f"Error rewriting content: {e}")
        return add_html_formatting(full_text)  # Return formatted original text

def get_category(full_text, client, model_name):
    """Get article category"""
    lang_prompts = LANGUAGE_PROMPTS[config['target_language']]
    
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": lang_prompts['category']},
                {"role": "user", "content": full_text[:500]}  # Use first 500 chars
            ],
            max_tokens=10
        )
        
        category = response.choices[0].message.content.strip().split()[0]
        return category
    except Exception as e:
        print(f"Error getting category: {e}")
        return "Nieuws" if config['target_language'] == 'Dutch' else "News"

def get_tags(full_text, client, model_name):
    """Get article tags"""
    lang_prompts = LANGUAGE_PROMPTS[config['target_language']]
    
    try:
        tag_prompt = lang_prompts['tags'].replace("drie", str(config['num_tags']))
        
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": tag_prompt},
                {"role": "user", "content": full_text[:300]}  # Use first 300 chars
            ],
            max_tokens=50
        )
        
        tags_text = response.choices[0].message.content.strip()
        tags = [tag.strip() for tag in tags_text.split(',')][:config['num_tags']]
        return tags
    except Exception as e:
        print(f"Error getting tags: {e}")
        default_tags = {
            'Dutch': ["Nederland", "Nieuws", "Actueel"],
            'English': ["News", "Current", "Events"],
            'German': ["Nachrichten", "Aktuell", "Deutschland"]
        }
        return default_tags[config['target_language']][:config['num_tags']]

def get_current_timestamp():
    """Get current timestamp with UTC+02:00 offset"""
    amsterdam_tz = timezone(timedelta(hours=2))
    return datetime.now(amsterdam_tz).strftime('%Y-%m-%d %H:%M:%S')

def process_articles(client, model_name, db):
    """Main article processing function"""
    print(f"\n🔄 Starting article processing...")
    print(f"📊 Configuration: {config['rewrite_style']} style, {config['target_language']} language")
    
    try:
        # Get unprocessed articles
        raw_articles = db.collection("HetNieuws_Raw").stream()
        processed_articles = db.collection(config['collection_name']).stream()
        
        # Get processed article titles for deduplication
        processed_titles = set()
        for doc in processed_articles:
            data = doc.to_dict()
            if 'title' in data:
                processed_titles.add(data['title'])
        
        print(f"Found {len(processed_titles)} already processed articles")
        
        # Filter unprocessed articles
        unprocessed_articles = []
        for doc in raw_articles:
            article = doc.to_dict()
            if article.get('title') not in processed_titles:
                # Skip video and premium content
                title = article.get('title', '')
                if 'Video |' in title or 'NU+ |' in title:
                    print(f"⏭️ Skipping: {title[:50]}...")
                    continue
                unprocessed_articles.append(article)
        
        print(f"Found {len(unprocessed_articles)} unprocessed articles")
        
        if not unprocessed_articles:
            print("✅ All articles have been processed!")
            return
        
        # Process articles in batches
        articles_to_process = unprocessed_articles[:config['batch_size']]
        print(f"Processing {len(articles_to_process)} articles...")
        
        for i, article in enumerate(articles_to_process, 1):
            print(f"\n🔄 Processing article {i}/{len(articles_to_process)}: {article.get('title', 'No title')[:60]}...")
            
            full_text = article.get('full_text', article.get('body', ''))
            if not full_text or full_text == "Full text not found.":
                print("⏭️ Skipping article without full text")
                continue
            
            # Process the article
            rewritten_content = rewrite_article_content(full_text, client, model_name)
            optimized_title = generate_optimized_title(rewritten_content, client, model_name)
            category = get_category(full_text, client, model_name)
            tags = get_tags(full_text, client, model_name)
            
            # Prepare document for Firestore
            processed_article = {
                "title": optimized_title,
                "full_text": rewritten_content,
                "summary": rewritten_content[:300] + "..." if len(rewritten_content) > 300 else rewritten_content,
                "category": category,
                "tags": tags,
                "original_title": article.get("title", ""),
                "original_link": article.get("link", ""),
                "published": article.get("published", ""),
                "language": config['target_language'].lower(),
                "style": config['rewrite_style'].lower(),
                "timestamp": get_current_timestamp(),
                "source": "advanced-rewriter"
            }
            
            # Save to Firestore
            try:
                doc_ref = db.collection(config['collection_name']).add(processed_article)
                print(f"✅ Article saved with ID: {doc_ref[1].id}")
                
                print(f"📝 Title: {optimized_title}")
                print(f"📁 Category: {category}")
                print(f"🏷️ Tags: {', '.join(tags)}")
                
            except Exception as e:
                print(f"❌ Error saving article: {e}")
                continue
            
            # Rate limiting
            if i < len(articles_to_process):
                print("⏳ Waiting 3 seconds to respect rate limits...")
                time.sleep(3)
        
        print(f"\n✅ Successfully processed {len(articles_to_process)} articles!")
        
    except Exception as e:
        print(f"❌ Error in processing: {e}")

def main():
    """Main application loop"""
    try:
        # Initialize Firebase
        initialize_firebase()
        db = firestore.client()
        print("Successfully connected to Firebase Firestore")
        
        # Initialize AI client
        client, model_name = initialize_ai_client()
        if not client:
            print("❌ No AI client available. Exiting.")
            return
        
        while True:
            display_main_menu()
            choice = input("Select option (A-G): ").strip().upper()
            
            if choice == 'A':
                configure_rewrite_style()
            elif choice == 'B':
                configure_target_language()
            elif choice == 'C':
                configure_database_settings()
            elif choice == 'D':
                process_articles(client, model_name, db)
            elif choice == 'E':
                view_configuration()
            elif choice == 'F':
                reset_to_defaults()
            elif choice == 'G':
                print("👋 Goodbye! Exiting Advanced Firebase Rewriter")
                break
            else:
                print("❌ Invalid choice. Please select A-G.")
    
    except KeyboardInterrupt:
        print("\n\n⏹️ Process interrupted by user")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()
