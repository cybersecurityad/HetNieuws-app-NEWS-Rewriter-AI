# 🔗 **HetNieuws App - Isolated Components**

## 📁 **Architecture Overview**

The HetNieuws app now has **isolated components** for better modularity and cost control:

```
hetnieuws-app/
├── rewrite-python/
│   ├── firebase-rewriter.py     ← Main text rewriter (no images)
│   ├── image_generator.py       ← Isolated image generator
│   ├── news-ripper-selenium.py  ← Article scraper
│   └── setup-ai-provider.sh     ← AI provider setup
```

## 🧠 **Text Rewriting (FREE with Groq)**

### What it does:
- ✅ Rewrites article titles and content
- ✅ Generates categories and tags
- ✅ Saves to Firestore (`HetNieuws_Rewritten`)
- ✅ **Cost: $0.00** (using Groq AI)

### How to run:
```bash
cd rewrite-python
python firebase-rewriter.py
```

### Features:
- 🔄 Processes 3 articles at a time (rate limit friendly)
- ⚡ Uses Groq AI (free tier with 6000 tokens/minute)
- 🏠 Falls back to Ollama (local, free) if available
- 💰 Falls back to DeepSeek (very cheap) if configured

---

## 🎨 **Image Generation (ISOLATED)**

### What it does:
- 🖼️ Generates images for articles
- ☁️ Uploads to Firebase Storage
- 🔗 Updates articles with image URLs
- 💸 **Cost varies by provider**

### Supported providers:
1. **OpenAI DALL-E** - $0.02 per image
2. **Stability AI** - $0.01 per image
3. **Replicate** - $0.005 per image

### How to run:
```bash
# Test image generation
python image_generator.py

# Add images to existing articles
python image_generator.py add-to-existing
```

### Setup:
```bash
# For OpenAI (has billing issue currently)
export OPENAI_API_KEY="your-key"

# For Stability AI (recommended for images)
export STABILITY_API_KEY="your-key"

# For Replicate (cheapest)
export REPLICATE_API_TOKEN="your-key"
```

---

## 🔄 **Complete Workflow**

### 1. Scrape Articles
```bash
python news-ripper-selenium.py
```
**Result**: Raw articles saved to `HetNieuws_Raw` collection

### 2. Rewrite Articles (FREE)
```bash
python firebase-rewriter.py
```
**Result**: Rewritten articles saved to `HetNieuws_Rewritten` collection

### 3. Add Images (OPTIONAL)
```bash
python image_generator.py add-to-existing
```
**Result**: Images added to articles in both collections

### 4. Website Display
- Frontend loads from `HetNieuws_Raw` collection
- Articles appear on https://hetnieuws.app/

---

## 💡 **Benefits of Isolation**

### ✅ **Cost Control**
- Run text rewriting for FREE (Groq)
- Run image generation only when needed
- Choose different AI providers for different tasks

### ✅ **Flexibility**
- Text rewriting works without images
- Can add images later to existing articles
- Easy to test different image providers

### ✅ **Reliability**
- Text rewriting won't fail due to image issues
- Can process large batches of text quickly
- Images processed separately at own pace

### ✅ **Scalability**
- Process hundreds of articles (text only) quickly
- Generate images for selected articles only
- Easy to run on different schedules

---

## 🚀 **Current Status**

### ✅ **Working**
- Article scraping from NU.nl
- Text rewriting with Groq (FREE)
- Article display on website
- Firebase integration

### 🎯 **Optional**
- Image generation (when budget allows)
- Multiple AI provider support
- Batch image processing

### 💰 **Costs**
- **Article scraping**: FREE
- **Text rewriting**: FREE (Groq)
- **Website hosting**: FREE (Firebase)
- **Image generation**: $0.005-$0.02 per image (optional)

---

## 🔧 **Quick Commands**

```bash
# Full pipeline without images (FREE)
python news-ripper-selenium.py && python firebase-rewriter.py

# Add images to 3 articles
python image_generator.py add-to-existing

# Check what articles need images
python -c "
import firebase_admin
from firebase_admin import credentials, firestore
firebase_admin.initialize_app(credentials.Certificate('../serviceAccountKey.json'))
db = firestore.client()
docs = db.collection('HetNieuws_Raw').get()
no_image = sum(1 for doc in docs if not doc.to_dict().get('image_url'))
print(f'Articles without images: {no_image}')
"
```
