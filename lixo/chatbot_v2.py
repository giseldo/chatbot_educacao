import openai
import gradio as gr
import time
import os

# openai.api_key = os.environ["OPENAI_API_KEY"]
assistant_id = "asst_T1h8P9nGszxDp4P7S7g64XJ9"

def assistant_response(message, history, thread_id=None):
    if thread_id is None:
        thread = openai.beta.threads.create()
        thread_id = thread.id

    openai.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=message
    )

    run = openai.beta.threads.runs.create(
         thread_id=thread_id,
         assistant_id=assistant_id
    )

    while run.status in ['queued', 'in_progress']:
        run = openai.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run.id
        )
        time.sleep(1)

    messages = openai.beta.threads.messages.list(thread_id=thread_id)
    assistant_message = messages.data[0].content[0].text.value
    return assistant_message, thread_id

css = """
footer {display: none !important;}
.centered-text {
    text-align: center;
}
"""

with gr.Blocks(title="Conversa sobre raciocíonio probabilístico", css=css) as iface:

    chatbot = gr.Chatbot(height=350,  label="Chatbot")
    textbox = gr.Textbox(placeholder="Digite sua mensagem aqui...", label="Mensagem")
    state = gr.State(None)
    clear_button = gr.Button("Limpar")
    
    gr.Markdown("<div class='centered-text'>Criado por Giseldo Neo.</div>") 
    def respond(message, chat_history, thread_id=None):
        if thread_id is None:
            thread_id = state.value
            if thread_id is None:
                thread = openai.beta.threads.create()
                thread_id = thread.id
        bot_message, thread_id = assistant_response(message, chat_history, thread_id)
        chat_history.append((message, bot_message))
        return "", chat_history, thread_id

    def clear():
        return None, [], None

    textbox.submit(respond, [textbox, chatbot, state], [textbox, chatbot, state])
    clear_button.click(clear, None, [state, chatbot, state])

iface.launch()