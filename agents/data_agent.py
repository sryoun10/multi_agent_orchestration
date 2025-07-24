# agents/data_agent.py
import asyncio
from logging_config import logger

async def fetch_data():
    logger.info("Data Agent: Fetching mock stock data ...")
    await asyncio.sleep(1) # To simulate I/O delay
    mock_data = {"stock": "WFC", "price": 81.26, "user": "Steve"}
    logger.info(f"Mock data: {mock_data}")
    return mock_data