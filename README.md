# 🧠 MemoryCart AI

### Hindsight-Powered E-commerce Customer Support Agent

MemoryCart AI is an intelligent customer support assistant that remembers customers across conversations using **Hindsight Memory**.

The system combines:

* 🧠 Hindsight Memory (Core Feature)
* 📚 Policy Question Answering (RAG)
* 📦 Order Tracking Tool
* 💰 Refund Tracking Tool
* ⚡ FastAPI Backend
* ⚛️ React Frontend
* 🗄️ MySQL Database
* 🔍 ChromaDB Vector Search
* 🤖 Groq LLM Integration

---

# 🚀 Problem Statement

Traditional customer support chatbots forget users after every session.

Customers repeatedly explain:

* Previous issues
* Refund requests
* Order concerns
* Support history

MemoryCart AI solves this by using **persistent memory** to remember customer interactions and personalize future responses.

---

# ✨ Key Features

## 1. Hindsight Memory (Hero Feature)

Stores and retrieves:

* Previous issues
* Order discussions
* Refund requests
* Conversation summaries
* Customer preferences

Example:

User:

> Where is my order?

Later:

> What happened to that order I asked about yesterday?

The assistant recalls previous conversations automatically.

---

## 2. Policy Assistant (RAG)

Answers questions about:

* Return Policy
* Shipping Policy
* Delivery Information
* FAQs

Powered by:

* LangChain
* ChromaDB
* HuggingFace Embeddings

---

## 3. Order Tracking

Input:

```text
Order ID
```

Output:

```text
Order Status
Delivery Date
Product Details
```

Example:

```text
Order #1001 is out for delivery and expected tomorrow.
```

---

## 4. Refund Tracking

Input:

```text
Refund ID
```

Output:

```text
Refund Status
Refund Amount
```

Example:

```text
Refund #1001 has been approved and is being processed.
```

---

## 5. Memory Panel

Displays:

* Previous Issues
* Last Order
* Last Refund
* Memory Summary

Users can visually see what the AI remembers.

---

# 🏗️ Architecture

```text
User Message
      │
      ▼
Retrieve Hindsight Memory
      │
      ▼
Intent Detection
      │
 ┌────┼────┐
 │    │    │
 ▼    ▼    ▼
RAG Order Refund
 │    │    │
 └────┼────┘
      ▼
Generate Response
      │
      ▼
Store New Memory
```

---

# 🛠 Tech Stack

## Frontend

* React
* Vite
* Tailwind CSS
* Axios

## Backend

* FastAPI
* Python

## LLM

* Groq (Llama 3)

## Memory

* Hindsight

## RAG

* LangChain
* ChromaDB
* HuggingFace Embeddings

## Database

* MySQL

## Deployment

* Vercel (Frontend)
* Render (Backend)

---

# 📂 Project Structure

```text
memorycart_ai/

├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   └── ChatPage.jsx
│   │   ├── components/
│   │   │   ├── ChatWindow.jsx
│   │   │   ├── MessageInput.jsx
│   │   │   ├── MemoryPanel.jsx
│   │   │   └── MemoryCard.jsx
│   │   ├── services/
│   │   │   └── api.js
│   │   └── App.jsx
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── services/
│   │   ├── memory/
│   │   ├── rag/
│   │   ├── models/
│   │   ├── schemas/
│   │   └── main.py
│   │
│   ├── documents/
│   ├── database/
│   └── requirements.txt
│
└── README.md
```

---

# 🗄️ Database Schema

## Users

| Field      | Type      |
| ---------- | --------- |
| user_id    | PK        |
| name       | String    |
| created_at | Timestamp |

## Memories

| Field      | Type      |
| ---------- | --------- |
| memory_id  | PK        |
| user_id    | FK        |
| summary    | Text      |
| issue_type | String    |
| created_at | Timestamp |

## Orders

| Field         | Type   |
| ------------- | ------ |
| order_id      | PK     |
| user_id       | FK     |
| product_name  | String |
| status        | String |
| delivery_date | Date   |

## Refunds

| Field     | Type    |
| --------- | ------- |
| refund_id | PK      |
| order_id  | FK      |
| status    | String  |
| amount    | Decimal |

---

# 🔌 API Endpoints

## Chat

```http
POST /chat
```

Request:

```json
{
  "user_id": 1,
  "message": "Where is my order?"
}
```

---

## Memory

```http
GET /memory/{user_id}
```

---

## Orders

```http
GET /orders/{order_id}
```

---

## Refunds

```http
GET /refunds/{refund_id}
```

---

# ⚙️ Installation

## Clone Repository

```bash
git clone https://github.com/Ruchira6174/MemoryCart_AI.git
cd MemoryCart_AI
```

---

## Backend Setup

```bash
cd backend

pip install -r requirements.txt
```

Create `.env`

```env
DB_HOST=localhost
DB_PORT=3306
DB_NAME=memorycart_ai
DB_USER=root
DB_PASSWORD=your_password

GROQ_API_KEY=your_groq_key

HINDSIGHT_API_KEY=your_hindsight_key
HINDSIGHT_BANK_ID=your_bank_id
```

Run backend:

```bash
python -m uvicorn app.main:app --reload
```

---

## Initialize Database

```bash
python app/database/init_db.py
```

---

## Build Vector Store

Place PDFs inside:

```text
backend/documents/
```

Then run:

```bash
python -m app.rag.ingest
```

---

## Frontend Setup

```bash
cd frontend

npm install
npm run dev
```

Frontend:

```text
http://localhost:5173
```

Backend:

```text
http://localhost:8000
```

Swagger:

```text
http://localhost:8000/docs
```

---

# 🎯 Demo Scenarios

## Scenario 1 – Memory Recall

User:

```text
My refund for order 1001 is delayed.
```

Later:

```text
Any update on that refund?
```

AI recalls previous refund discussion automatically.

---

## Scenario 2 – Policy Question

User:

```text
What is your return policy?
```

AI retrieves policy information from ChromaDB.

---

## Scenario 3 – Order Tracking

User:

```text
Track order 1001
```

AI retrieves live order details.

---

## Scenario 4 – Refund Tracking

User:

```text
Check refund 1001
```

AI retrieves refund status.

---

# 🧪 Success Criteria

* ✅ Agent remembers previous conversations
* ✅ Hindsight influences responses
* ✅ Policy Q&A works
* ✅ Order tracking works
* ✅ Refund tracking works
* ✅ Memory panel updates in real-time
* ✅ Backend and frontend integrated

---

# 👥 Team

Built for the Hindsight Memory Hackathon.

MemoryCart AI demonstrates how persistent memory can transform customer support from transactional conversations into continuous customer relationships.

---

# 📜 License

MIT License
