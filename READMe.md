# **RFP RAG – Intelligent RFP Analysis System**

This project is an **LLM-powered Retrieval-Augmented Generation (RAG)** system designed to help organizations **analyze complex RFP documents** quickly and accurately.

It extracts scattered requirements, retrieves the most relevant sections, and generates structured, explainable outputs.

The system uses:

* **Gemini 2.5 Flash** (API) for reasoning and generation
* **Jina Embeddings v3** (API) for vector representations
* **ChromaDB** (local disk) as the vector store

---

## 🚀 **Features**

* Smart, RFP-aware question answering
* Optional metadata filters (file, company, project)
* PDF ingestion with chunking → stored in ChromaDB
* Structured JSON output with reasoning and confidence
* Automatic evaluation pipeline
* FastAPI endpoints for ingestion, querying, and evaluation
* Full RAG pipeline using **Gemini + Jina + Chroma**

---

## 📦 **Installation**

1. Create a new conda/virtual environment
   *(tested with Python `3.13.5`)*

2. Install dependencies:

```bash
pip install -r requirements.txt
```

---
## **Add Following API keys in your .env file**
- create .env file in root directory
- add following variable with your API in this .env file
```
GOOGLE_API_KEY = ""
JINA_API_KEY = ""
```
- For GOOGLE_API_KEY, refer [here](https://aistudio.google.com/api-keys)
- For JINA_API_KEY, refer [here](https://jina.ai/).
## ▶️ **Run the API**

```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

---

# 📡 **API Endpoints**

---

## **1. `/ingest` – PDF Ingestion**

* Reads all RFP PDFs
* Splits into chunks
* Creates Jina embeddings via API
* Stores vectors in **ChromaDB** (saved automatically on disk)

**Output**

```json
{
  "message": "Ingestion completed successfully.",
  "total_chunks": 132
}
```

---

## **2. `/query` – RFP-aware Question Answering**

### What happens:

1. A router prompt checks if the query is RFP-relevant
   (Gemini 2.5 Flash → output `1` or `0`)
2. If relevant → Run full RAG

   * Embed question (Jina API)
   * Retrieve from ChromaDB
   * Gemini generates structured response
3. If not relevant → Gemini returns a general AI response

---

### **📌 Example 1 — With Metadata Filtering**

```json
{
  "user_query": "what will be the evaluation procedures?",
  "metadata": {
    "file_name": "RFP3.pdf",
    "company": "Edgemont Union Free School District",
    "project": "Controlled Testing & Inspections for District Wide Additions & Alterations"
  }
}
```

**Output (shortened)**

```json
{
  "user_query": "what will be the evaluation procedures?",
  "answer": "...",
  "reasoning": "...",
  "extracted_requirements": [
    {
      "metadata": {
        "company": "Edgemont Union Free School District",
        "file_name": "RFP3.pdf",
        "project": "CONTROLLED TESTING & INSPECTIONS FOR DISTRICT WIDE ADDITIONS & ALTERATIONS"
      },
      "page_content": "...",
      "type": "Document"
    }
  ]
}
```

---

### **📌 Example 2 — Without Metadata Filters**

```json
{
  "user_query": "what will be the evaluation procedures?",
  "metadata": { "file_name": "", "company": "", "project": "" }
}
```

**Output**

```json
{
  "user_query": "what will be the evaluation procedures?",
  "answer": "...",
  "reasoning": "...",
  "extracted_requirements": [...]
}
```

---

### **📌 Example 3 — General Non-RFP Query**

```json
{
  "user_query": "Hi, how are you doing today",
  "metadata": { "file_name": "", "company": "", "project": "" }
}
```

**Output**

```json
{
  "user_query": "Hi, how are you doing today",
  "answer": "Hi there! I'm doing great...",
  "reasoning": "",
  "extracted_requirements": []
}
```

---

# **3. `/eval_rfp` – Evaluation Pipeline**

Evaluates:

* **Answer relevancy score**
* **Reasoning quality score**
* **Retrieved document relevancy score**

Uses **Gemini 2.5 Flash** for evaluation.

---

### **Example Output**

```json
{
  "evaluation": {
    "answer_relevancy_score": 96.67,
    "reasoning_quality_score": 90,
    "retrieved_relevancy_score": 100
  }
}
```
**Note:** For detail result, refer this `demo/endpoint_responses.md` file.
---

# 🧠 **Tech Stack**

| Component         | Technology                     |
| ----------------- | ------------------------------ |
| LLM               | Gemini 2.5 Flash (API)         |
| Embeddings        | Jina v3 Embeddings (API)       |
| Vector DB         | ChromaDB (saved locally)       |
| API Framework     | FastAPI                        |
| PDF Parsing       | PyMuPDF                        |
| RAG Orchestration | Python + custom graph pipeline |

---

# 🗂️ Directory Structure (Simplified)

```
src/
  rag/
    graph.py
    router_prompt.py
    evaluators/
    retriever.py
  ingestion/
    pdf_loader.py
    chunker.py
  eval/
    eval_rag.py
app.py
```

---

# ⚡ Notes

* ChromaDB **automatically persists embeddings** to disk
* Ingestion can be re-run anytime, before the `query` endpoint, need to ingest data first.
* If you want a fresh vector store → delete the Chroma `./chroma` folder manually

---