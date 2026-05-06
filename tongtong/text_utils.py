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
    text = re.sub(r'\*\*|__|\*|_|#|`|>', '', text)

    # 3. Basic whitespace cleaning
    text = re.sub(r'\s+', ' ', text).strip()
    
    # 4. Protect ellipsis before sentence splitting
    ELLIPSIS_PLACEHOLDER = "<<<ELLIPSIS>>>"
    text = text.replace("...", ELLIPSIS_PLACEHOLDER)
    
    # 5. Fuzzy Sentence-level deduplication
    sentences = re.split(r'([。！？.!?])', text)
    cleaned_sentences = []
    seen_prefixes = set() 
    
    for i in range(0, len(sentences)-1, 2):
        s = sentences[i].strip()
        punc = sentences[i+1] if i+1 < len(sentences) else ""
        if not s: continue
        
        prefix = s[:15].lower()
        if prefix not in seen_prefixes:
            cleaned_sentences.append(s + punc)
            seen_prefixes.add(prefix)
    
    if len(sentences) > 0 and len(sentences) % 2 != 0:
        last_s = sentences[-1].strip()
        if last_s and last_s[:15].lower() not in seen_prefixes:
            cleaned_sentences.append(last_s)
    
    # 6. Language check: ONLY filter out purely English sentences if they are long/noisy
    # We want to KEEP emojis and mixed Chinese/English content
    final_list = []
    for s in cleaned_sentences:
        has_chinese = any('\u4e00' <= char <= '\u9fff' for char in s)
        # Check for emoji characters (broad range)
        has_emoji = any(ord(char) > 0x2000 for char in s if not ('\u4e00' <= char <= '\u9fff'))
        
        # Keep if it has Chinese OR Emoji OR it's short (like "OK" or "123")
        if has_chinese or has_emoji or len(s.replace(' ', '')) < 20:
            final_list.append(s)
        else:
            # It's a long sentence with NO Chinese and NO Emoji -> likely noise
            pass

    final_text = "".join(final_list)
    
    # 7. Restore ellipsis
    final_text = final_text.replace(ELLIPSIS_PLACEHOLDER, "...")
    return final_text.strip()

def bot_speak_re(text):
    """
    Cleans up text specifically for speech synthesis.
    Removes emojis and special symbols while keeping Chinese, English, and numbers.
    """
    if not text: return ""

    # 1. Apply general cleaning (markdown, citations, etc.)
    text = bot_clean_text(text)

    # 1.25 Normalize time ranges for speech, e.g. "7:00 - 8:00" -> "7點到8點"
    text = re.sub(r'(?:(上午|中午|下午|晚上)\s*)?(\d{1,2}):00\s*[-–—~至到]\s*(\d{1,2}):00',
                  lambda m: f"{m.group(1) + ' ' if m.group(1) else ''}{m.group(2)}點到{m.group(3)}點",
                  text)

    # 1.5 Remove fortune disclaimer from speech, but keep it in display text
    disclaimer = "※ 以上僅供娛樂參考，請理性看待喔！"
    if disclaimer in text:
        text = text.replace(disclaimer, '').strip()
    
    # 2. Remove emojis and other special symbols by iterating character by character
    # Keep: Chinese characters, English letters, numbers, common punctuation, spaces
    result = []
    for char in text:
        code = ord(char)
        # Chinese characters (CJK Unified Ideographs)
        if 0x4e00 <= code <= 0x9fff:
            result.append(char)
        # English letters and numbers
        elif (0x41 <= code <= 0x5a) or (0x61 <= code <= 0x7a) or (0x30 <= code <= 0x39):
            result.append(char)
        # Common punctuation and spaces
        elif char in '，。！？、：；（）()「」『』\s\t\n\r -–—～':
            result.append(char)
        # Chinese punctuation marks that might not be in the above list
        elif code in [65292, 65294, 65281, 65311, 12289, 12290, 12291]:  # Chinese punctuation
            result.append(char)
    
    text = "".join(result).strip()
    
    # 3. Limit length
    if len(text) > 300:
        text = text[:300] + "，內容太長了，我先唸到這裡。"
        
    return text.strip()

def normalize_chars(text):
    """
    Fixes common character errors from web scraping.
    Examples: 颱灣 -> 臺灣 (typhoon 'tai' vs Taiwan 'tai')
    """
    # Common OCR/encoding errors
    char_mapping = {
        '颱': '臺',  # typhoon tai -> Taiwan tai
        '滣': '灣',  # wrong char -> wan
        '灿': '璀',  # brightness issues
    }
    
    for wrong_char, correct_char in char_mapping.items():
        text = text.replace(wrong_char, correct_char)
    
    return text

def to_traditional(text):
    """
    Converts text to Traditional Chinese and normalizes character errors.
    """
    text = HanziConv.toTraditional(text)
    text = normalize_chars(text)
    return text

def bot_get_google(text):
    """
    Placeholder for more advanced semantic analysis if needed.
    Currently just converts to traditional.
    """
    return to_traditional(text)
