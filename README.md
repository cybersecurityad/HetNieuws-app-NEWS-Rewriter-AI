# HetNieuws-app NEWS Rewriter AI

## Overview
HetNieuws-app NEWS Rewriter AI is a Python-powered CLI tool for rewriting news and media articles, generating SEO-optimized HTML (with canonical URLs, meta tags, and structured data), and publishing them to Firebase Storage for public access. It supports AI model selection, automated Firestore integration, and ensures all articles are discoverable and indexable by search engines.

## Features
- Rewrite news/media articles using AI (Groq, OpenAI, etc.)
- Generate SEO-optimized HTML with:
  - Canonical URLs
  - Article-specific meta tags (title, description, keywords)
  - Open Graph and Twitter Card tags
  - JSON-LD NewsArticle structured data
- Save output to `/public/category/[category]/[slug]/index.html`
- Upload identical HTML to Firebase Storage for public access
- Firestore integration for article metadata
- CLI menu for workflow automation
- Debug output for verification

## SEO Best Practices
- Each article HTML includes unique canonical and meta tags
- Structured data (JSON-LD) for Google News and rich snippets
- Open Graph and Twitter tags for social sharing
- Output structure matches best URL practices (`/category/[category]/[slug]/index.html`)
- Firebase Storage rules allow public read for all articles

## Installation

### Prerequisites
- Python 3.8+
- Node.js (for Firebase CLI)
- Firebase project with Storage and Firestore enabled
- Service account key (`serviceAccountKey.json`)

### Setup
1. Clone the repository:
   ```sh
   git clone https://github.com/cybersecurityad/HetNieuws-app-NEWS-Rewriter-AI.git
   cd HetNieuws-app-NEWS-Rewriter-AI
   ```
2. Install Python dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. Install Firebase CLI (if not already):
   ```sh
   npm install -g firebase-tools
   ```
4. Add your Firebase service account key to `serviceAccountKey.json`.
5. Configure Firebase Storage rules for public read access (see `storage.rules`).
6. Run the CLI:
   ```sh
   cd rewrite-python
   python3 firebase-rewriter.py
   ```

## Usage
- Follow the CLI prompts to rewrite and publish articles.
- Output HTML is saved locally and uploaded to Firebase Storage.
- Access published articles at `https://hetnieuws.app/category/[category]/[slug]/`.

## License
This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

## Contributing
Pull requests and issues are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md).

## Security
See [SECURITY.md](SECURITY.md) for vulnerability reporting and security best practices.

## Contact
For support or questions, open an issue or contact the repository owner via GitHub.

---

### SEO Tips for Editors
- Use clear, descriptive titles and summaries
- Add relevant keywords to each article
- Ensure images have alt text and are uploaded via the CLI
- Check canonical URLs match the public article URL
- Validate structured data with Google's Rich Results Test
