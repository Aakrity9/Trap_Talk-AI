# Product Requirements Document (PRD): TrapTalk AI

## Product Overview
TrapTalk AI is an API-first agentic scam honeypot platform designed to detect scam intent, autonomously engage scammers through a believable human-like persona, and extract structured fraud intelligence from multi-turn conversations.[cite:1] The product is based on the original hackathon problem statement, which requires a public REST API that accepts incoming message events, detects fraud, activates an AI agent, continues the conversation, extracts intelligence, and returns structured JSON responses secured by an API key.[cite:1]

## Problem Statement
Online scams such as bank fraud, UPI fraud, phishing, and fake offers are increasingly adaptive, which makes static detection systems less effective.[cite:1] The challenge requires a system that does more than classify messages as suspicious; it must actively interact with scammers, preserve a believable persona, and gather actionable intelligence without exposing that the system has detected fraud.[cite:1]

## Vision
TrapTalk AI aims to become a defensive conversation layer for anti-fraud systems, helping teams automatically analyze suspicious outreach, waste scammer effort, and produce usable intelligence for fraud analysis.[cite:1] In the hackathon scope, the product will serve as a deployable AI-driven honeypot API with a visible demo flow and a clear intelligence extraction pipeline.[cite:1]

## Goals
### Primary Goals
- Detect scam or fraudulent messages accurately across conversation turns.[cite:1]
- Activate an autonomous AI agent only when scam intent is detected.[cite:1]
- Maintain a believable human-like persona during engagement.[cite:1]
- Extract actionable intelligence from the conversation in structured form.[cite:1]
- Return stable JSON responses through a secured public REST API.[cite:1]

### Secondary Goals
- Produce a session-level fraud report for demo and product use.[cite:1]
- Support channel-aware simulation using metadata such as SMS, WhatsApp, Email, and Chat.[cite:1]
- Demonstrate safe and ethical behavior through constrained agent responses.[cite:1]

## Success Criteria
The original evaluation focuses on scam detection accuracy, quality of agentic engagement, intelligence extraction, API stability and response time, and ethical behavior.[cite:1] Accordingly, TrapTalk AI will be considered successful if it reliably detects scam patterns, sustains convincing multi-turn engagement, extracts high-value intelligence fields, and responds with low-latency structured output under valid authenticated requests.[cite:1]

## Target Users
### Primary Users
- Fraud detection teams
- Cybersecurity researchers
- Fintech or banking security teams
- Messaging safety platforms
- Hackathon judges evaluating the system

### Secondary Users
- Developers integrating a fraud-intelligence API
- Product teams building anti-scam workflows
- End-user safety tools that need automated scam conversation handling

## User Problem
Users need a system that can analyze suspicious incoming messages, continue the conversation without exposing detection, and generate useful structured intelligence rather than merely flagging a scam attempt.[cite:1] Existing manual review flows are slow, and traditional rule-based filters do not adapt well when scammers change tactics dynamically during conversation.[cite:1]

## Product Strategy
TrapTalk AI will combine three layers: scam intent detection, persona-driven agentic conversation, and structured intelligence extraction.[cite:1] The strongest product differentiation will come from transforming a passive scam classifier into an active anti-scam intelligence engine that can operate across multiple turns within the same session.[cite:1]

## Core Use Cases
### Use Case 1: Initial Suspicious Message
A suspected scammer sends the first message in a conversation, with an empty `conversationHistory` array and session metadata.[cite:1] The system validates the request, checks for scam intent, and if the risk is sufficient, generates a natural reply that encourages the scammer to reveal more details.[cite:1]

### Use Case 2: Follow-Up Conversation Handling
The same session continues with additional messages, and prior turns are provided in `conversationHistory`.[cite:1] The agent uses this context to adapt its next reply, preserve consistency, and continue extracting entities such as UPI IDs, phishing links, or phone numbers.[cite:1]

### Use Case 3: Final Intelligence Reporting
Once scam intent is confirmed and sufficient engagement has happened, the system produces a structured session result including `sessionId`, `scamDetected`, `totalMessagesExchanged`, extracted intelligence fields, and `agentNotes`.[cite:1] The original hackathon specification requires this final extracted intelligence to be sent to the GUVI callback endpoint after the engagement is complete.[cite:1]

## Functional Requirements
### 1. Authentication
- The API must validate an `x-api-key` header for every request.[cite:1]
- Requests without a valid API key must be rejected.[cite:1]

### 2. Request Handling
- The system must accept one incoming message event per API request.[cite:1]
- Each request must include `sessionId` and a `message` object with `sender`, `text`, and `timestamp`.[cite:1]
- `conversationHistory` must support empty arrays for first-message scenarios and prior turns for follow-up scenarios.[cite:1]
- `metadata` should support `channel`, `language`, and `locale` fields.[cite:1]

### 3. Scam Detection
- The system must analyze the latest message and relevant conversation history for scam intent.[cite:1]
- The system should classify the session into an internal scam category such as bank threat, UPI fraud, phishing, or fake offer, based on the scam types described in the problem statement.[cite:1]
- The system should generate an internal risk score to decide whether the agent should be activated.[cite:1]

### 4. Agent Activation
- If scam intent is detected, the system must activate an AI agent.[cite:1]
- The AI agent must maintain a believable human-like persona.[cite:1]
- The agent must support multi-turn conversations and adapt dynamically to new scammer messages.[cite:1]
- The agent must avoid revealing that the system has detected scam behavior.[cite:1]
- The agent must perform self-correction when required.[cite:1]

### 5. Response Format
- The API must return a structured JSON response.[cite:1]
- A minimum successful response should follow the shape `{ "status": "success", "reply": "..." }`, consistent with the sample in the problem statement.[cite:1]
- Error responses should return a structured object such as `{ "status": "error", "message": "..." }`.[cite:1]

### 6. Intelligence Extraction
- The system must extract actionable scam intelligence from the conversation.[cite:1]
- The extracted intelligence model must support at least these fields: `bankAccounts`, `upiIds`, `phishingLinks`, `phoneNumbers`, `suspiciousKeywords`, and `agentNotes`.[cite:1]
- The system should update extracted entities incrementally across turns in the same session.[cite:1]

### 7. Session Management
- The product must preserve session continuity using `sessionId`.[cite:1]
- The system must count total messages exchanged in the conversation.[cite:1]
- The system should maintain conversation state even when requests arrive one message at a time.[cite:1]

### 8. Final Callback Compatibility
- The system must be capable of constructing the final callback payload specified in the original challenge.[cite:1]
- The payload must include `sessionId`, `scamDetected`, `totalMessagesExchanged`, `extractedIntelligence`, and `agentNotes`.[cite:1]
- The callback should be triggered only after scam intent is confirmed, engagement is sufficient, and intelligence extraction is complete.[cite:1]

## Non-Functional Requirements
- The API must be reliable and respond quickly under repeated evaluation requests, because API stability and response time are part of the judging criteria.[cite:1]
- The product must be secure at the request layer through API-key validation.[cite:1]
- The system must produce stable JSON formats so evaluators and downstream tools can parse responses consistently.[cite:1]
- The agent behavior must remain safe, controlled, and ethically bounded across all supported scenarios.[cite:1]
- Logs should support debugging of session flow, extracted entities, and callback/report generation states.

## User Stories
- As an evaluator, I want to send a suspected scam message to a public endpoint so that I can test whether the system detects scam intent correctly.[cite:1]
- As an evaluator, I want the system to continue a believable multi-turn conversation so that I can assess the quality of agentic engagement.[cite:1]
- As an evaluator, I want the system to extract structured intelligence from the conversation so that I can measure the usefulness of the honeypot.[cite:1]
- As a fraud analyst, I want a summary of scammer tactics and extracted entities so that I can review the threat quickly.
- As a developer, I want a stable JSON contract so that I can integrate the system into a broader anti-fraud workflow.[cite:1]

## Product Architecture
### Module 1: API Gateway
Responsible for receiving incoming requests, validating headers, validating schema, and routing the request into the core pipeline.[cite:1]

### Module 2: Scam Intent Engine
Scores each incoming message and conversation context for fraud likelihood, assigns internal categories, and determines whether the AI agent should be activated.[cite:1]

### Module 3: Persona Agent Engine
Generates human-like responses, preserves conversational consistency, avoids exposing scam detection, and steers the scammer toward revealing actionable information.[cite:1]

### Module 4: Intelligence Extraction Engine
Extracts structured entities and tactics from the combined conversation transcript, including phone numbers, UPI IDs, suspicious keywords, phishing links, and notes.[cite:1]

### Module 5: Session Store
Stores message history, session metadata, risk level, extracted intelligence, and completion state for each session.[cite:1]

### Module 6: Final Report / Callback Layer
Builds the final structured result and supports compatibility with the original GUVI callback lifecycle described in the problem statement.[cite:1]

## Data Model
### Session Object
| Field | Type | Description |
|---|---|---|
| sessionId | string | Unique session identifier from the platform.[cite:1] |
| scamDetected | boolean | Whether scam intent was confirmed.[cite:1] |
| riskScore | number | Internal risk score for orchestration. |
| scamCategory | string | Internal classification such as phishing or UPI fraud. |
| totalMessagesExchanged | integer | Number of exchanged messages in the session.[cite:1] |
| status | string | Session state such as active, completed, or escalated. |
| metadata | object | Channel, language, and locale context.[cite:1] |

### Intelligence Object
| Field | Type | Description |
|---|---|---|
| bankAccounts | array | Bank account identifiers extracted from the scammer conversation.[cite:1] |
| upiIds | array | UPI IDs extracted from the conversation.[cite:1] |
| phishingLinks | array | Links shared during the scam flow.[cite:1] |
| phoneNumbers | array | Phone numbers referenced during the scam flow.[cite:1] |
| suspiciousKeywords | array | Scam phrases such as urgency or account-block language.[cite:1] |
| agentNotes | string | Summary of scammer behavior and tactics.[cite:1] |

## API Contract
### Request Example
```json
{
  "sessionId": "wertyu-dfghj-ertyui",
  "message": {
    "sender": "scammer",
    "text": "Your bank account will be blocked today. Verify immediately.",
    "timestamp": 1770005528731
  },
  "conversationHistory": [],
  "metadata": {
    "channel": "SMS",
    "language": "English",
    "locale": "IN"
  }
}
```
This request structure follows the sample initial-message format provided in the problem statement.[cite:1]

### Success Response Example
```json
{
  "status": "success",
  "reply": "Why is my account being suspended?"
}
```
This response structure matches the sample agent output required by the challenge.[cite:1]

### Final Callback Payload Example
```json
{
  "sessionId": "abc123-session-id",
  "scamDetected": true,
  "totalMessagesExchanged": 18,
  "extractedIntelligence": {
    "bankAccounts": ["XXXX-XXXX-XXXX"],
    "upiIds": ["scammer@upi"],
    "phishingLinks": ["http://malicious-link.example"],
    "phoneNumbers": ["+91XXXXXXXXXX"],
    "suspiciousKeywords": ["urgent", "verify now", "account blocked"]
  },
  "agentNotes": "Scammer used urgency tactics and payment redirection"
}
```
This payload is based directly on the mandatory final result callback specification in the challenge brief.[cite:1]

## AI Behavior Requirements
- The persona must feel like a real ordinary user rather than a security bot.[cite:1]
- The agent must ask concise, natural follow-up questions.[cite:1]
- The agent must aim to reveal payment methods, identities claimed by the scammer, contact numbers, links, and urgency patterns.[cite:1]
- The agent must not impersonate real individuals, provide illegal instructions, or harass the scammer, in line with the ethics constraints.[cite:1]
- The system should avoid overlong answers and preserve human conversational realism.

## UX and Demo Requirements
Although the original challenge is API-focused, the product version should include a simple demo interface to make the system understandable during evaluation. The demo should show the incoming scam message, generated agent reply, risk score, extracted intelligence, and session summary in real time.[cite:1]

## MVP Scope
### In Scope
- One production-ready honeypot API endpoint
- API-key authentication
- Multi-turn session handling
- Scam detection engine
- Human-like agent reply generation
- Structured intelligence extraction
- Final session reporting
- Demo conversation simulator

### Out of Scope for MVP
- Voice channel support
- Real-time messaging integrations with telecom providers
- Full analyst dashboard with role-based access control
- Large-scale threat intelligence clustering across multiple sessions

## Risks and Mitigations
| Risk | Impact | Mitigation |
|---|---|---|
| Agent sounds robotic | Weak engagement quality | Use short persona-controlled prompts and response constraints. |
| Scam detection is too sensitive or too weak | False positives or weak agent activation | Combine rules, context scoring, and iterative testing. |
| Session continuity breaks | Poor multi-turn quality | Store normalized session state by `sessionId`.[cite:1] |
| Extracted intelligence is incomplete | Weak scoring on intelligence quality | Use regex plus summarization-based extraction. |
| Callback endpoint is unavailable | Original evaluation path breaks | Keep callback compatibility but also surface a local final report mode. |

## Milestones
### Phase 1: Foundation
- Finalize API schema
- Set up authentication
- Implement message validation
- Create session model

### Phase 2: Intelligence Core
- Implement scam intent scoring
- Build persona response engine
- Add entity extraction for links, phone numbers, UPI IDs, and suspicious phrases

### Phase 3: Productization
- Add reporting layer
- Build demo UI
- Add test scenarios and logs
- Prepare documentation and submission assets

## Acceptance Criteria
- Valid authenticated requests produce structured success responses.[cite:1]
- Invalid API-key requests are rejected.[cite:1]
- The system supports both first-message and follow-up message flows using `conversationHistory`.[cite:1]
- The AI agent produces natural replies without exposing detection.[cite:1]
- The system extracts structured intelligence fields from multi-turn conversations.[cite:1]
- The final session report includes all required intelligence fields and notes.[cite:1]
- The system complies with ethical constraints against impersonation, illegal instructions, and harassment.[cite:1]

## Future Scope
- Add multilingual scam handling
- Support persona variations by region or age group
- Add analytics across scam campaigns
- Add institution claim verification
- Add threat clustering and scammer fingerprinting

## One-Sentence Product Summary
TrapTalk AI is an API-first agentic honeypot that detects scam intent, autonomously engages scammers through a believable persona, extracts structured fraud intelligence from multi-turn conversations, and produces actionable anti-scam reports without exposing detection.[cite:1]
