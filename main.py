def split_text(text, max_length=1500):
    sentences = text.split(". ")
    parts = []
    current = ""

    for sentence in sentences:
        sentence += ". "

        if len(current) + len(sentence) <= max_length:
            current += sentence
        else:
            parts.append(current.strip())
            current = sentence

    if current:
        parts.append(current.strip())

    return parts
