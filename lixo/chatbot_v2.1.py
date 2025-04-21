import openai
import gradio as gr
import time
import base64
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

def download_pdf():
    return gr.File("documento.pdf")

with gr.Blocks(title="Conversa sobre raciocíonio probabilístico", css=css) as iface:

    with gr.Row():
        with gr.Column(scale=1):

            download_btn = gr.Button("Download PDF")
            file_output = gr.File(label="Arquivo PDF")
            download_btn.click(fn=download_pdf, inputs=None, outputs=file_output)
    
            resumo_btn = gr.Button("Faça um Resumo")
            guia_btn = gr.Button("Gere um Guia de estudo")
            gere_questoes_btn = gr.Button("Gere questões")
            perguntas_frequentes_btn = gr.Button("Quais são as Perguntas frequentes")
            
        with gr.Column(scale=4):
            chatbot = gr.Chatbot(height=350,  label="Chatbot")
            textbox = gr.Textbox(placeholder="Digite sua mensagem aqui...", label="Mensagem")
            state = gr.State(None)
            clear_button = gr.Button("Limpar")
            gr.Markdown("<div class='centered-text'>Criado por Giseldo Neo 2025.</div>") 

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

    def resumo_click(chat_history, thread_id=None):
        return respond("Resuma o documento", chat_history, thread_id)
    def guia_btn_click(chat_history, thread_id=None):
        return respond("Gere um Guia de estudo", chat_history, thread_id)
    def gere_questoes_click(chat_history, thread_id=None):
        return respond("Gere questões", chat_history, thread_id)
    def perguntas_frequentes_click(chat_history, thread_id=None):
        return respond("Gere perguntas frequentes", chat_history, thread_id)

    textbox.submit(respond, [textbox, chatbot, state], [textbox, chatbot, state])
    clear_button.click(clear, None, [state, chatbot, state])
    
    resumo_btn.click(resumo_click, [chatbot, state], [textbox, chatbot, state])
    guia_btn.click(guia_btn_click, [chatbot, state], [textbox, chatbot, state])
    gere_questoes_btn.click(gere_questoes_click, [chatbot, state], [textbox, chatbot, state])
    perguntas_frequentes_btn.click(perguntas_frequentes_click, [chatbot, state], [textbox, chatbot, state])

iface.launch()