
import base64
import os
import tempfile
from pathlib import Path

import numpy as np
import streamlit as st
from dotenv import load_dotenv
from google import genai

from pdf_loader import load_pdf
from Embedding import create_embeddings, create_query_embedding
from Retrieval import create_index, retrieve_chunk
from prompts import RESEARCH_REVIEW_PROMPT

load_dotenv()

# ---------- Page configuration ----------
st.set_page_config(
    page_title="ScholarMind AI",
    page_icon="🔬",
    layout="wide",
)

FEATURES = [
    "AI Manuscript Review",
    "Claim-to-Evidence Checking",
    "Scientific Writing Improvement",
    "Citation Checking",
]

FEATURE_META = [
    {
        "title": "📄 AI Manuscript Review",
        "description": "Review papers, ask questions, and inspect evidence.",
        "image": "images/review.png",
        "button": "Open Manuscript Review",
    },
    {
        "title": "🔎 Claim-to-Evidence Checking",
        "description": "Check scientific claims against retrieved passages.",
        "image": "images/evidnance.png",
        "button": "Check a Claim",
    },
    {
        "title": "✍️ Scientific Writing Improvement",
        "description": "Improve clarity, grammar, flow, and academic tone.",
        "image": "images/writing.png",
        "button": "Improve Writing",
    },
    {
        "title": "📚 Citation Checking",
        "description": "Inspect reference formatting and missing details.",
        "image": "images/citation.png",
        "button": "Check Citations",
    },
]

# ---------- Session state ----------
if "selected_feature" not in st.session_state:
    st.session_state.selected_feature = FEATURES[0]

if "chunks" not in st.session_state:
    st.session_state.chunks = None

if "index" not in st.session_state:
    st.session_state.index = None

if "paper_name" not in st.session_state:
    st.session_state.paper_name = None


# ---------- Scientific wallpaper and styling ----------
def apply_wallpaper():
    wallpaper_path = Path("images/wallpaper.png")

    if not wallpaper_path.exists():
        st.warning(
            "Wallpaper not found. Save it as "
            "images/wallpaper.png."
        )
        return

    encoded_image = base64.b64encode(
        wallpaper_path.read_bytes()
    ).decode("utf-8")

    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image:
                linear-gradient(
                    rgba(235, 245, 255, 0.74),
                    rgba(239, 247, 255, 0.79)
                ),
                url("data:image/png;base64,{encoded_image}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}

        [data-testid="stHeader"] {{
            background: rgba(255, 255, 255, 0.18);
        }}

        .block-container {{
            max-width: 1500px;
            padding-top: 1.5rem;
            padding-bottom: 3rem;
        }}

        h1, h2, h3 {{
            color: #12315b;
        }}

        [data-testid="stVerticalBlockBorderWrapper"] {{
            background: rgba(255, 255, 255, 0.76);
            border: 1px solid rgba(255, 255, 255, 0.9);
            border-radius: 18px;
            box-shadow: 0 8px 24px rgba(30, 85, 140, 0.12);
            padding: 0.65rem;
        }}

        [data-testid="stFileUploader"],
        [data-testid="stTextArea"],
        [data-testid="stTextInput"],
        [data-testid="stSelectbox"] {{
            background: rgba(255, 255, 255, 0.82);
            border-radius: 12px;
        }}

        div.stButton > button,
        div.stDownloadButton > button {{
            border-radius: 12px;
            border: 1px solid #9dbdf7;
            font-weight: 600;
            min-height: 2.7rem;
        }}

        div.stButton > button[kind="primary"] {{
            background: linear-gradient(90deg, #315cff, #5978ff);
            color: white;
            border: none;
        }}

        hr {{
            border-color: rgba(73, 128, 190, 0.25);
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


apply_wallpaper()


# ---------- Gemini response ----------
def generate_answer(prompt):
    api_key = None

    # Read Streamlit Cloud secret if configured.
    try:
        api_key = st.secrets.get("GEMINI_API_KEY")
    except Exception:
        pass

    # Otherwise use the local .env environment variable.
    api_key = api_key or os.getenv("GEMINI_API_KEY")

    if api_key:
        client = genai.Client(api_key=api_key)
    else:
        client = genai.Client()

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )

    return response.text or "No response was generated."


# ---------- PDF processing ----------
def process_pdf(uploaded_file):
    temp_path = None

    try:
        with st.spinner("Reading PDF and creating embeddings..."):
            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".pdf",
            ) as temp_file:
                temp_file.write(uploaded_file.getvalue())
                temp_path = Path(temp_file.name)

            chunks = load_pdf(temp_path)

            if not chunks:
                st.error(
                    "No readable text was found. "
                    "This PDF may be scanned or image-only."
                )
                return

            embeddings = np.asarray(
                create_embeddings(chunks),
                dtype="float32",
            )

            index = create_index(embeddings)

            st.session_state.chunks = chunks
            st.session_state.index = index
            st.session_state.paper_name = uploaded_file.name

        st.success(
            f"Paper ready: {uploaded_file.name} "
            f"({len(chunks)} text chunks)"
        )

    except Exception as e:
        st.error(f"PDF processing failed: {e}")

    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)


# ---------- Evidence retrieval ----------
def get_evidence(question):
    query_embedding = np.asarray(
        create_query_embedding(question),
        dtype="float32",
    )

    results = retrieve_chunk(
        query_embedding,
        st.session_state.index,
        st.session_state.chunks,
        top_k=5,
    )

    context = "\n\n".join(
        f"[Page {chunk['page']}] {chunk['text']}"
        for chunk in results
    )

    return results, context


def show_evidence(results):
    with st.expander("View Retrieved Evidence"):
        for chunk in results:
            st.markdown(f"**Page {chunk['page']}**")
            st.write(chunk["text"])
            st.divider()


def paper_upload(key):
    uploaded_file = st.file_uploader(
        "Upload your research paper (PDF)",
        type=["pdf"],
        key=f"pdf_{key}",
        help="Large PDFs may take longer to process.",
    )

    if uploaded_file is not None:
        if st.button(
            "Process Research Paper",
            key=f"process_{key}",
            type="primary",
        ):
            process_pdf(uploaded_file)

    if st.session_state.index is not None:
        st.success(
            f"Active paper: {st.session_state.paper_name}"
        )


# ---------- Header ----------
header_col, tagline_col = st.columns([3, 2])

with header_col:
    st.title("🔬 ScholarMind AI")
    st.write(
        "Your AI-powered assistant for scientific research, "
        "manuscript review, and evidence-based insights."
    )
with tagline_col:
    st.markdown(
        """
        <div style="
            margin-top: 1.2rem;
            padding: 1rem;
            background: rgba(255,255,255,0.72);
            border: 1px solid rgba(255,255,255,0.9);
            border-radius: 16px;
            text-align: center;
            color: #214a7a;
            font-weight: 600;">
            Research · Write · Verify · Discover
        </div>
        """,
        unsafe_allow_html=True,
    )

st.divider()


# ---------- Four aligned feature cards ----------
st.subheader("Choose Your Research Tool")

columns = st.columns(4, gap="medium")


for i, (column, meta) in enumerate(zip(columns, FEATURE_META)):
    with column:
        with st.container(border=True):
            image_path = Path(meta["image"])

            if image_path.exists():
                st.image(
                    str(image_path),
                    width="stretch",
                )

            # Keep titles at a consistent height
            st.markdown(
                f"""
                <div style="
                    height: 68px;
                    display: flex;
                    align-items: center;
                    font-size: 1.25rem;
                    font-weight: 600;
                    line-height: 1.3;
                ">
                    {meta['title']}
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Keep descriptions at a consistent height
            st.markdown(
                f"""
                <div style="
                    height: 64px;
                    line-height: 1.5;
                    overflow: hidden;
                ">
                    {meta['description']}
                </div>
                """,
                unsafe_allow_html=True,
            )

            if st.button(
                meta["button"],
                key=f"card_feature_{i}",
                width="stretch",
                type=(
                    "primary"
                    if st.session_state.selected_feature == FEATURES[i]
                    else "secondary"
                ),
            ):
                st.session_state.selected_feature = FEATURES[i]
                st.rerun()

st.divider()


# ---------- Selected feature workspace ----------
feature = st.session_state.selected_feature
st.header(feature)


# Feature 1: AI Manuscript Review
if feature == FEATURES[0]:

    paper_upload("review")

    question = st.text_area(
        "Ask a question about your paper",
        placeholder=(
            "Summarize the paper, identify its limitations, "
            "or explain the methodology."
        ),
        key="review_question",
    )

    if st.button(
        "Generate Review",
        type="primary",
        key="generate_review",
    ):
        if st.session_state.index is None:
            st.warning("Upload and process a PDF first.")

        elif not question.strip():
            st.warning("Enter a question first.")

        else:
            try:
                with st.spinner("Reviewing the paper..."):
                    results, context = get_evidence(question)

                    prompt = RESEARCH_REVIEW_PROMPT.format(
                        context=context,
                        question=question,
                    )

                    answer = generate_answer(prompt)

                st.subheader("AI Review")
                st.markdown(answer)
                show_evidence(results)

            except Exception as e:
                st.error(f"Review failed: {e}")


# Feature 2: Claim-to-Evidence Checking
elif feature == FEATURES[1]:

    paper_upload("evidence")

    claim = st.text_area(
        "Enter the scientific claim",
        placeholder=(
            "Example: The material improves photocatalytic "
            "hydrogen production."
        ),
        key="claim_input",
    )

    if st.button(
        "Check Claim",
        type="primary",
        key="check_claim",
    ):
        if st.session_state.index is None:
            st.warning("Upload and process a PDF first.")

        elif not claim.strip():
            st.warning("Enter a claim first.")

        else:
            try:
                with st.spinner("Checking retrieved evidence..."):
                    results, context = get_evidence(claim)

                    prompt = f"""
You are a scientific evidence-checking assistant.

Claim:
{claim}

Retrieved paper passages:
{context}

Classify the claim as:
- Supported
- Partially supported
- Contradicted
- Insufficient evidence

Explain your decision using the supplied passages.
Cite page numbers where available.
Separate direct evidence from interpretation.
Never invent data or citations.
Do not treat missing evidence in these passages as proof
that a claim is false.
"""

                    answer = generate_answer(prompt)

                st.subheader("Evidence Check Result")
                st.markdown(answer)
                show_evidence(results)

            except Exception as e:
                st.error(f"Claim checking failed: {e}")


# Feature 3: Scientific Writing Improvement
elif feature == FEATURES[2]:

    original_text = st.text_area(
        "Paste your scientific paragraph",
        height=220,
        placeholder="Paste your manuscript text here...",
        key="writing_input",
    )

    if st.button(
        "Improve Writing",
        type="primary",
        key="improve_writing",
    ):
        if not original_text.strip():
            st.warning("Paste a paragraph first.")

        else:
            try:
                with st.spinner("Improving your writing..."):
                    prompt = f"""
You are an expert scientific editor.

Improve the paragraph below.
1. Correct grammar and awkward phrasing.
2. Improve clarity, flow, and academic tone.
3. Preserve the scientific meaning.
4. Do not invent facts, results, or citations.
5. Return the revised paragraph first.
6. Then briefly explain the main changes.

Original paragraph:
{original_text}
"""

                    answer = generate_answer(prompt)

                st.subheader("Improved Version")
                st.markdown(answer)

                st.download_button(
                    "Download Improved Text",
                    data=answer,
                    file_name="improved_scientific_writing.txt",
                    mime="text/plain",
                )

            except Exception as e:
                st.error(f"Writing improvement failed: {e}")


# Feature 4: Citation Checking
elif feature == FEATURES[3]:

    references = st.text_area(
        "Paste your reference list",
        height=220,
        placeholder="Paste your references here...",
        key="references_input",
    )

   
citation_style = st.selectbox(
    "Choose citation style or target journal",
    [
        "ACS",
        "RSC (Royal Society of Chemistry)",
        "Wiley",
        "Elsevier",
        "Springer Nature",
        "Nature",
        "Science",
        "APA",
        "IEEE",
        "Vancouver",
        "Other",
    ],
    key="citation_style",
    )


if st.button(
        "Check References",
        type="primary",
        key="check_references",
    ):
        if not references.strip():
            st.warning("Paste your references first.")

        else:
            try:
                with st.spinner("Checking reference formatting..."):
                    prompt = f"""
You are a scientific reference-formatting assistant.

Preferred style: {citation_style}

References:
{references}

Tasks:
1. Check formatting consistency.
2. Identify potentially missing bibliographic details.
3. Flag possible duplicates and inconsistencies.
4. Suggest formatting improvements for the chosen style.
5. Never invent missing information.
6. Do not claim references or DOIs are verified externally.
7. Flag details that require manual verification.

Organize your response into:
- Formatting issues
- Missing information
- Possible inconsistencies
- Suggested corrections
"""

                    answer = generate_answer(prompt)

                st.subheader("Citation Check Result")
                st.markdown(answer)

                st.download_button(
                    "Download Citation Report",
                    data=answer,
                    file_name="citation_check_report.txt",
                    mime="text/plain",
                )

            except Exception as e:
                st.error(f"Citation checking failed: {e}")


# ---------- Footer ----------
st.divider()

st.caption(
    "ScholarMind AI | Verify scientific conclusions and "
    "bibliographic details before relying on AI-generated output."
)
