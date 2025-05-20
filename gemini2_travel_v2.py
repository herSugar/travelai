# import os
# import uvicorn
# import asyncio
# import logging
# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel
# from typing import List, Optional
# from serpapi import GoogleSearch
# from crewai import Agent, Task, Crew, Process, LLM
# from datetime import datetime
# from functools import lru_cache

# # Load API Keys
# GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY", "AIzaSyD_0RFDO2mHrlCsKJTe2pHImFobkMExZcI")
# SERP_API_KEY = os.getenv("SERP_API_KEY", "d53db559de3b31a71ba128683631d81df9c97db2b426165857b2faa787795bb0")

# # Initialize Logger
# logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
# logger = logging.getLogger(__name__)


# # ==============================================
# # 🤖 Initialize Google Gemini AI (LLM)
# # ==============================================
# @lru_cache(maxsize=1)
# def initialize_llm():
#     """Initialize and cache the LLM instance to avoid repeated initializations."""
#     return LLM(
#         model="gemini/gemini-2.0-flash",
#         provider="google",
#         api_key=GEMINI_API_KEY
#     )

# # ==============================================
# # 📝 Pydantic Models
# # ==============================================
# class FlightRequest(BaseModel):
#     origin: str
#     destination: str
#     outbound_date: str
#     return_date: str


# class HotelRequest(BaseModel):
#     location: str
#     check_in_date: str
#     check_out_date: str


# class ItineraryRequest(BaseModel):
#     destination: str
#     check_in_date: str
#     check_out_date: str
#     flights: str
#     hotels: str


# class FlightInfo(BaseModel):
#     airline: str
#     price: str
#     duration: str
#     stops: str
#     departure: str
#     arrival: str
#     travel_class: str
#     return_date: str
#     airline_logo: str


# class HotelInfo(BaseModel):
#     name: str
#     price: str
#     rating: float
#     location: str
#     link: str


# class AIResponse(BaseModel):
#     flights: List[FlightInfo] = []
#     hotels: List[HotelInfo] = []
#     ai_flight_recommendation: str = ""
#     ai_hotel_recommendation: str = ""
#     itinerary: str = ""


# # ==============================================
# # 🚀 Initialize FastAPI
# # ==============================================
# app = FastAPI(title="Travel Planning API", version="1.1.0")


# # ==============================================
# # 🛫 Fetch Data from SerpAPI
# # ==============================================
# async def run_search(params):
#     """Generic function to run SerpAPI searches asynchronously."""
#     try:
#         return await asyncio.to_thread(lambda: GoogleSearch(params).get_dict())
#     except Exception as e:
#         logger.exception(f"SerpAPI search error: {str(e)}")
#         raise HTTPException(status_code=500, detail=f"Search API error: {str(e)}")


# async def search_flights(flight_request: FlightRequest):
#     """Fetch real-time flight details from Google Flights using SerpAPI."""
#     logger.info(f"Searching flights: {flight_request.origin} to {flight_request.destination}")

#     params = {
#         "api_key": SERP_API_KEY,
#         "engine": "google_flights",
#         "hl": "en",
#         "gl": "us",
#         "departure_id": flight_request.origin.strip().upper(),
#         "arrival_id": flight_request.destination.strip().upper(),
#         "outbound_date": flight_request.outbound_date,
#         "return_date": flight_request.return_date,
#         "currency": "USD"
#     }

#     search_results = await run_search(params)

#     if "error" in search_results:
#         logger.error(f"Flight search error: {search_results['error']}")
#         return {"error": search_results["error"]}

#     best_flights = search_results.get("best_flights", [])
#     if not best_flights:
#         logger.warning("No flights found in search results")
#         return []

#     formatted_flights = []
#     for flight in best_flights:
#         if not flight.get("flights") or len(flight["flights"]) == 0:
#             continue

#         first_leg = flight["flights"][0]
#         formatted_flights.append(FlightInfo(
#             airline=first_leg.get("airline", "Unknown Airline"),
#             price=str(flight.get("price", "N/A")),
#             duration=f"{flight.get('total_duration', 'N/A')} min",
#             stops="Nonstop" if len(flight["flights"]) == 1 else f"{len(flight['flights']) - 1} stop(s)",
#             departure=f"{first_leg.get('departure_airport', {}).get('name', 'Unknown')} ({first_leg.get('departure_airport', {}).get('id', '???')}) at {first_leg.get('departure_airport', {}).get('time', 'N/A')}",
#             arrival=f"{first_leg.get('arrival_airport', {}).get('name', 'Unknown')} ({first_leg.get('arrival_airport', {}).get('id', '???')}) at {first_leg.get('arrival_airport', {}).get('time', 'N/A')}",
#             travel_class=first_leg.get("travel_class", "Economy"),
#             return_date=flight_request.return_date,
#             airline_logo=first_leg.get("airline_logo", "")
#         ))

#     logger.info(f"Found {len(formatted_flights)} flights")
#     return formatted_flights


# async def search_hotels(hotel_request: HotelRequest):
#     """Fetch hotel information from SerpAPI."""
#     logger.info(f"Searching hotels for: {hotel_request.location}")

#     params = {
#         "api_key": SERP_API_KEY,
#         "engine": "google_hotels",
#         "q": hotel_request.location,
#         "hl": "en",
#         "gl": "us",
#         "check_in_date": hotel_request.check_in_date,
#         "check_out_date": hotel_request.check_out_date,
#         "currency": "USD",
#         "sort_by": 3,
#         "rating": 8
#     }

#     search_results = await run_search(params)

#     if "error" in search_results:
#         logger.error(f"Hotel search error: {search_results['error']}")
#         return {"error": search_results["error"]}

#     hotel_properties = search_results.get("properties", [])
#     if not hotel_properties:
#         logger.warning("No hotels found in search results")
#         return []

#     formatted_hotels = []
#     for hotel in hotel_properties:
#         try:
#             formatted_hotels.append(HotelInfo(
#                 name=hotel.get("name", "Unknown Hotel"),
#                 price=hotel.get("rate_per_night", {}).get("lowest", "N/A"),
#                 rating=hotel.get("overall_rating", 0.0),
#                 location=hotel.get("location", "N/A"),
#                 link=hotel.get("link", "N/A")
#             ))
#         except Exception as e:
#             logger.warning(f"Error formatting hotel data: {str(e)}")
#             # Continue with next hotel rather than failing completely

#     logger.info(f"Found {len(formatted_hotels)} hotels")
#     return formatted_hotels

# # async def search_destinastion(hotel_request: HotelRequest):
# #     """Fetch hotel information from SerpAPI."""
# #     logger.info(f"Searching hotels for: {hotel_request.location}")

# #     params = {
# #         "api_key": SERP_API_KEY,
# #         "engine": "google_hotels",
# #         "q": hotel_request.location,
# #         "hl": "en",
# #         "gl": "us",
# #         "check_in_date": hotel_request.check_in_date,
# #         "check_out_date": hotel_request.check_out_date,
# #         "currency": "USD",
# #         "sort_by": 3,
# #         "rating": 8
# #     }

# #     search_results = await run_search(params)

# #     if "error" in search_results:
# #         logger.error(f"Hotel search error: {search_results['error']}")
# #         return {"error": search_results["error"]}

# #     hotel_properties = search_results.get("properties", [])
# #     if not hotel_properties:
# #         logger.warning("No hotels found in search results")
# #         return []

# #     formatted_hotels = []
# #     for hotel in hotel_properties:
# #         try:
# #             formatted_hotels.append(HotelInfo(
# #                 name=hotel.get("name", "Unknown Hotel"),
# #                 price=hotel.get("rate_per_night", {}).get("lowest", "N/A"),
# #                 rating=hotel.get("overall_rating", 0.0),
# #                 location=hotel.get("location", "N/A"),
# #                 link=hotel.get("link", "N/A")
# #             ))
# #         except Exception as e:
# #             logger.warning(f"Error formatting hotel data: {str(e)}")
# #             # Continue with next hotel rather than failing completely

# #     logger.info(f"Found {len(formatted_hotels)} hotels")
# #     return formatted_hotels


# # ==============================================
# # 🔄 Format Data for AI
# # ==============================================
# def format_travel_data(data_type, data):
#     """Generic formatter for both flight and hotel data."""
#     if not data:
#         return f"No {data_type} available."

#     if data_type == "flights":
#         formatted_text = "✈️ **Available flight options**:\n\n"
#         for i, flight in enumerate(data):
#             formatted_text += (
#                 f"**Flight {i + 1}:**\n"
#                 f"✈️ **Airline:** {flight.airline}\n"
#                 f"💰 **Price:** ${flight.price}\n"
#                 f"⏱️ **Duration:** {flight.duration}\n"
#                 f"🛑 **Stops:** {flight.stops}\n"
#                 f"🕔 **Departure:** {flight.departure}\n"
#                 f"🕖 **Arrival:** {flight.arrival}\n"
#                 f"💺 **Class:** {flight.travel_class}\n\n"
#             )
#     elif data_type == "hotels":
#         formatted_text = "🏨 **Available Hotel Options**:\n\n"
#         for i, hotel in enumerate(data):
#             formatted_text += (
#                 f"**Hotel {i + 1}:**\n"
#                 f"🏨 **Name:** {hotel.name}\n"
#                 f"💰 **Price:** ${hotel.price}\n"
#                 f"⭐ **Rating:** {hotel.rating}\n"
#                 f"📍 **Location:** {hotel.location}\n"
#                 f"🔗 **More Info:** [Link]({hotel.link})\n\n"
#             )
#     else:
#         return "Invalid data type."

#     return formatted_text.strip()


# # ==============================================
# # 🧠 AI Analysis Functions
# # ==============================================
# async def get_ai_recommendation(data_type, formatted_data):
#     """Unified function for getting AI recommendations for both flights and hotels."""
#     logger.info(f"Getting {data_type} analysis from AI")
#     llm_model = initialize_llm()

#     # Configure agent based on data type
#     if data_type == "flights":
#         role = "AI Flight Analyst"
#         goal = "Analyze flight options and recommend the best one considering price, duration, stops, and overall convenience."
#         backstory = f"AI expert that provides in-depth analysis comparing flight options based on multiple factors."
#         description = """
#         Recommend the best flight from the available options, based on the details provided below:

#         **Reasoning for Recommendation:**
#         - **💰 Price:** Provide a detailed explanation about why this flight offers the best value compared to others.
#         - **⏱️ Duration:** Explain why this flight has the best duration in comparison to others.
#         - **🛑 Stops:** Discuss why this flight has minimal or optimal stops.
#         - **💺 Travel Class:** Describe why this flight provides the best comfort and amenities.

#         Use the provided flight data as the basis for your recommendation. Be sure to justify your choice using clear reasoning for each attribute. Do not repeat the flight details in your response.
#         """
#     elif data_type == "hotels":
#         role = "AI Hotel Analyst"
#         goal = "Analyze hotel options and recommend the best one considering price, rating, location, and amenities."
#         backstory = f"AI expert that provides in-depth analysis comparing hotel options based on multiple factors."
#         description = """
#         Based on the following analysis, generate a detailed recommendation for the best hotel. Your response should include clear reasoning based on price, rating, location, and amenities.

#         **🏆 AI Hotel Recommendation**
#         We recommend the best hotel based on the following analysis:

#         **Reasoning for Recommendation**:
#         - **💰 Price:** The recommended hotel is the best option for the price compared to others, offering the best value for the amenities and services provided.
#         - **⭐ Rating:** With a higher rating compared to the alternatives, it ensures a better overall guest experience. Explain why this makes it the best choice.
#         - **📍 Location:** The hotel is in a prime location, close to important attractions, making it convenient for travelers.
#         - **🛋️ Amenities:** The hotel offers amenities like Wi-Fi, pool, fitness center, free breakfast, etc. Discuss how these amenities enhance the experience, making it suitable for different types of travelers.

#         📝 **Reasoning Requirements**:
#         - Ensure that each section clearly explains why this hotel is the best option based on the factors of price, rating, location, and amenities.
#         - Compare it against the other options and explain why this one stands out.
#         - Provide concise, well-structured reasoning to make the recommendation clear to the traveler.
#         - Your recommendation should help a traveler make an informed decision based on multiple factors, not just one.
#         """
#     else:
#         raise ValueError("Invalid data type for AI recommendation")

#     # Create the agent and task
#     analyze_agent = Agent(
#         role=role,
#         goal=goal,
#         backstory=backstory,
#         llm=llm_model,
#         verbose=False
#     )

#     analyze_task = Task(
#         description=f"{description}\n\nData to analyze:\n{formatted_data}",
#         agent=analyze_agent,
#         expected_output=f"A structured recommendation explaining the best {data_type} choice based on the analysis of provided details."
#     )

#     analyst_crew = Crew(
#         agents=[analyze_agent],
#         tasks=[analyze_task],
#         process=Process.sequential,
#         verbose=False
#     )

#     try:
#         # Run the CrewAI analysis in a thread pool
#         crew_results = await asyncio.to_thread(analyst_crew.kickoff)

#         # Handle different possible return types from CrewAI
#         if hasattr(crew_results, 'outputs') and crew_results.outputs:
#             return crew_results.outputs[0]
#         elif hasattr(crew_results, 'get'):
#             return crew_results.get(role, f"No {data_type} recommendation available.")
#         else:
#             return str(crew_results)
#     except Exception as e:
#         logger.exception(f"Error in AI {data_type} analysis: {str(e)}")
#         return f"Unable to generate {data_type} recommendation due to an error."


# async def generate_itinerary(destination, flights_text, hotels_text, check_in_date, check_out_date):
#     """Generate a detailed travel itinerary based on flight and hotel information."""
#     try:
#         # Convert the string dates to datetime objects
#         check_in = datetime.strptime(check_in_date, "%Y-%m-%d")
#         check_out = datetime.strptime(check_out_date, "%Y-%m-%d")

#         # Calculate the difference in days
#         days = (check_out - check_in).days

#         llm_model = initialize_llm()

#         analyze_agent = Agent(
#             role="AI Travel Planner",
#             goal="Create a detailed itinerary for the user based on flight and hotel information",
#             backstory="AI travel expert generating a day-by-day itinerary including flight details, hotel stays, and must-visit locations in the destination.",
#             llm=llm_model,
#             verbose=False
#         )

#         analyze_task = Task(
#             description=f"""
#             Based on the following details, create a {days}-day itinerary for the user:

#             **Flight Details**:
#             {flights_text}

#             **Hotel Details**:
#             {hotels_text}

#             **Destination**: {destination}

#             **Travel Dates**: {check_in_date} to {check_out_date} ({days} days)

#             The itinerary should include:
#             - Flight arrival and departure information
#             - Hotel check-in and check-out details
#             - Day-by-day breakdown of activities
#             - Must-visit attractions and estimated visit times
#             - Restaurant recommendations for meals
#             - Tips for local transportation

#             📝 **Format Requirements**:
#             - Use markdown formatting with clear headings (# for main headings, ## for days, ### for sections)
#             - Include emojis for different types of activities (🏛️ for landmarks, 🍽️ for restaurants, etc.)
#             - Use bullet points for listing activities
#             - Include estimated timings for each activity
#             - Format the itinerary to be visually appealing and easy to read
#             """,
#             agent=analyze_agent,
#             expected_output="A well-structured, visually appealing itinerary in markdown format, including flight, hotel, and day-wise breakdown with emojis, headers, and bullet points."
#         )

#         itinerary_planner_crew = Crew(
#             agents=[analyze_agent],
#             tasks=[analyze_task],
#             process=Process.sequential,
#             verbose=False
#         )

#         crew_results = await asyncio.to_thread(itinerary_planner_crew.kickoff)

#         # Handle different possible return types from CrewAI
#         if hasattr(crew_results, 'outputs') and crew_results.outputs:
#             return crew_results.outputs[0]
#         elif hasattr(crew_results, 'get'):
#             return crew_results.get("AI Travel Planner", "No itinerary available.")
#         else:
#             return str(crew_results)

#     except Exception as e:
#         logger.exception(f"Error generating itinerary: {str(e)}")
#         return "Unable to generate itinerary due to an error. Please try again later."


# # ==============================================
# # 🚀 API Endpoints
# # ==============================================
# @app.post("/search_flights/", response_model=AIResponse)
# async def get_flight_recommendations(flight_request: FlightRequest):
#     """Search flights and get AI recommendation."""
#     try:
#         # Search for flights
#         flights = await search_flights(flight_request)

#         # Handle errors
#         if isinstance(flights, dict) and "error" in flights:
#             raise HTTPException(status_code=400, detail=flights["error"])

#         if not flights:
#             raise HTTPException(status_code=404, detail="No flights found")

#         # Format flight data for AI
#         flights_text = format_travel_data("flights", flights)

#         # Get AI recommendation
#         ai_recommendation = await get_ai_recommendation("flights", flights_text)

#         # Return response
#         return AIResponse(
#             flights=flights,
#             ai_flight_recommendation=ai_recommendation
#         )
#     except HTTPException:
#         # Re-raise HTTP exceptions to preserve status codes
#         raise
#     except Exception as e:
#         logger.exception(f"Flight search endpoint error: {str(e)}")
#         raise HTTPException(status_code=500, detail=f"Flight search error: {str(e)}")


# @app.post("/search_hotels/", response_model=AIResponse)
# async def get_hotel_recommendations(hotel_request: HotelRequest):
#     """Search hotels and get AI recommendation."""
#     try:
#         # Fetch hotel data
#         hotels = await search_hotels(hotel_request)

#         # Handle errors
#         if isinstance(hotels, dict) and "error" in hotels:
#             raise HTTPException(status_code=400, detail=hotels["error"])

#         if not hotels:
#             raise HTTPException(status_code=404, detail="No hotels found")

#         # Format hotel data for AI
#         hotels_text = format_travel_data("hotels", hotels)

#         # Get AI recommendation
#         ai_recommendation = await get_ai_recommendation("hotels", hotels_text)

#         # Return response
#         return AIResponse(
#             hotels=hotels,
#             ai_hotel_recommendation=ai_recommendation
#         )
#     except HTTPException:
#         # Re-raise HTTP exceptions to preserve status codes
#         raise
#     except Exception as e:
#         logger.exception(f"Hotel search endpoint error: {str(e)}")
#         raise HTTPException(status_code=500, detail=f"Hotel search error: {str(e)}")


# @app.post("/complete_search/", response_model=AIResponse)
# async def complete_travel_search(flight_request: FlightRequest, hotel_request: Optional[HotelRequest] = None):
#     """Search for flights and hotels concurrently and get AI recommendations for both."""
#     try:
#         # If hotel request is not provided, create one from flight request
#         if hotel_request is None:
#             hotel_request = HotelRequest(
#                 location=flight_request.destination,
#                 check_in_date=flight_request.outbound_date,
#                 check_out_date=flight_request.return_date
#             )

#         # Run flight and hotel searches concurrently
#         flight_task = asyncio.create_task(get_flight_recommendations(flight_request))
#         hotel_task = asyncio.create_task(get_hotel_recommendations(hotel_request))

#         # Wait for both tasks to complete
#         flight_results, hotel_results = await asyncio.gather(flight_task, hotel_task, return_exceptions=True)

#         # Check for exceptions
#         if isinstance(flight_results, Exception):
#             logger.error(f"Flight search failed: {str(flight_results)}")
#             flight_results = AIResponse(flights=[], ai_flight_recommendation="Could not retrieve flights.")

#         if isinstance(hotel_results, Exception):
#             logger.error(f"Hotel search failed: {str(hotel_results)}")
#             hotel_results = AIResponse(hotels=[], ai_hotel_recommendation="Could not retrieve hotels.")

#         # Format data for itinerary generation
#         flights_text = format_travel_data("flights", flight_results.flights)
#         hotels_text = format_travel_data("hotels", hotel_results.hotels)

#         # Generate itinerary if both searches were successful
#         itinerary = ""
#         if flight_results.flights and hotel_results.hotels:
#             itinerary = await generate_itinerary(
#                 destination=flight_request.destination,
#                 flights_text=flights_text,
#                 hotels_text=hotels_text,
#                 check_in_date=flight_request.outbound_date,
#                 check_out_date=flight_request.return_date
#             )

#         # Combine results
#         return AIResponse(
#             flights=flight_results.flights,
#             hotels=hotel_results.hotels,
#             ai_flight_recommendation=flight_results.ai_flight_recommendation,
#             ai_hotel_recommendation=hotel_results.ai_hotel_recommendation,
#             itinerary=itinerary
#         )
#     except Exception as e:
#         logger.exception(f"Complete travel search error: {str(e)}")
#         raise HTTPException(status_code=500, detail=f"Travel search error: {str(e)}")


# @app.post("/generate_itinerary/", response_model=AIResponse)
# async def get_itinerary(itinerary_request: ItineraryRequest):
#     """Generate an itinerary based on provided flight and hotel information."""
#     try:
#         itinerary = await generate_itinerary(
#             destination=itinerary_request.destination,
#             flights_text=itinerary_request.flights,
#             hotels_text=itinerary_request.hotels,
#             check_in_date=itinerary_request.check_in_date,
#             check_out_date=itinerary_request.check_out_date
#         )

#         return AIResponse(itinerary=itinerary)
#     except Exception as e:
#         logger.exception(f"Itinerary generation error: {str(e)}")
#         raise HTTPException(status_code=500, detail=f"Itinerary generation error: {str(e)}")


# # ==============================================
# # 🌐 Run FastAPI Server
# # ==============================================
# if __name__ == "__main__":
#     logger.info("Starting Travel Planning API server")
#     uvicorn.run(app, host="0.0.0.0", port=8000)

# =====================================================================================================================

# import os
# import uvicorn
# import asyncio
# import logging
# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel
# from typing import List, Optional, Dict
# from serpapi import GoogleSearch
# from crewai import Agent, Task, Crew, Process, LLM
# from datetime import datetime
# from functools import lru_cache

# # Load API Keys
# GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY", "AIzaSyD_0RFDO2mHrlCsKJTe2pHImFobkMExZcI")
# SERP_API_KEY = os.getenv("SERP_API_KEY", "d53db559de3b31a71ba128683631d81df9c97db2b426165857b2faa787795bb0")

# # Initialize Logger
# logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
# logger = logging.getLogger(__name__)

# # List of major Asian airlines
# ASIAN_AIRLINES = [
#     "SQ", "TG", "MH", "CX", "JL", "NH", "OZ", "KE",
#     "BR", "CI", "PR", "GA", "AK", "D7", "5J", "FD",
#     "VN", "HU", "CZ", "MU", "MF", "3U", "CA", "9C"
# ]

# # ==============================================
# # 🤖 Initialize Google Gemini AI (LLM)
# # ==============================================
# @lru_cache(maxsize=1)
# def initialize_llm():
#     return LLM(
#         model="gemini/gemini-2.0-flash",
#         provider="google",
#         api_key=GEMINI_API_KEY
#     )

# # ==============================================
# # 📝 Chatbot Models
# # ==============================================
# class ChatMessage(BaseModel):
#     role: str  # user or assistant
#     content: str

# class ChatRequest(BaseModel):
#     conversation: List[ChatMessage]
#     current_input: str
#     user_preferences: Optional[Dict] = None

# class ChatResponse(BaseModel):
#     response: str
#     suggestions: List[str]
#     needs_more_info: bool
#     is_complete: bool

# class TravelPlan(BaseModel):
#     destination: str
#     dates: str
#     budget: str
#     interests: List[str]

# # ==============================================
# # 🗃️ Conversation Memory
# # ==============================================
# class ConversationMemory:
#     def __init__(self):
#         self.memory = {}
        
#     def get_conversation(self, session_id: str):
#         return self.memory.get(session_id, [])
    
#     def add_message(self, session_id: str, message: ChatMessage):
#         if session_id not in self.memory:
#             self.memory[session_id] = []
#         self.memory[session_id].append(message)
        
#     def clear_conversation(self, session_id: str):
#         if session_id in self.memory:
#             del self.memory[session_id]

# memory = ConversationMemory()

# # ==============================================
# # 🛫 Travel Search Functions (Asia Focus)
# # ==============================================
# async def search_flights(origin: str, destination: str, outbound_date: str, return_date: str):
#     params = {
#         "api_key": SERP_API_KEY,
#         "engine": "google_flights",
#         "hl": "en",
#         "gl": "sg",
#         "departure_id": origin.strip().upper(),
#         "arrival_id": destination.strip().upper(),
#         "outbound_date": outbound_date,
#         "return_date": return_date,
#         "currency": "USD",
#         "region": "asia"
#     }
    
#     try:
#         search_results = await asyncio.to_thread(lambda: GoogleSearch(params).get_dict())
#         return process_flight_results(search_results)
#     except Exception as e:
#         logger.error(f"Flight search error: {str(e)}")
#         return None

# def process_flight_results(search_results):
#     if "error" in search_results:
#         return None
        
#     flights = search_results.get("best_flights", []) + search_results.get("other_flights", [])
#     processed = []
    
#     for flight in flights[:5]:  # Limit to top 5
#         if not flight.get("flights"):
#             continue
            
#         first_leg = flight["flights"][0]
#         airline_code = first_leg.get("airline", "").split()[0].upper()
        
#         processed.append({
#             "airline": first_leg.get("airline", "Unknown"),
#             "price": flight.get("price", "N/A"),
#             "duration": flight.get("total_duration", "N/A"),
#             "stops": "Nonstop" if len(flight["flights"]) == 1 else f"{len(flight['flights'])-1} stops",
#             "departure": f"{first_leg.get('departure_airport', {}).get('time', '')} from {first_leg.get('departure_airport', {}).get('id', '')}",
#             "arrival": f"{first_leg.get('arrival_airport', {}).get('time', '')} at {first_leg.get('arrival_airport', {}).get('id', '')}",
#             "is_asian": airline_code in ASIAN_AIRLINES
#         })
    
#     return processed

# async def search_hotels(location: str, check_in: str, check_out: str):
#     params = {
#         "api_key": SERP_API_KEY,
#         "engine": "google_hotels",
#         "q": location,
#         "hl": "en",
#         "gl": "sg",
#         "check_in_date": check_in,
#         "check_out_date": check_out,
#         "currency": "USD",
#         "sort_by": 3,
#         "rating": 8,
#         "region": "asia"
#     }
    
#     try:
#         search_results = await asyncio.to_thread(lambda: GoogleSearch(params).get_dict())
#         return process_hotel_results(search_results)
#     except Exception as e:
#         logger.error(f"Hotel search error: {str(e)}")
#         return None

# def process_hotel_results(search_results):
#     if "error" in search_results:
#         return None
        
#     hotels = search_results.get("properties", [])
#     processed = []
    
#     for hotel in hotels[:5]:  # Limit to top 5
#         processed.append({
#             "name": hotel.get("name", "Unknown"),
#             "price": hotel.get("rate_per_night", {}).get("lowest", "N/A"),
#             "rating": hotel.get("overall_rating", 0),
#             "location": hotel.get("location", "N/A"),
#             "asian_hospitality": "asian" in hotel.get("description", "").lower()
#         })
    
#     return processed

# # ==============================================
# # 💬 Chatbot Core Functions
# # ==============================================
# def extract_travel_info(conversation: List[ChatMessage]):
#     """Extract travel details from conversation history"""
#     info = {
#         "destination": None,
#         "origin": None,
#         "dates": None,
#         "budget": None,
#         "interests": []
#     }
    
#     for msg in conversation:
#         content = msg.content.lower()
        
#         # Extract destination
#         if " ke " in content or " ke-" in content or " ke " in content:
#             parts = content.split(" ke ")
#             if len(parts) > 1:
#                 info["destination"] = parts[1].split()[0].title()
        
#         # Extract dates
#         if "tanggal" in content or "bulan" in content:
#             if "tanggal" in content:
#                 date_part = content.split("tanggal")[1].strip()
#                 info["dates"] = date_part.split()[0]
    
#     return info

# async def generate_chat_response(conversation: List[ChatMessage], user_input: str):
#     """Generate chatbot response based on conversation context"""
#     llm = initialize_llm()
    
#     # Analyze conversation stage
#     travel_info = extract_travel_info(conversation)
#     context = "\n".join([f"{msg.role}: {msg.content}" for msg in conversation])
    
#     # Determine response type based on conversation stage
#     if not travel_info["destination"]:
#         return await ask_for_destination(llm, user_input)
#     elif not travel_info["dates"]:
#         return await ask_for_dates(llm, user_input, travel_info)
#     else:
#         return await provide_recommendations(llm, user_input, travel_info)

# async def ask_for_destination(llm, user_input):
#     """First step - ask for destination"""
#     agent = Agent(
#         role="Asia Travel Assistant",
#         goal="Help users plan their trip to Asia",
#         backstory="Friendly travel expert specializing in Asian destinations",
#         llm=llm,
#         verbose=False
#     )
    
#     task = Task(
#         description=f"""User said: '{user_input}'
        
#         Respond naturally to start a conversation about their Asian travel plans.
#         Ask what Asian destination they want to visit.
#         Be friendly and enthusiastic about Asian travel.""",
#         agent=agent,
#         expected_output="A friendly message asking where in Asia the user wants to visit"
#     )
    
#     crew = Crew(agents=[agent], tasks=[task], process=Process.sequential)
#     response = await asyncio.to_thread(crew.kickoff)
    
#     return ChatResponse(
#         response=str(response),
#         suggestions=["Tokyo", "Bali", "Bangkok", "Seoul"],
#         needs_more_info=True,
#         is_complete=False
#     )

# async def ask_for_dates(llm, user_input, travel_info):
#     """Second step - ask for travel dates"""
#     agent = Agent(
#         role="Asia Travel Assistant",
#         goal="Get travel dates from user",
#         backstory="Helpful assistant that helps plan travel itineraries",
#         llm=llm,
#         verbose=False
#     )
    
#     task = Task(
#         description=f"""User wants to visit {travel_info['destination']} in Asia.
#         They said: '{user_input}'
        
#         Ask when they plan to travel (month or specific dates).
#         Provide examples of good times to visit this destination.""",
#         agent=agent,
#         expected_output="A message asking for travel dates with seasonal advice"
#     )
    
#     crew = Crew(agents=[agent], tasks=[task], process=Process.sequential)
#     response = await asyncio.to_thread(crew.kickoff)
    
#     return ChatResponse(
#         response=str(response),
#         suggestions=["Next month", "In 3 months", "Next year"],
#         needs_more_info=True,
#         is_complete=False
#     )

# async def provide_recommendations(llm, user_input, travel_info):
#     """Final step - provide travel recommendations"""
#     # Search for flights and hotels
#     flights = await search_flights(
#         origin="CGK",  # Default from Jakarta
#         destination=travel_info["destination"],
#         outbound_date=travel_info["dates"],
#         return_date=travel_info["dates"]  # Simplified for demo
#     )
    
#     hotels = await search_hotels(
#         location=travel_info["destination"],
#         check_in=travel_info["dates"],
#         check_out=travel_info["dates"]  # Simplified for demo
#     )
    
#     # Generate response
#     agent = Agent(
#         role="Asia Travel Expert",
#         goal="Provide excellent travel recommendations for Asia",
#         backstory="Professional travel consultant with deep knowledge of Asia",
#         llm=llm,
#         verbose=False
#     )
    
#     task = Task(
#         description=f"""User is planning a trip to {travel_info['destination']} on {travel_info['dates']}.
        
#         Flight options:
#         {flights[:3] if flights else "No flights found"}
        
#         Hotel options:
#         {hotels[:3] if hotels else "No hotels found"}
        
#         Create a friendly response summarizing these options.
#         Highlight Asian airlines and hotels with local hospitality.
#         Provide 2-3 suggestions for things to do in this destination.""",
#         agent=agent,
#         expected_output="A friendly message with travel recommendations"
#     )
    
#     crew = Crew(agents=[agent], tasks=[task], process=Process.sequential)
#     response = await asyncio.to_thread(crew.kickoff)
    
#     return ChatResponse(
#         response=str(response),
#         suggestions=["Book flights", "See more hotels", "Plan itinerary"],
#         needs_more_info=False,
#         is_complete=True
#     )

# # ==============================================
# # 🚀 FastAPI Endpoints
# # ==============================================
# app = FastAPI(title="Asia Travel Chatbot", version="1.0")

# @app.post("/chat/", response_model=ChatResponse)
# async def chat_endpoint(request: ChatRequest):
#     """Main chatbot endpoint"""
#     try:
#         # For simplicity, using session ID "default" in this example
#         session_id = "default"
        
#         # Add user message to memory
#         memory.add_message(session_id, ChatMessage(role="user", content=request.current_input))
        
#         # Get conversation history
#         conversation = memory.get_conversation(session_id)
        
#         # Generate response
#         response = await generate_chat_response(conversation, request.current_input)
        
#         # Add assistant response to memory
#         memory.add_message(session_id, ChatMessage(role="assistant", content=response.response))
        
#         return response
        
#     except Exception as e:
#         logger.error(f"Chat error: {str(e)}")
#         return ChatResponse(
#             response="Maaf, terjadi kesalahan dalam memproses permintaan Anda.",
#             suggestions=[],
#             needs_more_info=False,
#             is_complete=False
#         )

# @app.post("/start_over/")
# async def start_over():
#     """Reset conversation"""
#     memory.clear_conversation("default")
#     return {"status": "Conversation reset"}

# # ==============================================
# # 🌐 Run FastAPI Server
# # ==============================================
# if __name__ == "__main__":
#     logger.info("Starting Asia Travel Chatbot")
#     uvicorn.run(app, host="0.0.0.0", port=8000)

# =======================================================================================

import os
import uvicorn
import asyncio
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Union
from serpapi import GoogleSearch
from crewai import Agent, Task, Crew, Process, LLM
from datetime import datetime
from functools import lru_cache

# Load API Keys
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY", "AIzaSyD_0RFDO2mHrlCsKJTe2pHImFobkMExZcI")
SERP_API_KEY = os.getenv("SERP_API_KEY", "d53db559de3b31a71ba128683631d81df9c97db2b426165857b2faa787795bb0")

# Initialize Logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# ==============================================
# 🤖 Initialize Google Gemini AI (LLM)
# ==============================================
@lru_cache(maxsize=1)
def initialize_llm():
    """Initialize and cache the LLM instance to avoid repeated initializations."""
    return LLM(
        model="gemini/gemini-2.0-flash",
        provider="google",
        api_key=GEMINI_API_KEY
    )

# ==============================================
# 📝 Pydantic Models
# ==============================================
class FlightRequest(BaseModel):
    origin: str
    destination: str
    outbound_date: str
    return_date: str


class HotelRequest(BaseModel):
    location: str
    check_in_date: str
    check_out_date: str


class ItineraryRequest(BaseModel):
    destination: str
    check_in_date: str
    check_out_date: str
    flights: str
    hotels: str


class ChatRequest(BaseModel):
    message: str
    context: Optional[dict] = None


class FlightInfo(BaseModel):
    airline: str
    price: str
    duration: str
    stops: str
    departure: str
    arrival: str
    travel_class: str
    return_date: str
    airline_logo: str


class HotelInfo(BaseModel):
    name: str
    price: str
    rating: float
    location: str
    link: str


class DestinationInfo(BaseModel):
    name: str
    description: str
    attractions: List[str]
    best_time_to_visit: str
    local_cuisine: List[str]
    cultural_tips: str


class AIResponse(BaseModel):
    flights: List[FlightInfo] = []
    hotels: List[HotelInfo] = []
    destination_info: Optional[DestinationInfo] = None
    ai_flight_recommendation: str = ""
    ai_hotel_recommendation: str = ""
    itinerary: str = ""
    chat_response: str = ""
    context: Optional[dict] = None


# ==============================================
# 🚀 Initialize FastAPI
# ==============================================
app = FastAPI(
    title="Travel Planning Chatbot API",
    version="2.0.0",
    description="A conversational chatbot that helps with travel planning and destination information"
)


# ==============================================
# 🛫 Fetch Data from SerpAPI
# ==============================================
async def run_search(params):
    """Generic function to run SerpAPI searches asynchronously."""
    try:
        return await asyncio.to_thread(lambda: GoogleSearch(params).get_dict())
    except Exception as e:
        logger.exception(f"SerpAPI search error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Search API error: {str(e)}")


async def search_flights(flight_request: FlightRequest):
    """Fetch real-time flight details from Google Flights using SerpAPI."""
    logger.info(f"Searching flights: {flight_request.origin} to {flight_request.destination}")

    params = {
        "api_key": SERP_API_KEY,
        "engine": "google_flights",
        "hl": "en",
        "gl": "us",
        "departure_id": flight_request.origin.strip().upper(),
        "arrival_id": flight_request.destination.strip().upper(),
        "outbound_date": flight_request.outbound_date,
        "return_date": flight_request.return_date,
        "currency": "USD"
    }

    search_results = await run_search(params)

    if "error" in search_results:
        logger.error(f"Flight search error: {search_results['error']}")
        return {"error": search_results["error"]}

    best_flights = search_results.get("best_flights", [])
    if not best_flights:
        logger.warning("No flights found in search results")
        return []

    formatted_flights = []
    for flight in best_flights:
        if not flight.get("flights") or len(flight["flights"]) == 0:
            continue

        first_leg = flight["flights"][0]
        formatted_flights.append(FlightInfo(
            airline=first_leg.get("airline", "Unknown Airline"),
            price=str(flight.get("price", "N/A")),
            duration=f"{flight.get('total_duration', 'N/A')} min",
            stops="Nonstop" if len(flight["flights"]) == 1 else f"{len(flight['flights']) - 1} stop(s)",
            departure=f"{first_leg.get('departure_airport', {}).get('name', 'Unknown')} ({first_leg.get('departure_airport', {}).get('id', '???')}) at {first_leg.get('departure_airport', {}).get('time', 'N/A')}",
            arrival=f"{first_leg.get('arrival_airport', {}).get('name', 'Unknown')} ({first_leg.get('arrival_airport', {}).get('id', '???')}) at {first_leg.get('arrival_airport', {}).get('time', 'N/A')}",
            travel_class=first_leg.get("travel_class", "Economy"),
            return_date=flight_request.return_date,
            airline_logo=first_leg.get("airline_logo", "")
        ))

    logger.info(f"Found {len(formatted_flights)} flights")
    return formatted_flights


async def search_hotels(hotel_request: HotelRequest):
    """Fetch hotel information from SerpAPI."""
    logger.info(f"Searching hotels for: {hotel_request.location}")

    params = {
        "api_key": SERP_API_KEY,
        "engine": "google_hotels",
        "q": hotel_request.location,
        "hl": "en",
        "gl": "us",
        "check_in_date": hotel_request.check_in_date,
        "check_out_date": hotel_request.check_out_date,
        "currency": "USD",
        "sort_by": 3,
        "rating": 8
    }

    search_results = await run_search(params)

    if "error" in search_results:
        logger.error(f"Hotel search error: {search_results['error']}")
        return {"error": search_results["error"]}

    hotel_properties = search_results.get("properties", [])
    if not hotel_properties:
        logger.warning("No hotels found in search results")
        return []

    formatted_hotels = []
    for hotel in hotel_properties:
        try:
            formatted_hotels.append(HotelInfo(
                name=hotel.get("name", "Unknown Hotel"),
                price=hotel.get("rate_per_night", {}).get("lowest", "N/A"),
                rating=hotel.get("overall_rating", 0.0),
                location=hotel.get("location", "N/A"),
                link=hotel.get("link", "N/A")
            ))
        except Exception as e:
            logger.warning(f"Error formatting hotel data: {str(e)}")

    logger.info(f"Found {len(formatted_hotels)} hotels")
    return formatted_hotels


async def search_destination(destination: str):
    """Fetch destination information from SerpAPI and analyze with AI."""
    logger.info(f"Searching information for destination: {destination}")

    # First search for general destination information
    params = {
        "api_key": SERP_API_KEY,
        "engine": "google",
        "q": f"{destination} travel guide",
        "hl": "en",
        "gl": "us"
    }

    search_results = await run_search(params)

    if "error" in search_results:
        logger.error(f"Destination search error: {search_results['error']}")
        return {"error": search_results["error"]}

    # Extract relevant information from search results
    knowledge_graph = search_results.get("knowledge_graph", {})
    organic_results = search_results.get("organic_results", [])
    
    # Prepare context for AI analysis
    context = {
        "destination": destination,
        "knowledge_graph": knowledge_graph,
        "top_results": [result.get("title", "") + ": " + result.get("snippet", "") 
                         for result in organic_results[:3]]
    }

    # Get AI analysis of the destination
    llm_model = initialize_llm()

    destination_agent = Agent(
        role="Travel Destination Expert",
        goal="Provide comprehensive information about travel destinations including attractions, culture, and travel tips",
        backstory="An experienced travel guide with deep knowledge of global destinations, cultures, and travel logistics",
        llm=llm_model,
        verbose=False
    )

    destination_task = Task(
        description=f"""
        Analyze the following information about {destination} and provide a comprehensive overview:
        
        Context: {context}
        
        Your response should include:
        1. A brief description of the destination
        2. Top attractions to visit
        3. Best time to visit with climate considerations
        4. Local cuisine recommendations
        5. Cultural tips and etiquette
        
        Format your response in a structured way that would be helpful for travelers.
        Include emojis to make it more engaging.
        """,
        agent=destination_agent,
        expected_output="A well-structured destination guide with sections for description, attractions, best time to visit, cuisine, and cultural tips."
    )

    destination_crew = Crew(
        agents=[destination_agent],
        tasks=[destination_task],
        process=Process.sequential,
        verbose=False
    )

    try:
        crew_results = await asyncio.to_thread(destination_crew.kickoff)
        
        # Parse the AI response into structured data
        return DestinationInfo(
            name=destination,
            description=crew_results,
            attractions=[],  # Will be extracted by another agent
            best_time_to_visit="",  # Will be extracted by another agent
            local_cuisine=[],  # Will be extracted by another agent
            cultural_tips=""  # Will be extracted by another agent
        )
    except Exception as e:
        logger.exception(f"Error analyzing destination: {str(e)}")
        return DestinationInfo(
            name=destination,
            description=f"Could not retrieve detailed information about {destination}",
            attractions=[],
            best_time_to_visit="",
            local_cuisine=[],
            cultural_tips=""
        )


# ==============================================
# 🔄 Format Data for AI
# ==============================================
def format_travel_data(data_type, data):
    """Generic formatter for both flight and hotel data."""
    if not data:
        return f"No {data_type} available."

    if data_type == "flights":
        formatted_text = "✈️ **Available flight options**:\n\n"
        for i, flight in enumerate(data):
            formatted_text += (
                f"**Flight {i + 1}:**\n"
                f"✈️ **Airline:** {flight.airline}\n"
                f"💰 **Price:** ${flight.price}\n"
                f"⏱️ **Duration:** {flight.duration}\n"
                f"🛑 **Stops:** {flight.stops}\n"
                f"🕔 **Departure:** {flight.departure}\n"
                f"🕖 **Arrival:** {flight.arrival}\n"
                f"💺 **Class:** {flight.travel_class}\n\n"
            )
    elif data_type == "hotels":
        formatted_text = "🏨 **Available Hotel Options**:\n\n"
        for i, hotel in enumerate(data):
            formatted_text += (
                f"**Hotel {i + 1}:**\n"
                f"🏨 **Name:** {hotel.name}\n"
                f"💰 **Price:** ${hotel.price}\n"
                f"⭐ **Rating:** {hotel.rating}\n"
                f"📍 **Location:** {hotel.location}\n"
                f"🔗 **More Info:** [Link]({hotel.link})\n\n"
            )
    else:
        return "Invalid data type."

    return formatted_text.strip()


# ==============================================
# 🧠 AI Analysis Functions
# ==============================================
async def get_ai_recommendation(data_type, formatted_data):
    """Unified function for getting AI recommendations for both flights and hotels."""
    logger.info(f"Getting {data_type} analysis from AI")
    llm_model = initialize_llm()

    if data_type == "flights":
        role = "AI Flight Analyst"
        goal = "Analyze flight options and recommend the best one considering price, duration, stops, and overall convenience."
        backstory = f"AI expert that provides in-depth analysis comparing flight options based on multiple factors."
        description = """
        Recommend the best flight from the available options, based on the details provided below:

        **Reasoning for Recommendation:**
        - **💰 Price:** Provide a detailed explanation about why this flight offers the best value compared to others.
        - **⏱️ Duration:** Explain why this flight has the best duration in comparison to others.
        - **🛑 Stops:** Discuss why this flight has minimal or optimal stops.
        - **💺 Travel Class:** Describe why this flight provides the best comfort and amenities.

        Use the provided flight data as the basis for your recommendation. Be sure to justify your choice using clear reasoning for each attribute. Do not repeat the flight details in your response.
        """
    elif data_type == "hotels":
        role = "AI Hotel Analyst"
        goal = "Analyze hotel options and recommend the best one considering price, rating, location, and amenities."
        backstory = f"AI expert that provides in-depth analysis comparing hotel options based on multiple factors."
        description = """
        Based on the following analysis, generate a detailed recommendation for the best hotel. Your response should include clear reasoning based on price, rating, location, and amenities.

        **🏆 AI Hotel Recommendation**
        We recommend the best hotel based on the following analysis:

        **Reasoning for Recommendation**:
        - **💰 Price:** The recommended hotel is the best option for the price compared to others, offering the best value for the amenities and services provided.
        - **⭐ Rating:** With a higher rating compared to the alternatives, it ensures a better overall guest experience. Explain why this makes it the best choice.
        - **📍 Location:** The hotel is in a prime location, close to important attractions, making it convenient for travelers.
        - **🛋️ Amenities:** The hotel offers amenities like Wi-Fi, pool, fitness center, free breakfast, etc. Discuss how these amenities enhance the experience, making it suitable for different types of travelers.

        📝 **Reasoning Requirements**:
        - Ensure that each section clearly explains why this hotel is the best option based on the factors of price, rating, location, and amenities.
        - Compare it against the other options and explain why this one stands out.
        - Provide concise, well-structured reasoning to make the recommendation clear to the traveler.
        - Your recommendation should help a traveler make an informed decision based on multiple factors, not just one.
        """
    else:
        raise ValueError("Invalid data type for AI recommendation")

    analyze_agent = Agent(
        role=role,
        goal=goal,
        backstory=backstory,
        llm=llm_model,
        verbose=False
    )

    analyze_task = Task(
        description=f"{description}\n\nData to analyze:\n{formatted_data}",
        agent=analyze_agent,
        expected_output=f"A structured recommendation explaining the best {data_type} choice based on the analysis of provided details."
    )

    analyst_crew = Crew(
        agents=[analyze_agent],
        tasks=[analyze_task],
        process=Process.sequential,
        verbose=False
    )

    try:
        crew_results = await asyncio.to_thread(analyst_crew.kickoff)

        if hasattr(crew_results, 'outputs') and crew_results.outputs:
            return crew_results.outputs[0]
        elif hasattr(crew_results, 'get'):
            return crew_results.get(role, f"No {data_type} recommendation available.")
        else:
            return str(crew_results)
    except Exception as e:
        logger.exception(f"Error in AI {data_type} analysis: {str(e)}")
        return f"Unable to generate {data_type} recommendation due to an error."


async def generate_itinerary(destination, flights_text, hotels_text, check_in_date, check_out_date):
    """Generate a detailed travel itinerary based on flight and hotel information."""
    try:
        check_in = datetime.strptime(check_in_date, "%Y-%m-%d")
        check_out = datetime.strptime(check_out_date, "%Y-%m-%d")
        days = (check_out - check_in).days

        llm_model = initialize_llm()

        analyze_agent = Agent(
            role="AI Travel Planner",
            goal="Create a detailed itinerary for the user based on flight and hotel information",
            backstory="AI travel expert generating a day-by-day itinerary including flight details, hotel stays, and must-visit locations in the destination.",
            llm=llm_model,
            verbose=False
        )

        analyze_task = Task(
            description=f"""
            Based on the following details, create a {days}-day itinerary for the user:

            **Flight Details**:
            {flights_text}

            **Hotel Details**:
            {hotels_text}

            **Destination**: {destination}

            **Travel Dates**: {check_in_date} to {check_out_date} ({days} days)

            The itinerary should include:
            - Flight arrival and departure information
            - Hotel check-in and check-out details
            - Day-by-day breakdown of activities
            - Must-visit attractions and estimated visit times
            - Restaurant recommendations for meals
            - Tips for local transportation

            📝 **Format Requirements**:
            - Use markdown formatting with clear headings (# for main headings, ## for days, ### for sections)
            - Include emojis for different types of activities (🏛️ for landmarks, 🍽️ for restaurants, etc.)
            - Use bullet points for listing activities
            - Include estimated timings for each activity
            - Format the itinerary to be visually appealing and easy to read
            """,
            agent=analyze_agent,
            expected_output="A well-structured, visually appealing itinerary in markdown format, including flight, hotel, and day-wise breakdown with emojis, headers, and bullet points."
        )

        itinerary_planner_crew = Crew(
            agents=[analyze_agent],
            tasks=[analyze_task],
            process=Process.sequential,
            verbose=False
        )

        crew_results = await asyncio.to_thread(itinerary_planner_crew.kickoff)

        if hasattr(crew_results, 'outputs') and crew_results.outputs:
            return crew_results.outputs[0]
        elif hasattr(crew_results, 'get'):
            return crew_results.get("AI Travel Planner", "No itinerary available.")
        else:
            return str(crew_results)

    except Exception as e:
        logger.exception(f"Error generating itinerary: {str(e)}")
        return "Unable to generate itinerary due to an error. Please try again later."


async def handle_chat_message(chat_request: ChatRequest):
    """Handle conversational chat messages about travel destinations."""
    logger.info(f"Processing chat message: {chat_request.message}")
    llm_model = initialize_llm()

    # Determine the context for the conversation
    context = chat_request.context or {}
    current_step = context.get("current_step", "greeting")
    
    # Create the appropriate agent based on conversation context
    if current_step == "destination_info":
        role = "Travel Destination Expert"
        goal = "Provide detailed information about travel destinations"
        backstory = "An experienced travel guide with extensive knowledge of global destinations"
    elif current_step == "flight_help":
        role = "Flight Booking Assistant"
        goal = "Help users find and book flights"
        backstory = "An expert in flight routes, airlines, and booking strategies"
    elif current_step == "hotel_help":
        role = "Hotel Booking Assistant"
        goal = "Help users find and book hotels"
        backstory = "An expert in hotel accommodations and booking strategies"
    else:
        role = "Travel Planning Assistant"
        goal = "Help users plan their travels and answer general travel questions"
        backstory = "A friendly and knowledgeable travel assistant"

    chat_agent = Agent(
        role=role,
        goal=goal,
        backstory=backstory,
        llm=llm_model,
        verbose=False
    )

    chat_task = Task(
        description=f"""
        You are a travel planning assistant chatbot. The user has sent you the following message:
        
        "{chat_request.message}"
        
        Context: {context}
        
        Your response should be:
        - Friendly and conversational
        - Helpful and informative
        - If asking for more information, be specific about what you need
        - Use emojis where appropriate to make the conversation more engaging
        - Keep responses concise but thorough
        
        If the user is asking about a specific destination, provide interesting facts and travel tips.
        If the user needs help with flights or hotels, ask for the necessary details to assist them.
        """,
        agent=chat_agent,
        expected_output="A friendly, helpful response to the user's message in natural conversation style."
    )

    chat_crew = Crew(
        agents=[chat_agent],
        tasks=[chat_task],
        process=Process.sequential,
        verbose=False
    )

    try:
        crew_results = await asyncio.to_thread(chat_crew.kickoff)
        
        # Update context based on the conversation
        new_context = context.copy()
        
        # Detect if user is asking about a specific topic
        message_lower = chat_request.message.lower()
        if "flight" in message_lower or "fly" in message_lower:
            new_context["current_step"] = "flight_help"
        elif "hotel" in message_lower or "stay" in message_lower or "accommodation" in message_lower:
            new_context["current_step"] = "hotel_help"
        elif any(word in message_lower for word in ["about", "tell me", "know about", "information"]):
            new_context["current_step"] = "destination_info"
        
        # Format the response
        if hasattr(crew_results, 'outputs') and crew_results.outputs:
            response = crew_results.outputs[0]
        elif hasattr(crew_results, 'get'):
            response = crew_results.get(role, "I'm not sure how to respond to that.")
        else:
            response = str(crew_results)
            
        return response, new_context
        
    except Exception as e:
        logger.exception(f"Error processing chat message: {str(e)}")
        return "I'm having trouble understanding that. Could you rephrase your question?", context


# ==============================================
# 🚀 API Endpoints
# ==============================================
@app.post("/search_flights/", response_model=AIResponse)
async def get_flight_recommendations(flight_request: FlightRequest):
    """Search flights and get AI recommendation."""
    try:
        flights = await search_flights(flight_request)

        if isinstance(flights, dict) and "error" in flights:
            raise HTTPException(status_code=400, detail=flights["error"])

        if not flights:
            raise HTTPException(status_code=404, detail="No flights found")

        flights_text = format_travel_data("flights", flights)
        ai_recommendation = await get_ai_recommendation("flights", flights_text)

        return AIResponse(
            flights=flights,
            ai_flight_recommendation=ai_recommendation
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Flight search endpoint error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Flight search error: {str(e)}")


@app.post("/search_hotels/", response_model=AIResponse)
async def get_hotel_recommendations(hotel_request: HotelRequest):
    """Search hotels and get AI recommendation."""
    try:
        hotels = await search_hotels(hotel_request)

        if isinstance(hotels, dict) and "error" in hotels:
            raise HTTPException(status_code=400, detail=hotels["error"])

        if not hotels:
            raise HTTPException(status_code=404, detail="No hotels found")

        hotels_text = format_travel_data("hotels", hotels)
        ai_recommendation = await get_ai_recommendation("hotels", hotels_text)

        return AIResponse(
            hotels=hotels,
            ai_hotel_recommendation=ai_recommendation
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Hotel search endpoint error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Hotel search error: {str(e)}")


@app.post("/search_destination/", response_model=AIResponse)
async def get_destination_info(destination: str):
    """Get information about a travel destination."""
    try:
        destination_info = await search_destination(destination)
        return AIResponse(
            destination_info=destination_info,
            chat_response=f"Here's some information about {destination}:\n\n{destination_info.description}"
        )
    except Exception as e:
        logger.exception(f"Destination search error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Could not retrieve information about {destination}")


@app.post("/complete_search/", response_model=AIResponse)
async def complete_travel_search(flight_request: FlightRequest, hotel_request: Optional[HotelRequest] = None):
    """Search for flights and hotels concurrently and get AI recommendations for both."""
    try:
        if hotel_request is None:
            hotel_request = HotelRequest(
                location=flight_request.destination,
                check_in_date=flight_request.outbound_date,
                check_out_date=flight_request.return_date
            )

        flight_task = asyncio.create_task(get_flight_recommendations(flight_request))
        hotel_task = asyncio.create_task(get_hotel_recommendations(hotel_request))
        destination_task = asyncio.create_task(get_destination_info(flight_request.destination))

        flight_results, hotel_results, destination_results = await asyncio.gather(
            flight_task, hotel_task, destination_task, 
            return_exceptions=True
        )

        if isinstance(flight_results, Exception):
            logger.error(f"Flight search failed: {str(flight_results)}")
            flight_results = AIResponse(flights=[], ai_flight_recommendation="Could not retrieve flights.")

        if isinstance(hotel_results, Exception):
            logger.error(f"Hotel search failed: {str(hotel_results)}")
            hotel_results = AIResponse(hotels=[], ai_hotel_recommendation="Could not retrieve hotels.")

        if isinstance(destination_results, Exception):
            logger.error(f"Destination search failed: {str(destination_results)}")
            destination_results = AIResponse(destination_info=None)

        flights_text = format_travel_data("flights", flight_results.flights)
        hotels_text = format_travel_data("hotels", hotel_results.hotels)

        itinerary = ""
        if flight_results.flights and hotel_results.hotels:
            itinerary = await generate_itinerary(
                destination=flight_request.destination,
                flights_text=flights_text,
                hotels_text=hotels_text,
                check_in_date=flight_request.outbound_date,
                check_out_date=flight_request.return_date
            )

        return AIResponse(
            flights=flight_results.flights,
            hotels=hotel_results.hotels,
            destination_info=destination_results.destination_info,
            ai_flight_recommendation=flight_results.ai_flight_recommendation,
            ai_hotel_recommendation=hotel_results.ai_hotel_recommendation,
            itinerary=itinerary
        )
    except Exception as e:
        logger.exception(f"Complete travel search error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Travel search error: {str(e)}")


@app.post("/generate_itinerary/", response_model=AIResponse)
async def get_itinerary(itinerary_request: ItineraryRequest):
    """Generate an itinerary based on provided flight and hotel information."""
    try:
        itinerary = await generate_itinerary(
            destination=itinerary_request.destination,
            flights_text=itinerary_request.flights,
            hotels_text=itinerary_request.hotels,
            check_in_date=itinerary_request.check_in_date,
            check_out_date=itinerary_request.check_out_date
        )

        return AIResponse(itinerary=itinerary)
    except Exception as e:
        logger.exception(f"Itinerary generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Itinerary generation error: {str(e)}")


@app.post("/chat/", response_model=AIResponse)
async def chat_with_bot(chat_request: ChatRequest):
    """Endpoint for conversational interaction with the travel chatbot."""
    try:
        chat_response, new_context = await handle_chat_message(chat_request)
        return AIResponse(
            chat_response=chat_response,
            context=new_context
        )
    except Exception as e:
        logger.exception(f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")


# ==============================================
# 🌐 Run FastAPI Server
# ==============================================
if __name__ == "__main__":
    logger.info("Starting Travel Planning Chatbot API server")
    uvicorn.run(app, host="0.0.0.0", port=8000)