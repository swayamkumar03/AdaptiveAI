"""
app/services/rag_service.py

Basic RAG retrieval and answer generation with adaptive verified experience integration.
"""

from __future__ import annotations

import asyncio

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.providers.base import LLMMessage, LLMRequest
from app.ai.providers.gemini_provider import (
    GeminiEmbeddingProvider,
    GeminiProvider,
)
from app.config import settings
from app.models.document_chunk import DocumentChunk
from app.models.experience import Experience, ExperienceVerificationStatus


async def retrieve_chunks_with_scores(
    db: AsyncSession,
    company_id,
    query_embedding: list[float],
    top_k: int | None = None,
) -> list[tuple[DocumentChunk, float]]:
    """
    Find the most relevant document chunks for a company with cosine similarity scores.
    Cosine similarity = max(0.0, 1.0 - cosine_distance).
    """
    k = top_k or settings.rag_top_k
    distance_col = DocumentChunk.embedding.cosine_distance(query_embedding)

    result = await db.execute(
        select(DocumentChunk, distance_col.label("dist"))
        .where(
            DocumentChunk.company_id == company_id,
            DocumentChunk.embedding.is_not(None),
        )
        .order_by(distance_col)
        .limit(k)
    )

    rows = result.all()
    return [(chunk, max(0.0, 1.0 - float(dist))) for chunk, dist in rows]


async def retrieve_chunks(
    db: AsyncSession,
    company_id,
    query: str | None = None,
    query_embedding: list[float] | None = None,
) -> list[DocumentChunk]:
    """
    Find the most relevant document chunks for a company.
    Preserves original signature for backward compatibility.
    """
    if query_embedding is None:
        if not query:
            return []
        embedding_provider = GeminiEmbeddingProvider()
        query_embedding_response = (
            await embedding_provider.generate_embedding(query)
        )
        query_embedding = query_embedding_response.embedding

    chunks_with_scores = await retrieve_chunks_with_scores(
        db=db,
        company_id=company_id,
        query_embedding=query_embedding,
    )
    return [chunk for chunk, _ in chunks_with_scores]


async def retrieve_verified_experiences_with_scores(
    db: AsyncSession,
    company_id,
    query_embedding: list[float],
    top_k: int = 3,
) -> list[tuple[Experience, float]]:
    """
    Find relevant verified (approved) experiences for a company with cosine similarity scores.
    Only approved experiences with valid embeddings belonging to the current
    company are retrieved and filtered by cosine similarity threshold.
    """
    distance_col = Experience.embedding.cosine_distance(query_embedding)

    result = await db.execute(
        select(Experience, distance_col.label("dist"))
        .where(
            Experience.company_id == company_id,
            Experience.verification_status == ExperienceVerificationStatus.APPROVED,
            Experience.embedding.is_not(None),
            distance_col <= (1.0 - settings.rag_similarity_threshold),
        )
        .order_by(distance_col)
        .limit(top_k)
    )

    rows = result.all()
    return [(exp, max(0.0, 1.0 - float(dist))) for exp, dist in rows]


async def retrieve_verified_experiences(
    db: AsyncSession,
    company_id,
    query_embedding: list[float],
    top_k: int = 3,
) -> list[Experience]:
    """
    Find relevant verified (approved) experiences for a company.
    Preserves original signature for backward compatibility.
    """
    exps_with_scores = await retrieve_verified_experiences_with_scores(
        db=db,
        company_id=company_id,
        query_embedding=query_embedding,
        top_k=top_k,
    )
    return [exp for exp, _ in exps_with_scores]


def calculate_confidence_score(
    chunk_scores: list[float],
    experience_scores: list[float],
    similarity_threshold: float,
    low_confidence_threshold: float,
) -> float:
    """
    Calculate an explainable and deterministic confidence score in range [0.0, 1.0].

    Confidence measures the availability and relevance of company knowledge:
    1. Verified Experience match: If an approved, human-verified experience exceeds
       the similarity threshold (e.g. >= 0.70), this is the strongest signal of
       trustworthy company knowledge.
    2. Document Chunk match: If relevant document chunks exceed similarity threshold,
       confidence reflects the best chunk similarity.
    3. Weak / Out-of-domain knowledge: If neither meets the similarity threshold,
       the query is outside the available company knowledge. The score is scaled
       below low_confidence_threshold (< 0.50), deterministically triggering escalation.
    """
    best_exp_sim = max(experience_scores) if experience_scores else 0.0
    best_chunk_sim = max(chunk_scores) if chunk_scores else 0.0

    # Strong signal 1: Approved verified experience matching the question
    if best_exp_sim >= similarity_threshold:
        return round(best_exp_sim, 4)

    # Strong signal 2: Document chunk matching the question
    if best_chunk_sim >= similarity_threshold:
        return round(best_chunk_sim, 4)

    # Weak / No retrieval: knowledge is missing or irrelevant
    max_sim = max(best_chunk_sim, best_exp_sim)
    if max_sim <= 0.40:
        return 0.0

    # Linearly scale similarity between 0.40 and similarity_threshold
    # into the low-confidence band: [0.0, low_confidence_threshold - 0.05]
    scaled = (
        (max_sim - 0.40) / (similarity_threshold - 0.40)
    ) * (low_confidence_threshold - 0.05)
    return round(max(0.0, min(low_confidence_threshold - 0.01, scaled)), 4)


async def generate_rag_answer(
    db: AsyncSession,
    company_id,
    question: str,
    conversation_history: list[dict] | None = None,
) -> dict:
    """
    Retrieve relevant company knowledge (documents + verified experiences),
    evaluate confidence, and generate an answer or trigger human escalation.
    """

    # ---------------------------------------------------------
    # 1. Generate query embedding
    # ---------------------------------------------------------
    embedding_provider = GeminiEmbeddingProvider()
    query_embedding_response = (
        await embedding_provider.generate_embedding(question)
    )
    query_embedding = query_embedding_response.embedding

    # ---------------------------------------------------------
    # 2. Retrieve relevant document chunks and verified experiences with scores
    # ---------------------------------------------------------
    chunks_with_scores = await retrieve_chunks_with_scores(
        db=db,
        company_id=company_id,
        query_embedding=query_embedding,
    )

    experiences_with_scores = await retrieve_verified_experiences_with_scores(
        db=db,
        company_id=company_id,
        query_embedding=query_embedding,
    )

    chunk_scores = [sim for _, sim in chunks_with_scores]
    exp_scores = [sim for _, sim in experiences_with_scores]

    # Deterministic confidence calculation (§16)
    confidence_score = calculate_confidence_score(
        chunk_scores=chunk_scores,
        experience_scores=exp_scores,
        similarity_threshold=settings.rag_similarity_threshold,
        low_confidence_threshold=settings.confidence_low_threshold,
    )

    # Filter chunks that are sufficiently relevant to provide context
    relevant_chunks = [
        chunk for chunk, sim in chunks_with_scores
        if sim >= settings.rag_similarity_threshold
    ]
    relevant_experiences = [exp for exp, _ in experiences_with_scores]

    # ---------------------------------------------------------
    # 3. Check Confidence / Escalation Threshold (§17)
    # ---------------------------------------------------------
    if confidence_score < settings.confidence_low_threshold:
        return {
            "answer": (
                "I couldn't find enough verified information in the "
                "company's knowledge base to answer this confidently. "
                "I've escalated your question to a company representative."
            ),
            "confidence_score": confidence_score,
            "is_escalated": True,
            "sources": [],
            "model": None,
            "retrieved_chunks": len(relevant_chunks),
            "retrieved_experiences": len(relevant_experiences),
            "prompt_tokens": None,
            "completion_tokens": None,
        }

    # High confidence: continue with knowledge-grounded Gemini generation
    chunks = relevant_chunks
    experiences = relevant_experiences

    # ---------------------------------------------------------
    # 3. Build knowledge context with distinguished source types
    # ---------------------------------------------------------
    context_parts = []
    sources = []

    # Include verified experiences first to emphasize corrected/verified knowledge
    for index, exp in enumerate(experiences, start=1):
        context_parts.append(
            f"[Verified Experience {index}]\n"
            f"Question: {exp.question}\n"
            f"Verified Answer: {exp.corrected_answer or exp.original_answer}"
        )
        sources.append(
            {
                "type": "verified_experience",
                "experience_id": str(exp.id),
                "source_title": f"Verified Experience {index}",
                "chunk_id": None,
            }
        )

    for index, chunk in enumerate(chunks, start=1):
        context_parts.append(
            f"[Document Source {index}]\n{chunk.content}"
        )
        sources.append(
            {
                "type": "document_chunk",
                "chunk_id": str(chunk.id),
                "document_id": str(chunk.document_id),
                "page_number": chunk.page_number,
                "chunk_index": chunk.chunk_index,
                "source_title": f"Document Source {index}",
            }
        )

    context = "\n\n".join(context_parts)

    # ---------------------------------------------------------
    # 4. Build conversation history
    # ---------------------------------------------------------
    history_text = ""

    if conversation_history:
        history_parts = []

        for message in conversation_history:
            role = message["role"].capitalize()
            content = message["content"]

            history_parts.append(
                f"{role}: {content}"
            )

        history_text = "\n".join(history_parts)

    # ---------------------------------------------------------
    # 5. System prompt
    # ---------------------------------------------------------
    system_prompt = """
You are AdaptiveAI, an enterprise knowledge assistant.

Answer the user's question using ONLY the provided company knowledge context.

Context may contain Document Sources and Verified Experiences:
- Document Sources provide information from company documents.
- Verified Experiences represent human-reviewed corrections and verified company knowledge. When a verified experience conflicts with a document source, the verified experience MUST take precedence.

You may use previous conversation messages to understand what the user is referring to.

Rules:
1. Do not invent information.
2. If the company knowledge context does not contain the answer, say that you could not find the information in the company's knowledge base.
3. Be concise and directly answer the question.
4. When a verified experience provides updated or corrected information on a topic, use that verified information as the truth.
5. Use source references (e.g. [Verified Experience 1], [Document Source 1]) when citing information.
6. Use conversation history only for context and clarification.
"""

    # ---------------------------------------------------------
    # 6. User prompt
    # ---------------------------------------------------------
    user_prompt = f"""
Company knowledge context:

{context}

Previous conversation:

{history_text if history_text else "No previous conversation."}

Current user question:

{question}
"""

    # ---------------------------------------------------------
    # 7. Generate Gemini response
    # ---------------------------------------------------------
    llm_provider = GeminiProvider()

    llm_request = LLMRequest(
        messages=[
            LLMMessage(
                role="system",
                content=system_prompt,
            ),
            LLMMessage(
                role="user",
                content=user_prompt,
            ),
        ],
        temperature=0.2,
        max_tokens=2048,
    )

    response = None

    # Retry temporary Gemini 503 errors
    for attempt in range(3):
        try:
            response = await llm_provider.generate_response(
                llm_request
            )
            break

        except Exception as e:
            error_text = str(e)

            if "503" in error_text or "UNAVAILABLE" in error_text:
                if attempt < 2:
                    await asyncio.sleep(2 ** attempt)
                    continue

            raise

    # ---------------------------------------------------------
    # 8. Return result
    # ---------------------------------------------------------
    if response is None:
        raise RuntimeError("Failed to generate a response from the AI provider.")

    return {
        "answer": response.content,
        "confidence_score": confidence_score,
        "is_escalated": False,
        "sources": sources,
        "model": response.model,
        "retrieved_chunks": len(chunks),
        "retrieved_experiences": len(experiences),
        "prompt_tokens": response.prompt_tokens,
        "completion_tokens": response.completion_tokens,
    }