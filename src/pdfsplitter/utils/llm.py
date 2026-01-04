from typing import Optional
from openai import OpenAI, RateLimitError, APIError
from ..config import settings

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=settings.OPENROUTER_API_KEY,
    default_headers={
        "HTTP-Referer": "https://pdfsplitter.local",
        "X-Title": "PDFSplitter",
    },
)


def analyze_for_ocr(text_samples: list[str]) -> tuple[Optional[bool], str]:
    """
    Query LLM to determine if OCR is needed.
    Returns tuple of (result, reasoning) where result is None on failure.
    """
    prompt = """Analyze the following document samples and determine if OCR processing is needed.

Look for these indicators:
1. Text is garbled, nonsensical, or contains mojibake (encoding errors)
2. Contains scanned page image artifacts
3. Very little extractable text (< 50 chars per page)
4. Text in non-Latin scripts requiring OCR

Document samples:
---
{content}
---

Respond with EXACTLY ONE WORD: "YES" if OCR is needed, "NO" if not needed.
If the document appears to be a table of contents or blank pages, respond "NO"."""

    try:
        response = client.chat.completions.create(
            model=settings.MODEL_NAME,
            messages=[
                {
                    "role": "user",
                    "content": prompt.format(content="\n\n---\n\n".join(text_samples)),
                }
            ],
            temperature=0.1,
            max_tokens=10,
        )
        content = response.choices[0].message.content
        if not content:
            return None, "Empty response from LLM"

        result = content.strip().upper()
        if "YES" in result:
            return True, "LLM determined OCR is needed"
        elif "NO" in result:
            return False, "LLM determined document is already searchable"
        else:
            return None, f"Unexpected LLM response: {content}"
    except RateLimitError as e:
        return None, f"Rate limit error: {str(e)}"
    except APIError as e:
        return None, f"API error: {str(e)}"
    except Exception as e:
        return None, f"Unexpected error: {str(e)}"
