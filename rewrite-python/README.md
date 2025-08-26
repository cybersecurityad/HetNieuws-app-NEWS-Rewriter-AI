# HetNieuws Article Rewriter - Python Backend

This directory contains Python scripts for automatically rewriting Dutch news articles using AI providers like Groq and OpenAI.

## 🚀 Quick Start

### 1. Setup Environment
```bash
# Set your Groq API key
export GROQ_API_KEY="your_api_key_here"

# Run the setup script
./setup-ai-provider.sh
```

### 2. Run the Advanced Rewriter
```bash
python firebase-rewriter-advanced.py
```

## 📁 File Structure

### Core Scripts
- **`firebase-rewriter-advanced.py`** - Advanced rewriter with menu system, multiple languages, styles, and HTML formatting
- **`firebase-rewriter.py`** - Original simple rewriter (legacy)
- **`news-ripper-selenium.py`** - Article extraction from NU.nl using Selenium
- **`image_generator.py`** - Isolated image generation functionality

### Setup & Configuration
- **`setup-ai-provider.sh`** - One-click setup for AI provider credentials
- **`firebase-rewriter-backup.py`** - Backup copy of original rewriter

### Documentation
- **`ai-providers-info.md`** - Information about AI providers (Groq, OpenAI, costs, etc.)
- **`DUTCH-LANGUAGE-FIX.md`** - Solutions for Dutch language processing
- **`ISOLATED-ARCHITECTURE.md`** - Architecture documentation for separated concerns

## 🎯 Features

### Advanced Rewriter (`firebase-rewriter-advanced.py`)
- **🎨 Multiple Writing Styles**: Professional, Casual, Formal
- **🌍 Multi-language Support**: Dutch (NL), English (EN), German (DE), French (FR)
- **📄 HTML Formatting**: Clean HTML output with proper structure
- **🔄 Batch Processing**: Process multiple articles efficiently
- **⚡ Groq Integration**: Free/cheap AI processing
- **🛡️ Error Handling**: Comprehensive error management and retries
- **📊 Menu System**: Interactive command-line interface

### News Ripper (`news-ripper-selenium.py`)
- **🔍 Article Extraction**: Automated scraping from NU.nl
- **📱 Dynamic Content**: Handles JavaScript-rendered content
- **🎯 Smart Filtering**: Skips video content and premium articles
- **🔄 Firestore Integration**: Direct upload to Firebase database

## 🎛️ Usage Examples

### Interactive Menu Mode
```bash
python firebase-rewriter-advanced.py
# Follow the interactive prompts to select:
# 1. Writing style (Professional/Casual/Formal)
# 2. Language (NL/EN/DE/FR)
# 3. Output format (Plain text/HTML)
# 4. Processing mode (Single/Batch)
```

### Environment Variables
```bash
# Required
export GROQ_API_KEY="gsk_..."

# Optional
export OPENAI_API_KEY="sk-..."  # Fallback provider
export BATCH_SIZE="10"          # Articles per batch
export MAX_RETRIES="3"          # Retry attempts on failure
```

## 🔧 Dependencies

```bash
pip install firebase-admin groq openai selenium beautifulsoup4 python-dateutil
```

## 📋 Prerequisites

1. **Firebase Setup**: Service account key (`serviceAccountKey.json`)
2. **Groq API Key**: Free tier available at [console.groq.com](https://console.groq.com)
3. **Chrome/Firefox**: For Selenium web scraping
4. **Python 3.8+**: Required for all scripts

## 🌐 AI Providers

### Groq (Recommended)
- **Cost**: Free tier available
- **Speed**: Very fast inference
- **Models**: llama3-8b-8192, mixtral-8x7b-32768
- **Setup**: Get API key from console.groq.com

### OpenAI (Fallback)
- **Cost**: Pay per token
- **Models**: gpt-3.5-turbo, gpt-4
- **Setup**: Get API key from platform.openai.com

## 🔍 Architecture

```
rewrite-python/
├── Core Processing
│   ├── firebase-rewriter-advanced.py  # Main rewriter with menu
│   ├── firebase-rewriter.py           # Legacy simple rewriter
│   └── news-ripper-selenium.py        # Article extraction
├── Utilities
│   ├── image_generator.py             # Image processing
│   └── setup-ai-provider.sh           # Environment setup
└── Documentation
    ├── README.md                      # This file
    ├── ai-providers-info.md           # AI provider details
    ├── DUTCH-LANGUAGE-FIX.md          # Language processing
    └── ISOLATED-ARCHITECTURE.md       # Architecture docs
```

## 🚀 Deployment

### Production Setup
1. **Set Environment Variables**:
   ```bash
   export GROQ_API_KEY="your_production_key"
   export FIREBASE_PROJECT_ID="your_project_id"
   ```

2. **Run Rewriter**:
   ```bash
   # Single article mode
   python firebase-rewriter-advanced.py

   # Batch processing
   python firebase-rewriter-advanced.py --batch
   ```

3. **Monitor Logs**:
   ```bash
   tail -f rewriter.log
   ```

## 🛠️ Troubleshooting

### Common Issues

1. **"No API key found"**
   ```bash
   export GROQ_API_KEY="your_key_here"
   source ~/.bashrc  # or ~/.zshrc
   ```

2. **"Chrome driver not found"**
   ```bash
   # Install ChromeDriver
   brew install chromedriver  # macOS
   # or download from https://chromedriver.chromium.org/
   ```

3. **"Firebase permission denied"**
   - Check `serviceAccountKey.json` exists
   - Verify Firebase project permissions
   - Update Firestore security rules

4. **"Article content too long"**
   - Content is automatically truncated to model limits
   - Consider splitting long articles into sections

### Performance Tips

- **Use Groq for speed** (recommended for production)
- **Batch process** for efficiency (10-20 articles at once)
- **Monitor API quotas** to avoid rate limiting
- **Cache results** to avoid re-processing

## 📈 Development

### Adding New Languages
1. Update `LANGUAGE_OPTIONS` in `firebase-rewriter-advanced.py`
2. Add corresponding prompts for the new language
3. Test with sample articles

### Adding New AI Providers
1. Create new client class (similar to `GroqClient`)
2. Add provider option to menu system
3. Update environment variable handling

### Testing
```bash
# Test with sample article
python firebase-rewriter-advanced.py --test

# Test specific language
python firebase-rewriter-advanced.py --lang=en --test

# Test batch processing
python firebase-rewriter-advanced.py --batch --limit=5
```

## 📚 Related Files

- **Frontend**: `/public/index.html` - Displays rewritten articles
- **Firebase Config**: `/firebase.json` - Hosting and rewrites
- **Firestore Rules**: `/firestore.rules` - Database security
- **Main Config**: `/package.json` - Project configuration

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes in the `rewrite-python/` directory
4. Test thoroughly with sample articles
5. Submit a pull request with descriptive commit messages

## 📄 License

This project is part of the HetNieuws.app platform. See the main project LICENSE file for details.

---

**Last Updated**: January 2025  
**Version**: 2.0.0 (Advanced Rewriter)  
**Maintainer**: HetNieuws.app Development Team
