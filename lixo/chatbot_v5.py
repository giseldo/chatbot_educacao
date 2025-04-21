import gradio as gr
import openai
import time
from pathlib import Path

# Inicializa cliente OpenAI (certifique-se de ter sua chave API configurada via OPENAI_API_KEY)
client = openai.OpenAI()

# Criação do Vector Store (executado uma vez por sessão)
vector_store = client.vector_stores.create(name="Base RAG Giseldo")

# Criação do assistente com file_search apontando para o Vector Store
assistant = client.beta.assistants.create(
    name="Consultor de Documentos PDF",
    instructions="Responda com base nos arquivos fornecidos e cite sempre a fonte.",
    model="gpt-4-1106-preview",
    tools=[{"type": "file_search"}],
    tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}}
)

# Função principal chamada pelo Gradio
def responder(pergunta, arquivo_pdf):
    if not pergunta or not arquivo_pdf:
        return "⚠️ Por favor, envie um PDF e escreva uma pergunta."

    # ✅ Caminho robusto para o arquivo (compatível com diferentes versões do Gradio)
    file_path = Path(arquivo_pdf.name if hasattr(arquivo_pdf, "name") else arquivo_pdf)

    # Upload do arquivo para a OpenAI
    with file_path.open("rb") as f:
        file_upload = client.files.create(file=f, purpose="assistants")

    # Envia o arquivo ao Vector Store e aguarda o processamento
    client.vector_stores.file_batches.upload_and_poll(
        vector_store_id=vector_store.id,
        files=[file_upload.id]
    )

    # Cria um novo thread de conversa
    thread = client.beta.threads.create()

    # Envia a pergunta do usuário ao thread
    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=pergunta
    )

    # Executa o assistente
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id
    )

    # Aguarda a execução terminar
    while True:
        status = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
        if status.status == "completed":
            break
        time.sleep(1)

    # Recupera as mensagens geradas
    messages = client.beta.threads.messages.list(thread_id=thread.id)

    resposta_final = ""
    for msg in reversed(messages.data):
        if msg.role == "assistant":
            resposta_final += f"💬 **Resposta:**\n{msg.content[0].text.value}\n\n"

            # Verifica e exibe citações
            annotations = msg.content[0].text.annotations
            for ann in annotations:
                if ann.type == "file_citation":
                    citation = ann.file_citation
                    fonte = client.files.retrieve(citation.file_id)
                    resposta_final += f"📚 **Fonte**: `{fonte.filename}`\nTrecho: _{citation.quote}_\n\n"
            break

    return resposta_final or "⚠️ Nenhuma resposta foi gerada."

# Interface Gradio
gr.Interface(
    fn=responder,
    inputs=[
        gr.Textbox(label="Digite sua pergunta"),
        gr.File(label="Envie um PDF", file_types=[".pdf"])
    ],
    outputs=gr.Markdown(label="Resposta com Fonte"),
    title="🔍 RAG com OpenAI Assistants + GPT-4",
    description="Envie um PDF e faça perguntas sobre ele. O assistente responderá com base no conteúdo e citará a fonte."
).launch()
