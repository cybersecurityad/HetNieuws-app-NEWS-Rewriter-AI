#!/bin/bash

# AI Provider Setup Script for HetNieuws App

echo "🤖 AI Provider Setup for News Rewriter"
echo "======================================"
echo ""

echo "Available AI Providers:"
echo "1. DeepSeek (Recommended - Very cheap, excellent quality)"
echo "2. Groq (Free tier available)"
echo "3. Together AI (Free credits)"
echo "4. Ollama (Free local)"
echo "5. OpenAI (Most expensive)"
echo ""

read -p "Which provider would you like to set up? (1-5): " choice

case $choice in
    1)
        echo ""
        echo "🧠 Setting up DeepSeek..."
        echo "1. Go to https://platform.deepseek.com"
        echo "2. Sign up for an account"
        echo "3. Get your API key from the dashboard"
        echo "4. Copy your API key and paste it below:"
        echo ""
        read -p "DeepSeek API Key: " deepseek_key
        echo "export DEEPSEEK_API_KEY=\"$deepseek_key\"" >> ~/.zshrc
        echo "export DEEPSEEK_API_KEY=\"$deepseek_key\"" >> ~/.bash_profile
        export DEEPSEEK_API_KEY="$deepseek_key"
        echo "✅ DeepSeek API key saved!"
        echo "💰 Cost: ~\$0.14 per 1M tokens (very cheap!)"
        ;;
    2)
        echo ""
        echo "⚡ Setting up Groq..."
        echo "1. Go to https://console.groq.com"
        echo "2. Sign up for an account"
        echo "3. Get your API key"
        echo "4. Copy your API key and paste it below:"
        echo ""
        read -p "Groq API Key: " groq_key
        echo "export GROQ_API_KEY=\"$groq_key\"" >> ~/.zshrc
        echo "export GROQ_API_KEY=\"$groq_key\"" >> ~/.bash_profile
        export GROQ_API_KEY="$groq_key"
        echo "✅ Groq API key saved!"
        echo "💰 Cost: Free tier available!"
        ;;
    3)
        echo ""
        echo "🤝 Setting up Together AI..."
        echo "1. Go to https://api.together.xyz"
        echo "2. Sign up for an account"
        echo "3. Get your API key"
        echo "4. Copy your API key and paste it below:"
        echo ""
        read -p "Together AI API Key: " together_key
        echo "export TOGETHER_API_KEY=\"$together_key\"" >> ~/.zshrc
        echo "export TOGETHER_API_KEY=\"$together_key\"" >> ~/.bash_profile
        export TOGETHER_API_KEY="$together_key"
        echo "✅ Together AI API key saved!"
        echo "💰 Cost: \$5 free credits, then \$0.20-\$0.80 per 1M tokens"
        ;;
    4)
        echo ""
        echo "🏠 Setting up Ollama (Local)..."
        echo "1. Go to https://ollama.ai"
        echo "2. Download and install Ollama for macOS"
        echo "3. Run: ollama pull llama3"
        echo "4. Start Ollama service"
        echo ""
        echo "Would you like to install Ollama now? (y/n)"
        read -p "Install Ollama: " install_ollama
        if [ "$install_ollama" = "y" ]; then
            curl -fsSL https://ollama.ai/install.sh | sh
            ollama pull llama3
            echo "✅ Ollama installed and Llama3 model downloaded!"
        fi
        echo "💰 Cost: Completely free (runs locally)"
        ;;
    5)
        echo ""
        echo "🔓 Setting up OpenAI..."
        echo "1. Go to https://platform.openai.com"
        echo "2. Sign up and add billing information"
        echo "3. Get your API key"
        echo "4. Copy your API key and paste it below:"
        echo ""
        read -p "OpenAI API Key: " openai_key
        echo "export OPENAI_API_KEY=\"$openai_key\"" >> ~/.zshrc
        echo "export OPENAI_API_KEY=\"$openai_key\"" >> ~/.bash_profile
        export OPENAI_API_KEY="$openai_key"
        echo "✅ OpenAI API key saved!"
        echo "💰 Cost: \$0.50-\$2.00 per 1M tokens (expensive)"
        ;;
    *)
        echo "Invalid choice. Please run the script again."
        exit 1
        ;;
esac

echo ""
echo "🔄 Reloading shell configuration..."
source ~/.zshrc 2>/dev/null || source ~/.bash_profile 2>/dev/null || true

echo ""
echo "✅ Setup complete!"
echo "🚀 You can now run the news rewriter script:"
echo "   cd /Users/_akira/CSAD/websites-new-2025/work-in-progress/hetnieuws-app/rewrite-python"
echo "   python firebase-rewriter.py"
echo ""
echo "💡 Tip: DeepSeek offers the best quality/price ratio!"
