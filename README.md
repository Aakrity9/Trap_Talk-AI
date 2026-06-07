# TrapTalk AI 🛡️🤖
> **Autonomous Agentic Honeypot Framework for Real-Time Scam Elicitation & Financial Intelligence Gathering.**

[![Framework - FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Frontend - Next.js](https://img.shields.io/badge/Frontend-Next.js_15-000000?style=for-the-badge&logo=nextdotjs&logoColor=white)](https://nextjs.org/)
[![Deployment - Vercel](https://img.shields.io/badge/Deploy-Vercel-000000?style=for-the-badge&logo=vercel&logoColor=white)](https://vercel.com/)
[![Deployment - Railway](https://img.shields.io/badge/Deploy-Railway-130f40?style=for-the-badge&logo=railway&logoColor=white)](https://railway.app/)

---

## 🌐 Live Deployments
* **⚡ Production Web Console (Frontend):** [https://trap-talk-ai.vercel.app](https://trap-talk-ai.vercel.app)
* **🔌 Dynamic Core Routing Engine (Backend):** [https://trap-talk-ai-production.up.railway.app](https://trap-talk-ai-production.up.railway.app)

---

## 🛑 The Core Problem
Traditional anti-scam tools are strictly reactive—they block fraudulent numbers or phishing URLs **after** the financial damage has already occurred. This leaves a critical visibility gap: law enforcement and fraud intelligence cells cannot actively track illicit financial endpoints (like disposable UPI IDs, mule bank accounts, or short-lived phishing redirection layers) because scammers rotate them rapidly.

## ⚡ The Tactical Solution: TrapTalk AI
**TrapTalk AI (powered by SANKATE_OS)** turns the tables on malicious threat actors. It functions as an automated cognitive honeypot application:
1. **Instant Mobilization:** Users can seamlessly capture incoming scam vectors (SMS, WhatsApp text) through a mobile **Progressive Web App (PWA) Share Target**.
2. **Autonomous Interaction:** Once triggered, the backend orchestrates conversational AI agents running highly believable fallback personas (e.g., *Ramesh - a vulnerable citizen*).
3. **Intelligence Elicitation:** The agent engages the scammer in deep, multi-turn dialogue to bait out and extract actionable malicious infrastructure elements in real-time.

---

## 🏗️ System Architecture & Data Pipeline

```text
  [ Scammer Text ]
         │
         ▼  (Native Long-Press Share)
   ┌───────────┐
   │ PWA App   │  (Standalone Mobile Interface Client)
   └─────┬─────┘
         │
         ▼  (Secure HTTPS Gateway payload)
   ┌───────────┐
   │ Vercel    │  (Next.js Web Console UI Server)
   └─────┬─────┘
         │
         ▼  (Asynchronous Request Pipeline - x-api-key)
   ┌───────────┐
   │ Railway   │  (FastAPI Architectural Core Engine)
   └─────┬─────┘
         │
         ├─► [ OODA Orchestrator Loop ] ──► Heuristic Risk Scoring (0-100)
         ├─► [ LLM Persona Router ] ───► Generates Believable Traps
         ▼
   ┌───────────┐
   │ Supabase  │  (PostgreSQL Session State Tracking Registry)
   └───────────┘
```

---

## ✨ Key Technical Highlights

* **📱 Mobile Share Target Integration:** Fully integrated Web Manifest with native share sheets. Android users can forward raw scam texts straight into the security matrix with zero manual typing.
* **🌀 Advanced OODA Loop Pipeline:** Features a state-controlled Orchestrator that cyles through **Observe -> Orient -> Decide -> Act** patterns for evaluating incoming threats.
* **🛡️ Hardened Security Architecture:** Cross-origin requests (CORS) are tightly governed, and all server communications require mandatory header verification via cryptographically structured `x-api-key` validation tokens.
* **📈 Dynamic Threat Assessment:** Incorporates analytical Pydantic schemas to dynamically parse metadata structures and isolate illicit network elements under an isolated sandbox session.

---

## 🤖 How GitHub Copilot Assisted the Build
This production-grade deployment was built and optimized with the predictive intelligence of **GitHub Copilot**:
* **JSON Schema Generation:** Copilot accelerated the implementation of the intricate PWA `manifest.json` Share Target specifications, ensuring perfect operating system compatibility.
* **TypeScript Prerender Fixes:** Guided the deployment debugging by wrapping server-reliant navigation utilities inside strict Next.js `<Suspense>` boundaries to completely clear hydration/prerender build limits.
* **FastAPI Micro-routes:** Code completion accurately anticipated data validation loops for processing Pydantic state machines and multi-turn session records smoothly.

---

## 🛠️ Installation & Local Development

### Prerequisites
* Python 3.10+
* Node.js 18+

### 1. Backend Configuration
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
### 2. Frontend Configuration

Run the following commands in your terminal to install dependencies and spin up the local development server:

```bash
cd frontend
npm install
npm run dev
```

Create a .env.local file in the frontend root directory and add the local API pointer:

```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```
