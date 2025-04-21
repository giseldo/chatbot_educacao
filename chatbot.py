import gradio as gr
import openai
import time
from openai import OpenAI

client = OpenAI()

vector_store_id = "vs_68055e977e3c81919eee2394f47c2f6c"


def responder(mensagem, historico, btn_resumo, btn_diagrama):

    # criar um novo assistente
    assistant = client.beta.assistants.create(
        name="IA Tutor",
        instructions="""Você é um assistente especializado em responder perguntas com base exclusivamente no conteúdo do documento fornecido.
        Antes de responder, consulte sua base de dados vetorial para recuperar trechos relevantes.
        Responda de forma clara, objetiva e baseada nas informações do documento.
        Se a resposta não estiver no documento, diga explicitamente: 'Esta informação não está presente no documento.'
        Não invente respostas nem use conhecimento externo.""",
        model="gpt-4.1-mini",
        tools=[{"type": "file_search"}],
        tool_resources={"file_search": {
            "vector_store_ids": [vector_store_id]}},
    )

    # criar uma tread para o assistente
    thread = client.beta.threads.create()

    # executar o assistente
    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread.id,
        assistant_id=assistant.id,
        instructions=mensagem
    )

    # verifico o estado
    while run.status in ['queued', 'in_progress']:
        run = openai.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
        )
        time.sleep(1)

    # busca as mensagens de retorno
    messages = client.beta.threads.messages.list(thread_id=thread.id)
    assistant_message = messages.data[0].content[0].text.value

    return assistant_message


btn_resumo = gr.Button("Resumo")
btn_diagrama = gr.Button("Diagrama")

iface = gr.ChatInterface(
    responder,
    title="Chatbot de Educação",
    description="Um chatbot simples usando Gradio.",
    additional_inputs=[btn_resumo, btn_diagrama],
)

if __name__ == "__main__":
    iface.launch()
