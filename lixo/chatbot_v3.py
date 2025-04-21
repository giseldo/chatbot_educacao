import gradio as gr
import openai
import time

assistant = openai.beta.assistants.create(
    name="Consultor de Documentos",
    instructions="Use os arquivos enviados para responder. Cite sempre a fonte.",
    tools=[{"type": "file_search"}],
    model="gpt-4o"
)

# 2. Função principal para interação
def responder(pergunta, arquivo_pdf):
    if not pergunta or not arquivo_pdf:
        return "Envie um arquivo PDF e uma pergunta."

    # Upload do arquivo para a OpenAI
    uploaded_file = openai.files.create(
        file=open(arquivo_pdf.name, "rb"),
        purpose="assistants"
    )

    
    thread = openai.beta.threads.create()

    openai.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=pergunta
    )

    run = openai.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id,
        tools=[{"type": "file_search"}],
        file_ids=[uploaded_file.id]     
    )

    # # Enviar pergunta com o arquivo
    # openai.beta.threads.messages.create(
    #     thread_id=thread.id,
    #     role="user",
    #     content=pergunta,
    #     file_ids=[uploaded_file.id]
    # )

    # # Rodar o assistant
    # run = openai.beta.threads.runs.create(
    #     thread_id=thread.id,
    #     assistant_id=assistant.id
    # )

    # Aguardar conclusão
    while True:
        status = openai.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
        if status.status == "completed":
            break
        time.sleep(1)

    # Obter resposta
    messages = openai.beta.threads.messages.list(thread_id=thread.id)

    resposta_final = ""
    for msg in messages.data:
        if msg.role == "assistant":
            resposta_final += f"💬 **Resposta**:\n{msg.content[0].text.value}\n\n"

            # Citações
            annotations = msg.content[0].text.annotations
            for ann in annotations:
                if ann.type == "file_citation":
                    citation = ann.file_citation
                    fonte = openai.files.retrieve(citation.file_id)
                    resposta_final += f"📚 **Fonte**: `{fonte.filename}`\nTrecho: _{citation.quote}_\n\n"

    return resposta_final

# 3. Interface Gradio
gr.Interface(
    fn=responder,
    inputs=[
        gr.Textbox(label="Digite sua pergunta"),
        gr.File(label="Envie um PDF", file_types=[".pdf"])
    ],
    outputs=gr.Markdown(label="Resposta com Fonte"),
    title="RAG com Assistants API",
    description="Faça perguntas com base em documentos PDF. A resposta será gerada usando GPT-4 com citação da fonte."
).launch()
