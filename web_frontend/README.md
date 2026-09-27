# ⚛️ `web_frontend/` — Future React Single-Page Application (SPA)

> **Status:** 🚧 **PLANNED / FUTURE WORKMODULE (NOT CURRENTLY FUNCTIONAL)**  
> **Primary Interface:** The fully functional, production interface for HealthChain AI is the **Streamlit Dashboard** located in `frontend/main.py`.

---

## 📌 Overview

This directory contains the initial Vite + React project structure intended for a future web-native Single Page Application (SPA) alternative to the Streamlit dashboard.

Currently, this folder contains starter boilerplate and is **not connected to the Flask API backend**.

---

## ⚙️ Primary Production Interface

To run the active, operational user portal, use the Streamlit application:

```bash
# From project root
cd frontend
streamlit run main.py
```

---

## 🚀 Roadmap for `web_frontend/`

When active development on the React SPA begins, it will feature:
- Modern React 18 / Vite architecture with Tailwind CSS styling
- Full REST API integration with `backend/app.py`
- Patient & Doctor role-based navigation & JWT session handling
- Web-native PDF report rendering and interactive vital input forms

---
*For full architecture details, refer to `project_analysis.md` in the project root.*
