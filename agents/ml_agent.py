from transformers import pipeline

summarizer = pipeline("summarization", model="t5-small")

async def summarize_text(text: str) -> str:
    result = summarizer(text, max_length=50, min_length=25, do_sample=False)
    return result[0]["summary_text"]