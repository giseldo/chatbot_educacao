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
.full-height-chatbot {
    height: 100%;
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
    
            resumo_btn = gr.Button("Faça um resumo do documento")
            guia_btn = gr.Button("Gere um Guia de estudo do documento")
            gere_questoes_btn = gr.Button("Gere questões sobre o documento")
            perguntas_frequentes_btn = gr.Button("Gere Perguntas frequentes do doccumento")
            diagrama_btn = gr.Button("Gere um diagrama")
            
            gr.Markdown("<div class='centered-text'>Criado por Giseldo Neo 2025.</div>") 

        with gr.Column(scale=4):
            chatbot = gr.Chatbot(label="Chatbot", elem_id="main-chatbot", elem_classes=["full-height-chatbot"])
            textbox = gr.Textbox(placeholder="Digite sua mensagem aqui...", label="Mensagem")
            state = gr.State(None)
            clear_button = gr.Button("Limpar")

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
        return respond("Resuma o conteúdo disponível nos arquivos carregados", chat_history, thread_id)
    def guia_btn_click(chat_history, thread_id=None):
        return respond("Gere um Guia de estudo a partir do conteúdo disponível nos arquivos carregados", chat_history, thread_id)
    def gere_questoes_btn_click(chat_history, thread_id=None):
        return respond("Gere questões", chat_history, thread_id)
    def perguntas_btn_frequentes_click(chat_history, thread_id=None):
        return respond("Gere perguntas frequentes a partir do conteúdo disponível nos arquivos carregados", chat_history, thread_id)
    def diagrama_btn_click(chat_history, thread_id=None):
        return respond("gere um diagrama mermaid com os principais topicos do conteúdo disponível nos arquivos carregados", chat_history, thread_id)

    textbox.submit(respond, [textbox, chatbot, state], [textbox, chatbot, state])
    clear_button.click(clear, None, [state, chatbot, state])
    
    resumo_btn.click(resumo_click, [chatbot, state], [textbox, chatbot, state])
    guia_btn.click(guia_btn_click, [chatbot, state], [textbox, chatbot, state])
    gere_questoes_btn.click(gere_questoes_btn_click, [chatbot, state], [textbox, chatbot, state])
    perguntas_frequentes_btn.click(perguntas_btn_frequentes_click, [chatbot, state], [textbox, chatbot, state])

    diagrama_btn.click(diagrama_btn_click, [chatbot, state], [textbox, chatbot, state])
    
    

iface.launch()