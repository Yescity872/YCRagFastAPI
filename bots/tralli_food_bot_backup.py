# from service.gemini import call_gemini_model

# def food_bot(query: str) -> str:
#     prompt = f"""
# You are a food assistant for travelers. Respond helpfully to queries about food, local dishes, restaurants, or street food.

# User query: {query}

# Answer:
# """
#     return call_gemini_model(prompt)

import os
from dotenv import load_dotenv
from typing import Optional, List
from langchain_community.vectorstores import FAISS
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.llms.base import LLM
from langchain_huggingface import HuggingFaceEmbeddings
from pydantic import PrivateAttr
from groq import Groq

load_dotenv()
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

# Custom Groq LLM Wrapper
class GroqLLM(LLM):
    model: str = "meta-llama/llama-4-scout-17b-16e-instruct"
    temperature: float = 0.5
    _client: Groq = PrivateAttr()

    def __init__(self, api_key: str, model_name: Optional[str] = None, temperature: float = 0.5):
        super().__init__()
        self._client = Groq(api_key=api_key)
        self.model = model_name or self.model
        self.temperature = temperature

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        completion = self._client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=self.temperature,
            max_tokens=2048,
            top_p=1,
        )
        return completion.choices[0].message.content

    @property
    def _llm_type(self) -> str:
        return "groq-llm"

    class Config:
        arbitrary_types_allowed = True


def food_bot(query: str, city: str = "varanasi") -> str:
    city = city.lower()
    DB_FAISS_PATH = f"vectorstore/db_faiss_{city}"

    if not os.path.exists(DB_FAISS_PATH):
        return {"error": f"No food data found for {city.title()}"}

    # Load Vector DB
    embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    db = FAISS.load_local(DB_FAISS_PATH, embedding_model, allow_dangerous_deserialization=True)
    retriever = db.as_retriever(search_type="mmr", search_kwargs={'k': 15})

    # Prompt
    # FOOD_PROMPT_TEMPLATE = """
    # You are a food assistant bot . Based on the user query and the following context, generate a structured JSON output about a food place.

    # Rules:
    # - Return result in this JSON format ONLY:
    # {{
    # "food-place": "...",
    # "lat-lon": "...",
    # "address": "...",
    # "location-link": "...",
    # "category": "...",
    # "veg/non-veg": "...",
    # "value-for-money": ...,
    # "service": ...,
    # "taste": ...,
    # "hygeine": ...,
    # "menu-special": "...",
    # "menu-link": "...",
    # "open-day": "...",
    # "open-time": "...",
    # "phone": "...",
    # "description": "...",
    # "image0": "...",
    # "image1": "...",
    # "image2": "...",
    # "video": "..."
    # }}

    # If you don't find enough info, fill unknown fields with "N/A".

    # --- CONTEXT ---
    # {context}

    # --- USER QUERY ---
    # {question}

    # Return valid JSON only.
    # """


    FOOD_PROMPT_TEMPLATE = """You are Tralii Food Expert, an AI assistant specializing in regional cuisine knowledge. Follow these guidelines:

1. CITY CONTEXT: You're answering for {city} (also known as Benaras/Kashi when applicable)
2. RESPONSE STYLE: Friendly, informative, with local cultural insights
3. SAFETY: Always mention dietary restrictions when relevant

**Current Query**: {question}

**Relevant Food Information**:
{context}

**Response Requirements**:
- Begin with appropriate greeting in local language if possible (e.g., "Ram Ram!" for Varanasi)
- Structure response:
  1. Direct answer to query
  2. Local specialties (if applicable)
  3. Cultural significance
  4. Where to find recommendations (when known)
  5. Safety/health considerations

**Special Instructions for Varanasi**:
- Highlight these when relevant:
  * Famous shops: Kashi Chat Bhandar, Blue Lassi, Deena Chat Bhandar
  * Must-try items: Malaiyyo (winter special), Tamatar Chaat, Baati Chokha
  * Street food areas: Godowlia, Lanka, Dashashwamedh Gali
  * Sweet shops: Ram Bhandar, Ksheer Sagar

**Example Structure**:
"Ram Ram! [Answer]. In {city}, don't miss [local specialties]. These are particularly [cultural note]. You can find the best at [locations]. Note that [health/safety info]."

**Now generate response for**: {question}
"""

    prompt = PromptTemplate(template=FOOD_PROMPT_TEMPLATE, input_variables=["context", "question"])
    llm = GroqLLM(api_key=os.getenv("GROQ_API_KEY"))

    docs = retriever.get_relevant_documents(query)
    if not docs:
        return {"error": "Sorry, no relevant food information found."}

    context_text = "\n\n".join([doc.page_content for doc in docs])
    qa_chain = LLMChain(llm=llm, prompt=prompt)
    response = qa_chain.run({"context": context_text, "question": query})

    return response

# import os
# from dotenv import load_dotenv
# from typing import Optional, List
# from langchain_community.vectorstores import FAISS
# from langchain.prompts import PromptTemplate
# from langchain.chains import LLMChain
# from langchain.llms.base import LLM
# from langchain_huggingface import HuggingFaceEmbeddings
# from pydantic import PrivateAttr
# from groq import Groq
# from langchain.docstore.document import Document
# import json

# # Load API Key
# load_dotenv()
# os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

# class FoodBot:
#     def __init__(self):
#         self.embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    
#     def load_vectorstore(self, city: str):
#         DB_FAISS_PATH = f"vectorstore/db_faiss_{city.lower()}"
#         if not os.path.exists(DB_FAISS_PATH):
#             return None
#         return FAISS.load_local(DB_FAISS_PATH, self.embedding_model, allow_dangerous_deserialization=True)
    
#     def analyze_query(self, query: str, llm: LLM) -> dict:
#         """Analyze the user query to extract filters and sorting preferences"""
#         prompt = f"""
#         Analyze this food-related query to determine:
#         1. Is the user looking for veg or non-veg places? (return 'veg', 'non-veg', or None)
#         2. What sorting criteria is implied? 
#            - For 'best' or 'delicious' → 'taste'
#            - For 'clean' or 'hygienic' → 'hygeine'
#            - For 'affordable' or 'cheap' → 'value-for-money'
#            - For 'good service' → 'service'
#            - Default → 'taste'
#         3. Is there a specific food item mentioned? (return the item name or None)
        
#         Return ONLY a JSON object with these keys: food_type, sort_by, item
        
#         Query: "{query}"
#         """
        
#         try:
#             response = llm._call(prompt)
#             return json.loads(response)
#         except:
#             return {"food_type": None, "sort_by": "taste", "item": None}
    
#     def parse_food_data(self, content: str) -> Optional[dict]:
#         """Convert document content back to original JSON structure if it's a food place"""
#         if "category: Spiritual" in content or "category: 5-star hotel" in content:
#             return None
            
#         data = {}
#         lines = content.split('\n')
#         for line in lines:
#             if ':' in line:
#                 key, value = line.split(':', 1)
#                 key = key.strip().lower()
#                 value = value.strip()
                
#                 # Map to original JSON keys
#                 if key == "food place": data["food-place"] = value
#                 elif key == "location": data["lat-lon"] = value
#                 elif key == "address": data["address"] = value
#                 elif key == "google maps": data["location-link"] = value
#                 elif key == "category": data["category"] = value
#                 elif key == "type": data["veg/non-veg"] = value
#                 elif key == "contact": data["phone"] = value
#                 elif key == "open days": data["open-day"] = value
#                 elif key == "timings": data["open-time"] = value
#                 elif key == "specialties": data["menu-special"] = value
#                 elif key == "menu": data["menu-link"] = value
#                 elif "value:" in key: data["value-for-money"] = float(value.split('/')[0])
#                 elif "service:" in key: data["service"] = float(value.split('/')[0])
#                 elif "taste:" in key: data["taste"] = float(value.split('/')[0])
#                 elif "hygiene:" in key: data["hygeine"] = float(value.split('/')[0])
#                 elif key == "description": data["description"] = value
#                 elif key == "images": 
#                     images = [img.strip() for img in value.split(',')]
#                     for i, img in enumerate(images[:3]):
#                         data[f"image{i}"] = img
#                 elif key == "video": data["video"] = value
        
#         return data if data.get("food-place") else None

#     def get_food_recommendations(self, query: str, city: str, llm: LLM):
#         db = self.load_vectorstore(city)
#         if not db:
#             return {"error": f"No food data available for {city}"}
        
#         # Analyze the query
#         filters = self.analyze_query(query, llm)
        
#         # Get relevant documents
#         retriever = db.as_retriever(search_type="mmr", search_kwargs={'k': 20})
#         docs = retriever.get_relevant_documents(query)
        
#         # Process and filter food places
#         food_places = []
#         for doc in docs:
#             food_data = self.parse_food_data(doc.page_content)
#             if not food_data:
#                 continue
                
#             # Apply filters from query analysis
#             if filters["food_type"] and food_data.get("veg/non-veg", "").lower() != filters["food_type"]:
#                 continue
#             if filters["item"] and filters["item"].lower() not in food_data.get("menu-special", "").lower():
#                 continue
                
#             food_places.append(food_data)
        
#         # Sort results based on query analysis
#         if food_places:
#             sort_key = filters["sort_by"] or "taste"
#             food_places.sort(
#                 key=lambda x: x.get(sort_key, 0),
#                 reverse=True  # Descending order for ratings
#             )
        
#         return {"results": food_places[:5]}  # Return top 5 results

# class GroqLLM(LLM):
#     model: str = "meta-llama/llama-4-scout-17b-16e-instruct"
#     temperature: float = 0.5
#     _client: Groq = PrivateAttr()

#     def __init__(self, api_key: str, model_name: Optional[str] = None, temperature: float = 0.5):
#         super().__init__()
#         self._client = Groq(api_key=api_key)
#         self.model = model_name or self.model
#         self.temperature = temperature

#     def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
#         completion = self._client.chat.completions.create(
#             model=self.model,
#             messages=[{"role": "user", "content": prompt}],
#             temperature=self.temperature,
#             max_tokens=2048,
#             top_p=1,
#         )
#         return completion.choices[0].message.content

#     @property
#     def _llm_type(self) -> str:
#         return "groq-llm"

#     class Config:
#         arbitrary_types_allowed = True

# def food_bot(query: str, city: str) -> str:
#     # Initialize components
#     bot = FoodBot()
#     llm = GroqLLM(api_key=os.getenv("GROQ_API_KEY"))
    
#     # Get food recommendations
#     result = bot.get_food_recommendations(query, city, llm)
    
#     # Format the response
#     if "error" in result:
#         return json.dumps({"error": result["error"]}, indent=2)
    
#     if not result["results"]:
#         return json.dumps({"error": "No matching restaurants found for your query"}, indent=2)
    
#     return json.dumps(result, indent=2)

# # Example usage
# if __name__ == "__main__":
#     query = "best restaurants in Varanasi"
#     city = "varanasi"
#     print(food_bot(query, city))

