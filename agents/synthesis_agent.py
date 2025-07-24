import asyncio
from logging_config import logger

async def summarize_data(data: dict) -> str:
    logger.info("Synthesis Agent: Summarizing data ...")
    await asyncio.sleep(1) # To simulate processing
    return f"{data['user']} owns {data['stock']} stock priced at ${data['price']}."