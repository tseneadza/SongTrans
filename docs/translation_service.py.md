# translation_service.py Documentation

## Overview
Service class for translating song lyrics using OpenAI's GPT-4o-mini model with strict line-by-line structure preservation.

## Dependencies
- **os**: Environment variable access
- **openai**: OpenAI API client library
- **dotenv**: Load environment variables from .env file

## Class: TranslationService

### `__init__(self)`
**Description**: Initialize the OpenAI API client with authentication

**Process**:
1. Loads environment variables from .env file
2. Retrieves OPENAI_API_KEY from environment
3. Raises ValueError if API key not found
4. Creates OpenAI client instance

**Raises**:
- `ValueError`: If OPENAI_API_KEY not found in environment

**Example**:
```python
try:
    translation_service = TranslationService()
except ValueError as e:
    print(f"Error: {e}")
```

---

### `translate_lyrics(self, lyrics, target_language='English', source_language=None)`
**Description**: Translate song lyrics while preserving line-by-line structure

**Parameters**:
- `lyrics` (str): Original lyrics text to translate
- `target_language` (str, optional): Target language name (default: 'English')
- `source_language` (str, optional): Source language (default: None, auto-detected)

**Returns**:
- `dict`: Translation data if successful
  ```python
  {
      'translated': str,         # Translated lyrics text
      'source_language': str     # Source language or 'auto-detected'
  }
  ```
- `None`: If translation fails

**Translation Rules** (Enforced via prompt):
1. **Line-by-line**: Each original line → exactly one translated line
2. **Same line count**: Output must have same number of lines as input
3. **Preserve line breaks**: All line breaks maintained exactly
4. **Empty lines**: Blank lines remain blank in translation
5. **No additions**: No explanations, notes, or extra text
6. **No merging/splitting**: Lines not combined or separated
7. **Maintain poetry**: Keep poetic quality while following rules

**Model Configuration**:
```python
model="gpt-4o-mini"    # Fast, cost-effective model
temperature=0.3         # Low temperature for consistency
```

**Prompt Structure**:
- System message: Defines role as professional lyrics translator
- User message: Includes 7 strict rules + lyrics
- Temperature 0.3: More deterministic translations

**Error Handling**:
- Catches all exceptions
- Prints error message to console
- Returns None on any error

**Example Usage**:
```python
lyrics = "Hello, how are you?\nI am fine, thank you."
result = translation_service.translate_lyrics(
    lyrics=lyrics,
    target_language="Spanish",
    source_language="English"
)

if result:
    print(f"Source: {result['source_language']}")
    print(f"Translation:\n{result['translated']}")
else:
    print("Translation failed")
```

**Auto-Detection**:
```python
# Source language will be auto-detected
result = translation_service.translate_lyrics(
    lyrics="Bonjour, comment allez-vous?",
    target_language="English"
)
# result['source_language'] == 'auto-detected'
```

**Cost Considerations**:
- Uses gpt-4o-mini (most cost-effective GPT-4 model)
- ~$0.0001-0.0005 per song translation
- Cost scales with lyrics length
- Cache translations to minimize API calls

**Quality Factors**:
1. **Accuracy**: GPT-4o-mini provides high-quality translations
2. **Consistency**: Low temperature (0.3) ensures consistent results
3. **Context**: Full lyrics provided for context-aware translation
4. **Structure**: Strict rules maintain formatting
5. **Poetry**: Attempts to preserve rhyme/rhythm when possible

**Limitations**:
- Requires valid OPENAI_API_KEY
- Subject to OpenAI API rate limits
- May struggle with very complex wordplay
- Idiomatic expressions may be literal
- Rhyme schemes difficult to preserve across languages

**Best Practices**:
- Always cache results (implemented in app.py)
- Handle rate limiting gracefully
- Provide source language when known
- Test with various languages
- Validate line count matches
