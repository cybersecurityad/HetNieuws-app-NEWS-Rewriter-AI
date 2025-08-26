# API Documentation

## HetNieuws.app API Reference

### Base URL
```
https://hetnieuws.app/api
```

### Authentication
Currently, the API does not require authentication for public endpoints. Private endpoints use Firebase Admin SDK.

### Content Endpoints

#### Get Latest News
```http
GET /api/news/latest
```

**Parameters:**
- `limit` (optional): Number of articles to return (default: 10, max: 50)
- `category` (optional): Filter by category

**Response:**
```json
{
  "status": "success",
  "data": [
    {
      "id": "article_id",
      "title": "Article Title",
      "content": "Article content...",
      "category": "politics",
      "timestamp": "2024-08-26T12:00:00Z",
      "source": "source_name"
    }
  ]
}
```

#### Get News by Category
```http
GET /api/news/category/{category}
```

**Parameters:**
- `category`: Category name (politics, sports, culture, etc.)
- `limit` (optional): Number of articles to return

#### Search News
```http
GET /api/news/search
```

**Parameters:**
- `q`: Search query
- `limit` (optional): Number of results to return

### Categories

Available categories:
- `politics` - Political news
- `sports` - Sports coverage
- `culture` - Cultural events
- `health` - Health and medical news
- `technology` - Technology updates
- `international` - International news

### Response Format

All API responses follow this format:
```json
{
  "status": "success|error",
  "data": {},
  "message": "Optional message",
  "timestamp": "2024-08-26T12:00:00Z"
}
```

### Error Handling

Error responses include:
- `400` - Bad Request
- `404` - Not Found
- `500` - Internal Server Error

### Rate Limiting

- 100 requests per minute per IP
- 1000 requests per hour per IP

### Content Processing

#### AI Rewriting Endpoint
```http
POST /api/content/rewrite
```

**Headers:**
```
Content-Type: application/json
Authorization: Bearer {api_key}
```

**Body:**
```json
{
  "content": "Original content to rewrite",
  "target_language": "nl",
  "style": "news"
}
```

### Webhooks

#### Content Update Webhook
```http
POST /api/webhooks/content-update
```

Triggered when new content is processed and available.

### SDK Usage

#### Node.js Example
```javascript
const axios = require('axios');

async function getLatestNews() {
  try {
    const response = await axios.get('https://hetnieuws.app/api/news/latest');
    return response.data;
  } catch (error) {
    console.error('Error fetching news:', error);
  }
}
```

#### Python Example
```python
import requests

def get_latest_news():
    try:
        response = requests.get('https://hetnieuws.app/api/news/latest')
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching news: {e}")
```

### Contributing

To contribute to the API:
1. Fork the repository
2. Create a feature branch
3. Add your changes
4. Submit a pull request

### Support

For API support:
- GitHub Issues: [Report bugs](https://github.com/cybersecurityad/HetNieuws-app-NEWS-Rewriter-AI/issues)
- Email: api@hetnieuws.app
- Documentation: [Wiki](https://github.com/cybersecurityad/HetNieuws-app-NEWS-Rewriter-AI/wiki)
