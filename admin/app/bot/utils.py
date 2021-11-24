def limit_word(word: str, limit_symbols: int) -> str:
    if len(word) <= limit_symbols:
        return word
    return f"{word[:30]}..."
