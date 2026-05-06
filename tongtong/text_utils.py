import re
from hanziconv import HanziConv

def bot_clean_text(text):
    """
    General purpose text cleaning.
    Removes citations, excessive whitespace, duplicates, and non-Chinese results when possible.
    """
    # 1. Remove citations
    text = re.sub(r'\[.*?\]', '', text)
    
    # 2. Whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # 3. Fuzzy Sentence-level deduplication
    sentences = re.split(r'([。！？.!?])', text)
    cleaned_sentences = []
    seen_prefixes = set() # Store the first 15 chars of each sentence
    
    for i in range(0, len(sentences)-1, 2):
        s = sentences[i].strip()
        punc = sentences[i+1] if i+1 < len(sentences) else ""
        if not s: continue
        
        # Fuzzy check: If the first 15 characters are nearly identical, skip
        prefix = s[:15].lower()
        if prefix not in seen_prefixes:
            # Language check: If we have multiple results, prefer those with Chinese characters
            # (Only applies if there's a mix of Chinese and English)
            has_chinese = any('\u4e00' <= char <= '\u9fff' for char in s)
            
            cleaned_sentences.append(s + punc)
            seen_prefixes.add(prefix)
    
    # Final check: If we have multiple sentences and some are English while others are Chinese,
    # consider filtering out the English ones to keep it consistent (as requested by user).
    final_list = []
    has_any_chinese = any(any('\u4e00' <= char <= '\u9fff' for char in s) for s in cleaned_sentences)
    
    if has_any_chinese:
        # If there's Chinese content, remove purely English sentences
        for s in cleaned_sentences:
            if any('\u4e00' <= char <= '\u9fff' for char in s):
                final_list.append(s)
    else:
        final_list = cleaned_sentences

    final_text = "".join(final_list)
    return final_text.strip()

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
