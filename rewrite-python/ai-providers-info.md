# Free/Cheap AI Providers for Text Rewriting

## 1. DeepSeek (Recommended - Very Cheap)
- **Cost**: ~$0.14 per 1M tokens (vs OpenAI $0.50-$2.00)
- **Quality**: Excellent, comparable to GPT-3.5
- **Setup**: Get API key from https://platform.deepseek.com
- **Environment variable**: `DEEPSEEK_API_KEY`

## 2. Groq (Free Tier)
- **Cost**: Free tier with rate limits
- **Speed**: Very fast inference
- **Models**: Llama 3, Mixtral, Gemma
- **Setup**: Get API key from https://console.groq.com
- **Environment variable**: `GROQ_API_KEY`

## 3. Together AI (Free Credits)
- **Cost**: $5 free credits, then $0.20-$0.80 per 1M tokens
- **Models**: Many open source models
- **Setup**: Get API key from https://api.together.xyz
- **Environment variable**: `TOGETHER_API_KEY`

## 4. Ollama (Completely Free - Local)
- **Cost**: Free (runs on your computer)
- **Models**: Llama 3, Mistral, CodeLlama, etc.
- **Setup**: Download from https://ollama.ai
- **Note**: Requires good computer specs

## 5. Hugging Face (Free)
- **Cost**: Free with rate limits
- **Models**: Many open source models
- **Setup**: Get API key from https://huggingface.co
- **Environment variable**: `HUGGINGFACE_API_KEY`

## Quick Setup for DeepSeek (Recommended):

1. Go to https://platform.deepseek.com
2. Sign up and get an API key
3. Set environment variable:
   ```bash
   export DEEPSEEK_API_KEY="your-api-key-here"
   ```
4. Run the script - it will automatically use DeepSeek

## Cost Comparison (per 1M tokens):
- OpenAI GPT-3.5: $0.50-$2.00
- OpenAI GPT-4: $10-$30
- DeepSeek: $0.14
- Groq: Free tier
- Together AI: $0.20-$0.80
- Ollama: Free (local)
