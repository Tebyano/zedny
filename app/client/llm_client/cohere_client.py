import os

import cohere

COHERE_API_KEY = os.getenv("COHERE_API_KEY")
co = cohere.ClientV2(COHERE_API_KEY) if COHERE_API_KEY else None


def generate_text(
    prompt: str,
    max_tokens: int = 200,
    temperature: float = 0.7,
    model="command-xlarge-nightly", 

) -> str:
    
    if not co:
        return "Error: Cohere client not initialized. Set COHERE_API_KEY in environment."

    try:
        response = co.chat(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature,
        )

        if getattr(response, "message", None) and getattr(response.message, "content", None):
            for content_block in response.message.content:
                text = getattr(content_block, "text", None)
                if text:
                    return text

        text = getattr(response, "text", None)
        if text:
            return text

        return "Error: Empty response text from Cohere Chat API."
    except Exception as e:
        return f"Error: {str(e)}"
 