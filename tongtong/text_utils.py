import re
from hanziconv import HanziConv

def bot_clean_text(text):
    """
    General purpose text cleaning.
    Removes citations, markdown symbols, excessive whitespace, and duplicates.
    """
    if not text: return ""

    # 1. Remove citations [1], [2][3], [note 1]
    text = re.sub(r'\[.*?\]', '', text)
    
    # 2. Aggressively remove Markdown markers: **, *, __, _, #, `
    # Using regex to handle patterns like **bold** or *italic*
    text = re.sub(r'\*\*|__|\*|_|#|`|>', '', text)

    # 3. Basic whitespace cleaning
    text = re.sub(r'\s+', ' ', text).strip()
    
    # 4. Fuzzy Sentence-level deduplication
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
    
    # Final check: If there's any Chinese content, remove purely English sentences
    has_any_chinese = any(any('\u4e00' <= char <= '\u9fff' for char in s) for s in cleaned_sentences)
    final_list = []
    
    if has_any_chinese:
        for s in cleaned_sentences:
            if any('\u4e00' <= char <= '\u9fff' for char in s):
                final_list.append(s)
    else:
        # If NO Chinese was found but we expected it (checked by presence of Chinese in query usually, 
        # but here we just check if it's longer than a certain threshold or purely alphanumeric)
        # For safety, if it's 100% English and longer than 50 chars, it's likely a bad search result
        is_pure_english = all(ord(c) < 128 for c in text.replace(' ', ''))
        if is_pure_english and len(text) > 50:
            return "我幫你上網找了資料，但看到的好像都是英文網頁，暫時沒辦法為您總結中文答案喔。"
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
