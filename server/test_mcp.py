import asyncio
import os
from dedalus_labs import AsyncDedalus, DedalusRunner
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO)
load_dotenv()

async def main():
    if not os.getenv("DEDALUS_API_KEY"):
        print("Error: DEDALUS_API_KEY not found")
        return

    client = AsyncDedalus()
    runner = DedalusRunner(client)
    
    try:
        print("Querying tool arguments...")
        result = await runner.run(
            input="Please read the PDF at file:///Users/arnavvadnere/Developer/Northstar/server/samples/invoice.pdf using the `functions.mcp-pdf_to_text` tool.",
            model="openai/gpt-4o",
            mcp_servers=["meanerbeaver/pdf-parse"]
        )
        print(f"\n[Final Output]: {result.final_output}")
                
    except Exception as e:
        print(f"\n[Error]: {e}")

if __name__ == "__main__":
    asyncio.run(main())
