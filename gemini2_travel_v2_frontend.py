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

import streamlit as st
import requests
from datetime import datetime, timedelta
import json

# API URLs
API_BASE_URL = "http://localhost:8000"
CHAT_API_URL = f"{API_BASE_URL}/chat/"
RESET_API_URL = f"{API_BASE_URL}/start_over/"

# Page configuration
st.set_page_config(
    page_title="✈️ Asia Travel Chatbot",
    page_icon="🗾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I'm your Asia Travel Assistant. Where in Asia would you like to visit?"}
    ]

# Initialize form state
if "show_form" not in st.session_state:
    st.session_state.show_form = False

# Sidebar for additional options
with st.sidebar:
    st.title("⚙️ Chat Options")
    st.markdown("---")
    if st.button("🔄 Start New Conversation"):
        try:
            response = requests.post(RESET_API_URL)
            if response.status_code == 200:
                st.session_state.messages = [
                    {"role": "assistant", "content": "Let's start over! Where in Asia would you like to visit?"}
                ]
                st.session_state.show_form = False
                st.rerun()
        except Exception as e:
            st.error(f"Error resetting conversation: {str(e)}")
    
    st.markdown("---")
    st.caption("Asia Travel Chatbot v2.0")
    st.caption("Specializing in Asian destinations")

# Main header
st.title("🗾 Asia Travel Chatbot")
st.markdown("Plan your perfect Asian adventure with our AI assistant!")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        # Display flight/hotel cards if present in message
        if "flights" in message:
            with st.expander("✈️ Flight Options"):
                for flight in message["flights"][:3]:
                    st.markdown(f"""
                    **{flight['airline']}**  
                    🕒 {flight['departure']} → {flight['arrival']}  
                    ⏱️ {flight['duration']} • 🛑 {flight['stops']}  
                    💰 ${flight['price']}  
                    {'🇦🇸 Asian airline' if flight['is_asian'] else ''}
                    """)
                    st.markdown("---")
        
        if "hotels" in message:
            with st.expander("🏨 Hotel Options"):
                for hotel in message["hotels"][:3]:
                    st.markdown(f"""
                    **{hotel['name']}**  
                    ⭐ {hotel['rating']}/10 • 💰 ${hotel['price']}/night  
                    📍 {hotel['location']}  
                    {'🏯 Asian hospitality' if hotel['asian_hospitality'] else ''}
                    """)
                    st.markdown("---")

# Chat input
if prompt := st.chat_input("Type your message..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Show assistant response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        # Prepare chat request
        chat_request = {
            "conversation": st.session_state.messages[:-1],  # All except the last user message
            "current_input": prompt
        }
        
        try:
            with st.spinner("Thinking..."):
                response = requests.post(CHAT_API_URL, json=chat_request)
                
                if response.status_code == 200:
                    result = response.json()
                    full_response = result["response"]
                    
                    # Display response incrementally
                    message_placeholder.markdown(full_response + "▌")
                    message_placeholder.markdown(full_response)
                    
                    # Add to chat history
                    new_message = {"role": "assistant", "content": full_response}
                    
                    # Check if we need to show the travel form
                    if "needs_more_info" in result and result["needs_more_info"]:
                        st.session_state.show_form = True
                    
                    # Add any suggestions as quick replies
                    if "suggestions" in result and result["suggestions"]:
                        with st.container():
                            st.write("Quick suggestions:")
                            cols = st.columns(len(result["suggestions"]))
                            for i, suggestion in enumerate(result["suggestions"]):
                                with cols[i]:
                                    if st.button(suggestion):
                                        # Add the suggestion as a user message
                                        st.session_state.messages.append({"role": "user", "content": suggestion})
                                        st.rerun()
                    
                    st.session_state.messages.append(new_message)
                
                else:
                    error_msg = f"Error: {response.json().get('detail', 'Unknown error')}"
                    message_placeholder.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
        
        except Exception as e:
            error_msg = f"Sorry, I encountered an error: {str(e)}"
            message_placeholder.error(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})

# Travel details form (shown when needed)
if st.session_state.show_form:
    with st.form(key="travel_details_form"):
        st.subheader("✈️ Tell me more about your trip")
        
        cols = st.columns(2)
        with cols[0]:
            destination = st.text_input("Asian destination you want to visit", "Tokyo")
            origin = st.text_input("Your departure city", "Jakarta")
            
            # Set default dates
            today = datetime.now()
            next_month = today + timedelta(days=30)
            
            travel_dates = st.date_input(
                "When will you travel?",
                (today, next_month),
                format="MM/DD/YYYY"
            )
        
        with cols[1]:
            interests = st.multiselect(
                "What are you interested in?",
                ["Cultural sites", "Beaches", "Shopping", "Food", "Nature", "Adventure"],
                ["Cultural sites", "Food"]
            )
            
            budget = st.select_slider(
                "Your budget level",
                options=["Budget", "Mid-range", "Luxury"],
                value="Mid-range"
            )
        
        submitted = st.form_submit_button("Plan My Trip")
        
        if submitted:
            if len(travel_dates) != 2:
                st.error("Please select both departure and return dates")
            else:
                # Prepare travel plan
                travel_plan = {
                    "destination": destination,
                    "origin": origin,
                    "departure_date": str(travel_dates[0]),
                    "return_date": str(travel_dates[1]),
                    "interests": interests,
                    "budget": budget
                }
                
                # Add to chat history
                st.session_state.messages.append({
                    "role": "user",
                    "content": f"I want to visit {destination} from {travel_dates[0]} to {travel_dates[1]}. My interests are {', '.join(interests)} and my budget is {budget}."
                })
                
                # Show assistant is thinking
                with st.chat_message("assistant"):
                    message_placeholder = st.empty()
                    message_placeholder.markdown("Searching for the best Asian travel options...▌")
                    
                    try:
                        # Call API to get travel recommendations
                        chat_request = {
                            "conversation": st.session_state.messages,
                            "current_input": json.dumps(travel_plan)
                        }
                        
                        response = requests.post(CHAT_API_URL, json=chat_request)
                        
                        if response.status_code == 200:
                            result = response.json()
                            full_response = result["response"]
                            
                            # Display the response
                            message_placeholder.markdown(full_response)
                            
                            # Add to chat history
                            new_message = {"role": "assistant", "content": full_response}
                            
                            # Add any data cards
                            if "flights" in result:
                                new_message["flights"] = result["flights"]
                            
                            if "hotels" in result:
                                new_message["hotels"] = result["hotels"]
                            
                            st.session_state.messages.append(new_message)
                            st.session_state.show_form = False
                            st.rerun()
                        
                        else:
                            error_msg = f"Error: {response.json().get('detail', 'Unknown error')}"
                            message_placeholder.error(error_msg)
                            st.session_state.messages.append({"role": "assistant", "content": error_msg})
                    
                    except Exception as e:
                        error_msg = f"Sorry, I encountered an error: {str(e)}"
                        message_placeholder.error(error_msg)
                        st.session_state.messages.append({"role": "assistant", "content": error_msg})