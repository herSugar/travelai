# import streamlit as st
# import requests
# from datetime import datetime, timedelta

# # API URLs
# API_BASE_URL = "http://localhost:8000"
# API_URL_FLIGHTS = f"{API_BASE_URL}/search_flights/"
# API_URL_HOTELS = f"{API_BASE_URL}/search_hotels/"
# API_URL_COMPLETE = f"{API_BASE_URL}/complete_search/"
# API_URL_ITINERARY = f"{API_BASE_URL}/generate_itinerary/"

# # Page configuration
# st.set_page_config(
#     page_title="✈️ AI-Powered Travel Planner",
#     page_icon="✈️",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# # Sidebar for additional options
# with st.sidebar:
#     st.title("⚙️ Options")
#     search_mode = st.radio(
#         "Search Mode",
#         ["Complete (Flights + Hotels + Itinerary)", "Flights Only", "Hotels Only"]
#     )

#     st.markdown("---")
#     st.caption("AI-Powered Travel Planner v2.0")
#     st.caption("© 2025 Travel AI Solutions")

# # Main header
# st.title("✈️ AI-Powered Travel Planner")
# st.markdown("""
#     **Find flights, hotels, and get personalized recommendations with AI! Create your perfect travel itinerary in seconds.**
# """)

# # Travel search form
# with st.form(key="travel_search_form"):
#     cols = st.columns([1, 1])

#     with cols[0]:
#         st.subheader("🛫 Flight Details")
#         origin = st.text_input("Departure Airport (IATA code)", "ATL")
#         destination = st.text_input("Arrival Airport (IATA code)", "LAX")

#         # Set default dates (departure tomorrow, return in 7 days)
#         tomorrow = datetime.now() + timedelta(days=1)
#         next_week = tomorrow + timedelta(days=7)

#         outbound_date = st.date_input("Departure Date", tomorrow)
#         return_date = st.date_input("Return Date", next_week)

#     with cols[1]:
#         st.subheader("🏨 Hotel Details")
#         use_flight_destination = st.checkbox("Use flight destination for hotel", value=True)

#         if use_flight_destination:
#             location = destination
#             st.info(f"Using flight destination ({destination}) for hotel search")
#         else:
#             location = st.text_input("Hotel Location", "")

#         check_in_date = st.date_input("Check-In Date", outbound_date)
#         check_out_date = st.date_input("Check-Out Date", return_date)

#     # Submit button
#     submit_col1, submit_col2 = st.columns([3, 1])
#     with submit_col2:
#         submit_button = st.form_submit_button("🔍 Search", use_container_width=True)

# # Handle form submission
# if submit_button:
#     # Validate inputs
#     if not origin or not destination:
#         st.error("Please provide both origin and destination airports.")
#     elif outbound_date >= return_date:
#         st.error("Return date must be after departure date.")
#     elif check_in_date >= check_out_date:
#         st.error("Check-out date must be after check-in date.")
#     else:
#         # Prepare request data
#         flight_data = {
#             "origin": origin,
#             "destination": destination,
#             "outbound_date": str(outbound_date),
#             "return_date": str(return_date)
#         }

#         hotel_data = {
#             "location": location,
#             "check_in_date": str(check_in_date),
#             "check_out_date": str(check_out_date)
#         }

#         # Show loading spinner
#         with st.spinner("Searching for the perfect travel options for you..."):
#             try:
#                 # Choose API endpoint based on selected mode
#                 if search_mode == "Complete (Flights + Hotels + Itinerary)":
#                     # Use the new optimized endpoint for complete search
#                     # Structure the request with nested flight_request and hotel_request objects
#                     complete_data = {
#                         "flight_request": flight_data,
#                         "hotel_request": hotel_data
#                     }
#                     response = requests.post(API_URL_COMPLETE, json=complete_data)
#                     if response.status_code == 200:
#                         result = response.json()
#                         flights = result.get("flights", [])
#                         hotels = result.get("hotels", [])
#                         ai_flight_recommendation = result.get("ai_flight_recommendation", "")
#                         ai_hotel_recommendation = result.get("ai_hotel_recommendation", "")
#                         itinerary = result.get("itinerary", "")
#                     else:
#                         st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
#                         st.stop()

#                 elif search_mode == "Flights Only":
#                     response = requests.post(API_URL_FLIGHTS, json=flight_data)
#                     if response.status_code == 200:
#                         result = response.json()
#                         flights = result.get("flights", [])
#                         ai_flight_recommendation = result.get("ai_flight_recommendation", "")
#                         hotels = []
#                         ai_hotel_recommendation = ""
#                         itinerary = ""
#                     else:
#                         st.error(f"Flight Search Error: {response.json().get('detail', 'Unknown error')}")
#                         st.stop()

#                 elif search_mode == "Hotels Only":
#                     response = requests.post(API_URL_HOTELS, json=hotel_data)
#                     if response.status_code == 200:
#                         result = response.json()
#                         hotels = result.get("hotels", [])
#                         ai_hotel_recommendation = result.get("ai_hotel_recommendation", "")
#                         flights = []
#                         ai_flight_recommendation = ""
#                         itinerary = ""
#                     else:
#                         st.error(f"Hotel Search Error: {response.json().get('detail', 'Unknown error')}")
#                         st.stop()

#             except Exception as e:
#                 st.error(f"An error occurred: {str(e)}")
#                 st.stop()

#         # Display results in tabs
#         if search_mode == "Flights Only":
#             tabs = st.tabs(["✈️ Flights", "🏆 AI Recommendation"])
#         elif search_mode == "Hotels Only":
#             tabs = st.tabs(["🏨 Hotels", "🏆 AI Recommendation"])
#         else:
#             tabs = st.tabs(["✈️ Flights", "🏨 Hotels", "🏆 AI Recommendations", "📅 Itinerary"])

#         # Flights tab
#         if search_mode != "Hotels Only":
#             with tabs[0]:
#                 st.subheader(f"✈️ Available Flights from {origin} to {destination}")

#                 if flights:
#                     # Create two columns for flight cards
#                     flight_cols = st.columns(2)

#                     for i, flight in enumerate(flights):
#                         col_idx = i % 2
#                         with flight_cols[col_idx]:
#                             with st.container(border=True):
#                                 st.markdown(f"""
#                                 ### ✈️ {flight['airline']} - {flight['stops']} Flight

#                                 🕒 **Departure**: {flight['departure']}  
#                                 🕘 **Arrival**: {flight['arrival']}  
#                                 ⏱️ **Duration**: {flight['duration']}  
#                                 💰 **Price**: **${flight['price']}**  
#                                 💺 **Class**: {flight['travel_class']}
#                                 """)
#                                 st.button(f"🔖 Select This Flight", key=f"flight_{i}")
#                 else:
#                     st.info("No flights found for your search criteria.")

#         # Hotels tab
#         if search_mode != "Flights Only":
#             with tabs[1 if search_mode == "Hotels Only" else 1]:
#                 st.subheader(f"🏨 Available Hotels in {location}")

#                 if hotels:
#                     # Create columns for hotel cards
#                     hotel_cols = st.columns(3)

#                     for i, hotel in enumerate(hotels):
#                         col_idx = i % 3
#                         with hotel_cols[col_idx]:
#                             with st.container(border=True):
#                                 st.markdown(f"""
#                                 ### 🏨 {hotel['name']}

#                                 💰 **Price**: ${hotel['price']} per night  
#                                 ⭐ **Rating**: {hotel['rating']}  
#                                 📍 **Location**: {hotel['location']}
#                                 """)
#                                 cols = st.columns([1, 1])
#                                 with cols[0]:
#                                     st.button(f"🔖 Select", key=f"hotel_{i}")
#                                 with cols[1]:
#                                     st.link_button("🔗 Details", hotel['link'])
#                 else:
#                     st.info("No hotels found for your search criteria.")

#         # AI Recommendations tab
#         recommendation_tab_index = 1 if search_mode in ["Flights Only", "Hotels Only"] else 2
#         with tabs[recommendation_tab_index]:
#             if search_mode != "Hotels Only" and ai_flight_recommendation:
#                 st.subheader("✈️ AI Flight Recommendation")
#                 with st.container(border=True):
#                     st.markdown(ai_flight_recommendation)

#             if search_mode != "Flights Only" and ai_hotel_recommendation:
#                 st.subheader("🏨 AI Hotel Recommendation")
#                 with st.container(border=True):
#                     st.markdown(ai_hotel_recommendation)

#         # Itinerary tab
#         if search_mode == "Complete (Flights + Hotels + Itinerary)" and itinerary:
#             with tabs[3]:
#                 st.subheader("📅 Your Travel Itinerary")
#                 with st.container(border=True):
#                     st.markdown(itinerary)

#                 # Download button for itinerary
#                 st.download_button(
#                     label="📥 Download Itinerary",
#                     data=itinerary,
#                     file_name=f"travel_itinerary_{destination}_{outbound_date}.md",
#                     mime="text/markdown"
#                 )

# ======================================================================================================================

# import streamlit as st
# import requests
# from datetime import datetime, timedelta
# import json

# # API URLs
# API_BASE_URL = "http://localhost:8000"
# CHAT_API_URL = f"{API_BASE_URL}/chat/"
# RESET_API_URL = f"{API_BASE_URL}/start_over/"

# # Page configuration
# st.set_page_config(
#     page_title="✈️ Asia Travel Chatbot",
#     page_icon="🗾",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# # Initialize chat history
# if "messages" not in st.session_state:
#     st.session_state.messages = [
#         {"role": "assistant", "content": "Hello! I'm your Asia Travel Assistant. Where in Asia would you like to visit?"}
#     ]

# # Initialize form state
# if "show_form" not in st.session_state:
#     st.session_state.show_form = False

# # Sidebar for additional options
# with st.sidebar:
#     st.title("⚙️ Chat Options")
#     st.markdown("---")
#     if st.button("🔄 Start New Conversation"):
#         try:
#             response = requests.post(RESET_API_URL)
#             if response.status_code == 200:
#                 st.session_state.messages = [
#                     {"role": "assistant", "content": "Let's start over! Where in Asia would you like to visit?"}
#                 ]
#                 st.session_state.show_form = False
#                 st.rerun()
#         except Exception as e:
#             st.error(f"Error resetting conversation: {str(e)}")
    
#     st.markdown("---")
#     st.caption("Asia Travel Chatbot v2.0")
#     st.caption("Specializing in Asian destinations")

# # Main header
# st.title("🗾 Asia Travel Chatbot")
# st.markdown("Plan your perfect Asian adventure with our AI assistant!")

# # Display chat messages
# for message in st.session_state.messages:
#     with st.chat_message(message["role"]):
#         st.markdown(message["content"])

#         # Display flight/hotel cards if present in message
#         if "flights" in message:
#             with st.expander("✈️ Flight Options"):
#                 for flight in message["flights"][:3]:
#                     st.markdown(f"""
#                     **{flight['airline']}**  
#                     🕒 {flight['departure']} → {flight['arrival']}  
#                     ⏱️ {flight['duration']} • 🛑 {flight['stops']}  
#                     💰 ${flight['price']}  
#                     {'🇦🇸 Asian airline' if flight['is_asian'] else ''}
#                     """)
#                     st.markdown("---")
        
#         if "hotels" in message:
#             with st.expander("🏨 Hotel Options"):
#                 for hotel in message["hotels"][:3]:
#                     st.markdown(f"""
#                     **{hotel['name']}**  
#                     ⭐ {hotel['rating']}/10 • 💰 ${hotel['price']}/night  
#                     📍 {hotel['location']}  
#                     {'🏯 Asian hospitality' if hotel['asian_hospitality'] else ''}
#                     """)
#                     st.markdown("---")

# # Chat input
# if prompt := st.chat_input("Type your message..."):
#     # Add user message to chat history
#     st.session_state.messages.append({"role": "user", "content": prompt})
    
#     # Display user message in chat message container
#     with st.chat_message("user"):
#         st.markdown(prompt)
    
#     # Show assistant response
#     with st.chat_message("assistant"):
#         message_placeholder = st.empty()
#         full_response = ""
        
#         # Prepare chat request
#         chat_request = {
#             "conversation": st.session_state.messages[:-1],  # All except the last user message
#             "current_input": prompt
#         }
        
#         try:
#             with st.spinner("Thinking..."):
#                 response = requests.post(CHAT_API_URL, json=chat_request)
                
#                 if response.status_code == 200:
#                     result = response.json()
#                     full_response = result["response"]
                    
#                     # Display response incrementally
#                     message_placeholder.markdown(full_response + "▌")
#                     message_placeholder.markdown(full_response)
                    
#                     # Add to chat history
#                     new_message = {"role": "assistant", "content": full_response}
                    
#                     # Check if we need to show the travel form
#                     if "needs_more_info" in result and result["needs_more_info"]:
#                         st.session_state.show_form = True
                    
#                     # Add any suggestions as quick replies
#                     if "suggestions" in result and result["suggestions"]:
#                         with st.container():
#                             st.write("Quick suggestions:")
#                             cols = st.columns(len(result["suggestions"]))
#                             for i, suggestion in enumerate(result["suggestions"]):
#                                 with cols[i]:
#                                     if st.button(suggestion):
#                                         # Add the suggestion as a user message
#                                         st.session_state.messages.append({"role": "user", "content": suggestion})
#                                         st.rerun()
                    
#                     st.session_state.messages.append(new_message)
                
#                 else:
#                     error_msg = f"Error: {response.json().get('detail', 'Unknown error')}"
#                     message_placeholder.error(error_msg)
#                     st.session_state.messages.append({"role": "assistant", "content": error_msg})
        
#         except Exception as e:
#             error_msg = f"Sorry, I encountered an error: {str(e)}"
#             message_placeholder.error(error_msg)
#             st.session_state.messages.append({"role": "assistant", "content": error_msg})

# # Travel details form (shown when needed)
# if st.session_state.show_form:
#     with st.form(key="travel_details_form"):
#         st.subheader("✈️ Tell me more about your trip")
        
#         cols = st.columns(2)
#         with cols[0]:
#             destination = st.text_input("Asian destination you want to visit", "Tokyo")
#             origin = st.text_input("Your departure city", "Jakarta")
            
#             # Set default dates
#             today = datetime.now()
#             next_month = today + timedelta(days=30)
            
#             travel_dates = st.date_input(
#                 "When will you travel?",
#                 (today, next_month),
#                 format="MM/DD/YYYY"
#             )
        
#         with cols[1]:
#             interests = st.multiselect(
#                 "What are you interested in?",
#                 ["Cultural sites", "Beaches", "Shopping", "Food", "Nature", "Adventure"],
#                 ["Cultural sites", "Food"]
#             )
            
#             budget = st.select_slider(
#                 "Your budget level",
#                 options=["Budget", "Mid-range", "Luxury"],
#                 value="Mid-range"
#             )
        
#         submitted = st.form_submit_button("Plan My Trip")
        
#         if submitted:
#             if len(travel_dates) != 2:
#                 st.error("Please select both departure and return dates")
#             else:
#                 # Prepare travel plan
#                 travel_plan = {
#                     "destination": destination,
#                     "origin": origin,
#                     "departure_date": str(travel_dates[0]),
#                     "return_date": str(travel_dates[1]),
#                     "interests": interests,
#                     "budget": budget
#                 }
                
#                 # Add to chat history
#                 st.session_state.messages.append({
#                     "role": "user",
#                     "content": f"I want to visit {destination} from {travel_dates[0]} to {travel_dates[1]}. My interests are {', '.join(interests)} and my budget is {budget}."
#                 })
                
#                 # Show assistant is thinking
#                 with st.chat_message("assistant"):
#                     message_placeholder = st.empty()
#                     message_placeholder.markdown("Searching for the best Asian travel options...▌")
                    
#                     try:
#                         # Call API to get travel recommendations
#                         chat_request = {
#                             "conversation": st.session_state.messages,
#                             "current_input": json.dumps(travel_plan)
#                         }
                        
#                         response = requests.post(CHAT_API_URL, json=chat_request)
                        
#                         if response.status_code == 200:
#                             result = response.json()
#                             full_response = result["response"]
                            
#                             # Display the response
#                             message_placeholder.markdown(full_response)
                            
#                             # Add to chat history
#                             new_message = {"role": "assistant", "content": full_response}
                            
#                             # Add any data cards
#                             if "flights" in result:
#                                 new_message["flights"] = result["flights"]
                            
#                             if "hotels" in result:
#                                 new_message["hotels"] = result["hotels"]
                            
#                             st.session_state.messages.append(new_message)
#                             st.session_state.show_form = False
#                             st.rerun()
                        
#                         else:
#                             error_msg = f"Error: {response.json().get('detail', 'Unknown error')}"
#                             message_placeholder.error(error_msg)
#                             st.session_state.messages.append({"role": "assistant", "content": error_msg})
                    
#                     except Exception as e:
#                         error_msg = f"Sorry, I encountered an error: {str(e)}"
#                         message_placeholder.error(error_msg)
#                         st.session_state.messages.append({"role": "assistant", "content": error_msg})
                        
# =====================================================================================================================

# import streamlit as st
# import requests
# from datetime import datetime, timedelta
# import json

# # API configuration
# API_BASE_URL = "http://localhost:8000"
# CHAT_API_URL = f"{API_BASE_URL}/chat/"
# FLIGHT_API_URL = f"{API_BASE_URL}/search_flights/"
# HOTEL_API_URL = f"{API_BASE_URL}/search_hotels/"
# COMPLETE_API_URL = f"{API_BASE_URL}/complete_search/"
# # RESET_API_URL = f"{API_BASE_URL}/start_over/"

# # Page configuration
# st.set_page_config(
#     page_title="✈️ AI Travel Assistant",
#     page_icon="🗺️",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# # Initialize session state
# if "messages" not in st.session_state:
#     st.session_state.messages = [
#         {"role": "assistant", "content": "Hello! I'm your AI Travel Assistant. Where would you like to go?"}
#     ]

# if "show_form" not in st.session_state:
#     st.session_state.show_form = False

# # Sidebar
# with st.sidebar:
#     st.title("⚙️ Travel Options")
#     search_mode = st.radio(
#         "Search Mode",
#         ["Chat Mode", "Quick Search (Flights + Hotels)"],
#         index=0
#     )
    
#     st.markdown("---")
#     if st.button("🔄 Start New Conversation"):
#         try:
#             response = requests.post(RESET_API_URL)
#             if response.status_code == 200:
#                 st.session_state.messages = [
#                     {"role": "assistant", "content": "Let's start over! Where would you like to go?"}
#                 ]
#                 st.session_state.show_form = False
#                 st.rerun()
#         except Exception as e:
#             st.error(f"Error: {str(e)}")
    
#     st.markdown("---")
#     st.caption("AI Travel Assistant v2.0")
#     st.caption("© 2024 Travel AI Solutions")

# # Main interface
# st.title("🤖 AI Travel Assistant")
# st.markdown("Plan your perfect trip with our AI assistant!")

# # Display chat messages
# for message in st.session_state.messages:
#     with st.chat_message(message["role"]):
#         st.markdown(message["content"])
        
#         # Display any cards or expanders
#         if "flights" in message:
#             with st.expander("✈️ Flight Options"):
#                 for flight in message["flights"][:3]:
#                     st.markdown(f"""
#                     **{flight['airline']}**  
#                     🕒 {flight['departure']} → {flight['arrival']}  
#                     ⏱️ {flight['duration']} • 🛑 {flight['stops']}  
#                     💰 ${flight['price']}  
#                     {'🇦🇸 Asian airline' if flight.get('is_asian_airline') else ''}
#                     """)
#                     st.markdown("---")
        
#         if "hotels" in message:
#             with st.expander("🏨 Hotel Options"):
#                 for hotel in message["hotels"][:3]:
#                     st.markdown(f"""
#                     **{hotel['name']}**  
#                     ⭐ {hotel['rating']}/10 • 💰 ${hotel['price']}/night  
#                     📍 {hotel['location']}  
#                     {'🏯 Asian hospitality' if hotel.get('asian_hospitality') else ''}
#                     """)
#                     st.markdown("---")

# # Chat input
# if prompt := st.chat_input("Type your message..."):
#     # Add user message to chat history
#     st.session_state.messages.append({"role": "user", "content": prompt})
    
#     # Display user message
#     with st.chat_message("user"):
#         st.markdown(prompt)
    
#     # Show assistant response
#     with st.chat_message("assistant"):
#         message_placeholder = st.empty()
#         full_response = ""
        
#         if search_mode == "Chat Mode":
#             # Prepare chat request
#             # chat_request = {
#             #     "conversation": st.session_state.messages[:-1],
#             #     "current_input": prompt
#             # }
#             chat_request = {
#                 "message": prompt,
#                 "context": st.session_state.get("context", {})
#             }
            
#             try:
#                 with st.spinner("Thinking..."):
#                     response = requests.post(CHAT_API_URL, json=chat_request)
                    
#                     if response.status_code == 200:
#                         result = response.json()
#                         full_response = result["response"]
                        
#                         # Display response
#                         message_placeholder.markdown(full_response)
                        
#                         # Add to chat history
#                         new_message = {"role": "assistant", "content": full_response}
                        
#                         # Check if we need to show the travel form
#                         if result.get("needs_more_info", False):
#                             st.session_state.show_form = True
                        
#                         # Add any suggestions as quick replies
#                         if result.get("suggestions"):
#                             st.write("Quick suggestions:")
#                             cols = st.columns(len(result["suggestions"]))
#                             for i, suggestion in enumerate(result["suggestions"]):
#                                 with cols[i]:
#                                     if st.button(suggestion):
#                                         st.session_state.messages.append({"role": "user", "content": suggestion})
#                                         st.rerun()
                        
#                         st.session_state.messages.append(new_message)
                    
#                     else:
#                         error_msg = f"Error: {response.json().get('detail', 'Unknown error')}"
#                         message_placeholder.error(error_msg)
#                         st.session_state.messages.append({"role": "assistant", "content": error_msg})
            
#             except Exception as e:
#                 error_msg = f"Sorry, I encountered an error: {str(e)}"
#                 message_placeholder.error(error_msg)
#                 st.session_state.messages.append({"role": "assistant", "content": error_msg})
        
#         else:  # Quick Search mode
#             st.session_state.show_form = True
#             message_placeholder.info("Please fill out the travel details below")

# # Travel details form (shown when needed)
# if st.session_state.show_form:
#     with st.form(key="travel_details_form"):
#         st.subheader("✈️ Travel Details")
        
#         cols = st.columns(2)
#         with cols[0]:
#             origin = st.text_input("Departure City (IATA code)", "CGK")
#             destination = st.text_input("Destination City", "Tokyo")
            
#             # Set default dates
#             today = datetime.now()
#             next_week = today + timedelta(days=7)
            
#             outbound_date = st.date_input("Departure Date", today)
#             return_date = st.date_input("Return Date", next_week)
        
#         with cols[1]:
#             st.subheader("🏨 Hotel Options")
#             check_in_date = st.date_input("Check-In Date", outbound_date)
#             check_out_date = st.date_input("Check-Out Date", return_date)
#             min_rating = st.slider("Minimum Hotel Rating", 0.0, 5.0, 4.0, 0.5)
        
#         submitted = st.form_submit_button("🔍 Search for Options")
        
#         if submitted:
#             if outbound_date >= return_date:
#                 st.error("Return date must be after departure date")
#             elif check_in_date >= check_out_date:
#                 st.error("Check-out date must be after check-in date")
#             else:
#                 with st.spinner("Searching for travel options..."):
#                     try:
#                         flight_request = {
#                             "origin": origin,
#                             "destination": destination,
#                             "outbound_date": str(outbound_date),
#                             "return_date": str(return_date)
#                         }
                        
#                         hotel_request = {
#                             "location": destination,
#                             "check_in_date": str(check_in_date),
#                             "check_out_date": str(check_out_date),
#                             "min_rating": min_rating
#                         }
                        
#                         complete_request = {
#                             "flight_request": flight_request,
#                             "hotel_request": hotel_request
#                         }
                        
#                         response = requests.post(COMPLETE_API_URL, json=complete_request)
                        
#                         if response.status_code == 200:
#                             result = response.json()
                            
#                             # Format response
#                             response_text = f"Here are travel options for your trip to {destination}:\n\n"
                            
#                             if result.get("flights"):
#                                 response_text += "**✈️ Flight Options:**\n"
#                                 for flight in result["flights"][:3]:
#                                     response_text += (
#                                         f"- {flight['airline']}: {flight['departure']} to {flight['arrival']} "
#                                         f"(Duration: {flight['duration']}, Price: ${flight['price']})\n"
#                                     )
                            
#                             if result.get("hotels"):
#                                 response_text += "\n**🏨 Hotel Options:**\n"
#                                 for hotel in result["hotels"][:3]:
#                                     response_text += (
#                                         f"- {hotel['name']}: ${hotel['price']}/night, Rating: {hotel['rating']}\n"
#                                     )
                            
#                             if result.get("ai_flight_recommendation"):
#                                 response_text += f"\n**AI Flight Recommendation:**\n{result['ai_flight_recommendation']}\n"
                            
#                             if result.get("ai_hotel_recommendation"):
#                                 response_text += f"\n**AI Hotel Recommendation:**\n{result['ai_hotel_recommendation']}\n"
                            
#                             if result.get("itinerary"):
#                                 response_text += f"\n**📅 Suggested Itinerary:**\n{result['itinerary']}\n"
                            
#                             # Add to chat history
#                             st.session_state.messages.append({
#                                 "role": "assistant",
#                                 "content": response_text,
#                                 "flights": result.get("flights", []),
#                                 "hotels": result.get("hotels", [])
#                             })
                            
#                             st.session_state.show_form = False
#                             st.rerun()
                        
#                         else:
#                             error_msg = f"Error: {response.json().get('detail', 'Unknown error')}"
#                             st.error(error_msg)
#                             st.session_state.messages.append({"role": "assistant", "content": error_msg})
                    
#                     except Exception as e:
#                         error_msg = f"An error occurred: {str(e)}"
#                         st.error(error_msg)
#                         st.session_state.messages.append({"role": "assistant", "content": error_msg})

# ===================================================================================================================================

import streamlit as st
import requests
from datetime import datetime, timedelta
from streamlit.components.v1 import html

# API configuration
API_BASE_URL = "http://localhost:8000"
CHAT_API_URL = f"{API_BASE_URL}/chat/"
FLIGHT_API_URL = f"{API_BASE_URL}/search_flights/"
HOTEL_API_URL = f"{API_BASE_URL}/search_hotels/"
COMPLETE_API_URL = f"{API_BASE_URL}/complete_search/"
DESTINATION_API_URL = f"{API_BASE_URL}/search_destination/"

# Page configuration
st.set_page_config(
    page_title="✈️ AI Travel Assistant",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    /* Main chat container */
    .stChatMessage {
        padding: 12px;
        border-radius: 12px;
        margin-bottom: 20px;
    }
    
    /* Assistant message bubble */
    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] {
        background-color: #1a2a3a;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #4682b4;
    }
    
    /* User message bubble */
    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] {
        background-color: #1a2a3a;
        padding: 1.5rem;
        border-radius: 15px;
    }
    
    /* Buttons */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        border: 1px solid #ddd;
        background-color: #1a2a3a;
    }
    
    /* Expanders */
    .stExpander {
        background-color: white;
        border: 1px solid #e1e4e8;
        border-radius: 8px;
        margin: 10px 0;
    }
    
    /* Adjust avatar alignment */
    [data-testid="stChatMessage"] [data-testid="stImage"] {
        align-self: flex-start;
        margin-top: 12px;
    }
</style>
""", unsafe_allow_html=True)

# Loading animation component
def loading_animation():
    html("""
    <div style='display:flex;justify-content:center;margin:1rem;'>
        <lottie-player src='https://assets10.lottiefiles.com/packages/lf20_raiw2hpe.json' 
         background='transparent' speed='1' style='width:200px;height:200px' loop autoplay>
        </lottie-player>
    </div>
    """, height=220)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I'm your AI Travel Assistant. Where would you like to go?"}
    ]

if "show_form" not in st.session_state:
    st.session_state.show_form = False

if "context" not in st.session_state:
    st.session_state.context = {}

# Sidebar
with st.sidebar:
    st.title("⚙️ Travel Options")
    search_mode = st.radio(
        "Search Mode",
        ["Chat Mode", "Quick Search (Flights + Hotels)"],
        index=0
    )
    
    st.markdown("---")
    if st.button("🔄 Start New Conversation"):
        st.session_state.messages = [
            {"role": "assistant", "content": "Let's start over! Where would you like to go?"}
        ]
        st.session_state.show_form = False
        st.session_state.context = {}
        st.rerun()
    
    st.markdown("---")
    st.caption("AI Travel Assistant v2.0")
    st.caption("© 2024 Travel AI Solutions")

# Main interface
st.title("🤖 AI Travel Assistant")
st.markdown("Plan your perfect trip with our AI assistant!")

# Display chat messages
for message in st.session_state.messages:
    if message["role"] == "assistant":
        with st.chat_message("assistant", avatar="🗺️"):
            st.markdown(f"""
            <div style='background-color:#1a2a3a;padding:1.5rem;border-radius:15px;border-left:4px solid #4682b4;'>
                {message["content"]}
            </div>
            """, unsafe_allow_html=True)
            
            # Display flight options if available
            if "flights" in message and isinstance(message["flights"], list) and len(message["flights"]) > 0:
                with st.expander(f"✈️ {len(message['flights'])} Flight Options"):
                    for flight in message["flights"][:3]:
                        st.markdown(f"""
                        **{flight.get('airline', 'Unknown Airline')}**  
                        🕒 {flight.get('departure', 'N/A')} → {flight.get('arrival', 'N/A')}  
                        ⏱️ {flight.get('duration', 'N/A')} • 🛑 {flight.get('stops', 'N/A')}  
                        💰 ${flight.get('price', 'N/A')}  
                        """)
                        st.markdown("---")
            
            # Display hotel options if available
            if "hotels" in message and isinstance(message["hotels"], list) and len(message["hotels"]) > 0:
                with st.expander(f"🏨 {len(message['hotels'])} Hotel Options"):
                    for hotel in message["hotels"][:3]:
                        st.markdown(f"""
                        **{hotel.get('name', 'Unknown Hotel')}**  
                        ⭐ {hotel.get('rating', 'N/A')} • 💰 ${hotel.get('price', 'N/A')}/night  
                        📍 {hotel.get('location', 'N/A')}  
                        🔗 [More Info]({hotel.get('link', '#')})
                        """)
                        st.markdown("---")
            
            # Display destination info if available
            if "destination_info" in message and message["destination_info"]:
                info = message["destination_info"]
                with st.expander(f"🌍 About {info.get('name', 'this destination')}"):
                    if info.get('description'):
                        st.markdown(info['description'])
                        st.markdown("---")
                    if info.get('attractions'):
                        st.markdown(f"**⭐ Top Attractions:** {', '.join(info['attractions'][:3])}")
                    if info.get('best_time_to_visit'):
                        st.markdown(f"**📅 Best Time to Visit:** {info['best_time_to_visit']}")
                    if info.get('local_cuisine'):
                        st.markdown(f"**🍽️ Local Cuisine:** {', '.join(info['local_cuisine'][:3])}")
    else:
        with st.chat_message("user"):
            st.markdown(message["content"])

# Quick action buttons
if st.session_state.messages and st.session_state.messages[-1]["role"] == "assistant":
    st.write("Quick actions:")
    cols = st.columns(3)
    with cols[0]:
        if st.button("🌍 Get destination info", help="Learn more about this destination"):
            st.session_state.messages.append({"role": "user", "content": "Tell me more about this destination"})
            st.rerun()
    with cols[1]:
        if st.button("✈️ Find flights", help="Search for flight options"):
            st.session_state.messages.append({"role": "user", "content": "Show me flight options"})
            st.rerun()
    with cols[2]:
        if st.button("🏨 Find hotels", help="Search for hotel options"):
            st.session_state.messages.append({"role": "user", "content": "Show me hotel options"})
            st.rerun()

# Chat input
if prompt := st.chat_input("Type your message..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Show assistant response
    with st.chat_message("assistant", avatar="🗺️"):
        message_placeholder = st.empty()
        
        if search_mode == "Chat Mode":
            try:
                with st.spinner(""):
                    loading_animation()
                    
                    # Prepare chat request
                    chat_request = {
                        "message": prompt,
                        "context": st.session_state.context
                    }
                    
                    # Make API call
                    response = requests.post(CHAT_API_URL, json=chat_request)
                    
                    if response.status_code == 200:
                        result = response.json()
                        
                        # Display main response
                        message_placeholder.markdown(f"""
                        <div style='background-color:#1a2a3a;padding:1.5rem;border-radius:15px;border-left:4px solid #4682b4;'>
                            {result.get('chat_response', 'I encountered an error processing your request.')}
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Update context
                        if "context" in result:
                            st.session_state.context = result["context"]
                        
                        # Create assistant message with all data
                        assistant_message = {
                            "role": "assistant",
                            "content": result.get("chat_response", "")
                        }
                        
                        # Add any additional data to the message
                        if "flights" in result and result["flights"]:
                            assistant_message["flights"] = result["flights"]
                        if "hotels" in result and result["hotels"]:
                            assistant_message["hotels"] = result["hotels"]
                        if "destination_info" in result and result["destination_info"]:
                            assistant_message["destination_info"] = result["destination_info"]
                        
                        st.session_state.messages.append(assistant_message)
                        
                        # Check if we should show the travel form
                        if result.get("needs_details", False):
                            st.session_state.show_form = True
                    
                    else:
                        error_msg = f"Error: {response.json().get('detail', 'Unknown error')}"
                        message_placeholder.error(error_msg)
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": error_msg
                        })
            
            except Exception as e:
                error_msg = f"Sorry, I encountered an error: {str(e)}"
                message_placeholder.error(error_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg
                })
        
        else:  # Quick Search mode
            message_placeholder.info("Please fill out the travel details below")
            st.session_state.show_form = True

# Travel details form (shown when needed)
if st.session_state.show_form:
    with st.form(key="travel_details_form"):
        st.subheader("✈️ Travel Details")
        
        cols = st.columns([1, 1, 1])
        with cols[0]:
            origin = st.text_input("Departure City (IATA code)", "CGK")
            destination = st.text_input("Destination City", "Tokyo")
            adults = st.number_input("Adults", 1, 10, 2)
            
        with cols[1]:
            today = datetime.now().date()
            next_week = today + timedelta(days=7)
            outbound_date = st.date_input("Departure Date", today)
            return_date = st.date_input("Return Date", next_week)
            children = st.number_input("Children", 0, 10, 0)
            
        with cols[2]:
            st.subheader("Preferences")
            travel_class = st.selectbox("Class", ["Economy", "Premium Economy", "Business", "First"])
            budget = st.slider("Budget Range (USD)", 0, 10000, (200, 2000))
            min_rating = st.slider("Minimum Hotel Rating", 0.0, 5.0, 4.0, 0.5)
        
        submitted = st.form_submit_button("🔍 Search for Options")
        
        if submitted:
            if outbound_date >= return_date:
                st.error("Return date must be after departure date")
            else:
                with st.spinner("Searching for travel options..."):
                    try:
                        # Prepare requests
                        flight_request = {
                            "origin": origin,
                            "destination": destination,
                            "outbound_date": str(outbound_date),
                            "return_date": str(return_date)
                        }
                        
                        hotel_request = {
                            "location": destination,
                            "check_in_date": str(outbound_date),
                            "check_out_date": str(return_date),
                            "min_rating": min_rating
                        }
                        
                        # Make API call
                        response = requests.post(
                            COMPLETE_API_URL,
                            json={
                                "flight_request": flight_request,
                                "hotel_request": hotel_request
                            }
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            
                            # Format response
                            response_text = f"Here are travel options for your trip to {destination}:\n\n"
                            
                            if result.get("flights") and isinstance(result["flights"], list):
                                response_text += "**✈️ Flight Options:**\n"
                                for flight in result["flights"][:3]:
                                    response_text += (
                                        f"- {flight.get('airline', 'Unknown')}: "
                                        f"{flight.get('departure', 'N/A')} to {flight.get('arrival', 'N/A')} "
                                        f"(Duration: {flight.get('duration', 'N/A')}, "
                                        f"Price: ${flight.get('price', 'N/A')})\n"
                                    )
                            
                            if result.get("hotels") and isinstance(result["hotels"], list):
                                response_text += "\n**🏨 Hotel Options:**\n"
                                for hotel in result["hotels"][:3]:
                                    response_text += (
                                        f"- {hotel.get('name', 'Unknown')}: "
                                        f"${hotel.get('price', 'N/A')}/night, "
                                        f"Rating: {hotel.get('rating', 'N/A')}\n"
                                    )
                            
                            if result.get("ai_flight_recommendation"):
                                response_text += f"\n**AI Flight Recommendation:**\n{result['ai_flight_recommendation']}\n"
                            
                            if result.get("ai_hotel_recommendation"):
                                response_text += f"\n**AI Hotel Recommendation:**\n{result['ai_hotel_recommendation']}\n"
                            
                            if result.get("itinerary"):
                                response_text += f"\n**📅 Suggested Itinerary:**\n{result['itinerary']}\n"
                            
                            # Add to chat history
                            assistant_message = {
                                "role": "assistant",
                                "content": response_text
                            }
                            
                            # Add additional data if available
                            if "flights" in result and result["flights"]:
                                assistant_message["flights"] = result["flights"]
                            if "hotels" in result and result["hotels"]:
                                assistant_message["hotels"] = result["hotels"]
                            if "destination_info" in result and result["destination_info"]:
                                assistant_message["destination_info"] = result["destination_info"]
                            
                            st.session_state.messages.append(assistant_message)
                            st.session_state.show_form = False
                            st.rerun()
                        
                        else:
                            error_msg = f"Error: {response.json().get('detail', 'Unknown error')}"
                            st.error(error_msg)
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": error_msg
                            })
                    
                    except Exception as e:
                        error_msg = f"An error occurred: {str(e)}"
                        st.error(error_msg)
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": error_msg
                        })