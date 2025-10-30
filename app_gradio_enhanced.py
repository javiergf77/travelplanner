"""
Enhanced Travel Booker with Full Features
- CrewAI agents with Ollama
- Travel history analysis
- Trip enrichment
- Booking workflow
"""
import gradio as gr
from crew_setup_new import run_travel_crew
from tools.booking import execute_booking

GLOBAL_CSS = """
html { font-size: 100%; line-height: 1.4; }
h1 { margin-top: 0.5rem !important; margin-bottom: 0.5rem !important; }
h2, h3 { margin-top: 0.3rem !important; margin-bottom: 0.3rem !important; }
.gr-prose { margin: 0.5rem 0 !important; }
.gr-form { gap: 0.5rem !important; }
.gr-box { padding: 0.5rem !important; }
"""

# Store current trip plan globally for booking
current_packages = {}


def chat_fn(messages, origin, destination, depart_date, return_date, trip_purpose, budget, mode, use_crewai):
    """Main planning function"""
    user_msg = messages[-1]["content"] if messages else ""
    
    # Add processing message
    processing_msg = "🔄 Processing your travel request...\n\n"
    if use_crewai and mode == "local":
        processing_msg += "Using CrewAI agents with local Ollama LLM.\nThis may take 30-60 seconds for the first request.\n\n"
        processing_msg += "**Make sure Ollama is running:** `ollama serve`\n"
        processing_msg += "**Model required:** `ollama pull llama3.2`"
    else:
        processing_msg += "Using simple mode (direct tools, no LLM).\nThis is faster and doesn't require Ollama."
    
    messages.append({"role": "assistant", "content": processing_msg})
    yield messages
    
    # Run travel planning
    result = run_travel_crew(
        user_query=user_msg,
        origin=origin,
        destination=destination,
        depart_date=depart_date,
        return_date=return_date,
        trip_purpose=trip_purpose,
        budget=budget,
        mode=mode,
        use_crewai=use_crewai,
    )
    
    # Store the result for booking
    global current_packages
    current_packages = {
        'result': result,
        'origin': origin,
        'destination': destination,
        'depart_date': depart_date,
        'return_date': return_date,
        'budget': budget
    }
    
    # Replace processing message with results
    messages[-1] = {"role": "assistant", "content": result}
    yield messages  # Changed from return to yield


def book_package(package_number, origin, destination, depart_date, return_date):
    """Execute booking for selected package"""
    try:
        # In a real implementation, parse the package from the previous response
        # For now, create a mock booking
        from tools.web_search import search_flights, search_hotels
        
        flights = search_flights(origin, destination, depart_date, return_date)
        hotels = search_hotels(destination, depart_date, return_date, "1200")
        
        if not flights or not hotels:
            return "❌ Error: Could not find flight or hotel options"
        
        selected_package = {
            "flight": flights[int(package_number) - 1] if len(flights) >= int(package_number) else flights[0],
            "hotel": hotels[int(package_number) - 1] if len(hotels) >= int(package_number) else hotels[0],
            "checkin": depart_date,
            "checkout": return_date
        }
        
        confirmation = execute_booking(selected_package)
        return confirmation
        
    except Exception as e:
        return f"❌ Booking error: {str(e)}"


with gr.Blocks(css=GLOBAL_CSS, title="AI Travel Booker") as demo:
    gr.Markdown("## 🧭 AI Travel Booker - Corporate Edition - Corporate Edition - Made by The Fellowship of the LLM 🗡🏹🪓")
    
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("""
            **Features:**
            - 🤖 CrewAI agents (local LLM)
            - 📊 Learns from travel history
            - 🛡️ Policy compliance
            """)
        with gr.Column(scale=1):
            gr.Markdown("""
            **Intelligence:**
            - 🌍 Destination research
            - ✈️ Smart recommendations
            - 💰 Budget optimization
            """)
    
    with gr.Row():
        with gr.Column(scale=2):
            chatbot = gr.Chatbot(
                type="messages",
                height=350,
                show_copy_button=True,
                avatar_images=(None, "🤖")
            )
            
            with gr.Row():
                user_in = gr.Textbox(
                    label="Your request",
                    placeholder="e.g., I need to visit our NYC office next week for client meetings",
                    scale=4
                )
                send_btn = gr.Button("🚀 Plan Trip", variant="primary", scale=1)
            
            # Booking section
            gr.Markdown("**💳 Ready to Book?** Select package & confirm:")
            
            package_selector = gr.Radio(
                choices=[
                    "📦 Package 1 - Best Value",
                    "📦 Package 2 - Preferred Airlines", 
                    "📦 Package 3 - Premium Option"
                ],
                label="",
                value="📦 Package 1 - Best Value",
                interactive=True,
                show_label=False
            )
            
            book_btn = gr.Button("✅ Confirm & Book", variant="primary", size="lg")
            booking_result = gr.Markdown()
        
        with gr.Column(scale=1):
            gr.Markdown("**📋 Trip Details**")
            
            with gr.Row():
                origin = gr.Textbox(label="🛫 From", value="Dallas", scale=1)
                destination = gr.Textbox(label="🛬 To", value="Raleigh", scale=1)
            
            with gr.Row():
                depart_date = gr.Textbox(label="📅 Depart", value="2025-11-05", scale=1)
                return_date = gr.Textbox(label="📅 Return", value="2025-11-08", scale=1)
            
            trip_purpose = gr.Textbox(label="💼 Purpose", value="Client meeting")
            budget = gr.Textbox(label="💰 Budget", value="1500")
            
            gr.Markdown("**⚙️ AI Settings**")
            
            use_crewai = gr.Checkbox(
                label="🤖 Use CrewAI Multi-Agent System",
                value=False,
                info="Enable to see AI agents collaborate and reason about your request (Requires Ollama running)"
            )
            
            mode = gr.Radio(
                ["local", "online"],
                value="local",
                label="Mode",
                show_label=False
            )
            
            gr.Markdown("""
            **Files:** `travel_history.xlsx`, `profile.json`, `policy.md`
            
            📖 [README.md](README.md) for full documentation
            """)
    
    def on_send(msg, chat_history, origin, destination, depart_date, return_date, trip_purpose, budget, mode, use_crewai):
        # Append user message
        chat_history = chat_history + [{"role": "user", "content": msg}]
        
        # Stream the response
        final_history = chat_history
        for updated_history in chat_fn(
            chat_history,
            origin,
            destination,
            depart_date,
            return_date,
            trip_purpose,
            budget,
            mode,
            use_crewai
        ):
            final_history = updated_history
            yield "", updated_history
        
        # Return final state
        return "", final_history
    
    def on_book(package_choice):
        """Handle booking when user clicks Confirm & Book"""
        global current_packages
        
        if not current_packages:
            return "⚠️ **Please plan a trip first before booking!**\n\nEnter your travel request above and click 'Plan Trip'."
        
        # Extract package number (1, 2, or 3)
        if "Package 1" in package_choice:
            package_num = "1"
            package_name = "Best Value"
        elif "Package 2" in package_choice:
            package_num = "2"
            package_name = "Preferred Airlines"
        elif "Package 3" in package_choice:
            package_num = "3"
            package_name = "Premium Option"
        else:
            package_num = "1"
            package_name = "Best Value"
        
        # Get trip details from stored packages
        origin = current_packages.get('origin', 'Unknown')
        destination = current_packages.get('destination', 'Unknown')
        depart_date = current_packages.get('depart_date', 'Unknown')
        return_date = current_packages.get('return_date', 'Unknown')
        
        # Show processing message
        processing = f"🔄 **Processing your booking...**\n\n📦 Selected: Package {package_num} - {package_name}\n✈️ Route: {origin} → {destination}"
        
        # Execute booking
        confirmation = book_package(package_num, origin, destination, depart_date, return_date)
        
        # Add success header
        final_confirmation = f"# ✅ Booking Confirmed!\n\n{confirmation}"
        
        return final_confirmation
    
    # Event handlers
    send_btn.click(
        on_send,
        inputs=[user_in, chatbot, origin, destination, depart_date, return_date, trip_purpose, budget, mode, use_crewai],
        outputs=[user_in, chatbot],
    )
    
    user_in.submit(
        on_send,
        inputs=[user_in, chatbot, origin, destination, depart_date, return_date, trip_purpose, budget, mode, use_crewai],
        outputs=[user_in, chatbot],
    )
    
    book_btn.click(
        on_book,
        inputs=[package_selector],
        outputs=[booking_result]
    )


if __name__ == "__main__":
    print("\n" + "="*60)
    print("🚀 AI Travel Booker - Corporate Edition")
    print("="*60)
    print("\n📂 Data Files:")
    print("   • data/sample_travel_history.xlsx - Travel history")
    print("   • data/travel_profile.json - User profile")
    print("   • data/company_policy.md - Company policy")
    print("\n🤖 AI Modes:")
    print("   • Simple Mode: Fast, no LLM needed (default)")
    print("   • CrewAI Mode: Full agents, requires Ollama")
    print("\n🔧 To use CrewAI mode:")
    print("   1. Install Ollama: https://ollama.com")
    print("   2. Run: ollama serve")
    print("   3. Install model: ollama pull llama3.2")
    print("\n" + "="*60)
    print("✨ Starting Gradio interface...")
    print("="*60 + "\n")
    
    demo.launch(
        server_port=7860,
        share=False,
        inbrowser=True  # This is the "magic" that makes the web address open automatically in your default browser! 🎩✨
    )
    
    print("\n" + "="*60)
    print("✅ If browser didn't open automatically, go to:")
    print("   👉 http://localhost:7860")
    print("   👉 http://127.0.0.1:7860")
    print("\n   Press Ctrl+C to stop the server")
    print("="*60)

