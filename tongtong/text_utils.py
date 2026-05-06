import re
from hanziconv import HanziConv

def bot_clean_text(text):
    """
    General purpose text cleaning for both display and speech.
    Removes Wikipedia citations [1], [2][3], [note 1] etc.
    """
    # Remove any content inside square brackets (common wiki citations)
    text = re.sub(r'\[.*?\]', '', text)
    
    # Remove excessive spaces
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()

def bot_speak_re(text):
    """
    Cleans up text specifically for speech synthesis.
    """
    # First apply general cleaning
    text = bot_clean_text(text)
    
    # Remove URLs
    text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
    
    # Remove special brackets and contents found in wiki/news (parentheses)
    text = re.sub(r'\(.*?\)', '', text)  
    
    # Remove some special characters but keep punctuation
    text = re.sub(r'[^\w\s\u4e00-\u9fff，。！？、：]', '', text)
    
    # Limit length
    if len(text) > 300:
        text = text[:300] + "，內容太長了，我先唸到這裡。"
        
    return text.strip()

def to_traditional(text):
    """
    Converts text to Traditional Chinese.
    """
    return HanziConv.toTraditional(text)

def bot_get_google(text):
    """
    Placeholder for more advanced semantic analysis if needed.
    Currently just converts to traditional.
    """
    return to_traditional(text)
