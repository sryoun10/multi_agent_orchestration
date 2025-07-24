from logging_config import logger

async def fallback_response(**kwargs):
    logger.info(f"Live Agent: Handling fallback with kwargs: {kwargs}")
    return f"I'm not sure how to help with that, but here's what I received: {kwargs}"