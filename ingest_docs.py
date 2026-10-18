"""
Ingest all .txt and .md files from a folder (and all subfolders) into a
local LightRAG knowledge base, using Ollama for both the LLM and embeddings.
"""

import os
import sys
import json
import asyncio

from lightrag import LightRAG
from lightrag.llm.ollama import ollama_model_complete, ollama_embed
from lightrag.utils import EmbeddingFunc
from lightrag.kg.shared_storage import initialize_pipeline_status

WORKING_DIR = "./star_story_kb" # where the knowledge base is stored
MANIFEST_PATH = os.path.join(WORKING_DIR, "ingested_files.json")


def load_manifest():
    if os.path.exists(MANIFEST_PATH):
        with open(MANIFEST_PATH, "r") as f:
            return set(json.load(f))
    return set()


def save_manifest(ingested_set):
    with open(MANIFEST_PATH, "w") as f:
        json.dump(sorted(ingested_set), f, indent=2)


async def build_rag():
    if not os.path.exists(WORKING_DIR):
        os.mkdir(WORKING_DIR)

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

    # Required as of recent LightRAG versions, sets up storage backends
    # and the pipeline status tracker. Insert calls will fail without this.
    await rag.initialize_storages()
    await initialize_pipeline_status()

    return rag


async def ingest_folder(rag, root_dir: str):
    ingested = load_manifest()
    newly_ingested = 0
    failed = 0

    for current_root, dirs, files in os.walk(root_dir):
        for filename in files:
            if not filename.lower().endswith((".txt", ".md")):
                continue

            filepath = os.path.join(current_root, filename)

            if filepath in ingested:
                continue  # already added in a previous run

            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read().strip()

                if not content:
                    print(f"Skipping empty file: {filepath}")
                    continue

                print(f"Ingesting: {filepath}")
                await rag.ainsert(content)
                ingested.add(filepath)
                newly_ingested += 1
                save_manifest(ingested)  # save progress after each file

            except Exception as e:
                print(f"  ERROR ingesting {filepath}: {e}")
                failed += 1

    save_manifest(ingested)

    print("\n--- Ingestion Summary ---")
    print(f"Newly ingested: {newly_ingested}")
    print(f"Already ingested (skipped): {len(ingested) - newly_ingested}")
    print(f"Failed: {failed}")
    print(f"Knowledge base stored in: {os.path.abspath(WORKING_DIR)}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python ingest_docs.py /path/to/notes")
        sys.exit(1)

    root_folder = sys.argv[1]

    if not os.path.isdir(root_folder):
        print(f"Error: {root_folder} is not a valid directory")
        sys.exit(1)

    async def main():
        rag = await build_rag()
        await ingest_folder(rag, root_folder)

    asyncio.run(main())
