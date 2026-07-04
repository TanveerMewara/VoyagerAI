# 🌍 Voyager AI

**Supervisor-Based Multi-Agent Travel Intelligence Platform**

Voyager AI is an AI-powered travel planning platform that uses a **Supervisor-based Multi-Agent Architecture** to generate personalized travel itineraries. Instead of relying on a single AI prompt, the system delegates responsibilities to multiple specialized agents and tools, then orchestrates their outputs into one comprehensive travel plan.

---

# 🚀 Features

- 🧠 Supervisor-based Multi-Agent Architecture
- 📅 AI Itinerary Planning
- 💰 Budget Estimation
- 🏨 Hotel Recommendations
- 🌤 Live Weather Integration
- 🗺 Interactive Destination Map
- 📊 Budget Analytics Dashboard
- 🔄 Multi-Agent Workflow Visualization
- 💬 Context-Aware AI Follow-up Chat
- 📄 PDF Travel Report Generation

---

# 🏗 Architecture

```
                    User Input
                         │
                         ▼
               Supervisor Agent
                         │
      ┌──────────┬──────────┬──────────┬──────────┐
      ▼          ▼          ▼          ▼
 Planner     Budget      Hotel      Weather
  Agent       Agent       Agent        Tool
      └──────────┴──────────┴──────────┘
                         │
                         ▼
          AI Travel Report Generation
                         │
      ┌──────────┬──────────┬──────────┐
      ▼          ▼          ▼
 Budget Chart   Map      PDF Report
                         │
                         ▼
                Contextual AI Chat
```

---

# 🛠 Tech Stack

## AI

- Google Gemini 2.5 Flash
- Multi-Agent Architecture

## Backend

- Python

## Frontend

- Streamlit

## Data Visualization

- Plotly
- Graphviz
- Folium

## PDF Generation

- ReportLab

---

# 📂 Project Structure

```
VoyagerAI/
│
├── agents/
├── tools/
├── utils/
├── assets/
├── ui/
├── app.py
├── graph.py
├── requirements.txt
└── README.md
```

---

# ⚙ Installation

Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/VoyagerAI.git
```

Move into the project folder

```bash
cd VoyagerAI
```

Create a virtual environment

```bash
python -m venv venv
```

Activate the environment

### Windows

```bash
venv\Scripts\activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Create a `.env` file

```
GOOGLE_API_KEY=YOUR_API_KEY
```

Run the application

```bash
streamlit run app.py
```

---

# 💡 How It Works

1. User provides travel preferences.
2. Supervisor Agent analyzes the request.
3. Specialized agents independently solve specific tasks.
4. The Supervisor combines all outputs.
5. Voyager AI generates a complete travel plan.
6. Users can continue asking contextual follow-up questions.

---

# 🎯 Future Improvements

- Retrieval-Augmented Generation (RAG)
- ChromaDB Vector Database
- LangGraph Orchestration
- Flight Booking APIs
- Hotel Booking APIs
- Google Maps Places API
- Persistent Conversation Memory
- Docker Deployment

---

# 👨‍💻 Author

**Tanveer Mewara**

B.Tech Artificial Intelligence & Data Science

Aspiring AI Engineer | Generative AI | Multi-Agent Systems | NLP | Python

---

⭐ If you found this project interesting, consider giving it a star.