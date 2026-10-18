"""
Query your local LightRAG knowledge base to help surface and draft
STAR (Situation, Task, Action, Result) stories from your own notes.
"""

import sys
import asyncio
from lightrag import LightRAG, QueryParam
from lightrag.llm.ollama import ollama_model_complete, ollama_embed
from lightrag.utils import EmbeddingFunc
from lightrag.kg.shared_storage import initialize_pipeline_status

WORKING_DIR = "./star_story_kb"


async def build_rag():
    rag = LightRAG(
        working_dir=WORKING_DIR,
        llm_model_func=ollama_model_complete,
        llm_model_name="llama3.1:8b",
        llm_model_kwargs={
            "host": "http://localhost:11434",
            "options": {"num_ctx": 8192},
        },
        embedding_func=EmbeddingFunc(
            embedding_dim=768,
            max_token_size=8192,
            func=lambda texts: ollama_embed.func(
                texts, embed_model="nomic-embed-text", host="http://localhost:11434"
            ),
        ),
    )

    await rag.initialize_storages()
    await initialize_pipeline_status()

    return rag


async def main(question: str):
    rag = await build_rag()
    # Hybrid mode runs two different searches on your notes and combines what both find before the AI writes its answer.
    result = await rag.aquery(question, param=QueryParam(mode="hybrid"))
    print("\n--- Answer ---\n")
    print(result)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('Usage: python query_kb.py "your question here"')
        sys.exit(1)

    asyncio.run(main(sys.argv[1]))
