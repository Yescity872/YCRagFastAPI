# YCRagFastAPI - Varanasi Travel Assistant

A FastAPI-based RAG (Retrieval-Augmented Generation) system that provides intelligent travel assistance for Varanasi, India. The system uses vector embeddings and AI models to answer queries about food, places, souvenirs, transportation, and general travel information.

## 🚀 Features

- **Multi-domain Travel Assistance**: Covers food, places, souvenirs, transportation, and miscellaneous travel queries
- **AI-Powered Responses**: Uses Google Gemini 2.0 Flash model for intelligent query processing
- **Vector Search**: FAISS-based vector database for semantic search across travel data
- **FastAPI Backend**: High-performance REST API with CORS support
- **Modular Architecture**: Separate bots for different travel categories

## 🏗️ Project Structure

```
YCRagFastAPI/
├── agents/                 # AI agent implementations
├── bots/                   # Specialized bots for different travel categories
│   ├── tralli_food_bot.py
│   ├── tralli_place_bot.py
│   ├── tralli_souvenir_bot.py
│   ├── tralli_transport_bot.py
│   └── tralli_misc_bot.py
├── create_memory/          # Scripts to create vector embeddings
├── data/                   # Travel data storage
├── routers/                # FastAPI route definitions
├── service/                # Core services (Gemini AI, query classification)
├── vectorstore/            # FAISS vector databases
│   └── varanasi/
│       ├── db_faiss_food/
│       ├── db_faiss_places/
│       ├── db_faiss_shopping/
│       └── db_faiss_transport/
├── app.py                  # Main FastAPI application
└── requirements.txt        # Python dependencies
```

## 🛠️ Installation

### Prerequisites

- Python 3.8+
- pip
- Google Gemini API key

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd YCRagFastAPI
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv .venv
   
   # On Windows
   .venv\Scripts\activate
   
   # On macOS/Linux
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Setup**
   Create a `.env` file in the root directory:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

## 🚀 Usage

### Starting the Server

```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### API Endpoints

- **GET /** - Health check endpoint
- **POST /tralli/query** - Main query endpoint for travel assistance

### Example Usage

```python
import requests

# Query the travel assistant
response = requests.post("http://localhost:8000/tralli/query", 
                        json={"query": "What are the best places to eat in Varanasi?"})

print(response.json())
```

## 🤖 Travel Categories

The system handles queries in the following categories:

1. **Food** - Restaurant recommendations, local cuisine, food places
2. **Places** - Tourist attractions, hidden gems, nearby spots
3. **Souvenirs** - Shopping recommendations, local crafts
4. **Transport** - Transportation options, getting around
5. **Miscellaneous** - General travel information and tips

## 🔧 Configuration

### Vector Database Setup

The system uses FAISS vector databases for efficient semantic search. To recreate the vector databases:

```bash
# Create food memory
python create_memory/create_food_memory.py

# Create place memory
python create_memory/create_place_memory.py

# Create souvenir memory
python create_memory/create_souvenir_memory.py

# Create transport memory
python create_memory/create_transport_memory.py

# Create city memory
python create_memory/create_city_memory.py
```

### Data Sources

Travel data is stored in JSON format in the `data/` directory, organized by category and city.

## 🧠 AI Models

- **Query Classification**: Uses Gemini 2.0 Flash for intelligent query categorization
- **Response Generation**: AI-powered responses based on vector search results
- **Semantic Understanding**: Advanced natural language processing for travel queries

## 📊 Performance

- Fast vector search using FAISS
- Efficient memory management
- Scalable FastAPI backend
- CORS-enabled for web applications

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
- Create an issue in the repository
- Check the API documentation at `http://localhost:8000/docs` when running

## 🔮 Future Enhancements

- Support for more cities
- Multi-language support
- Real-time data updates
- Mobile application
- Integration with booking platforms

---

**Built with ❤️ for travelers exploring Varanasi**
