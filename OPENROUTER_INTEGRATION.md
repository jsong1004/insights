# 🚀 OpenRouter Integration for CrewAI Newsletter

## Overview

The CrewAI newsletter system now supports **OpenRouter** as the primary AI provider, offering potentially lower costs and access to a variety of AI models compared to direct OpenAI API usage.

## 🆚 Comparison: OpenRouter vs OpenAI Direct

| Feature | OpenRouter | OpenAI Direct |
|---------|------------|---------------|
| **Cost** | 💰 Potentially lower | 💸 Standard pricing |
| **Models** | 🌟 100+ models available | 🔧 OpenAI models only |
| **Fallbacks** | ✅ Automatic model fallbacks | ❌ No fallbacks |
| **Rate Limits** | 🚀 Often better limits | ⚠️ Standard limits |
| **Setup** | 🔑 One API key | 🔑 One API key |

## 🔧 Setup Instructions

### 1. Get OpenRouter API Key
1. Go to [OpenRouter.ai](https://openrouter.ai)
2. Sign up for an account
3. Get your API key from the dashboard
4. **Pricing**: Many models are cheaper than OpenAI direct

### 2. Set Environment Variables
```bash
# Primary option - OpenRouter (recommended for cost savings)
export OPENROUTER_API_KEY="your-openrouter-api-key"

# Fallback option - OpenAI (will be used if OpenRouter key not available)
export OPENAI_API_KEY="your-openai-api-key"

# Search APIs (at least one required)
export SERPER_API_KEY="your-serper-api-key"
export TAVILY_API_KEY="your-tavily-api-key"

# Email configuration
export GMAIL_APP_PASSWORD="your-gmail-app-password"
export SENDER_EMAIL="your-email@gmail.com"
export RECIPIENT_EMAILS="recipient1@example.com,recipient2@example.com"
```

### 3. Run the Newsletter
```bash
python daily_ai_news_crewai.py
```

## 🎯 How It Works

1. **Automatic Selection**: The script checks for `OPENROUTER_API_KEY` first
2. **Fallback Support**: If OpenRouter key not found, uses `OPENAI_API_KEY`
3. **Model Configuration**: Uses `openai/gpt-4o-mini` via OpenRouter for optimal cost/performance
4. **Enhanced Headers**: Includes OpenRouter-specific headers for better tracking

## 💰 Cost Benefits

### Example Cost Comparison (estimated):
- **Original OpenAI Direct**: $65-105/month
- **With OpenRouter**: $35-65/month (potentially 40-50% savings)

*Note: Actual costs depend on usage patterns and OpenRouter's current pricing*

## 🔧 Technical Details

### LLM Configuration
```python
# OpenRouter configuration (preferred)
LLM(
    model="openai/gpt-4o-mini",
    api_key=openrouter_key,
    base_url="https://openrouter.ai/api/v1",
    temperature=0.1,
    max_tokens=2000,
    extra_headers={
        "HTTP-Referer": "https://github.com/crewai-newsletter",
        "X-Title": "CrewAI Newsletter System"
    }
)
```

### Agent Updates
All 4 AI agents now use the configured LLM:
- 🔍 **Research Agent** - Uses OpenRouter for news discovery
- 📊 **Analysis Agent** - Uses OpenRouter for quality scoring  
- 📝 **Curation Agent** - Uses OpenRouter for story selection
- ✍️ **Writing Agent** - Uses OpenRouter for content enhancement

## 🚨 Important Notes

1. **API Key Priority**: OpenRouter key takes precedence over OpenAI key
2. **Model Compatibility**: Uses OpenAI-compatible models via OpenRouter
3. **Error Handling**: Graceful fallback if OpenRouter has issues
4. **Logging**: Clear indicators of which API is being used

## ✅ Testing Your Setup

```bash
# Test the configuration
python -c "
from daily_ai_news_crewai import AINewsletterCrew, get_api_keys
tavily_key, serper_key, openrouter_key, openai_key, _, _ = get_api_keys()
print(f'OpenRouter: {\"✅\" if openrouter_key else \"❌\"}')
print(f'OpenAI Fallback: {\"✅\" if openai_key else \"❌\"}')
"
```

## 🎉 Benefits Summary

✅ **Cost Savings**: Potentially 40-50% lower AI costs  
✅ **Model Variety**: Access to 100+ different AI models  
✅ **Better Limits**: Often higher rate limits than direct APIs  
✅ **Automatic Fallbacks**: Built-in redundancy and reliability  
✅ **Easy Migration**: Drop-in replacement for OpenAI API  
✅ **Enhanced Features**: Better tracking and analytics  

## 🔄 Migration Guide

If you're currently using the OpenAI version:

1. **Keep existing setup**: Your `OPENAI_API_KEY` will still work as fallback
2. **Add OpenRouter**: Set `OPENROUTER_API_KEY` for immediate cost savings
3. **No code changes**: The script automatically detects and uses the best option
4. **Monitor costs**: Compare your usage costs before/after migration

**Ready to save money on AI costs while maintaining the same high-quality newsletter output!** 💰🚀 