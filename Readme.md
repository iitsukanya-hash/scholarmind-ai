# ScholarMind AI 🧪

**An AI-powered research assistant for scientific literature and manuscript preparation.**

ScholarMind AI is a Python-based application designed to help researchers interact with scientific papers, evaluate scientific claims against retrieved evidence, improve academic writing, and check reference formatting.

## ✨ Features

### 1. AI Manuscript Review
- Ask questions about an uploaded research paper.
- Generate concise, structured answers grounded in retrieved paper content.
- Summarize research objectives, methods, key results, proposed mechanisms, and conclusions when the evidence is available.

### 2. Claim-to-Evidence Checking
- Evaluate whether a scientific claim is supported by retrieved paper content.
- Identify partially supported claims, contradictions, and insufficient evidence.
- Suggest more accurate wording when appropriate.

### 3. Scientific Writing Improvement
- Improve grammar, clarity, academic tone, and readability.
- Preserve scientific meaning, numerical values, chemical formulae, and existing citation markers.
- Highlight ambiguous or potentially overstated claims.

### 4. Citation Checking
- Check reference formatting and consistency against a selected citation style.
- Identify missing bibliographic details.
- Suggest corrections without inventing missing reference information.

## 🛠️ Technology Stack

- **Language:** Python
- **User Interface:** Streamlit
- **Large Language Model:** Google Gemini API
- **Embeddings:** Sentence Transformers
- **Vector Search:** FAISS
- **PDF Processing:** PyMuPDF
- **Data Processing:** NumPy

## ⚙️ Run Locally

### 1. Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd RAG_PROJECT
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
```

Windows:

```powershell
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure your Gemini API key

Create a `.env` file in the project root:

```text
GEMINI_API_KEY=your_api_key_here
```

Replace the placeholder with your own API key. Never commit `.env` or expose your API key publicly.

### 5. Launch the application

```bash
python -m streamlit run streamlit_app.py
```

## 🔐 Security and Responsible Use

- Keep API keys and credentials private.
- Use research documents you have permission to process.
- Verify scientific claims, citations, and AI-generated suggestions against original sources.
- Treat generated feedback as assistance for researchers, not a substitute for expert review.
- Do not assume a reference has been externally verified unless an actual verification process was performed.

## 🚀 Deployment

The application is intended for deployment using Streamlit Community Cloud. Configure `GEMINI_API_KEY` through the deployment platform's Secrets settings rather than uploading your local `.env` file.

## 📌 Project Status

Developed as a research-assistance project exploring retrieval-augmented generation (RAG) for scientific literature workflows.

## 👩‍💻 Author

**Sukanya Saha**

