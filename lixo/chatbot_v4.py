import gradio as gr
import openai
import time


vector_store


assistant = openai.beta.assistants.create(
    name="Consultor de Documentos",
    instructions="Use os arquivos fornecidos para responder perguntas. Sempre cite suas fontes.",
    tools=[{"type": "file_search"}],
    model="gpt-4-1106-preview"
)

def responder(pergunta, arquivo_pdf):
    if not pergunta or not arquivo_pdf:
        return "⚠️ Por favor, envie um PDF e escreva uma pergunta."

    # 1. Upload do arquivo
    uploaded_file = openai.files.create(
        file=open(arquivo_pdf.name, "rb"),
        purpose="assistants"
    )

    # 2. Criar novo thread
    thread = openai.beta.threads.create()

    # 3. Adicionar a pergunta (sem anexar arquivo aqui)
    openai.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=pergunta
    )

    # 4. Criar o run e anexar o arquivo aqui via 'attachments'
    run = openai.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id,
        attachments=[{
            "file_id": uploaded_file.id,
            "tools": [{"type": "file_search"}]
        }]
    )

    # 5. Esperar a execução terminar
    while True:
        status = openai.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
        if status.status == "completed":
            break
        time.sleep(1)

    # 6. Obter a resposta
    messages = openai.beta.threads.messages.list(thread_id=thread.id)

    resposta_final = ""
    for msg in reversed(messages.data):
        if msg.role == "assistant":
            resposta_final += f"💬 **Resposta:**\n{msg.content[0].text.value}\n\n"

            # Citações (file_search)
            annotations = msg.content[0].text.annotations
            for ann in annotations:
                if ann.type == "file_citation":
                    citation = ann.file_citation
                    fonte = openai.files.retrieve(citation.file_id)
                    resposta_final += f"📚 **Fonte**: `{fonte.filename}`\nTrecho: _{citation.quote}_\n\n"
            break

    return resposta_final or "⚠️ Não foi possível gerar uma resposta."

# Interface Gradio
gr.Interface(
    fn=responder,
    inputs=[
        gr.Textbox(label="Digite sua pergunta"),
        gr.File(label="Envie um PDF", file_types=[".pdf"])
    ],
    outputs=gr.Markdown(label="Resposta com Fonte"),
    title="📚 RAG com OpenAI Assistants API",
    description="Envie um PDF e faça perguntas sobre ele. GPT-4 irá responder com base no conteúdo e citar a fonte."
).launch()
