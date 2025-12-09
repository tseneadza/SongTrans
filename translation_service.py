import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


class TranslationService:
    def __init__(self):
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        self.client = OpenAI(api_key=api_key)
    
    def translate_lyrics(self, lyrics, target_language='English', source_language=None):
        """
        Translate lyrics to target language while preserving verse structure.
        
        Args:
            lyrics: Original lyrics text
            target_language: Target language for translation
            source_language: Source language (optional, AI will detect)
        
        Returns:
            dict: {'translated': str, 'source_language': str}
        """
        try:
            source_info = f" from {source_language}" if source_language else ""
            
            prompt = f"""Translate the following song lyrics{source_info} to {target_language}.

IMPORTANT RULES:
1. Translate line-by-line - each line in the original MUST have exactly one corresponding line in the translation
2. Keep the EXACT SAME number of lines as the original
3. Preserve ALL line breaks exactly as they appear
4. If a line is empty/blank, keep it empty/blank in the translation
5. Do not add explanations, notes, or extra text
6. Do not merge or split lines
7. Maintain poetic quality while following these rules strictly

Lyrics:
{lyrics}"""

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a professional translator specializing in song lyrics. You MUST translate line-by-line maintaining exact line count and structure."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            translated_text = response.choices[0].message.content.strip()
            
            return {
                'translated': translated_text,
                'source_language': source_language or 'auto-detected'
            }
        except Exception as e:
            print(f"Error translating lyrics: {e}")
            return None
