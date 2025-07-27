import re
from collections import Counter

def extract_keywords(text, top_n=15):
    # Basic cleanup
    words = re.findall(r'\b\w{3,}\b', text.lower())
    
    # Common words to skip
    skip_words = {"the", "and", "for", "with", "you", "are", "that", "your", "will", "have", "our", "who"}

    words = [w for w in words if w not in skip_words]
    counter = Counter(words)
    return [word for word, _ in counter.most_common(top_n)]
