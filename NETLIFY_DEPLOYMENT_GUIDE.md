# 🚀 Netlify Hosting & Deployment Guide for ResearchGPT

This guide provides step-by-step instructions to deploy **ResearchGPT** on **Netlify** (for the modern Web UI) and host the **FastAPI Multi-Agent Backend** on a free Python cloud service (such as Render, Railway, Fly.io, or Hugging Face Spaces).

---

## 📌 Architecture Overview

| Component | Technology | Hosting Target | Description |
| :--- | :--- | :--- | :--- |
| **Frontend Web App** | HTML5, CSS3 Glassmorphism, JS (ES6) | **Netlify** | Static, ultra-fast web UI with agent visualization, document dropzone & Markdown renderer |
| **Backend API Engine** | Python 3.12, FastAPI, LangGraph, ChromaDB | **Render / Railway / Docker** | Multi-agent execution engine providing `/chat`, `/upload`, `/sources`, `/history` endpoints |

---

## 🌐 Quick Deployment Steps

### Option A: Deploy Frontend to Netlify via Netlify CLI

1. **Install Netlify CLI** (if not already installed):
   ```bash
   npm install -g netlify-cli
   ```

2. **Login to Netlify**:
   ```bash
   netlify login
   ```

3. **Deploy from project root**:
   ```bash
   netlify deploy --prod
   ```
   - Set **Publish Directory** to `public`.
   - Netlify will read configuration from [`netlify.toml`](file:///c:/Users/Hp/Desktop/llmchain/netlify.toml).

---

### Option B: Deploy Frontend via GitHub & Netlify Dashboard

1. Push your repository to GitHub / GitLab.
2. Log into [Netlify Dashboard](https://app.netlify.com/).
3. Click **Add new site** > **Import an existing project**.
4. Select your repository.
5. Netlify will auto-detect settings from `netlify.toml`:
   - **Build Command**: *(leave blank)*
   - **Publish Directory**: `public`
6. Click **Deploy Site**.

---

## 🐍 Deploying the FastAPI Backend Engine

Netlify hosts static sites and Node/Go edge functions. To run the Python FastAPI engine, deploy the backend to a Python host:

### Deploy to Render (Recommended - Free Tier):
1. Create a free account on [Render.com](https://render.com/).
2. Click **New +** > **Blueprint**.
3. Connect your GitHub repository. Render will automatically detect [`render.yaml`](file:///c:/Users/Hp/Desktop/llmchain/render.yaml).
4. Add your API Keys in Render environment variables:
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `TAVILY_API_KEY`: (Optional) Your Tavily search key
5. Click **Apply**. Render will generate a public backend URL (e.g. `https://researchgpt-backend.onrender.com`).

### Connect Netlify Frontend to Live Backend:
1. Open your published Netlify URL (or local test site).
2. Click the **API Settings** (⚙️ gear icon or status pill) in the top-right header.
3. Paste your backend URL (e.g. `https://researchgpt-backend.onrender.com`).
4. Click **Save & Apply**. Your status pill will switch to 🟢 **Connected**!

---

## ⚙️ Configuration Files Added

- [`netlify.toml`](file:///c:/Users/Hp/Desktop/llmchain/netlify.toml): Configures Netlify static publish folder (`public`), SPA redirects, and security headers.
- [`render.yaml`](file:///c:/Users/Hp/Desktop/llmchain/render.yaml): Automatic deployment blueprint for Render cloud backend.
- [`public/index.html`](file:///c:/Users/Hp/Desktop/llmchain/public/index.html): Main Web UI markup.
- [`public/styles.css`](file:///c:/Users/Hp/Desktop/llmchain/public/styles.css): Glassmorphism design system styles.
- [`public/app.js`](file:///c:/Users/Hp/Desktop/llmchain/public/app.js): Client-side API integration logic.
