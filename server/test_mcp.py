import asyncio
import os
import base64
from dedalus_labs import AsyncDedalus, DedalusRunner
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO)
load_dotenv()

PDF_PATH = os.path.join(os.path.dirname(__file__), "samples", "invoice.pdf")

async def main():
    if not os.getenv("DEDALUS_API_KEY"):
        print("Error: DEDALUS_API_KEY not found")
        return

    # Read and base64-encode the PDF
    with open(PDF_PATH, "rb") as f:
        pdf_b64 = base64.b64encode(f.read()).decode("utf-8")

    client = AsyncDedalus()
    runner = DedalusRunner(client)

    try:
        print(f"Testing legal-doc-mcp with {PDF_PATH} ...")
        result = await runner.run(
            input=(
                "Call the `mcp-detect_compliance_red_flags` tool with pdf_path set to "
                f"exactly this value: {pdf_b64}\n\n"
                "Then call `mcp-find_regulatory_sections` with pdf_path set to the same value "
                "and doc_type set to 'Invoice'.\n\n"
                "Report what both tools returned."
            ),
            model="openai/gpt-4o",
            max_steps=5,
            mcp_servers=["sdas04/legal-doc-mcp"]
        )
        print(f"\n[Final Output]: {result.final_output}")
        print(f"\n[Tools Called]: {getattr(result, 'tools_called', [])}")
        print(f"[Steps Used]: {getattr(result, 'steps_used', 'N/A')}")
        print(f"[MCP Results]: {getattr(result, 'mcp_results', [])}")

    except Exception as e:
        print(f"\n[Error]: {e}")

if __name__ == "__main__":
    asyncio.run(main())
