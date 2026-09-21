# ResearchAI Knowledge Base (Markdown Sample)

**Document ID:** RA-KB-MD-001  
**Audience:** AI engineering interns building a research assistant  
**Last updated:** 2026-09-20  
**Purpose:** Longer Markdown corpus for document loading, chunking, embeddings, and RAG answering demos.

---

## 1. Product goal

ResearchAI is a chat interface for research work. Users should be able to ask questions about their own materials—notes, drafts, experiment logs—and get answers that are grounded in those materials.

General LLM chat is not enough for research trust:

- Models can invent citations.
- Models can misremember numbers from a paper they vaguely “know.”
- Models cannot see a private lab notebook unless you give them the text.

**RAG (Retrieval-Augmented Generation)** is the pattern that closes that gap: retrieve relevant passages first, then generate an answer using those passages as context.

---

## 2. Two pipelines you must keep separate

### 2.1 Ingest pipeline (offline / on upload)

1. Accept a file (for this milestone: `.txt` or `.md` only).
2. Validate extension and encoding on the **backend**.
3. Load plain text (+ metadata like `source` filename).
4. Split into chunks.
5. Embed each chunk.
6. Store vectors and text in a vector index.

### 2.2 Chat pipeline (online / per question)

1. Take the user question (and conversation history if needed).
2. Embed the question.
3. Search the index for nearest chunks (`top_k`).
4. Build a prompt that includes retrieved context.
5. Call the chat model (Gemini in this project).
6. Optionally run tools (for example current time) when live facts are needed.
7. Return the final natural-language answer.

Ingest prepares knowledge. Chat consumes knowledge. Mixing these responsibilities in one giant function makes debugging painful.

---

## 3. Document loading details

### 3.1 What “load” means

Loading converts a file into a structure like:

```text
{"text": "<full document string>", "source": "sample_research_notes.md"}
```

The `text` field feeds chunking. The `source` field travels with every chunk so answers can cite where evidence came from.

### 3.2 Formats in scope now

| Format | How we load it | Notes |
|--------|----------------|-------|
| `.txt` | UTF-8 `read_text` | Simplest path |
| `.md`  | UTF-8 `read_text` | Keep headings; great for section-aware chunking later |

### 3.3 Formats out of scope for now

| Format | Why it is harder |
|--------|------------------|
| `.pdf` | Layout + fonts; scanned pages need OCR |
| `.docx` | ZIP + XML paragraph extraction |
| `.doc` | Legacy binary; usually convert first |
| `.png` / `.jpg` | No text layer; OCR or multimodal vision |

Frontend `accept` filters improve UX. Backend suffix checks are the real gate.

---

## 4. Chunking strategy for ResearchAI

### 4.1 Why chunk

- Context windows are finite.
- Embeddings work best on coherent mid-sized passages.
- Retrieval should return *parts* of a document, not always the whole file.

### 4.2 Practical starter settings

For an internship-friendly first version:

- **Chunk size:** roughly 500–1000 characters (or ~200–400 tokens).
- **Overlap:** roughly 10–20% so sentences near boundaries are less likely to vanish.
- **Preserve metadata:** every chunk inherits `source` and a `chunk_index`.

### 4.3 Trade-offs

- **Large chunks:** fewer vectors, noisier retrieval, more prompt waste.
- **Tiny chunks:** sharper matches, weaker local context, more fragmented answers.
- **No overlap:** definitions split across cuts are easy to miss.

Tune after you can ask real questions against a known corpus (like this file).

---

## 5. Embeddings and vector search

An **embedding** maps text to a high-dimensional vector. Similar meaning → nearby vectors.

At ingest:

> chunk text → embedding API/model → store vector

At query time:

> question → same embedding space → nearest-neighbor search → top chunks

Similarity metrics depend on the store (cosine, dot product, L2). What matters for learning is the loop, not the brand of database.

If a claim never appears in any chunk, RAG cannot magically retrieve it. Garbage OCR or empty extracts produce confident wrong answers because the index contains nothing useful.

---

## 6. Vector store responsibilities

A minimal store must support:

1. **Upsert / add** many chunk records.
2. **Query** by vector with `top_k`.
3. **Return** chunk text + metadata for prompting.

Local libraries are fine for ResearchAI demos. Hosted vector DBs become relevant when you need multi-tenant scale, filtering by user/project, or durable ops tooling.

Always store enough metadata to explain an answer:

- `source`
- `chunk_index`
- optional `heading` if you parse Markdown structure later

---

## 7. Retrieval & answering prompt shape

After retrieval, assemble something like:

```text
System:
You are ResearchAI, a research assistant.
Use the CONTEXT below when it is relevant.
If CONTEXT is insufficient, say what is missing.
Do not invent citations or experiment numbers.

CONTEXT:
[1] source=sample_research_notes.md chunk=3
...
[2] source=sample_research_notes.md chunk=8
...

User:
How does ResearchAI differ tools from RAG?
```

Then call `generate_content` (or your `generate_response` wrapper). The model’s job is synthesis; the retriever’s job is evidence selection.

---

## 8. Tools vs RAG (do not confuse them)

| Capability | Answers questions about… | Example |
|------------|--------------------------|---------|
| **RAG** | Content inside uploaded files | “What chunk size did we recommend?” |
| **Tools** | Live / external / computed facts | `get_current_time` in Pacific time |

A user can ask a hybrid question (“Based on my notes, summarize RAG, and also tell me the current Pacific time”). The assistant may need retrieval **and** a tool call. Those are complementary, not substitutes.

---

## 9. Reliability checklist for interns

Before calling the RAG path “done,” verify:

1. Invalid uploads (`.pdf`, `.png`) are rejected with a clear message.
2. Empty files fail loudly at load time.
3. Shell/manual tests can load both `doc/example/*.txt` and `*.md`.
4. Chunk counts look sane for document length (not 1 giant chunk, not thousands of tiny ones).
5. Asking a question whose answer exists only in this corpus returns grounded details.
6. Asking an unrelated question does not force a fake citation from weak neighbors.
7. Conversation memory still works for non-RAG chat turns.

---

## 10. Suggested quiz questions (for RAG QA)

Use these after 7.3 is wired:

1. What are the six steps in the ingest pipeline listed above?
2. Why is backend file validation required even with frontend `accept`?
3. What starter chunk size and overlap does this document recommend?
4. How should ResearchAI behave if retrieved context is insufficient?
5. Give one example where a tool is required instead of RAG.
6. Name three metadata fields worth storing with each chunk.
7. What failure happens if OCR yields an empty string but the UI still “uploads successfully”?

If answers paraphrase this Markdown closely, retrieval is working. If answers are generic textbook RAG without these specifics, inspect embedding consistency, `top_k`, or prompt packaging.

---

## 11. Mini case study: debugging a bad answer

**Symptom:** User asks “What formats are supported now?” Model answers “PDF, DOCX, and images.”

**Likely causes:**

- Wrong corpus indexed (old notes).
- Retrieval returned unrelated chunks; model fell back to parametric knowledge.
- System prompt did not instruct “prefer CONTEXT / admit gaps.”
- Chunks that mention `.txt` / `.md` were not in `top_k`.

**Debug order:** print retrieved chunks for the query → confirm they mention supported formats → tighten prompt → adjust `top_k` or chunking.

---

## 12. Glossary

- **RAG:** Retrieve relevant text, then generate with that text in context.
- **Chunk:** Indexed unit of document text.
- **Embedding:** Vector encoding of meaning.
- **top_k:** Number of nearest chunks inserted into the prompt.
- **Hallucination:** Fluent claim without grounding.
- **Metadata:** Side information stored with a chunk (source, index, page).
- **Ingest:** Offline preparation of searchable knowledge.
- **Retriever:** Component that maps a query to chunks.

---

## 13. Closing

This Markdown sample is intentionally long and slightly redundant so multiple phrasings of the same question can still hit useful chunks while you implement sections 7.1–7.3. Replace it later with real research artifacts: paper drafts, annotation dumps, experiment trackers, or reading notes.

When loaders, chunkers, embeddings, and retrieval are correct, ResearchAI stops being “a chatbot with a research theme” and becomes a system that can actually work over a user’s files.
