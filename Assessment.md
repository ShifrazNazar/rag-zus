# Mindhive Assessment

This technical assessment is for **Mindhive’s AI Software Engineer** role. You have **7 days** to complete all parts, demonstrating your ability to design multi-turn conversations, implement agentic planning, integrate external tools and custom APIs, handle unhappy flows, and build RAG pipelines.

## Expected Key Points

- State management & memory (tracking slots/variables across turns)
- Planner/controller logic (intent parsing, action selection, follow-up questions)
- Chat interface (front-end UI to interact with the chatbot)
- Tool integration (calling a calculator API, error handling)
- Custom API consumption & testing (FastAPI endpoints for restaurants, product KB, outlets)
- Retrieval-Augmented Generation (vector store + Text2SQL for domain data)
- Robustness (graceful degradation on missing input, downtime, or malicious payloads)

---

## Part 1: Sequential Conversation

**Objective:** Keep track of at least three related turns.

**Code-first option:** Use LangChain or any Python-based framework to implement memory or state.

### Example Flow

1. **User:** “Is there an outlet in Petaling Jaya?”
2. **Bot:** “Yes! Which outlet are you referring to?”
3. **User:** “SS 2, what’s the opening time?”
4. **Bot:** “Ah yes, the SS 2 outlet opens at 9:00 AM.”

### Deliverables

- Exported flow or framework project
- Automated tests for both happy and interrupted paths

---

## Part 2: Agentic Planning

**Objective:** Show how the bot decides its next action (ask, call a tool, or finish).

Implement a simple planner/controller loop that:

1. Parses intent and missing information
2. Chooses an action (ask follow-up, invoke calculator, call RAG/Text2SQL endpoint)
3. Executes the action and returns the result

### Deliverables

- Planner/controller code
- Short write-up of decision points

---

## Part 3: Tool Calling

**Objective:** Integrate a Calculator Tool for simple arithmetic.
Agents must detect arithmetic intent, invoke the calculator endpoint, parse responses, and handle errors gracefully.

### Deliverables

- Calculator API integration code or definition
- Example transcripts showing successful calculations and graceful failure handling

---

## Part 4: Custom API & RAG Integration

**Objective:** Build and consume FastAPI endpoints for domain data and test them as external APIs.

### 1. Product-KB Retrieval Endpoint

- Ingest ZUS product docs into a vector store (FAISS, Pinecone, etc.)

  - **Source:** [https://shop.zuscoffee.com/](https://shop.zuscoffee.com/) → _Drinkware only_

- Expose:

  ```
  /products?query=<user_question>
  ```

  Returns top-k retrieval + AI-generated summary.

### 2. Outlets Text2SQL Endpoint

- Maintain SQL DB of ZUS outlets (location, hours, services)

  - **Source:** [https://zuscoffee.com/category/store/kuala-lumpur-selangor/](https://zuscoffee.com/category/store/kuala-lumpur-selangor/)

- Expose:

  ```
  /outlets?query=<nl_query>
  ```

  Translate NL → SQL, execute, return results.

### Deliverables

- FastAPI repo with OpenAPI spec for `/products` and `/outlets`
- Vector-store ingestion scripts + retrieval code
- Text2SQL prompts/pipeline + DB schema and executor
- Chatbot integration demonstrating calls to all three endpoints
- Example transcripts showing success and failure cases

---

## Part 5: Unhappy Flows

**Objective:** Ensure robustness against invalid or malicious inputs.
Test at least three cases across your integrations:

- Missing parameters (e.g., “Calculate” with no operands)
- API downtime (simulate HTTP 500)
- Malicious payloads (e.g., SQL injection attempts in `/outlets`)

Bot must respond with clear error messages, recovery prompts, and never crash.

### Deliverables

- Test suite covering these scenarios
- Summary of your error-handling and security strategy

---

## Part 6: Frontend Chat UI (No Streamlit/Gradio)

**Objective:** Ship a chat interface that runs Parts 1–5 end-to-end.

**Restrictions:** No Streamlit/Gradio. Use React, Vue (preferred), or plain HTML+JS.

### Functional Requirements

- Chat surface
- Message list with avatars, timestamps, multi-turn threading
- Composer: multiline input, enter-to-send, Shift+Enter for newline
- Quick actions: `/calc`, `/products`, `/outlets`, `/reset` (with autocomplete)
- Persist conversation to `localStorage`
- Live updates after each turn (reflecting Part 1 memory behavior)

---

## Submission Checklist

- **GitHub repo:** Public link (no secrets)
- **Hosted demo:** e.g., Heroku, Vercel
- **README.md:**

  - Setup & run instructions
  - Architecture overview and trade-offs

- **Documentation:**

  - API specification (including RAG & Text2SQL endpoints)
  - Flow diagrams or screenshots of chatbot
