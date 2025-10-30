import gradio as gr
from crew_setup import run_travel_crew

# Gradio "fundamentals" template baseline (your preferred layout)
GLOBAL_CSS = """
html { font-size: 125%; line-height: 1.55; }
#status_box { min-height: 120px; }
#mode_radio label { font-size: 0.95rem; }
"""

def chat_fn(messages, origin, destination, depart_date, return_date, trip_purpose, budget, mode):
    # messages is the whole chat history (list of dicts)
    user_msg = messages[-1]["content"] if messages else ""
    result = run_travel_crew(
        user_query=user_msg,
        origin=origin,
        destination=destination,
        depart_date=depart_date,
        return_date=return_date,
        trip_purpose=trip_purpose,
        budget=budget,
        mode=mode,
    )

    # append assistant message
    messages.append({"role": "assistant", "content": result})
    return messages

with gr.Blocks(css=GLOBAL_CSS, title="Travel Booker 2.0") as demo:
    gr.Markdown("## 🧭 Travel Booker 2.0\nPlan trips with policy-aware agents (CrewAI)")

    with gr.Row():
        with gr.Column(scale=2):
            chatbot = gr.Chatbot(type="messages", height=450, show_copy_button=True)

            with gr.Row():
                user_in = gr.Textbox(label="Message", placeholder="e.g. I need to go to NYC next week")
                send_btn = gr.Button("Send")

        with gr.Column(scale=1):
            origin = gr.Textbox(label="Origin", value="Chicago")
            destination = gr.Textbox(label="Destination", value="New York")
            depart_date = gr.Textbox(label="Depart date (YYYY-MM-DD)", value="2025-11-05")
            return_date = gr.Textbox(label="Return date (YYYY-MM-DD)", value="2025-11-08")
            trip_purpose = gr.Textbox(label="Trip purpose", value="Client meeting")
            budget = gr.Textbox(label="Budget (USD)", value="1200")
            mode = gr.Radio(
                ["local", "online"],
                value="local",
                label="LLM mode",
                elem_id="mode_radio",
            )
            gr.Markdown(
                "ℹ️ **local** = use local/runtime-friendly models; **online** = assume remote API",
                elem_id="status_box",
            )

    def on_send(msg, chat_history, origin, destination, depart_date, return_date, trip_purpose, budget, mode):
        # append user
        chat_history = chat_history + [{"role": "user", "content": msg}]
        out_history = chat_fn(
            chat_history,
            origin,
            destination,
            depart_date,
            return_date,
            trip_purpose,
            budget,
            mode,
        )
        return "", out_history

    send_btn.click(
        on_send,
        inputs=[user_in, chatbot, origin, destination, depart_date, return_date, trip_purpose, budget, mode],
        outputs=[user_in, chatbot],
    )

    user_in.submit(
        on_send,
        inputs=[user_in, chatbot, origin, destination, depart_date, return_date, trip_purpose, budget, mode],
        outputs=[user_in, chatbot],
    )

if __name__ == "__main__":
    print("\n✨ Starting Gradio interface...")
    demo.launch()