## HoliInfoBot

HoliInfoBot is a simple Replit-based AI assistant designed to answer user queries based on PDFs or text content using vector search and conversational AI.

## 🎯 Project Goal

HoliInfoBot was built to support a Holi-themed playdate event hosted by the organization. The vision was - instead of a traditional landing page, customers would be redirected from an ad to this AI-powered assistant. We believed this would help them: 

- Ask a wide range of personalized questions
- Learn about the event in detail
- Get clarity on logistics, timing, age groups, and more

Enabling richer discovery and fewer drop-offs compared to static landing pages or requiring a phone call with a sales agent.

The event brochure and information packet used to train the bot is included in the repo under `attached_assets`.

## 🧠 What It Does

This bot processes documents, stores them in a vector database, and uses GPT-based chat prompts to answer user questions conversationally. It was built as a minimal prototype for information delivery around specific documents (e.g., school policies, brochures).

## ⚙️ Project Structure

- `main.py` – Entry point for the app
- `utils/chat_helper.py` – Handles GPT-based prompt construction
- `utils/pdf_processor.py` – Parses and cleans PDF content for embedding
- `utils/vector_store.py` – Manages saving and retrieving embeddings
- `.replit` – Allows one-click run and environment management on Replit

## 🚀 Getting Started on Replit

1. Fork this project to your Replit account
2. Click "Run"

No additional setup required — Replit handles all dependencies and environment configuration.

## 🧩 How It Works

1. Upload a PDF or provide input text
2. Content is chunked and embedded using OpenAI embeddings
3. A vector store is created and queried using similarity search
4. GPT constructs contextual answers based on top results

## 🪪 License

Internal demo project – not intended for public release.

