# 🚍 Magic Bus Intelligence Hub
### 🛡️ Secure, Privacy-First Financial Analytics Agent
> **Submitted for:** IITB FinEdge 2025 Hackathon  
> **Track:** Problem Statement 1 (Magic Bus India Foundation)

---

## 📖 Project Overview
**Magic Bus Intelligence Hub** is an on-premise, AI-powered analytics dashboard designed to solve the challenge of processing unstructured financial data (Excel, CSV, PDFs) without compromising data privacy.

Unlike standard AI tools that send sensitive data to public clouds, our solution runs **100% locally**, ensuring that donor data never leaves the organization's secure environment.

### 🎯 The Problem We Solve
- **Data Silos:** Financial data is trapped in multiple unorganized files.
- **Privacy Risks:** Strict regulations prevent using public LLMs (like ChatGPT) for sensitive donor analysis.
- **Manual Effort:** Creating reports from raw data takes days.

### 💡 Our Solution
A secure Python-based engine that parses, cleans, and visualizes data instantly using deterministic logic and rule-based NLP.

---

## 🚀 Key Features
| Feature | Description |
| :--- | :--- |
| **🔐 100% Privacy** | Zero data leakage. No API calls to external AI servers. Runs offline. |
| **📄 Universal Parsing** | Automatically reads complex **Excel sheets** and extracts text from **PDF reports**. |
| **📊 Smart Dashboard** | Interactive graphs for "Total Spend", "Budget Allocation", and "Project Trends". |
| **🤖 AI Chat Agent** | Ask questions like *"What is the total spend?"* and get instant answers. |
| **🛡️ Role-Based Access** | Secure login system for Admins and Finance Staff. |

---

## 🛠️ Tech Stack
- **Frontend:** Python Streamlit
- **Data Processing:** Pandas, NumPy
- **Visualization:** Plotly Express
- **Unstructured Data:** PDFPlumber
- **Security:** Local Authentication & Session State Management

---

## ⚙️ How to Run Locally
Follow these steps to run the project on your machine:

**1. Clone the Repository**
```bash
git clone [https://github.com/saifali098901-has/MagicBus-Intelligence-Hub.git](https://github.com/saifali098901-has/MagicBus-Intelligence-Hub.git)
cd MagicBus-Intelligence-Hub

