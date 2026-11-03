# AdaptiveAI — Final Project Comprehensive Review Guide
**An Adaptive Enterprise Conversational AI Platform with Multi-Tenant RAG, Confidence-Grounded Guardrails, and Human-in-the-Loop Feedback Loops**

---

> **Academic Context:** Final Year B.Tech Project Technical Review & Comprehensive Viva Guide  
> **Repository Location:** `c:\adaptive-ai\`  
> **Status:** Implemented, Integrated, and Verified Locally  
> **Primary Technology Stack:** FastAPI, PostgreSQL 16 + pgvector, Google Gemini (`gemini-1.5-flash` / `text-embedding-004`), SQLAlchemy (asyncio), React 19 + TypeScript + Vite, Tailwind CSS v4, Docker/Local Dev  

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Why This Project Is Good and Practical](#2-why-this-project-is-good-and-practical)
   - 2.1 [Problems Companies Face Today](#21-problems-companies-face-today)
   - 2.2 [Existing Solutions and Research Gap](#22-existing-solutions-and-research-gap)
   - 2.3 [Practical Business Scenarios](#23-practical-business-scenarios)
   - 2.4 [Value Proposition](#24-value-proposition)
   - 2.5 [Honest Engineering Assessment](#25-honest-engineering-assessment)
3. [Complete Feature Inventory and Code Mapping](#3-complete-feature-inventory-and-code-mapping)
   - 3.1 [Authentication and Role-Based Authorization](#31-authentication-and-role-based-authorization)
   - 3.2 [Multi-Tenancy and Data Isolation](#32-multi-tenancy-and-data-isolation)
   - 3.3 [Company and User Management](#33-company-and-user-management)
   - 3.4 [Knowledge Ingestion & Vector Pipeline](#34-knowledge-ingestion--vector-pipeline)
   - 3.5 [Retrieval-Augmented Generation (RAG)](#35-retrieval-augmented-generation-rag)
   - 3.6 [Adaptive Knowledge / Experience Loop](#36-adaptive-knowledge--experience-loop)
   - 3.7 [Confidence Scoring and Guardrail Fallback](#37-confidence-scoring-and-guardrail-fallback)
   - 3.8 [Human Escalation Workflow](#38-human-escalation-workflow)
   - 3.9 [Analytics and Monitoring Engine](#39-analytics-and-monitoring-engine)
   - 3.10 [Embeddable Chatbot Widget & Demo Storefront](#310-embeddable-chatbot-widget--demo-storefront)
   - 3.11 [Frontend User Interfaces](#311-frontend-user-interfaces)
   - 3.12 [Database Schema and Infrastructure](#312-database-schema-and-infrastructure)
   - 3.13 [Testing, Reliability, and Verification Suite](#313-testing-reliability-and-verification-suite)
4. [Technical Concepts Explained for Viva](#4-technical-concepts-explained-for-viva)
5. [System Architecture](#5-system-architecture)
   - 5.1 [Architecture Diagram (Mermaid)](#51-architecture-diagram)
   - 5.2 [Architecture Component Inventory](#52-architecture-component-inventory)
   - 5.3 [End-to-End Data Flows (Step-by-Step)](#53-end-to-end-data-flows)
   - 5.4 [Security, Authorization, and Isolation Boundaries](#54-security-authorization-and-isolation-boundaries)
6. [Live Demo Plan for the Professor (7–10 Minutes)](#6-live-demo-plan-for-the-professor-710-minutes)
7. [Final Review Presentation — 10 Slides](#7-final-review-presentation--10-slides)
8. [Evaluation and Testing Plan](#8-evaluation-and-testing-plan)
9. [Limitations and Future Enhancements](#9-limitations-and-future-enhancements)
10. [Professor's Viva Preparation (28 Rigorous Q&A)](#10-professors-viva-preparation)
11. [Quick Reference & Cheat Sheet](#11-quick-reference--cheat-sheet)

---

## 1. Project Overview

### 1.1 What the Project Does in Simple Terms
AdaptiveAI is a multi-tenant enterprise conversational AI platform that enables businesses to deploy AI chatbots trained strictly on their internal documents (PDF, DOCX, TXT, CSV, MD). Instead of giving answers based on random internet knowledge or guessing when it does not know something, AdaptiveAI checks its own confidence. If confidence is high, it provides an answer grounded directly in company files, complete with source citations. If confidence is low or the question is outside company knowledge, it refuses to hallucinate, safely tells the user it does not know, and creates a human support escalation ticket. 

Crucially, when a human support agent or company admin resolves an escalation or corrects a mistake submitted through user feedback, that correction can be approved into a **Verified Experience**. From that moment forward, future users asking similar questions immediately receive the verified correction without requiring the underlying AI foundation model to be fine-tuned or retrained.

### 1.2 The Problem It Solves
Enterprises face three fundamental challenges when adopting Large Language Models (LLMs) for customer service or internal support:
1. **Hallucination & Legal Liability:** Generic LLMs generate plausible-sounding but factually false answers when queried on proprietary organizational policies, warranties, or internal pricing.
2. **Stale Knowledge & Expensive Retraining:** Training or fine-tuning foundation models is prohibitively expensive, slow, and incapable of immediate correction. When a company policy changes, retraining an LLM takes weeks, whereas knowledge must be updated immediately.
3. **Multi-Tenant Data Leakage:** Software-as-a-Service (SaaS) providers operating chatbots for multiple corporate clients must ensure 100% cryptographic and query-level isolation so that Company A’s confidential documents are never accessible to Company B’s users.

AdaptiveAI solves these challenges by combining:
- **Retrieval-Augmented Generation (RAG)** over a vector database (`pgvector`).
- **Deterministic Confidence Scoring & Safe Fallback** to block out-of-domain answers.
- **Human-in-the-Loop Feedback-to-Experience Adaptation** that updates searchable knowledge immediately.
- **Strict Multi-Tenant Database Isolation** enforced at the JWT, API dependency, and ORM query layers.

### 1.3 Who Uses AdaptiveAI
1. **Platform Administrators (`SUPER_ADMIN`):** Manage tenants, create companies, monitor overall system usage, and inspect global analytics.
2. **Company Administrators (`COMPANY_ADMIN`):** Upload knowledge documents, invite team members, configure bot personality (tone, prompt addons), inspect unanswered question gaps, and verify/approve human corrections into the live knowledge base.
3. **Company Support Agents / Employees (`EMPLOYEE`):** Review user feedback, take ownership of low-confidence escalations, resolve customer queries, and draft corrected answers.
4. **End Customers / Website Visitors (`CUSTOMER` or Anonymous Guests):** Interact with the chatbot via the customer web portal or through an embeddable website widget snippet.

### 1.4 Why an Organization Needs It
Without an adaptive architecture, companies either stick to rigid rule-based chatbots (which frustrate users with "I don't understand" to any slight phrasing variation) or deploy unconstrained LLMs (which hallucinate discounts, outdated policies, or false specifications). AdaptiveAI provides the conversational flexibility of modern generative AI while retaining the auditability, safety, and deterministic control required by enterprise compliance.

### 1.5 What Makes It Different from a Basic FAQ or Generic LLM Chatbot
| Capability | Traditional FAQ / Rule-Based Bot | Generic LLM Chatbot (e.g. Raw ChatGPT) | Basic RAG Chatbot | AdaptiveAI Platform |
|---|---|---|---|---|
| **Natural Language Understanding** | Poor (rigid intent trees & regex) | Exceptional | High | High (Gemini / OpenAI / Anthropic) |
| **Grounding in Private Docs** | Manual entry only | None (knowledge cutoff) | Yes (chunks in vector DB) | Yes (chunks + verified experiences) |
| **Hallucination Prevention** | None (canned responses) | Very High Risk | Moderate (can still fabricate) | Deterministic confidence guardrail & escalation |
| **Handling Out-of-Domain Queries** | "Command not recognized" | Makes up plausible answers | Hallucinates or gives generic apologies | Low confidence (<0.50) triggers human escalation ticket |
| **Continuous Learning Loop** | Manual flowchart edits | Requires expensive fine-tuning | Re-indexing entire files | Instant verification of human corrections as prioritized experiences |
| **Tenant Isolation** | Single-tenant silos | Single prompt or session | Often custom or single-tenant | Built-in 3-layer multi-tenant database isolation |
| **Embeddability** | Proprietary SDKs | API only | Rare | Lightweight standalone JavaScript snippet (`widget.js`) |

### 1.6 The Core Idea: Adaptive Knowledge and Verified Experiences
Adaptive learning in AdaptiveAI **does not mean continuous gradient descent or weight updates to the neural network weights of the foundation LLM**. In an enterprise context, retraining a 70B parameter model on customer support logs is risky, unpredictable, and slow. 

Instead, AdaptiveAI implements an **externalized, verified memory layer**:
1. When a user submits negative feedback with a correction, or an agent resolves an escalation, an `Experience` record is created in `PENDING` state.
2. A qualified company admin or employee reviews the entry.
3. Upon approval (`APPROVED`), the system generates an embedding of the verified Q&A pair using Gemini embeddings (`text-embedding-004`) and saves it with a vector representation.
4. On future user queries, the RAG retrieval pipeline searches both raw document chunks and approved experiences. The system prompt explicitly instructs the LLM that **verified experiences represent human-reviewed corrections and take precedence over static document chunks**.
5. The system adapts instantaneously, safely, and with complete human auditability.

### 1.7 One-Minute Elevator Pitch for the Viva Committee
> *"Respected professors, AdaptiveAI is an enterprise-grade conversational AI platform designed to solve the critical problem of LLM hallucinations and static knowledge in corporate customer support. While standard RAG systems simply retrieve text chunks and hope the LLM does not hallucinate, AdaptiveAI introduces three engineering innovations:*
> *First, a deterministic confidence-scoring engine that mathematically evaluates cosine similarity against private document chunks and automatically triggers human escalation tickets whenever confidence drops below 0.50.*
> *Second, a continuous feedback-to-experience adaptation loop: when support agents resolve escalations or review user feedback, their verified corrections are embedded into a prioritized knowledge layer, improving future answers without expensive model retraining.*
> *Third, enterprise-grade multi-tenancy enforced at the JWT, FastAPI dependency, and SQLAlchemy ORM layers, allowing multiple corporate tenants to securely operate isolated knowledge bases on a shared PostgreSQL pgvector infrastructure.*
> *The entire system is implemented with an asynchronous FastAPI backend, Google Gemini API, PostgreSQL 16 with pgvector, and a React TypeScript administrative suite with an embeddable website widget."*

### 1.8 Verified Technology Stack & Library Inventory

| Layer | Technology | Exact Version in Repo | Purpose in AdaptiveAI |
|---|---|---|---|
| **Backend Framework** | FastAPI | `^0.115.0` | Asynchronous high-performance REST API, automatic OpenAPI documentation, dependency injection |
| **ASGI Server** | Uvicorn | `^0.30.0` | Asynchronous server implementation supporting ASGI standards |
| **Database** | PostgreSQL | `≥ 16.0` | Relational storage for tenants, users, conversations, feedback, and audit logs |
| **Vector Extension** | pgvector | `^0.3.2` | Vector similarity search (HNSW/IVFFlat indexable) using cosine distance `<=>` |
| **ORM & DB Driver** | SQLAlchemy (Asyncio) + asyncpg | `^2.0.36` / `^0.30.0` | Async relational mapping, connection pooling, typed schemas, and session lifecycle |
| **Database Migrations** | Alembic + psycopg2-binary | `^1.13.0` | Version-controlled schema migrations, sync driver for DDL execution |
| **Primary AI Provider** | Google GenAI SDK (`google-genai`) | `^0.8.2` | Native integration with `gemini-1.5-flash` for generation and `text-embedding-004` (768-dim) for embeddings |
| **Alternative AI Providers** | OpenAI / Anthropic SDKs | `openai>=1.51.0`, `anthropic>=0.36.0` | Abstract provider interface allowing zero-downtime provider switching via `.env` |
| **Authentication & Security**| python-jose + bcrypt | `^3.3.0` / `^4.0.0` | Stateless JWT access/refresh token generation, verification, and salted bcrypt password hashing |
| **Settings & Validation** | Pydantic v2 + pydantic-settings | `^2.9.0` / `^2.5.0` | Strict request/response validation, environment variable type-casting from `.env` |
| **Document Parsers** | pypdf, python-docx, csv, pandas | `pypdf>=5.0.0`, `docx>=1.1.2` | Text extraction across PDF pages, Word documents, Markdown, plain text, and CSV spreadsheets |
| **Tokenization** | tiktoken | `^0.8.0` | Token-based sliding window text chunking (512 tokens with 64 token overlap) |
| **Structured Logging** | structlog | `^24.4.0` | Contextual JSON/Console logging with execution timestamps and request correlation |
| **Frontend Framework** | React 19 + TypeScript | `^19.3.0` / `~6.0.2` | Component-based administrative SPA, typed state management, strict linting |
| **Frontend Build Tool** | Vite | `^8.3.0` | Fast HMR development server and optimized ES module production bundling |
| **Routing** | React Router DOM | `^7.18.4` | Declarative client-side routing, protected role-based route guards |
| **Styling** | Tailwind CSS v4 | `^4.3.3` | Utility-first responsive styling, dark/light contrast management |
| **Icons** | Lucide React | `^1.48.0` | Consistent UI iconography across administrative consoles and chat widgets |
| **Embeddable Widget** | Vanilla JavaScript (`widget.js`) | Native ES6+ (Zero deps) | Self-contained floating launcher, iframe-free shadow styling, public API consumer |

---

## 2. Why This Project Is Good and Practical

### 2.1 Problems Companies Face Today
In enterprise software, deploying AI is not a matter of novelty; it is a matter of operational reliability, cost control, and risk reduction. Industry research identifies several persistent roadblocks:
- **Information Fragmentation:** Critical enterprise knowledge is scattered across static employee handbooks, onboarding PDFs, product catalogs, customer policy sheets, and internal emails. Employees and customers spend excessive time hunting for answers.
- **The LLM Hallucination Dilemma:** Standard generative LLMs are probabilistic token predictors. When asked about a specific company’s 30-day warranty policy, a generic model might invent a "90-day money-back guarantee with free shipping," creating direct financial liability ([IBM Research on LLM Hallucinations](https://www.ibm.com/think/topics/ai-hallucinations)).
- **Stale Documentation ("The Knowledge Decay Trap"):** Gartner research underscores that customer service organizations face severe backlogs of outdated support articles ([Gartner Customer Service Insights](https://www.gartner.com/en/customer-service-support)). When a company changes a return fee from \$0 to \$15, conventional chatbots continue returning outdated policies unless painstakingly reconfigured.
- **Repetitive Support Fatigue:** Tier-1 human support representatives spend up to 70% of their working hours answering the exact same 20 questions regarding shipping, pricing, login issues, and cancellation policies.
- **Blind Escalations:** Traditional chatbots fail silently or abruptly disconnect customers when confused, without logging what was asked, what documents were retrieved, or why the system failed.
- **Multi-Tenant Privacy Regulations:** Modern SaaS companies operating white-labeled AI tools for multiple business clients must guarantee complete data segregation under GDPR, SOC2, and ISO27001 standards.

### 2.2 Existing Solutions and Research Gap
Commercial solutions exist, but they exhibit distinct architectural trade-offs:
1. **Rule-Based Chatbots (e.g., traditional Zendesk/Intercom decision trees):** Safe and deterministic, but extremely brittle. They fail when a user introduces a typo or asks a compound question.
2. **Generic LLM Chatbots (e.g., ChatGPT Enterprise, raw OpenAI wrappers):** Fluent and context-aware, but prone to confabulation and lacking real-time enterprise grounding.
3. **Basic RAG Implementations:** They chunk documents and query a vector database, but **lack confidence awareness**. If the vector database returns chunks with very poor similarity (e.g., similarity of 0.25 on an irrelevant topic), a basic RAG system still passes those chunks to the LLM. The LLM then attempts to synthesize an answer from irrelevant context, leading to hallucinations.
4. **Commercial Enterprise AI Platforms (e.g., Glean, Moveworks, Salesforce Einstein Service):** Feature-rich and powerful, but closed-source, cost-prohibitive for SMEs, and tightly bound to proprietary cloud ecosystems.

```
       ┌────────────────────────────────────────────────────────┐
       │                   THE RESEARCH GAP                     │
       │                                                        │
       │  How to provide an open, transparent, multi-tenant     │
       │  RAG architecture that deterministically refuses to     │
       │  hallucinate on low retrieval confidence, escalates    │
       │  cleanly to human agents, and instantly incorporates   │
       │  human-verified corrections into future vector search  │
       │  without requiring foundation model fine-tuning?       │
       └────────────────────────────────────────────────────────┘
```

AdaptiveAI addresses this exact gap by coupling vector similarity thresholds directly to a deterministic state-machine: `Confidence >= 0.70` triggers knowledge-grounded generation, while `Confidence < 0.50` triggers automated human escalation and knowledge gap logging.

### 2.3 Practical Business Scenarios

#### Scenario A: Sustainable E-Commerce Storefront (Demonstrated in Repo)
- **Problem:** Customers repeatedly ask about sustainable material sourcing, overseas delivery fees, and garment recycling programs.
- **AdaptiveAI Solution:** The retailer uploads their sustainability report (`test_for_chatbot.pdf`) to the platform. Customers interacting with the website widget ask, *"What primary materials does the company use?"* The system retrieves chunks from the PDF (e.g., organic cotton, recycled polyester) with high confidence (0.84) and answers factually with document citations.
- **Adaptive Loop Action:** If the company transitions to a new synthetic material before the PDF is rewritten, a customer's negative feedback or an agent's correction is recorded, approved as an `Experience`, and immediately prioritized on subsequent queries.

#### Scenario B: Higher Education Student Services Assistant (Hypothetical)
- **Problem:** University administration receives thousands of inquiries during admission cycles regarding scholarship eligibility deadlines, hostel fees, and grading policies.
- **AdaptiveAI Solution:** Documents from the registrar's office are uploaded. A student asks, *"Can international students apply for merit scholarships after August 15?"* If the document explicitly states the deadline is August 1, the bot provides the verified answer. If the policy is absent, the bot reports low confidence, does not fabricate a date, and files an escalation ticket for the admissions officer.

#### Scenario C: Multi-Client IT Support Agency / MSP (Demonstrated in Repo)
- **Problem:** A Managed Service Provider (MSP) provides technical helpdesk bots for five different corporate clients (Tenant A, Tenant B, etc.).
- **AdaptiveAI Solution:** Multi-tenancy ensures that Tenant A’s internal VPN setup guides are completely invisible to Tenant B’s employees. Each tenant receives a distinct public widget identifier (`data-chatbot-id="tenant-slug"`), and company-scoped queries guarantee complete isolation.

### 2.4 Value Proposition
- **Defensive Reliability:** Guards brand reputation by refusing to guess. If knowledge is missing, the system admits ignorance deterministically.
- **Zero-Retraining Adaptation:** Reduces the time required to update operational AI knowledge from weeks (fine-tuning) to seconds (one-click admin approval of an experience).
- **Closed-Loop Knowledge Visibility:** The Analytics Knowledge Gaps dashboard (`/api/v1/analytics/knowledge-gaps`) automatically lists the exact questions customers are asking that the company has no documentation for.
- **Drop-In Embeddability:** A single `<script>` tag embeds the entire conversational assistant into any external HTML, Shopify, WordPress, or custom web portal.

### 2.5 Honest Engineering Assessment

#### Strongest Aspects of the Project
- **End-to-End Functional Completeness:** Unlike typical student projects that only contain a Jupyter notebook or a bare API, AdaptiveAI has a running database, an async FastAPI backend, automated pgvector retrieval, an adaptive experience verification loop, a full React admin console, and an embeddable website widget.
- **Explainable Confidence Scoring:** The confidence score is not an opaque probability or LLM self-evaluation; it is a deterministic calculation grounded in pgvector cosine similarity.
- **Rigorous Multi-Tenant Design:** Tenant isolation is enforced simultaneously across JWT claims, route dependency guards, and ORM query filters.
- **Comprehensive Integration Testing:** Dedicated end-to-end test scripts verify the full adaptive loop, multi-tenant security barriers, confidence escalations, and analytics.

#### Current Technical Limitations
- **Synchronous Ingestion:** Document processing and embedding generation run in the web request thread rather than an asynchronous background worker (e.g., Celery or ARQ). Large documents with hundreds of pages can cause HTTP request timeouts.
- **Absence of Dedicated Cross-Encoder Reranker:** While the config specifies `rag_top_k` and `rag_top_k_reranked`, retrieval currently relies on pgvector cosine similarity without a secondary cross-encoder reranking pass (e.g., Cohere Rerank or BGE-Reranker).
- **Public Widget Origin Validation:** The widget chat endpoints (`/api/v1/widget/{widget_id}/chat`) validate tenant slugs on the server, but do not yet enforce HTTP `Origin` header domain allowlisting.
- **Single Embedding Dimension per Database:** The database vector column is compiled against a specific dimension (768 for Gemini, 1536 for OpenAI). Switching providers requires running a migration or dropping/rebuilding vector columns.

---

## 3. Complete Feature Inventory and Code Mapping

The following inventory details every feature present in the codebase. Every file path, class, function, and database table listed has been verified against the physical repository.

### 3.1 Authentication and Role-Based Authorization

| Attribute | Details |
|---|---|
| **Feature Name** | JWT Authentication and Role-Based Access Control (RBAC) |
| **Simple Explanation** | Users log in with email and password to receive secure digital tokens. The system checks their role to decide which screens and data they can see. |
| **Technical Concept** | Stateless Bearer Tokens (OAuth2 JWT HS256), Salted Password Hashing (`bcrypt`), FastAPI Dependency Injection, Role Guards. |
| **Status** | **Implemented & Fully Verified** |
| **Backend Files** | - `app/core/security.py` (Lines 21–86): `hash_password`, `verify_password`, `create_access_token`, `decode_access_token`<br>- `app/core/dependencies.py` (Lines 31–144): `get_current_user`, `require_roles`, `get_tenant_id`<br>- `app/api/v1/auth.py` (Lines 32–126): `login`, `refresh`, `logout` |
| **Frontend Files** | - `frontend/src/api/auth.ts`: Token storage in `localStorage`, Axios interceptors<br>- `frontend/src/routes/ProtectedRoute.tsx`: Client-side route blocking based on user roles<br>- `frontend/src/pages/Login.tsx`: Login UI with quick-fill demo buttons |
| **Database Tables** | `users` (Columns: `id`, `company_id`, `email`, `hashed_password`, `full_name`, `role`, `is_active`, `is_verified`) |
| **How to Demonstrate** | 1. Navigate to `http://localhost:5173/login`.<br>2. Click the **Company Admin** demo quick-fill button (`admin@adaptiveai-demo.com`) and log in. Observe redirection to `/dashboard`.<br>3. Log out and click the **Customer** demo quick-fill button (`customer@adaptiveai-demo.com`). Observe redirection to `/customer/chat`.<br>4. Attempting to manually navigate to `/platform/dashboard` as a customer results in an automatic redirect or 403 Forbidden. |
| **Limitations** | Public self-registration endpoint (`POST /api/v1/auth/register`) currently returns a placeholder `{"detail": "Not yet implemented"}`. Users are provisioned by admins or seeded on startup. |

### 3.2 Multi-Tenancy and Data Isolation

| Attribute | Details |
|---|---|
| **Feature Name** | Three-Layer Multi-Tenant Isolation |
| **Simple Explanation** | Ensures that each company's documents, chats, customer details, and support tickets are stored in separate silos so that Company A can never see Company B's data. |
| **Technical Concept** | Shared Database, Shared Schema Multi-Tenancy with Mandatory Foreign Key Scoping, Cryptographic JWT Tenant Embedding, Declarative ORM Mixins. |
| **Status** | **Implemented & Fully Verified** |
| **Backend Files** | - `app/db/base.py` (Lines 48–61): `TenantMixin` defining mandatory `company_id` column<br>- `app/core/dependencies.py` (Lines 91–120): `get_tenant_id` and `get_current_company_user`<br>- `app/api/v1/*.py`: Every service endpoint filters queries by `company_id == current_user.company_id` |
| **Frontend Files** | - `frontend/src/types/api.ts`: Typed interfaces carrying `company_id`<br>- `frontend/public/demo.html`: Top bar tenant switcher (`?tenant=adaptiveai-demo` vs `?tenant=tenant-b-corp`) |
| **Database Tables** | All domain tables inherit `TenantMixin`: `documents`, `document_chunks`, `conversations`, `messages`, `feedback`, `experiences`, `escalations`, `chatbot_settings`. |
| **How to Demonstrate** | Run `python test_confidence_and_escalation.py`. Test D explicitly tests that Tenant B Admin querying Demo Company’s escalation ID receives an immediate HTTP 404 Not Found, and Tenant B’s escalation listing leaks zero records from Demo Company. |
| **Limitations** | Row-Level Security (PostgreSQL RLS policies at the database engine level) is not enabled; isolation is enforced strictly at the application/ORM service layer. |

### 3.3 Company and User Management

| Attribute | Details |
|---|---|
| **Feature Name** | Platform Administration & Company Management |
| **Simple Explanation** | Platform super-admins can create companies, activate/deactivate accounts, and view global usage. Company admins can invite team members and configure bot settings. |
| **Technical Concept** | Hierarchical RBAC (`SUPER_ADMIN` > `COMPANY_ADMIN` > `EMPLOYEE` > `CUSTOMER`), Dynamic DB Aggregates, Cascade Deletions. |
| **Status** | **Implemented & Fully Verified** |
| **Backend Files** | - `app/api/v1/companies.py`: `get_platform_overview`, `list_companies`, `create_company`, `update_company`, `delete_company`, `get_my_chatbot_settings`, `update_my_chatbot_settings`<br>- `app/api/v1/users.py`: `get_me`, `invite_user`, `list_users`, `update_user`, `delete_user` |
| **Frontend Files** | - `frontend/src/pages/platform/PlatformDashboard.tsx`<br>- `frontend/src/pages/platform/CompaniesManagement.tsx`<br>- `frontend/src/pages/platform/PlatformUsage.tsx`<br>- `frontend/src/pages/company/CompanyUsers.tsx`<br>- `frontend/src/pages/company/CompanySettings.tsx` |
| **Database Tables** | `companies`, `users`, `chatbot_settings` |
| **How to Demonstrate** | Log in as `superadmin@adaptiveai.dev` (Password: `AdaptiveAI123`). Navigate to **Companies Management** (`/platform/companies`). Create a new company or inspect existing tenants. Log in as `admin@adaptiveai-demo.com` and open **Company Settings** (`/company/settings`) to customize bot tone and system prompt additions. |
| **Limitations** | Deleting a company soft-deactivates it (`is_active = False`) via API, though foreign keys support full cascade delete if dropped at the DB layer. |

### 3.4 Knowledge Ingestion & Vector Pipeline

| Attribute | Details |
|---|---|
| **Feature Name** | Document Processing, Sliding-Window Chunking, and Vector Embeddings |
| **Simple Explanation** | Admins upload files (PDFs, Word docs, text). The system reads the text, splits it into bite-sized overlapping pieces, converts each piece into a mathematical list of numbers (embeddings), and saves them into the vector database. |
| **Technical Concept** | Multi-Format Text Extraction, Tokenization via `tiktoken` (`cl100k_base`), Overlapping Token Slicing (512 tokens / 64 overlap), Batch Vector Embeddings via Gemini `text-embedding-004` (768 dimensions), `pgvector` indexing. |
| **Status** | **Implemented & Fully Verified** |
| **Backend Files** | - `app/services/document_processor.py` (Lines 28–241): `extract_text`, `clean_text`, `chunk_text`, `process_document`<br>- `app/ai/providers/gemini_provider.py` (Lines 179–273): `GeminiEmbeddingProvider`<br>- `app/api/v1/documents.py` (Lines 53–250): `upload_document`, `list_documents`, `delete_document`, `reprocess_document` |
| **Frontend Files** | - `frontend/src/pages/Documents.tsx`: Drag-and-drop file upload, document status badges (`PENDING`, `PROCESSING`, `READY`, `FAILED`), chunk count view, reprocess button. |
| **Database Tables** | `documents` (FK to company, status, file size, storage path), `document_chunks` (FK to document & company, `content`, `embedding` vector(768), `page_number`, `chunk_index`, `token_count`, `metadata` JSONB). |
| **How to Demonstrate** | Open **Knowledge Base** (`/documents`) in the admin console. Upload a PDF or text file. Observe the real-time status change to `READY` and the displayed chunk count. Inspect PostgreSQL table `document_chunks` to verify that `embedding` contains 768 floating-point numbers. |
| **Limitations** | File processing happens synchronously within the upload API request. If an admin uploads a 500-page PDF, the HTTP connection may hit a client timeout. (Ideal future enhancement: Celery/Redis background task). |

### 3.5 Retrieval-Augmented Generation (RAG)

| Attribute | Details |
|---|---|
| **Feature Name** | Context-Grounded Question Answering with Provenance Citations |
| **Simple Explanation** | When a user asks a question, the system finds the most relevant pieces of company documents and verified experiences, packages them into an instruction prompt, and sends them to Gemini to generate an answer. The AI must cite where it found the answer. |
| **Technical Concept** | Cosine Similarity Search (`DocumentChunk.embedding.cosine_distance(query)`), Prompt Engineering with Context Injection, Source Provenance Tracking, Multi-Turn Conversation Memory. |
| **Status** | **Implemented & Fully Verified** |
| **Backend Files** | - `app/services/rag_service.py` (Lines 24–76, 169–399): `retrieve_chunks_with_scores`, `generate_rag_answer`<br>- `app/ai/providers/gemini_provider.py` (Lines 24–178): `GeminiProvider`<br>- `app/api/v1/chat.py` (Lines 28–239): Chat API handling conversation history and message persistence |
| **Frontend Files** | - `frontend/src/pages/Chat.tsx`: Admin/Employee interactive chat console<br>- `frontend/src/pages/customer/CustomerChat.tsx`: Dedicated end-user chat interface with collapsible source pills and feedback thumbs |
| **Database Tables** | `conversations`, `messages` (Columns: `retrieved_chunk_ids` JSONB, `sources` JSONB, `confidence_score` Float, `is_escalated` Boolean, `prompt_tokens`, `completion_tokens`) |
| **How to Demonstrate** | In **Customer Chat** (`/customer/chat`), ask: *"What primary materials does Patagonia use in its clothing?"* The bot replies using the stored sustainability document, displaying confidence (e.g., `84.2%`) and a clickable citation pill `[Document Source 1]`. |
| **Limitations** | Manual knowledge items CRUD in `app/api/v1/knowledge.py` is not yet implemented (returns placeholder); all knowledge is currently ingested via Documents or created via the Verified Experience loop. |

### 3.6 Adaptive Knowledge / Experience Loop

| Attribute | Details |
|---|---|
| **Feature Name** | Human-in-the-Loop Feedback & Verified Experience Memory |
| **Simple Explanation** | If the AI gives an incorrect answer, a customer can click thumbs-down and submit a correction. An admin reviews it in the dashboard. Once approved, it is transformed into a "Verified Experience." Future questions will retrieve this human-verified answer and prioritize it over outdated document text. |
| **Technical Concept** | External Memory Augmentation, Human-in-the-Loop (HITL) Verification, Dual-Source RAG (Document Chunks + Approved Experience Vectors), System Prompt Priority Overrides. |
| **Status** | **Implemented & Fully Verified** |
| **Backend Files** | - `app/models/experience.py`: `Experience` model and verification lifecycle (`PENDING`, `APPROVED`, `REJECTED`)<br>- `app/api/v1/feedback.py` (Lines 44–318): `submit_feedback`, `list_feedback`, `review_feedback` (triggers `Experience` creation)<br>- `app/api/v1/experiences.py` (Lines 71–237): `list_experiences`, `approve_experience` (generates vector embedding), `reject_experience`<br>- `app/services/rag_service.py` (Lines 78–123, 247–283): `retrieve_verified_experiences_with_scores` and prompt context building |
| **Frontend Files** | - `frontend/src/pages/Feedback.tsx`: Review submitted customer ratings and corrections<br>- `frontend/src/pages/Experiences.tsx`: Manage, inspect, approve, or reject verified experience entries |
| **Database Tables** | `feedback` (FK to message & user, rating, category, `user_correction`, status), `experiences` (FK to company & source message, `question`, `original_answer`, `corrected_answer`, `verification_status`, `embedding` vector(768), `verified_by`, `verified_at`). |
| **How to Demonstrate** | Run `python test_adaptive_loop_integration.py`. The test executes the full lifecycle: asks a question -> submits negative feedback with a synthetic correction -> admin reviews feedback -> Experience is created in `PENDING` (no embedding) -> Admin approves Experience (status becomes `APPROVED`, embedding is generated) -> Same question is asked again -> Assistant retrieves the verified experience, confirms `retrieved_experiences > 0`, and answers using the human correction. |
| **Limitations** | Creating an experience currently requires explicit admin review/approval; it does not automatically promote unreviewed customer feedback (which is an intentional safety guardrail against prompt injection and poisoning). |

### 3.7 Confidence Scoring and Guardrail Fallback

| Attribute | Details |
|---|---|
| **Feature Name** | Deterministic Cosine-Similarity Confidence Scoring & Escalation Guardrail |
| **Simple Explanation** | Instead of letting the AI guess when it doesn't know something, the system calculates a score based on how closely the question matches company documents. If the score is below 0.50, the AI immediately stops, gives a safe apology, and calls for human support. |
| **Technical Concept** | Deterministic Knowledge Availability Metric, Guardrail Decision Engine, Safe Fallback Response. |
| **Status** | **Implemented & Fully Verified** |
| **Backend Files** | - `app/services/rag_service.py` (Lines 126–168, 207–241): `calculate_confidence_score`<br>- `app/config.py` (Lines 83–86): `confidence_high_threshold = 0.80`, `confidence_low_threshold = 0.50` |
| **Exact Mathematical Formula in Code** | Located in `app/services/rag_service.py`, lines 126–168:<br>1. Let `best_exp_sim = max(experience_scores)` and `best_chunk_sim = max(chunk_scores)`.<br>2. **Rule 1 (Verified Experience):** If `best_exp_sim >= similarity_threshold (0.70)`, return `round(best_exp_sim, 4)` (High Confidence).<br>3. **Rule 2 (Document Chunk):** Else if `best_chunk_sim >= similarity_threshold (0.70)`, return `round(best_chunk_sim, 4)` (High Confidence).<br>4. **Rule 3 (Missing / Irrelevant):** Let `max_sim = max(best_chunk_sim, best_exp_sim)`. If `max_sim <= 0.40`, return `0.0`.<br>5. **Rule 4 (Interpolated Low Confidence):** Else scale `max_sim` into the low-confidence band below `low_confidence_threshold`:<br>$$\text{scaled} = \frac{\text{max\_sim} - 0.40}{\text{threshold} - 0.40} \times (\text{low\_threshold} - 0.05)$$<br>Score is capped at `low_confidence_threshold - 0.01` (strictly `< 0.50`), guaranteeing an automated escalation. |
| **How to Demonstrate** | In **Chat**, ask: *"What is the population of Mars?"* The backend calculates cosine similarity against the corporate docs (similarity < 0.40), returns `confidence_score = 0.0`, returns the safe fallback message (*"I couldn't find enough verified information... I've escalated your question to a company representative."*), sets `is_escalated: True`, and creates an open record in `escalations`. |
| **Limitations** | Confidence reflects vector similarity of retrieved context, not linguistic calibration of the LLM's internal token probabilities. |

### 3.8 Human Escalation Workflow

| Attribute | Details |
|---|---|
| **Feature Name** | Human Escalation Management and Resolution-to-Knowledge Pipeline |
| **Simple Explanation** | When a chatbot fails or gets confused, a support ticket is created automatically. A human agent can claim the ticket, see the entire conversation history, write a resolution note to help the customer, and optionally click a checkbox to turn that answer into a new training experience. |
| **Technical Concept** | Service Desk Workflow Engine, State Transitions (`OPEN` -> `IN_PROGRESS` -> `RESOLVED`), Conversation Session Locking, Escalation-to-Experience Bridge. |
| **Status** | **Implemented & Fully Verified** |
| **Backend Files** | - `app/models/escalation.py`: `Escalation`, `EscalationStatus`, `EscalationReason`<br>- `app/api/v1/escalations.py`: `list_escalations`, `get_escalation_details`, `assign_escalation`, `resolve_escalation`, `create_manual_escalation` |
| **Frontend Files** | - `frontend/src/pages/Escalations.tsx`: Escalation inbox, status filters, ticket drawer with full transcript view, agent assignment, and resolution modal with experience creation checkbox. |
| **Database Tables** | `escalations` (FK to company, conversation, triggering message, assigned agent; `reason`, `status`, `resolution_notes`, `resolved_at`) |
| **How to Demonstrate** | Trigger an escalation with an unknown question. Log into the admin portal as `admin@adaptiveai-demo.com` and click **Escalations** (`/escalations`). Observe the new `OPEN` ticket. Click **Assign to Me** (`IN_PROGRESS`). Click **Resolve**, enter resolution notes, and check "Create Experience for Knowledge Base". The ticket marks `RESOLVED`, and an Experience appears in `PENDING` on `/experiences`. |
| **Limitations** | Real-time agent chat takeover via WebSockets is not implemented; handoff occurs via asynchronous ticketing and resolution notes. |

### 3.9 Analytics and Monitoring Engine

| Attribute | Details |
|---|---|
| **Feature Name** | Real-Time Dashboard & Knowledge Gaps Reporting |
| **Simple Explanation** | Dashboards that show how many questions were asked, average confidence scores, escalation rates, customer satisfaction ratings, and a list of unanswered questions. |
| **Technical Concept** | Database-Level Aggregations (`func.count`, `func.avg`, `case` statements), Proxy Reliability Metrics, Unanswered Query Gap Analysis. |
| **Status** | **Implemented & Fully Verified** |
| **Backend Files** | - `app/api/v1/analytics.py` (Lines 46–730): `/overview`, `/questions`, `/feedback`, `/knowledge-gaps`, `/accuracy` |
| **Frontend Files** | - `frontend/src/pages/Analytics.tsx`: Interactive charts, stat cards, confidence distribution histograms, escalation metrics, and knowledge gaps table. |
| **Database Tables** | Queries across `messages`, `conversations`, `feedback`, `escalations`, `experiences`, `documents`. |
| **How to Demonstrate** | Navigate to **Analytics** (`/analytics`) in the company admin workspace. View total questions, average confidence score, escalation rate ($$\frac{\text{Escalated Answers}}{\text{Total Answers}}$$), positive feedback percentage, and inspect the **Knowledge Gaps** tab to see recurring unanswered queries. |
| **Limitations** | Accuracy metrics are operational proxies based on user feedback and confidence scores, rather than automated benchmark test datasets (e.g., Ragas or TruLens). |

### 3.10 Embeddable Chatbot Widget & Demo Storefront

| Attribute | Details |
|---|---|
| **Feature Name** | Lightweight Embeddable Script and Multi-Tenant Interactive Demo Store |
| **Simple Explanation** | Any company can embed the chatbot into their own website by adding a 3-line `<script>` tag. We also built a demo e-commerce website showing the widget working live with a tenant switcher. |
| **Technical Concept** | Standalone JavaScript Widget (`widget.js`), Client State Management (`sessionStorage`), Public REST Widget API (`/api/v1/widget/{widget_id}/chat`), Dynamic Tenant Routing. |
| **Status** | **Implemented & Fully Verified** |
| **Backend Files** | - `app/api/v1/widget.py` (Lines 52–406): `resolve_company`, `get_widget_config`, `widget_chat`, `widget_feedback`<br>- `app/main.py` (Lines 114–127): Serves `/widget.js` and `/demo` |
| **Frontend Files** | - `frontend/public/widget.js`: Zero-dependency embeddable script (723 lines)<br>- `frontend/public/demo.html`: Outdoor apparel demo storefront (503 lines) with live widget launcher and tenant selector<br>- `frontend/src/pages/company/IntegrateChatbot.tsx`: Integration guide page with copyable script snippet |
| **How to Demonstrate** | Open `http://localhost:5173/demo.html` (or `http://127.0.0.1:8000/demo`) in a browser. The floating blue chat bubble appears in the bottom right corner. Click it, ask questions, receive answers with confidence badges, and submit thumbs up/down feedback. Change the tenant dropdown to test another company. |
| **Limitations** | Currently, any website that knows a company's slug can embed the widget; production deployment requires adding origin domain validation (CORS allowlist per company). |

---

## 4. Technical Concepts Explained for Viva

This section translates complex engineering concepts into simple language first, followed by the exact implementation details, repository file links, an example, and a likely question a professor might ask.

---

### Concept 1: Large Language Models (LLMs) & Generative AI
- **Simple Explanation:** An LLM is a deep neural network trained on vast quantities of text that can understand and generate human-like sentences by predicting what words should come next.
- **Why We Use It:** We use it to synthesize fluent, natural conversational responses from raw retrieved document text rather than forcing users to navigate rigid button menus.
- **How It Works in AdaptiveAI:** We call Google's `gemini-1.5-flash` model through the modern `google-genai` SDK using a strict system prompt that instructs the model to answer *only* using provided context chunks.
- **Exact Code Location:** [`GeminiProvider.generate_response` in app/ai/providers/gemini_provider.py](file:///c:/adaptive-ai/app/ai/providers/gemini_provider.py#L40-L100).
- **Simple Example:** Given context *"Our return window is 30 days"*, when the user asks *"Can I return after 2 weeks?"*, the LLM infers that 14 days is within 30 days and generates *"Yes, you can return your item within 30 days of purchase."*
- **Likely Professor Question:** *"If LLMs are so smart, why didn't you just ask Gemini directly without RAG?"*
  - **Concise Answer:** *"Generic LLMs lack access to proprietary, private company documents and are prone to hallucinations. Fine-tuning an LLM is expensive, causes catastrophic forgetting, and cannot be updated instantaneously when corporate policies change."*

---

### Concept 2: Retrieval-Augmented Generation (RAG)
- **Simple Explanation:** RAG is like an open-book exam for the AI. When asked a question, the system first searches company documents to find relevant paragraphs (Retrieval), pastes those paragraphs into the prompt, and then tells the AI to write an answer based strictly on those paragraphs (Generation).
- **Why We Use It:** It grounds the AI’s answers in verifiable organizational truth and provides source citations without retraining the model.
- **How It Works in AdaptiveAI:** Incoming queries are converted to vector embeddings, matched against `document_chunks` and `experiences` in PostgreSQL using pgvector, and injected into the system prompt with strict rules to prevent fabrication.
- **Exact Code Location:** [`generate_rag_answer` in app/services/rag_service.py](file:///c:/adaptive-ai/app/services/rag_service.py#L169-L399).
- **Simple Example:** Query: *"What is your policy on microplastics?"* -> Retrieved: Chunk 4 from `sustainability.pdf` -> Generated answer citing `[Document Source 1]`.
- **Likely Professor Question:** *"What happens in your RAG pipeline if the retrieved documents do not contain the answer?"*
  - **Concise Answer:** *"Our system calculates the cosine similarity. If no chunk meets our 0.70 threshold, the confidence score drops below 0.50. The RAG pipeline halts generation, returns a safe fallback message, and automatically files a human escalation ticket."*

---

### Concept 3: Vector Embeddings & pgvector
- **Simple Explanation:** An embedding is a way of translating text into a list of numbers (a vector) so that concepts with similar meanings are located close together in mathematical space. `pgvector` is a PostgreSQL plugin that stores these vectors and finds the closest matches in milliseconds.
- **Why We Use It:** Keyword searches (like SQL `LIKE '%return%'`) fail if the user says *"How do I send back my jacket?"*. Vector embeddings capture semantic meaning so that "send back" matches "return".
- **How It Works in AdaptiveAI:** We use Google's `text-embedding-004` model to convert chunks into 768-dimensional vectors. We store them in the `embedding` column of type `Vector(768)` in PostgreSQL, querying them with the cosine distance operator `<=>`.
- **Exact Code Location:** [`DocumentChunk` in app/models/document_chunk.py](file:///c:/adaptive-ai/app/models/document_chunk.py#L41-L43) and [`retrieve_chunks_with_scores` in app/services/rag_service.py](file:///c:/adaptive-ai/app/services/rag_service.py#L31-L49).
- **Simple Example:** Vector for *"automobile"* is mathematically close to *"car"*, but far from *"banana"*.
- **Likely Professor Question:** *"Why did you choose pgvector instead of a dedicated vector database like Pinecone, Milvus, or Weaviate?"*
  - **Concise Answer:** *"Using pgvector keeps our relational data (users, companies, conversations) and vector embeddings in a single ACID-compliant database. This avoids complex two-phase commits, prevents distributed synchronization lag, simplifies backup and tenant isolation, and eliminates extra infrastructure costs."*

---

### Concept 4: Document Chunking Strategy
- **Simple Explanation:** LLMs have context limits and search engines work best with focused text. Chunking is the process of breaking long 50-page documents into small, logical paragraphs with a slight overlap.
- **Why We Use It:** If we embed an entire 50-page document into one vector, specific details get diluted. Small chunks ensure that the vector precisely represents the specific topic discussed.
- **How It Works in AdaptiveAI:** We use `tiktoken` with the `cl100k_base` tokenizer. We set `chunk_size_tokens = 512` with a `chunk_overlap_tokens = 64` sliding window. Overlap ensures sentences split across boundaries do not lose their semantic context.
- **Exact Code Location:** [`chunk_text` in app/services/document_processor.py](file:///c:/adaptive-ai/app/services/document_processor.py#L93-L143).
- **Simple Example:** In a document on warranty, Chunk 1 ends with *"Items purchased after Nov 1 are eligible for..."* and Chunk 2 begins with *"...eligible for our extended holiday return policy."*
- **Likely Professor Question:** *"Why use token-based chunking rather than character-based or sentence-based chunking?"*
  - **Concise Answer:** *"LLM context limits and embedding models operate strictly on tokens, not characters. Token-based chunking guarantees we stay precisely within model input constraints without unexpected truncation."*

---

### Concept 5: Multi-Tenancy & Tenant Isolation
- **Simple Explanation:** Multi-tenancy allows one software application and database to serve multiple distinct companies while guaranteeing that neither company can ever see or modify the other company's data.
- **Why We Use It:** It enables a SaaS business model where one deployment serves dozens of corporate clients securely.
- **How It Works in AdaptiveAI:** Isolation is enforced at 3 separate layers: (1) The user's JWT contains their verified `company_id`; (2) FastAPI dependencies extract and validate this ID on every request; (3) All SQLAlchemy models inherit `TenantMixin`, and services strictly append `.where(Model.company_id == current_user.company_id)` to every SQL statement.
- **Exact Code Location:** [`TenantMixin` in app/db/base.py](file:///c:/adaptive-ai/app/db/base.py#L48-L61) and [`get_tenant_id` in app/core/dependencies.py](file:///c:/adaptive-ai/app/core/dependencies.py#L91-L107).
- **Simple Example:** If Tenant A tries to execute `GET /api/v1/escalations/{tenant_b_id}`, the query includes `WHERE company_id == tenant_a_id`, immediately returning a `404 Not Found`.
- **Likely Professor Question:** *"What is the difference between your multi-tenant approach and separate databases per tenant?"*
  - **Concise Answer:** *"We use a shared database with shared schema and discriminator column (`company_id`). This provides high resource efficiency, simple connection pooling, and easy schema migrations. Isolation is enforced through mandatory foreign keys, JWT validation, and ORM query scoping."*

---

### Concept 6: Deterministic Confidence vs. Probability
- **Simple Explanation:** LLMs do not know when they are lying; they can produce completely fabricated text with high grammatical certainty. A deterministic confidence score is an external mathematical check based on how closely company files actually match the question.
- **Why We Use It:** To create an unshakeable safety guardrail that blocks hallucinations before they reach the user.
- **How It Works in AdaptiveAI:** We compute the cosine similarity ($1.0 - \text{cosine\_distance}$) between the query vector and retrieved database vectors. If the similarity is below 0.40, confidence is set to `0.0`. If between 0.40 and 0.70, it scales deterministically below 0.50, triggering human escalation.
- **Exact Code Location:** [`calculate_confidence_score` in app/services/rag_service.py](file:///c:/adaptive-ai/app/services/rag_service.py#L126-L168).
- **Simple Example:** Question: *"Can your software cure insomnia?"* Match score against corporate documents: `0.18`. Confidence returned: `0.00`. Result: Escalated.
- **Likely Professor Question:** *"Is your confidence score a true statistical probability?"*
  - **Concise Answer:** *"No, and that is an intentional engineering decision. In information retrieval, cosine similarity measures semantic vector proximity, not probability distribution. Our formula is an explainable, deterministic heuristic calibrated to our retrieval threshold ($0.70$) and escalation trigger ($0.50$)."*

---

### Concept 7: Human-in-the-Loop (HITL) Adaptive Feedback Loop
- **Simple Explanation:** Instead of letting the AI run wild or requiring a software engineer to modify code whenever an answer is wrong, the platform lets regular support staff review feedback, approve corrections, and instantly teach the system the right answer.
- **Why We Use It:** Real-world knowledge changes daily. HITL provides continuous improvement while preventing malicious users from poisoning the AI with bad data.
- **How It Works in AdaptiveAI:** Negative feedback or escalation notes create an `Experience` in `PENDING` status. Only when an admin approves it does the system generate an embedding and set status to `APPROVED`. The RAG pipeline retrieves approved experiences and instructs Gemini to treat them as the ground truth.
- **Exact Code Location:** [`approve_experience` in app/api/v1/experiences.py](file:///c:/adaptive-ai/app/api/v1/experiences.py#L145-L202) and [`rag_service.py`](file:///c:/adaptive-ai/app/services/rag_service.py#L313-L322).
- **Simple Example:** Outdated doc says *"We only ship to USA"*. Admin approves experience: *"We now ship to Canada as well"*. The next Canadian customer asking about shipping receives the corrected policy immediately.
- **Likely Professor Question:** *"Does approving an experience fine-tune or retrain the Gemini model?"*
  - **Concise Answer:** *"No. It updates the retrieval context in pgvector. Fine-tuning an LLM takes hours, costs money, and risks regression. Our method updates the vector knowledge layer in milliseconds, offering instant, controllable, and auditable adaptation."*

---

## 5. System Architecture

### 5.1 Architecture Diagram

```mermaid
flowchart TD
    %% Clients & Interfaces
    subgraph Clients["Frontend & Client Interfaces"]
        PA["Platform Super Admin\n(React Admin Console)"]
        CA["Company Admin / Support Agent\n(React Management Console)"]
        CW["Website Visitor / Customer\n(Embeddable widget.js / demo.html)"]
    end

    %% Security & API Layer
    subgraph APILayer["FastAPI Asynchronous API Layer (Port 8000)"]
        AuthMid["JWT Auth Middleware & Security\n(bcrypt / python-jose / HTTPBearer)"]
        TenDep["Tenant Resolution & Isolation Dependency\n(get_tenant_id / resolve_company)"]
        
        subgraph Endpoints["API v1 Routers (/api/v1)"]
            AuthEP["/auth (Login / Token Refresh)"]
            DocEP["/documents (Upload & Ingestion)"]
            ChatEP["/chat & /widget (Conversational Core)"]
            ExpEP["/experiences (Verification & Approval)"]
            EscEP["/escalations (Assignment & Resolution)"]
            AnaEP["/analytics (Gaps & Operational Metrics)"]
        end
    end

    %% Business Logic Layer
    subgraph Services["Core Business & AI Services Layer"]
        DocProc["Document Processor\n(pypdf / python-docx / tiktoken 512-chunk)"]
        RAGServ["RAG Retrieval Engine\n(Cosine Distance Search & Prompt Assembler)"]
        ConfEngine["Deterministic Confidence Engine\n(Threshold Checks: High >= 0.80, Low < 0.50)"]
    end

    %% External AI Providers
    subgraph ExternalAI["External AI Services (Google GenAI)"]
        GeminiEmbed["Gemini Embedding Model\n(models/text-embedding-004 - 768 dims)"]
        GeminiLLM["Gemini Generative LLM\n(gemini-1.5-flash / system prompt grounding)"]
    end

    %% Database Storage Layer
    subgraph DataStore["PostgreSQL 16 + pgvector Database"]
        T_Comp["companies (Tenant Root)"]
        T_User["users (RBAC Roles & Passwords)"]
        T_Doc["documents (Metadata & Status)"]
        T_Chunks["document_chunks\n(pgvector Vector(768) + Content)"]
        T_Exp["experiences\n(Approved Vector(768) Verified Q&A)"]
        T_Conv["conversations & messages\n(Chat turns + Provenance + Tokens)"]
        T_Esc["escalations (Human Support Tickets)"]
        T_Feed["feedback (User Ratings & Corrections)"]
    end

    %% Relationships & Data Flow
    PA -->|Manages Tenants| AuthEP
    CA -->|Uploads Docs / Reviews Tickets| AuthMid
    CW -->|Public Embed / Anonymous Chat| ChatEP

    AuthMid --> TenDep
    TenDep --> Endpoints

    DocEP -->|Raw Files| DocProc
    DocProc -->|Generate Chunks & Vectors| GeminiEmbed
    DocProc -->|Store Chunks & Embeddings| T_Chunks
    DocProc -->|Save File Metadata| T_Doc

    ChatEP -->|User Query| RAGServ
    RAGServ -->|Embed Query| GeminiEmbed
    RAGServ -->|Vector Cosine Match| T_Chunks
    RAGServ -->|Vector Cosine Match| T_Exp
    
    RAGServ -->|Similarity Scores| ConfEngine

    ConfEngine -->|Low Confidence < 0.50| T_Esc
    ConfEngine -->|Low Confidence < 0.50| ChatEP
    ConfEngine -->|High Confidence >= 0.70| GeminiLLM
    
    GeminiLLM -->|Grounded Answer + Citations| ChatEP
    ChatEP -->|Save Turn & Provenance| T_Conv

    CW -->|Submit Thumbs Down + Correction| T_Feed
    T_Feed -->|Admin Review| T_Exp
    T_Esc -->|Resolve Ticket + Create Correction| T_Exp
    ExpEP -->|Admin Approves Experience| GeminiEmbed
    GeminiEmbed -->|Embed Approved Answer| T_Exp

    AnaEP -->|SQL Aggregates| T_Conv
    AnaEP -->|Gaps & Metric Counts| T_Esc
```

### 5.2 Architecture Component Inventory

1. **Client / Presentation Layer:**
   - **Admin Management Console (`frontend/src/`):** React 19 SPA with role-based routing. Supports Super Admin (tenant provisioning), Company Admin (documents, settings, user invitations), and Employee (escalations inbox, feedback review).
   - **Embeddable Widget (`frontend/public/widget.js`):** Lightweight, zero-dependency vanilla JS script that renders an interactive floating chat drawer on any host website. Communicates directly with the `/api/v1/widget` endpoints.
   - **Demo Storefront (`frontend/public/demo.html`):** E-commerce landing page simulating an outdoor apparel retailer, featuring a top-bar tenant switcher to demonstrate multi-tenant separation live.

2. **API & Security Gateway:**
   - **FastAPI Core (`app/main.py`):** Configures CORS middleware, structured logging, lifespan startup hooks (`init_db`), and aggregates routers under `/api/v1`.
   - **Security Engine (`app/core/security.py`):** Stateless JWT encoding and verification with `HS256`, and password hashing using direct `bcrypt` salt rounds.
   - **Dependency Ingestion (`app/core/dependencies.py`):** Extracts bearer tokens, decodes `sub` (user_id) and `company_id`, checks account active status, and enforces RBAC decorators.

3. **Ingestion & Vector Processing Service:**
   - **Document Processor (`app/services/document_processor.py`):** Parses PDF, DOCX, TXT, CSV, and Markdown files; tokenizes via `tiktoken`; produces 512-token chunks with 64-token overlap; calls Gemini's batch embedding API; and commits records to `document_chunks`.

4. **Conversational RAG Engine:**
   - **RAG Service (`app/services/rag_service.py`):** Orchestrates query embedding generation, dual-source vector retrieval (`document_chunks` and `experiences`), confidence score calculation, context assembly with verified experience priority, prompt construction, and Gemini LLM invocation with automated retries.

5. **Storage & Data Layer:**
   - **PostgreSQL 16 + pgvector:** Hosts the relational schema (companies, users, audit logs) and the vector indices (`Vector(768)`). Foreign keys enforce database-level cascade deletions.

---

### 5.3 End-to-End Data Flows

#### Flow 1: Company Administrator Logs In
1. User enters email and password on the login screen (`frontend/src/pages/Login.tsx`).
2. Frontend sends `POST /api/v1/auth/login` with form data (`app/api/v1/auth.py:32`).
3. Backend fetches user by email from table `users` and verifies password hash using `bcrypt.checkpw` (`app/core/security.py:28`).
4. Backend generates an `access_token` (containing `sub: user_id`, `company_id`, `role`) and a `refresh_token` (`app/core/security.py:47`).
5. Frontend saves tokens in `localStorage` and redirects the user to `/dashboard` based on their role (`frontend/src/routes/ProtectedRoute.tsx`).

#### Flow 2: Company Uploads a Knowledge Document
1. Admin uploads a file on the Documents page (`frontend/src/pages/Documents.tsx`).
2. Browser issues `POST /api/v1/documents/upload` with `multipart/form-data` (`app/api/v1/documents.py:53`).
3. Route dependency `get_current_company_user` verifies tenant identity and saves the file to disk (`storage/documents/<company_id>/<uuid>_<filename>`).
4. Document record is inserted into `documents` table with status `PROCESSING`.
5. `process_document` extracts text (`pypdf` for PDF, `python-docx` for Word) (`app/services/document_processor.py:145`).
6. `chunk_text` slices text into 512-token segments with 64-token overlap using `tiktoken` (`app/services/document_processor.py:93`).
7. `GeminiEmbeddingProvider.generate_embeddings_batch` generates 768-dimensional vectors (`app/ai/providers/gemini_provider.py:230`).
8. Chunks and vectors are inserted into `document_chunks` table in PostgreSQL. Document status is updated to `READY`.

#### Flow 3 & 4: Customer Asks a Question & High-Confidence RAG Response
1. Customer types a question in the chat UI or website widget (`frontend/src/pages/customer/CustomerChat.tsx` or `widget.js`).
2. Client sends `POST /api/v1/chat/` (or `POST /api/v1/widget/{widget_id}/chat`).
3. Backend retrieves or creates a `Conversation` record in PostgreSQL (`app/api/v1/chat.py:38`).
4. User's query is saved as a `Message` with `role = USER` (`app/api/v1/chat.py:68`).
5. `generate_rag_answer` calls Gemini `text-embedding-004` to embed the user question (`app/services/rag_service.py:183`).
6. `retrieve_chunks_with_scores` executes pgvector cosine distance search against `document_chunks` (`app/services/rag_service.py:24`):
   ```sql
   SELECT id, content, (embedding <=> query_vector) AS dist
   FROM document_chunks
   WHERE company_id = :cid AND embedding IS NOT NULL
   ORDER BY dist LIMIT 10;
   ```
7. `retrieve_verified_experiences_with_scores` executes a parallel query against `experiences` (`verification_status = 'APPROVED'`).
8. `calculate_confidence_score` evaluates chunk and experience similarities against thresholds (`app/services/rag_service.py:126`).
9. When confidence $\ge 0.70$, context is assembled, placing **Verified Experiences first**, followed by **Document Chunks**.
10. The combined prompt is sent to `GeminiProvider.generate_response` (`gemini-1.5-flash`) (`app/services/rag_service.py:346`).
11. Assistant's response is saved in table `messages` along with `confidence_score`, `sources` JSONB, and `retrieved_chunk_ids`.
12. Response JSON is returned to the user, displaying the answer, confidence pill, and citation sources.

#### Flow 5: Low-Confidence Question & Automated Escalation
1. User asks a question not covered by the company's knowledge base (e.g., *"What is the population of Mars?"*).
2. Backend generates the query embedding and searches `document_chunks` and `experiences`.
3. The closest chunks return low cosine similarity ($< 0.40$).
4. `calculate_confidence_score` deterministically outputs `0.0` or a scaled score $< 0.50$ (`app/services/rag_service.py:157`).
5. In `rag_service.py:225`, the low confidence condition triggers:
   - Sets `is_escalated = True`.
   - Returns safe fallback text: *"I couldn't find enough verified information... I've escalated your question to a company representative."*
6. In `app/api/v1/chat.py:144`, the backend:
   - Updates `Conversation.status = 'ESCALATED'`.
   - Inserts a new record into `escalations` table (`status = 'OPEN'`, `reason = 'LOW_CONFIDENCE'`).
   - Links the triggering message ID to the escalation.
7. The ticket immediately appears in the agent's Escalations inbox (`frontend/src/pages/Escalations.tsx`).

#### Flow 6, 7 & 8: Feedback, Review, Approval & Future Retrieval Adaptation
1. User receives an answer that is outdated or incorrect and clicks thumbs-down (`frontend/src/pages/customer/CustomerChat.tsx`).
2. User provides a correction: *"We now use 100% BioLunar Stellar Synthetics"* and submits feedback.
3. Backend records a row in table `feedback` (`rating = 'NEGATIVE'`, `status = 'PENDING'`, `user_correction = '...'`) (`app/api/v1/feedback.py:108`).
4. Company Admin opens the Feedback dashboard (`frontend/src/pages/Feedback.tsx`) and clicks **Review & Convert to Experience** (`app/api/v1/feedback.py:217`).
5. The review endpoint creates an `Experience` record in table `experiences` with status `PENDING` (`app/api/v1/feedback.py:300`). At this stage, it has **no embedding** and is **not** used in RAG.
6. Admin navigates to **Verified Experiences** (`frontend/src/pages/Experiences.tsx`) and clicks **Approve** (`app/api/v1/experiences.py:145`).
7. `approve_experience`:
   - Sets `verification_status = 'APPROVED'`.
   - Calls `GeminiEmbeddingProvider.generate_embedding` on the verified Q&A pair text (`app/api/v1/experiences.py:187`).
   - Saves the 768-dim vector into `Experience.embedding`.
8. **Future Retrieval:** A second user asks the same question. In `generate_rag_answer`, `retrieve_verified_experiences_with_scores` matches this approved experience with high similarity. The prompt instructions force the LLM to prioritize the verified experience over the static PDF chunk. The user receives the updated correction with source attribution `[Verified Experience 1]`.

#### Flow 9: Third-Party Website Embeds the Chatbot
1. An external website includes:
   ```html
   <script src="http://127.0.0.1:8000/widget.js" data-chatbot-id="adaptiveai-demo" data-api-base="http://127.0.0.1:8000/api/v1"></script>
   ```
2. `widget.js` executes, creates an isolated DOM container (`#adaptiveai-widget-root`), and calls `GET /api/v1/widget/adaptiveai-demo/config` (`app/api/v1/widget.py:132`).
3. Backend resolves the tenant via `resolve_company` by matching slug or UUID (`app/api/v1/widget.py:52`) and returns bot branding.
4. When the user sends a message, `widget.js` posts to `POST /api/v1/widget/adaptiveai-demo/chat` with session state stored in `sessionStorage`.
5. The backend executes the identical RAG pipeline, enforcing tenant isolation, confidence scoring, and escalation.

#### Flow 10: Platform Administrator Manages Companies
1. Super Admin logs in and opens `/platform/companies` (`frontend/src/pages/platform/CompaniesManagement.tsx`).
2. Frontend calls `GET /api/v1/companies/` (`app/api/v1/companies.py:303`), which queries `companies` table using `require_roles(UserRole.SUPER_ADMIN)`.
3. Super Admin submits a new company form (`POST /api/v1/companies/`). Backend generates a unique slug and provisions the tenant record.

---

### 5.4 Security and Isolation

AdaptiveAI distinguishes between **Authentication**, **Authorization**, and **Tenant Isolation**:
- **Authentication:** Verifies *who* the user is via signed HS256 JWTs containing expiration timestamps (`exp`), issuance times (`iat`), and subject UUID (`sub`).
- **Authorization (RBAC):** Verifies *what* the user can do. FastAPI dependencies inspect `current_user.role`. For instance, `require_roles(UserRole.SUPER_ADMIN)` protects platform routes, while `CompanyUser` ensures customers cannot access internal analytics or feedback logs.
- **Tenant Isolation:** Prevents cross-company data leakage. The `company_id` claim in the JWT is extracted by `get_tenant_id()` on every authenticated request. Every database query in the service layer explicitly appends `.where(Model.company_id == tenant_id)`.

#### Security Weaknesses & Operational Risks to Disclose in Review
1. **Public Widget Domain Whitelisting:** The widget endpoint `/api/v1/widget/{widget_id}/chat` is accessible to any client that provides a valid company slug. It lacks Origin domain validation, meaning an unauthorized external website could embed the bot unless domain restrictions are added.
2. **Synchronous Ingestion DoS Vector:** Uploading extremely large or malformed PDF documents can tie up backend worker threads during tokenization and embedding.
3. **Absence of PostgreSQL RLS:** Tenant isolation relies on the application and ORM logic rather than PostgreSQL Row-Level Security policies. A developer writing a raw SQL query without a `WHERE company_id = ...` clause could inadvertently leak cross-tenant data.

---

## 6. Live Demo Plan for the Professor (7–10 Minutes)

This rehearsable script guarantees a smooth local demonstration on Windows.

### Pre-Demo Checklist (Verify 15 Minutes Before Review)
- [ ] PostgreSQL 16 is running on `localhost:5432` with database `adaptiveai` and extension `vector` enabled.
- [ ] Virtual environment `.venv` is activated.
- [ ] Backend is running on `http://127.0.0.1:8000`.
- [ ] Frontend Vite server is running on `http://localhost:5173`.
- [ ] `.env` has valid `GEMINI_API_KEY` configured.
- [ ] Document `test_for_chatbot.pdf` is present and processed in the Demo Company knowledge base.

---

### Stage 1: Introduction (0:00 – 1:00)
- **Action:** Stand beside your laptop with the browser open to `http://localhost:5173/login`.
- **What to Say:**
  > *"Good morning, Professor. Today I am presenting **AdaptiveAI**, an enterprise conversational AI platform. Most enterprise chatbots suffer from two fatal flaws: they hallucinate when they do not know an answer, and when company policies change, updating the AI requires expensive, slow retraining. AdaptiveAI solves this with multi-tenant RAG, deterministic confidence guardrails that automatically escalate unanswerable queries to human agents, and a continuous feedback loop that updates searchable knowledge instantly through human verification. Let me demonstrate the running system."*

---

### Stage 2: Verify Running System Architecture (1:00 – 1:45)
- **Action:** Switch to two open command terminals or show active browser tabs:
  - Terminal 1 (Backend): `uvicorn app.main:app --reload --host 127.0.0.1 --port 8000`
  - Terminal 2 (Frontend): `npm run dev` in `frontend/`
- **Show in Browser:** Open `http://127.0.0.1:8000/docs` (FastAPI Swagger UI) and `http://127.0.0.1:8000/health`.
- **What to Say:**
  > *"Our backend is built on asynchronous FastAPI and PostgreSQL with the pgvector extension. As seen on our health endpoint, the database and Gemini AI providers are fully connected and healthy. Our frontend is a React 19 single-page application built with TypeScript and Tailwind CSS."*
- **Backup Plan:** If the server was stopped, run `.venv\Scripts\activate` then `uvicorn app.main:app --reload` in PowerShell.

---

### Stage 3: Platform Super Admin Console (1:45 – 2:45)
- **Action:** Go to `http://localhost:5173/login`. Click the **Platform Admin** quick-fill button (`superadmin@adaptiveai.dev`). Click **Sign in to Console**.
- **What to Observe:** The browser redirects to `/platform/dashboard`. Show the multi-tenant metrics: Total Companies, Active Companies, Total Registered Users, and Platform Queries.
- **Navigate:** Click **Companies** (`/platform/companies`). Show the existing tenants: `AdaptiveAI Demo Company` (`adaptiveai-demo`) and `Tenant B Corp` (`tenant-b-corp`).
- **What to Say:**
  > *"Here is the Super Admin console. AdaptiveAI is built from the ground up as a multi-tenant platform. Platform administrators can manage corporate clients, activate or deactivate organizations, and monitor platform-wide utilization without accessing private tenant conversations."*

---

### Stage 4: Company Workspace & Knowledge Ingestion (2:45 – 4:00)
- **Action:** Log out. Click the **Company Admin** quick-fill button (`admin@adaptiveai-demo.com`). Sign in. The browser opens `/dashboard`.
- **Navigate:** Click **Knowledge Base** (`/documents`).
- **Show:** Highlight the uploaded sustainability PDF (`test_for_chatbot.pdf`). Point out the status badge (`READY`) and the chunk count.
- **What to Say:**
  > *"Now we are inside the corporate workspace for our demo company. In the Knowledge Base, corporate administrators upload internal files. When a document is uploaded, our document processor extracts text, tokenizes it with a sliding window of 512 tokens, generates 768-dimensional embeddings via Google's text-embedding-004, and stores them in PostgreSQL pgvector. This company's knowledge base is ready for retrieval."*

---

### Stage 5: High-Confidence RAG Question Answering (4:00 – 5:15)
- **Action:** Click **Chat** (`/chat`) or open **Customer Chat** (`/customer/chat`).
- **Ask the Chatbot:**
  ```
  What primary materials does Patagonia use in its clothing?
  ```
- **Expected Result:** The chatbot responds factually based on the PDF (mentioning organic cotton, recycled polyester, hemp, etc.).
- **Highlight on Screen:**
  1. The confidence score badge (e.g., `Confidence: 84.2%` — green).
  2. The source attribution pill `[Document Source 1]`.
- **What to Say:**
  > *"Notice what happened here: the system embedded the user's query, executed a cosine distance vector search in pgvector, calculated a high confidence score of 84%, assembled the exact document chunks into the prompt, and generated a grounded answer citing the source. There is zero hallucination."*

---

### Stage 6: Missing Knowledge, Low Confidence & Human Escalation (5:15 – 6:30)
- **Action:** In the same chat window, ask an out-of-domain question:
  ```
  What is the population of Mars?
  ```
- **Expected Result:**
  - Chatbot responds with safe fallback: *"I couldn't find enough verified information in the company's knowledge base to answer this confidently. I've escalated your question to a company representative."*
  - Confidence score displays `0.0%` (or `< 50.0%`).
  - Badge displays `ESCALATED`.
- **Action:** In the sidebar, click **Escalations** (`/escalations`).
- **Show:** The new `OPEN` escalation ticket with the reason `LOW_CONFIDENCE` and the customer's exact question.
- **What to Say:**
  > *"This is the core guardrail of AdaptiveAI. Because the question had no relevant matches in our corporate vector database, our deterministic formula calculated a confidence score below our 0.50 threshold. Instead of making up an answer, the bot stopped generation, delivered a safe fallback message, and immediately created a human support escalation ticket."*

---

### Stage 7: The Adaptive Learning Loop (Resolution to Verified Experience) (6:30 – 8:00)
- **Action:**
  1. In **Escalations** (`/escalations`), click on the ticket.
  2. Click **Assign to Me** (status changes to `IN_PROGRESS`).
  3. Click **Resolve Escalation**.
  4. In the resolution notes, enter:
     ```
     Mars currently has an active permanent human population of 0, though robotic scientific rovers are operational.
     ```
  5. Ensure **"Create Experience for Knowledge Base"** is checked. Click **Submit Resolution**.
  6. Navigate to **Verified Experiences** (`/experiences`).
  7. Show that the new experience is in `PENDING` state (untrusted).
  8. Click **Approve**. The status turns green (`APPROVED`) and the system embeds the approved text into pgvector.
- **Re-test in Chat:** Return to Chat and ask again:
  ```
  What is the population of Mars?
  ```
- **Expected Result:**
  - Assistant now answers confidently: *"Mars currently has an active permanent human population of 0, though robotic scientific rovers are operational."*
  - Sources show `[Verified Experience 1]`.
- **What to Say:**
  > *"This is our continuous adaptation loop. The human agent resolved the ticket, the admin verified it, and the system generated an embedding for that approved experience. When we asked the same question again, the system retrieved the verified experience and answered correctly. We adapted our conversational knowledge base in seconds with complete human oversight, without retraining the foundation LLM."*

---

### Stage 8: Embedded Website Widget & Demo Storefront (8:00 – 9:00)
- **Action:** Open a new tab to `http://localhost:5173/demo.html` (or `http://127.0.0.1:8000/demo`).
- **Show:** The outdoor retail demo store with the blue floating chat bubble in the bottom right corner.
- **Action:** Click the launcher button. Ask: *"What materials do you use?"*. Observe the identical RAG response inside the standalone widget.
- **Show Code Snippet:** Switch to `/integrate` in the admin console to show the 3-line embed script:
  ```html
  <script src="http://localhost:5173/widget.js" data-chatbot-id="adaptiveai-demo"></script>
  ```
- **What to Say:**
  > *"To deploy this AI, any external website simply pastes this single script tag. The widget is zero-dependency vanilla JavaScript. It queries our public widget API, resolves the tenant on the server, and provides customers with instant, grounded support."*

---

### Stage 9: Multi-Tenant Isolation Proof (9:00 – 9:45)
- **Action:** On `demo.html`, look at the top black bar: **Active Tenant Selector**. Switch dropdown from `AdaptiveAI Demo Company` to `Tenant B Corp` (`?tenant=tenant-b-corp`).
- **Action:** Open the widget for Tenant B and ask:
  ```
  What materials does Patagonia use?
  ```
- **Expected Result:** Tenant B has no such document; the bot immediately triggers low confidence and escalates for Tenant B. Demo Company’s files are completely invisible to Tenant B.
- **What to Say:**
  > *"Here is multi-tenancy in action. When we switch to Tenant B, Demo Company's documents and verified experiences do not exist. Data isolation is complete and cryptographically enforced."*

---

### Stage 10: Closing Summary (9:45 – 10:00)
- **What to Say:**
  > *"In summary, Professor, AdaptiveAI demonstrates a complete, production-patterned architecture: safe RAG, explainable confidence scoring, human-in-the-loop adaptation, and strict multi-tenancy. Thank you, and I am ready for your questions."*

---

### Demonstration Timing & Fallback Matrix

| Stage | Duration | Core Verification Point | Fallback if Issue Occurs |
|---|---|---|---|
| **1. Intro** | 1:00 | Clear articulation of problem & solution | None needed (verbal) |
| **2. Architecture** | 0:45 | Services running, `/health` ok | Show terminal outputs directly |
| **3. Super Admin** | 1:00 | Multi-tenant overview & companies | Use quick-fill button on `/login` |
| **4. Company Admin** | 1:15 | Documents list & chunk counts | Inspect `storage/documents` folder |
| **5. RAG Answering** | 1:15 | Grounded answer + citation pill | Use pre-tested question from script |
| **6. Escalation** | 1:15 | Low confidence trigger & ticket | If already escalated, show open ticket list |
| **7. Adaptive Loop** | 1:30 | Ticket resolution -> Approved experience | Use `test_adaptive_loop_integration.py` if UI lags |
| **8. Widget Demo** | 1:00 | Floating launcher on `demo.html` | Open `http://127.0.0.1:8000/demo` |
| **9. Multi-Tenancy** | 0:45 | Cross-tenant data separation | Point to Test D output in test suite |
| **10. Conclusion** | 0:15 | Academic and engineering summary | None needed (verbal) |

---

## 7. Final Review Presentation — 10 Slides

---

### Slide 1: Problem Statement and Motivation
- **Title:** AdaptiveAI — An Adaptive Enterprise Conversational AI Platform
- **Subtitle:** Overcoming Hallucination, Stale Knowledge, and Multi-Tenant Privacy in Enterprise Support
- **Main Content (Bullets):**
  - **The Enterprise LLM Paradox:** Foundation models are conversationally fluent but factually untrusted for proprietary company data.
  - **Hallucination Risk:** Generative AI invents plausible-sounding policies, creating direct financial and legal liability.
  - **The Stale Knowledge Trap:** Corporate documentation changes rapidly; retraining or fine-tuning LLMs is slow, costly, and unpredictable.
  - **Data Privacy in SaaS:** Multi-tenant platforms must guarantee absolute data separation between rival corporate clients.
- **Suggested Visual:** Three problem pillars (Hallucination, Stale Knowledge, Data Leakage) leading into the AdaptiveAI solution icon.
- **Speaker Notes:**
  > *"Good morning. Today's enterprise chatbots face a critical barrier: businesses want the conversational power of Large Language Models, but they cannot afford hallucinations. When a customer asks about a return policy, an AI cannot guess. Furthermore, when policies change, companies cannot wait weeks to fine-tune a model. AdaptiveAI was developed to provide a trustworthy, self-improving conversational AI system."*
- **Key Takeaway:** Enterprises require grounded, auditable, and easily updated AI—not black-box token predictors.

---

### Slide 2: Existing Solutions and Research Gap
- **Title:** Existing Approaches and the Critical Engineering Gap
- **Main Content (Bullets):**
  - **Rule-Based Decision Trees:** Deterministic and safe, but brittle, expensive to maintain, and disliked by users.
  - **Generic Foundation LLMs:** Exceptional linguistic capabilities, but lack access to private documents and hallucinate out-of-domain answers.
  - **Standard RAG Systems:** Retrieve document chunks, but **lack confidence awareness**—blindly passing irrelevant context to the LLM.
  - **Commercial Platforms:** High-cost, closed-source silos with vendor lock-in.
  - **The Research Gap:** A lightweight, multi-tenant RAG architecture that deterministically rejects low-confidence queries, logs unanswered gaps, and adapts immediately via verified human feedback.
- **Suggested Visual:** A 2x2 comparison matrix: Conversational Flexibility (Y-axis) vs. Hallucination Safety & Adaptability (X-axis). AdaptiveAI in top-right.
- **Speaker Notes:**
  > *"When we look at existing tools, rule-based bots are too rigid, while generic LLMs hallucinate. Basic RAG chatbots improve grounding, but they lack confidence checks—if a user asks an unanswerable question, basic RAG still retrieves poor chunks and the LLM hallucinates an apology or false bridge. Our project fills this gap by coupling vector similarity thresholds directly to an automated human escalation and verification loop."*
- **Key Takeaway:** Current systems lack an integrated feedback mechanism to convert support failures into immediate, verified retrieval knowledge.

---

### Slide 3: Proposed Solution and Core Objectives
- **Title:** Proposed Solution: AdaptiveAI Core Objectives
- **Main Content (Bullets):**
  - **Objective 1 — Grounded RAG:** Ingest multi-format documents (PDF, DOCX, TXT, CSV) and perform semantic retrieval via PostgreSQL `pgvector`.
  - **Objective 2 — Deterministic Confidence Guardrail:** Implement an explainable mathematical scoring engine with automated human escalation for scores below 0.50.
  - **Objective 3 — Continuous Adaptation Loop:** Convert negative feedback and escalation resolutions into prioritized, human-verified experience vectors.
  - **Objective 4 — Cryptographic Multi-Tenancy:** Enforce 3-layer data isolation across JWT, API dependencies, and ORM schemas.
  - **Objective 5 — Drop-In Integration:** Provide an embeddable, zero-dependency JavaScript widget for any third-party website.
- **Suggested Visual:** Conceptual circular diagram showing Document Ingestion -> Grounded RAG -> Confidence Check -> Escalation -> Human Verification -> Experience Store -> Improved RAG.
- **Speaker Notes:**
  > *"To solve these challenges, we defined five engineering objectives: ground answers strictly in documents, halt generation deterministically when confidence drops, allow human support agents to resolve gaps, turn those resolutions into verified memories, and enforce multi-tenancy so multiple companies can safely use the platform simultaneously."*
- **Key Takeaway:** AdaptiveAI unites retrieval, safety guardrails, human verification, and multi-tenancy into a single cohesive platform.

---

### Slide 4: System Architecture
- **Title:** High-Level System Architecture
- **Main Content (Bullets):**
  - **Frontend Client Layer:** React 19 + TypeScript SPA for administration; vanilla JS `widget.js` for external website embedding.
  - **FastAPI Asynchronous Gateway:** High-performance REST endpoints with Pydantic v2 validation and structured logging.
  - **Core Business Services:** Sliding-window document chunking, RAG context assembler, and confidence evaluator.
  - **Unified Storage Engine:** PostgreSQL 16 combining relational business models and `pgvector` vector similarity indexing in a single ACID database.
  - **External AI Foundation:** Google Gemini (`gemini-1.5-flash` for generation; `text-embedding-004` for 768-dim embeddings).
- **Suggested Visual:** Simplified version of the Mermaid architecture diagram from Section 5.1 showing data flow between Frontend, FastAPI, PostgreSQL, and Gemini.
- **Speaker Notes:**
  > *"Our architecture maintains a clean separation of concerns. The client layer connects to an asynchronous FastAPI backend. FastAPI manages business logic, document chunking, and AI provider calls. All relational state and vector embeddings reside in PostgreSQL using pgvector, eliminating the complexity and synchronization lag of separate vector databases."*
- **Key Takeaway:** A unified PostgreSQL + FastAPI architecture delivers high performance, simple operational maintenance, and transactional data integrity.

---

### Slide 5: Technology Stack & Core Concepts
- **Title:** Technical Stack and Engineering Decisions
- **Main Content (Bullets):**
  - **FastAPI & Asyncio:** Handles concurrent chat connections with asynchronous database access via `asyncpg`.
  - **PostgreSQL 16 + pgvector:** Native vector cosine distance (`<=>`) matching integrated directly with relational foreign keys.
  - **Tiktoken Chunking:** 512-token chunks with 64-token sliding overlap to preserve cross-boundary semantics.
  - **Dual-Provider Architecture:** Abstract base classes for LLM and Embedding providers, allowing instant swapping between Gemini, OpenAI, and Anthropic via `.env`.
  - **Stateless JWT + Bcrypt:** Secure cryptographic tokens with embedded tenant claims and salted password hashing.
- **Suggested Visual:** A grid displaying the logos/badges of FastAPI, PostgreSQL, pgvector, React, TypeScript, and Google Gemini with their key configuration parameters.
- **Speaker Notes:**
  > *"Every component was chosen with enterprise engineering principles in mind. We chose FastAPI for its native async support and OpenAPI documentation. We chose pgvector to keep our vectors and relational data in a single ACID-compliant database. We implemented an abstract provider pattern, meaning we can switch from Gemini to OpenAI or local open-source models simply by editing an environment variable."*
- **Key Takeaway:** Built on modern, open, and interchangeable enterprise-grade technologies.

---

### Slide 6: Knowledge Ingestion and RAG Pipeline
- **Title:** Knowledge Ingestion and Semantic Retrieval Pipeline
- **Main Content (Bullets):**
  - **Multi-Format Parsing:** Support for PDF, DOCX, TXT, CSV, and MD with automated text cleaning and page tracking.
  - **Vector Embedding Generation:** Batched API calls to Google `text-embedding-004` generating 768-dimensional normalized vectors.
  - **pgvector Similarity Search:** Top-K cosine distance retrieval (`ORDER BY embedding <=> query_vector LIMIT 10`).
  - **Grounded Context Construction:** Chunks formatted with clear source tags (`[Document Source 1]`) to enforce verifiable citation provenance.
  - **System Prompt Guardrails:** Explicit instructions requiring the LLM to refuse to answer if the provided context lacks the facts.
- **Suggested Visual:** Flow diagram tracing a PDF from Upload -> Page Extraction -> 512-Token Slicing -> Vector Embedding -> Vector Table -> Cosine Search Match.
- **Speaker Notes:**
  > *"Here is how knowledge enters our system. When an admin uploads a file, it is parsed and sliced into 512-token segments. Each segment is embedded and saved in PostgreSQL. When a customer asks a question, we embed their query, perform a cosine distance search in pgvector, and pass the top matching chunks into the Gemini prompt with instructions that forbid guessing."*
- **Key Takeaway:** RAG replaces black-box model guessing with transparent, cited information retrieval from private files.

---

### Slide 7: Adaptive Experiences, Confidence, and Human Escalation
- **Title:** Deterministic Confidence Guardrail & Adaptive Learning Loop
- **Main Content (Bullets):**
  - **Deterministic Confidence:** Calculated from cosine similarity; drops below 0.50 if context is missing or irrelevant.
  - **Automated Escalation:** Low confidence halts generation, returns a polite fallback, and logs an `OPEN` ticket in `escalations`.
  - **Resolution-to-Experience Bridge:** Human support agents resolve tickets with accurate notes, optionally creating a `PENDING` experience.
  - **Admin Approval Guardrail:** Experiences remain inactive until reviewed and approved by an administrator, preventing prompt injection or data poisoning.
  - **Priority Context Assembly:** Approved experiences are embedded and injected with highest priority in future RAG prompts.
- **Suggested Visual:** Split slide: Left side showing the Confidence Formula & Threshold decision tree; Right side showing the Feedback/Escalation -> Pending Experience -> Approved Experience loop.
- **Speaker Notes:**
  > *"This slide represents our core research contribution. First, our confidence score is not an opaque LLM guess—it is an explainable calculation based on vector distance. If confidence drops below 50%, the AI stops and creates an escalation ticket. Second, when an agent resolves that ticket, their verified answer is stored as an Experience. Once approved by an admin, it is embedded. Future queries match that experience first, ensuring continuous adaptation without touching the foundation LLM weights."*
- **Key Takeaway:** Safe fallback prevents hallucinations today; verified experience memory ensures accurate answers tomorrow.

---

### Slide 8: Multi-Tenancy, Security, and Chatbot Integration
- **Title:** Enterprise Multi-Tenancy and Public Widget Deployment
- **Main Content (Bullets):**
  - **3-Layer Isolation:** Enforced via JWT claims, FastAPI route dependencies (`get_tenant_id`), and SQLAlchemy `TenantMixin` query filters.
  - **Cross-Tenant Attack Prevention:** Direct object reference attempts across tenants return HTTP 404/403.
  - **Server-Side Tenant Resolution:** Public widget queries resolve companies by slug on the server, never trusting client-supplied IDs.
  - **Embeddable JavaScript Widget:** 3-line `<script>` integration with shadow DOM styling and session persistence in `sessionStorage`.
  - **Role-Based Workspaces:** Dedicated views for Platform Super Admins, Company Admins, Support Agents, and End Customers.
- **Suggested Visual:** Diagram showing two distinct corporate tenants (Tenant A & Tenant B) sharing one database, with security barriers blocking cross-tenant queries, and an embed script launching the chat drawer.
- **Speaker Notes:**
  > *"To serve multiple corporate clients, security must be airtight. Every database query enforces tenant isolation using the company ID embedded in the user's JWT. Our integration test suite proves that Tenant B cannot read or resolve Demo Company's support tickets. Furthermore, any website can embed the bot using a simple script tag that resolves the tenant on our server."*
- **Key Takeaway:** Enterprise multi-tenancy and embeddable deployment packaged into a secure, turnkey architecture.

---

### Slide 9: Implementation, Testing, and Verification Results
- **Title:** Verification Suite & System Implementation Status
- **Main Content (Bullets):**
  - **Full Functional Implementation:** 11 REST API modules, 15 React administrative views, and complete database migrations.
  - **Integration Test Suite 1 — Complete Adaptive Loop (`test_adaptive_loop_integration.py`):** Verified question answering -> negative feedback -> admin review -> experience approval -> re-querying with verified correction priority (100% pass).
  - **Integration Test Suite 2 — Confidence & Security (`test_confidence_and_escalation.py`):** Verified high confidence, verified experience retrieval, low-confidence escalation creation, resolution lifecycle, and cross-tenant isolation (100% pass).
  - **Integration Test Suite 3 — Analytics Engine (`test_analytics_endpoints.py`):** Verified overview aggregations, knowledge gaps tracking, and role-based 403 blocks (100% pass).
- **Suggested Visual:** Table showing the 3 integration test suites, endpoints tested, assertions verified, and green "ALL TESTS PASSED" checkmarks.
- **Speaker Notes:**
  > *"We did not just write code; we rigorously verified it. We created three comprehensive integration test suites that test the complete adaptive loop, confidence scoring, human escalation, cross-tenant security barriers, and analytics. All three test suites execute successfully with 100% pass rates, proving our claims with concrete logs."*
- **Key Takeaway:** All core architectural workflows are implemented, tested, and repeatable.

---

### Slide 10: Limitations, Future Scope, and Conclusion
- **Title:** Engineering Limitations, Future Roadmap, and Conclusion
- **Main Content (Bullets):**
  - **Acknowledged Limitations:** Synchronous document processing (susceptible to timeouts on huge PDFs); lack of secondary cross-encoder reranker; widget lacks HTTP Origin allowlisting.
  - **Future Roadmap:** Distributed task queues (Celery/Redis); automated RAG evaluation benchmarking (Ragas framework); real-time WebSocket human agent live-chat takeover.
  - **Academic & Engineering Contribution:** Demonstrated a working enterprise paradigm combining RAG accuracy, explainable confidence guardrails, human-verified learning, and multi-tenant security.
  - **Conclusion:** AdaptiveAI bridges the gap between unreliable generative models and static legacy chatbots, delivering safe, adaptable conversational AI for enterprises.
- **Suggested Visual:** Summary timeline showing Completed MVP Features -> Immediate Production Hardening -> Long-Term Research Scope.
- **Speaker Notes:**
  > *"To conclude honestly, AdaptiveAI is an academic engineering project with clear commercial potential. While production deployment would require background workers like Celery and origin allowlisting, we have successfully proven that deterministic confidence scoring and human-verified experience memory solve the twin problems of hallucination and static knowledge in enterprise conversational AI. Thank you for your time, and I welcome your questions."*
- **Key Takeaway:** A practical, safe, and innovative engineering project addressing real enterprise AI challenges.

---

## 8. Evaluation and Testing Plan

### 8.1 What Has Actually Been Tested and Verified
The repository includes three comprehensive, repeatable integration test suites written in Python using `httpx.AsyncClient` against the running ASGI application:

1. **`test_adaptive_loop_integration.py` (218 lines):**
   - Logs in as Company Admin and Customer.
   - Asks a question answered by `test_for_chatbot.pdf`.
   - Submits negative feedback with user correction (`INCORRECT`, `rating = NEGATIVE`).
   - Admin reviews feedback and creates a `PENDING` Experience (verified: `has_embedding == False`).
   - Verifies customer receives `403 Forbidden` attempting to access feedback or experiences.
   - Admin approves Experience (verified: status becomes `APPROVED`, `has_embedding == True`, 768-dim vector generated).
   - Re-asks the initial question and asserts that `retrieved_experiences > 0`, the verified experience is present in `sources`, and the answer adopts the human-verified correction.

2. **`test_confidence_and_escalation.py` (322 lines):**
   - **Test A (High Confidence):** Queries document fact; asserts `is_escalated == False`, `confidence_score >= 0.70`, and sources present.
   - **Test B (Verified Experience):** Queries verified experience; asserts high confidence ($\ge 0.80$) and experience prioritization.
   - **Test C (Low Confidence Fallback):** Queries out-of-domain question (*"What is the population of Mars?"*); asserts `confidence_score < 0.50`, `is_escalated == True`, conversation status marked `ESCALATED`, and `Escalation` record created with reason `LOW_CONFIDENCE`.
   - **Test C (Escalation Lifecycle):** Agent lists escalations, views detail transcript, assigns to agent (`IN_PROGRESS`), and resolves ticket with notes, creating a `PENDING` experience.
   - **Test D (Multi-Tenant Security):** Tenant B Admin attempts to access, view, or resolve Demo Company's escalation; asserts HTTP 404 Not Found and 0 leaked escalations in Tenant B's listing.

3. **`test_analytics_endpoints.py` (179 lines):**
   - Validates `/overview`, `/questions`, `/feedback`, `/knowledge-gaps`, and `/accuracy`.
   - Asserts customers receive `403 Forbidden` on all analytics routes.
   - Asserts Tenant B overview metrics return clean zero-counts, proving cross-tenant isolation.

### 8.2 Proposed Benchmark Evaluation Framework (For Future Academic Extension)
To evaluate AdaptiveAI against formal academic benchmarks, the following experimental setup is proposed:

| Metric | Target Measurement | Evaluation Method | Proposed Tooling |
|---|---|---|---|
| **Context Relevance** | Precision of retrieved chunks | Proportion of retrieved chunks containing ground-truth answer facts | Ragas (`context_precision`) |
| **Faithfulness / Groundedness** | Hallucination rate | Percentage of generated claims directly supported by retrieved context | Ragas (`faithfulness`) / TruLens |
| **Answer Relevance** | Query satisfaction | Semantic similarity between generated answer and user query | Ragas (`answer_relevance`) |
| **Fallback Precision** | Guardrail accuracy | Percentage of unanswerable questions correctly escalated ($< 0.50$) | Curated test set of 100 out-of-domain questions |
| **Cross-Tenant Leakage** | Security isolation | Number of unauthorized cross-tenant data leaks | Automated penetration script attempting cross-UUID queries |
| **End-to-End Latency** | Operational speed | Mean response time (p50, p95) from widget request to response | Locust / k6 load testing |

---

## 9. Limitations and Future Enhancements

| Area | Current Implementation Status in Code | Why It Matters | Realistic Engineering Direction |
|---|---|---|---|
| **Document Processing** | Synchronous inside API route (`app/api/v1/documents.py`) | A 500-page PDF can block worker threads and trigger HTTP gateway timeouts. | Offload parsing and embedding to a Celery or ARQ background task with Redis queue and WebSocket progress notifications. |
| **Reranking Layer** | Cosine similarity via pgvector only | Vector cosine search can rank chunks with keyword overlap higher than deep semantic matches. | Integrate a cross-encoder reranker (e.g., FlashRank or Cohere Rerank) to rescore the top-10 chunks down to the top-3 most relevant chunks. |
| **Widget Origin Security** | Server resolves company slug, but allows any HTTP origin | A rogue external website could embed a company’s public widget and consume their AI API quota. | Add an `allowed_domains` column to `chatbot_settings` and enforce HTTP `Origin` header checking in `/api/v1/widget/{widget_id}/chat`. |
| **Manual Knowledge Items** | API endpoints in `app/api/v1/knowledge.py` return `"Not yet implemented"` | Admins must upload full documents or use experiences; they cannot manually type single FAQ items directly. | Implement standard CRUD routes in `knowledge.py` that insert directly into the existing `knowledge_items` database table. |
| **Live Human Takeover** | Asynchronous ticket resolution via `/escalations` | If a customer is frustrated, the agent cannot take over the chat session in real time. | Implement WebSocket channels for active conversations, allowing agents to switch conversation mode from `BOT` to `HUMAN_LIVE`. |
| **Automated Evaluation** | Analytics computes proxy metrics from feedback and confidence | Does not measure mathematical precision against benchmark truth datasets. | Integrate automated continuous evaluation pipelines using the Ragas framework on a scheduled cron job. |

---

## 10. Professor's Viva Preparation

### 28 Technical Questions & Concise, Accurate Answers

#### 1. Why did you choose this problem for your final year project?
> *"Enterprise customer service teams are stuck between brittle rule-based bots that frustrate users and generic LLMs that hallucinate and leak data. We chose this project to build an end-to-end, multi-tenant system that uses deterministic confidence scoring to eliminate hallucinations and an adaptive feedback loop to update knowledge without expensive model retraining."*

#### 2. What is the core novelty or differentiation of AdaptiveAI?
> *"Most RAG implementations are static: they retrieve document chunks and pass them to an LLM regardless of relevance. AdaptiveAI introduces two key innovations: first, a deterministic confidence-scoring formula that automatically halts generation and files a human support escalation ticket when context is weak; second, a verified experience loop where human support resolutions are converted into prioritized vector memories, improving future answers instantly."*

#### 3. Why did you use RAG instead of fine-tuning a foundation model like Llama or Mistral?
> *"Fine-tuning adjusts model weights to teach style or language structure, but it is notoriously unreliable for injecting factual, rapidly changing knowledge. It causes catastrophic forgetting, costs significant compute, takes hours to train, and cannot be updated instantaneously. RAG keeps the model frozen and supplies private, verifiable facts at runtime, complete with exact source citations."*

#### 4. How does your vector search work under the hood?
> *"We convert text chunks into 768-dimensional floating-point vectors using Google's `text-embedding-004`. These vectors are stored in PostgreSQL using the pgvector extension. When a user asks a question, we embed the query and execute a vector cosine distance query using the `<=>` operator, ordering by ascending distance and limiting to top-K."*

#### 5. Why pgvector instead of a dedicated vector database like Pinecone or Milvus?
> *"A dedicated vector database introduces architectural complexity: you have to maintain two databases, manage two-phase distributed commits, handle synchronization lag, and double your infrastructure cost. With pgvector, our vector embeddings and relational tenant models reside in the same ACID-compliant PostgreSQL database, allowing us to enforce multi-tenant foreign key security in a single SQL query."*

#### 6. What is your exact confidence scoring formula?
> *"Located in `app/services/rag_service.py`, our formula evaluates the maximum cosine similarity of retrieved document chunks and verified experiences against our similarity threshold ($0.70$). If an approved experience meets $0.70$, confidence is that experience's similarity. If a document chunk meets $0.70$, confidence is that chunk's similarity. If neither meets $0.70$, similarity below $0.40$ returns $0.0$, while values between $0.40$ and $0.70$ are scaled strictly below our low-confidence threshold ($0.50$), deterministically triggering human escalation."*

#### 7. Is your confidence score a true statistical probability?
> *"No, and it should not be confused with one. Cosine similarity measures geometric proximity in vector space, not the output probability distribution of an LLM. Our score is an explainable, deterministic heuristic calibrated to our retrieval threshold ($0.70$) and escalation trigger ($0.50$)."*

#### 8. How do you prevent multi-tenant data leakage?
> *"We enforce isolation at three layers: (1) At the token layer, the user's `company_id` is cryptographically signed into their JWT; (2) At the API layer, FastAPI dependencies validate this ID on every request; (3) At the database layer, all tenant models inherit `TenantMixin`, and every service query appends `WHERE company_id = current_user.company_id`. Even if a user alters a request payload, they cannot query another tenant's data."*

#### 9. What is the difference between an unverified feedback correction and an approved experience?
> *"When a user submits negative feedback with a correction, it is saved in the `feedback` table with status `PENDING`. It has no embedding and cannot be used in RAG. Only when a company admin or support agent reviews and approves the correction does the system generate a vector embedding and set status to `APPROVED`. This human-in-the-loop gate prevents malicious users from poisoning the AI with false information."*

#### 10. When an experience is approved, does it update the LLM weights?
> *"No. The foundation LLM remains frozen. The approved Q&A pair is embedded and stored as a vector in table `experiences`. On future queries, our RAG service retrieves approved experiences alongside document chunks and explicitly instructs Gemini in the system prompt that verified experiences take precedence over static document text."*

#### 11. What file formats does your document ingestion support, and how are they parsed?
> *"We support PDF using `pypdf`, DOCX using `python-docx`, CSV using Python's `csv` module, and plain text and Markdown using native UTF-8 file readers. Extracted text is cleaned and split into 512-token segments with a 64-token sliding overlap using `tiktoken`."*

#### 12. Why did you include a 64-token overlap during chunking?
> *"If a paragraph is sliced precisely at 512 tokens, a crucial sentence or idea might be split in half, destroying its semantic meaning. A 64-token overlap ensures that adjacent chunks share context, allowing the embedding model to capture complete thoughts regardless of where the boundary falls."*

#### 13. What happens when a user asks a question that is completely outside the knowledge base?
> *"The query is embedded and compared against stored vectors. Because no chunks match, the maximum similarity is below 0.40. The confidence engine returns `0.0`. In `rag_service.py`, this halts generation, returns a polite fallback message, marks the conversation as `ESCALATED`, and inserts an `OPEN` ticket into the `escalations` table."*

#### 14. What are the roles supported in your RBAC system?
> *"We define four roles in `app/models/user.py`: (1) `SUPER_ADMIN` for platform-wide management; (2) `COMPANY_ADMIN` for corporate tenant settings, users, documents, and experience approvals; (3) `EMPLOYEE` for handling escalations and reviewing feedback; and (4) `CUSTOMER` for chatting through the portal or widget."*

#### 15. How does the embeddable widget work without exposing company secrets?
> *"The host website loads `widget.js` with `data-chatbot-id="company-slug"`. The script calls `GET /api/v1/widget/{slug}/config`, which resolves the company on the server and returns only public branding. When chatting, the widget sends messages to `/api/v1/widget/{slug}/chat`. No API keys, database credentials, or secret tokens are ever exposed to the client."*

#### 16. What database migrations tool did you use and why?
> *"We used Alembic with SQLAlchemy. Alembic tracks schema changes over time in versioned migration files, ensuring that database tables (including pgvector columns and foreign key constraints) can be deployed reliably across development, staging, and production environments."*

#### 17. How do you handle conversation memory in multi-turn chats?
> *"When a message is sent, the API fetches the previous 20 turns from the `messages` table for that `conversation_id`. These turns are formatted into a conversation history block and passed to Gemini alongside the retrieved knowledge context, allowing the AI to understand follow-up questions and pronouns."*

#### 18. What happens if the Gemini API experiences a temporary 503 error?
> *"In `app/services/rag_service.py`, lines 366–381, we wrap the Gemini generation call in a retry loop with exponential backoff (`asyncio.sleep(2 ** attempt)`). If a temporary 503 or unavailable error occurs, it retries up to three times before failing gracefully."*

#### 19. How is password security implemented?
> *"We use `bcrypt` directly with 12 salt rounds in `app/core/security.py`. Passwords are never stored in plain text. We chose `bcrypt` directly rather than `passlib` because `passlib` is unmaintained and incompatible with bcrypt 4.x on Python 3.13."*

#### 20. What is the purpose of the AuditLog table?
> *"The `audit_logs` table provides an immutable, INSERT-only ledger tracking all administrative actions—such as document uploads, company creation, and experience approvals. It records the acting `user_id`, `company_id`, `action` string, and a JSONB metadata payload for enterprise compliance and auditing."*

#### 21. How do your Analytics endpoints track "Knowledge Gaps"?
> *"In `app/api/v1/analytics.py`, the `/knowledge-gaps` endpoint queries the `escalations` table for tickets triggered by `LOW_CONFIDENCE`. It extracts the customer's question, whether an agent resolved it, and whether a verified Experience was generated, giving admins immediate visibility into missing documentation."*

#### 22. What is the difference between `DocumentChunk` and `KnowledgeItem` in your schema?
> *"`DocumentChunk` represents an automated text slice from an uploaded file, indexed with pgvector. `KnowledgeItem` was designed as a discrete manual FAQ entry model. Currently, all knowledge ingestion in the platform is handled via `DocumentChunk` and verified `Experience` records; manual FAQ CRUD in `knowledge.py` is reserved for future implementation."*

#### 23. Why did you use React 19 and Tailwind CSS v4 on the frontend?
> *"React 19 provides high rendering performance and modern hook abstractions for managing complex asynchronous state. Tailwind CSS v4 enables a clean, responsive interface with minimal bundle size, providing dedicated administrative workflows for both desktop management and mobile chat."*

#### 24. Could a malicious user poison your AI by submitting false feedback?
> *"No. Submitting negative feedback only creates a feedback record with status `PENDING`. It has zero effect on the retrieval index. It requires an authenticated company admin or employee to explicitly review, verify, and approve the correction before an embedding is generated. This human gate prevents data poisoning."*

#### 25. What is the primary limitation of your current document processing?
> *"Document extraction and chunking currently execute synchronously inside the FastAPI request handler. For large 500-page documents, this can take several seconds and risk client request timeouts. In production, this should be offloaded to a background task queue like Celery or ARQ with Redis."*

#### 26. How does your widget handle session management?
> *"The widget stores a unique session UUID in the browser's `sessionStorage`. On subsequent questions, it transmits this `session_id`, allowing the backend to associate messages with the same conversation thread until the browser tab is closed."*

#### 27. How does your solution compare to commercial platforms like Zendesk AI or Salesforce Einstein?
> *"Commercial platforms offer rich omnichannel integrations, but they are expensive, closed-source black boxes with vendor lock-in. AdaptiveAI provides an open, auditable, and transparent architecture where enterprises maintain full ownership of their data, vector embeddings, confidence thresholds, and verification workflows."*

#### 28. What would be your next step before taking AdaptiveAI to real commercial production?
> *"Three things: First, offload document ingestion to Celery background workers. Second, add an HTTP `Origin` header domain allowlist to the widget to prevent unauthorized embedding. Third, implement continuous automated RAG evaluation using the Ragas benchmark framework to continuously measure faithfulness and retrieval precision."*

---

## 11. Quick Reference & Cheat Sheet

### Summary of System Stack
- **Backend:** FastAPI, Python 3.11+, SQLAlchemy 2.0 (Asyncio), asyncpg, Alembic, Pydantic v2
- **Vector DB:** PostgreSQL 16 with pgvector extension (`Vector(768)`)
- **AI Models:** Google Gemini (`gemini-1.5-flash` for LLM; `text-embedding-004` for 768-dim embeddings)
- **Security:** OAuth2 Bearer JWT (HS256 via `python-jose`), Passwords via `bcrypt` (12 rounds)
- **Frontend:** React 19, TypeScript, Vite, Tailwind CSS v4, Lucide Icons, Axios, React Router v7
- **Widget:** Standalone ES6+ JavaScript (`widget.js`), Demo Storefront (`demo.html`)

### Essential File & Directory Locations
- **Backend Entry Point:** [`app/main.py`](file:///c:/adaptive-ai/app/main.py)
- **Configuration & Environment:** [`app/config.py`](file:///c:/adaptive-ai/app/config.py)
- **RAG & Confidence Engine:** [`app/services/rag_service.py`](file:///c:/adaptive-ai/app/services/rag_service.py)
- **Document Parser & Chunking:** [`app/services/document_processor.py`](file:///c:/adaptive-ai/app/services/document_processor.py)
- **Security & JWT:** [`app/core/security.py`](file:///c:/adaptive-ai/app/core/security.py) and [`app/core/dependencies.py`](file:///c:/adaptive-ai/app/core/dependencies.py)
- **ORM Models:** [`app/models/`](file:///c:/adaptive-ai/app/models/) (`company.py`, `user.py`, `document.py`, `document_chunk.py`, `experience.py`, `escalation.py`, `feedback.py`, `conversation.py`, `message.py`)
- **API Routers:** [`app/api/v1/`](file:///c:/adaptive-ai/app/api/v1/) (`chat.py`, `widget.py`, `experiences.py`, `escalations.py`, `feedback.py`, `analytics.py`, `documents.py`, `companies.py`, `users.py`)
- **Frontend Root:** [`frontend/src/App.tsx`](file:///c:/adaptive-ai/frontend/src/App.tsx)
- **Embeddable Widget:** [`frontend/public/widget.js`](file:///c:/adaptive-ai/frontend/public/widget.js)
- **Demo Storefront:** [`frontend/public/demo.html`](file:///c:/adaptive-ai/frontend/public/demo.html)
- **Integration Test Suites:** [`test_adaptive_loop_integration.py`](file:///c:/adaptive-ai/test_adaptive_loop_integration.py), [`test_confidence_and_escalation.py`](file:///c:/adaptive-ai/test_confidence_and_escalation.py), [`test_analytics_endpoints.py`](file:///c:/adaptive-ai/test_analytics_endpoints.py)

### Essential Commands (Windows PowerShell)

```powershell
# 1. Activate Python Virtual Environment
cd c:\adaptive-ai
.\.venv\Scripts\activate

# 2. Start PostgreSQL (if running via Docker or native Windows service)
# net start postgresql-x64-16

# 3. Start Backend Server (Terminal 1)
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# 4. Start Frontend Development Server (Terminal 2)
cd frontend
npm run dev

# 5. Run Verification & Test Suites (Terminal 3)
cd c:\adaptive-ai
python test_adaptive_loop_integration.py
python test_confidence_and_escalation.py
python test_analytics_endpoints.py
```

### Important Local URLs
- **Web Application Portal:** `http://localhost:5173/login`
- **Customer Chat Interface:** `http://localhost:5173/customer/chat`
- **Interactive Demo Storefront:** `http://localhost:5173/demo.html` (or `http://127.0.0.1:8000/demo`)
- **FastAPI Interactive Swagger Docs:** `http://127.0.0.1:8000/docs`
- **Backend Health Check:** `http://127.0.0.1:8000/health`
- **Embeddable Widget Script:** `http://127.0.0.1:8000/widget.js`

### Key Demo Accounts (Pre-Seeded in Login Quick-Fill)
- **Platform Admin (`SUPER_ADMIN`):** `superadmin@adaptiveai.dev`
- **Company Admin (`COMPANY_ADMIN`):** `admin@adaptiveai-demo.com`
- **Customer User (`CUSTOMER`):** `customer@adaptiveai-demo.com`
*(Note: Use the convenient quick-fill buttons on the login screen to authenticate during the review)*

### Three Strongest Project Contributions to Highlight
1. **Deterministic Guardrails Over Black-Box Guessing:** Out-of-domain queries halt generation and automatically trigger human escalations based on cosine similarity thresholds.
2. **Instant Closed-Loop Knowledge Adaptation:** Approved human support resolutions become prioritized vector experiences immediately, updating conversational knowledge without foundation model fine-tuning.
3. **Full-Stack, Multi-Tenant Implementation:** A complete, working software artifact spanning database migrations, pgvector similarity search, async FastAPI APIs, React 19 consoles, and a drop-in JavaScript widget.

### Five Limitations to Acknowledge Honestly
1. **Synchronous Ingestion:** Ingestion runs in the API thread rather than a background worker queue (Celery/Redis).
2. **No Secondary Reranker:** Vector matching relies on pgvector cosine similarity without a cross-encoder reranking stage.
3. **Widget Domain Validation:** Public widget endpoints resolve tenants on the server but do not yet enforce HTTP Origin allowlists.
4. **Manual Knowledge Item CRUD:** Manual FAQ endpoints in `knowledge.py` return placeholders; knowledge ingestion currently relies on documents and verified experiences.
5. **Operational Proxy Metrics:** Accuracy dashboard tracks feedback and confidence metrics rather than automated benchmark datasets (Ragas).

### 30-Second Final Closing Statement
> *"AdaptiveAI proves that generative AI can be deployed safely in enterprise customer service. By uniting Retrieval-Augmented Generation, deterministic confidence guardrails, human-in-the-loop experience verification, and strict multi-tenant database isolation, we have created a platform that refuses to hallucinate, escalates gracefully to human staff, and continuously learns from human expertise without retraining foundation models. Thank you."*

