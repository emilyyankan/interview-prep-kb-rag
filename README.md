# Interview Prep Knowledge Base RAG

Find and draft interview-ready **STAR stories** (Situation, Task, Action, Result) from your own notes, using a local knowledge base that runs entirely on your machine.

Behavioral interviews ask things like *"Tell me about a time you showed leadership"* or *"Describe a conflict with a coworker."* The right example is usually buried somewhere in old notes, performance reviews, or project write-ups. This tool indexes those notes with [LightRAG](https://github.com/HKUDS/LightRAG) and lets you ask questions in plain English to surface relevant experiences and shape them into STAR answers.

Everything runs locally through [Ollama](https://ollama.com), so your personal notes never leave your computer and there are no API costs.

## Example

```bash
python query_kb.py "What are examples where I showed leadership?"
```

```
--- Answer ---

<the model's answer, drawing on experiences from your notes>
```

Other questions worth trying:

- "When did I handle a difficult stakeholder or customer?"
- "What's a time I made a mistake and what did I learn?"
- "Give me a STAR story about improving a process, with measurable results."

## How it works

1. Your notes are indexed into a LightRAG knowledge base stored in `./star_story_kb`. LightRAG builds both a vector index and a knowledge graph of the people, projects, and events in your notes.
2. When you ask a question, `query_kb.py` searches the knowledge base in **hybrid** mode, which combines specific-detail retrieval (individual events and facts) with broader-theme retrieval (patterns across many notes).
3. A local LLM (`llama3.1:8b`) writes an answer grounded in what it retrieved.

| Component | Model / tool |
| --- | --- |
| Retrieval framework | LightRAG |
| LLM | `llama3.1:8b` via Ollama |
| Embeddings | `nomic-embed-text` via Ollama (768 dimensions) |
| Context window | 8,192 tokens |

## Requirements

- Python 3.10+
- [Ollama](https://ollama.com/download) installed and running
- Roughly 8 GB of RAM free for the 8B model

## Setup

**1. Clone the repo and create a virtual environment**

```bash
git clone <your-repo-url>
cd <your-repo-folder>
python -m venv venv
source venv/bin/activate      # On Windows: venv\Scripts\activate
```

**2. Install dependencies**

```bash
pip install lightrag-hku ollama
```

**3. Pull the Ollama models**

```bash
ollama pull llama3.1:8b
ollama pull nomic-embed-text
```

Make sure Ollama is running (`ollama serve`, or just open the Ollama app). The script expects it at `http://localhost:11434`.

**4. Gather your notes**

Gather all your notes into one directory, such as `notes/` inside the project folder. Good sources include resumes, performance reviews, project write-ups, meeting notes, and anything else that describes work you've done. The more detail your notes have about what happened and what you did, the better the stories the tool can find.

The ingestion script reads `.txt` and `.md` files. If any of your notes are PDFs, convert them to text first with `convert_pdfs_to_txt.py`.

**5. Build the knowledge base**

The query script reads from `./star_story_kb`, so your notes need to be indexed there first.

```bash
python ingest_docs.py notes/
```

Point the script at your notes folder, not the whole project folder. It reads every `.txt` and `.md` file in that folder and all its subfolders.

Files that were already ingested are tracked in `star_story_kb/ingested_files.json` and skipped, so you can add new notes later and run the same command again to index only the new ones.

Indexing with a local model can take a while, since LightRAG uses the LLM to extract entities and relationships from every chunk.

## Usage

```bash
python query_kb.py "your question here"
```

Put the question in quotes. Running the script with no question prints the usage message.

### Changing the search mode

The mode is set in `main()`:

```python
result = await rag.aquery(question, param=QueryParam(mode="hybrid"))
```

| Mode | Best for |
| --- | --- |
| `naive` | Plain vector search, no knowledge graph |
| `local` | Specific details about particular events or people |
| `global` | Broad themes and patterns across all notes |
| `hybrid` | Both (the default, and usually best for STAR stories) |

## Configuration

Settings live at the top of `query_kb.py` and in `build_rag()`:

- `WORKING_DIR`: where the knowledge base is stored (`./star_story_kb`)
- `llm_model_name`: swap in another Ollama model, such as a larger one for better answers
- `host`: change if Ollama runs on another machine or port
- `num_ctx`: the model's context window

If you change the embedding model, also update `embedding_dim` to match it and rebuild the knowledge base, since existing embeddings won't be compatible.

## Privacy

Your notes, the knowledge base, and every query stay on your machine. Before pushing to GitHub, add the knowledge base and any personal notes to `.gitignore`:

```
star_story_kb/
notes/
venv/
```

## Limitations

- Answers are only as good as your notes. If an experience was never written down, the tool can't find it.
- An 8B local model can blur details together or overstate results. Treat each answer as a first draft and check it against your original notes before using it in an interview.
