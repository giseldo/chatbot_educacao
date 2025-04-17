from dotenv import load_dotenv
import gradio as gr
from openai import OpenAI
import os

load_dotenv()  # Carregar variáveis de ambiente do arquivo .env

USUARIO = os.environ.get("USUARIO")
SENHA = os.environ.get("SENHA")

client = OpenAI()

def process_message(message, history, temperature=1.0, max_tokens=2048, top_p=1.0, model="gpt-4.1", system_prompt=""):
    
    # Verificar se já existe uma mensagem do sistema no início do histórico
    system_message_exists = any(msg.get("role") == "system" for msg in history)
    
    # Se não existir e o system_prompt não estiver vazio, adicionar no início do histórico
    if not system_message_exists and system_prompt.strip():
        history.insert(0, {"role": "system", "content": system_prompt})
    
    history.append({"role": "user", "content": message})
    
    # Filtrar o histórico e remover metadata e options
    filtered_history = []
    for msg in history:
        if msg.get("role") in ["user", "system", "assistant"]:
            # Criar novo dicionário apenas com role e content
            filtered_msg = {
                "role": msg["role"],
                "content": msg["content"]
            }
            filtered_history.append(filtered_msg)
    
    print(history)

    response = client.responses.create(
        model=model, 
        input=filtered_history,  # Usando o histórico filtrado
        text={
            "format": {
                "type": "text"
            }
        },
        reasoning={},
        
        tools=[
        {
            "type": "file_search",
            "vector_store_ids": [
                "vs_680171e31fcc8191937768624f4f4a18"
            ]
        }
        ],
        
        temperature=temperature,  # Use as variáveis de parâmetros
        max_output_tokens=max_tokens,  # Corrigido de max_output_tokens para max_tokens
        top_p=top_p,
        store=True
    )
    
    # Atualize para obter o texto da resposta do objeto de resposta corretamente
    history.append({"role": "assistant", "content": response.output_text})
    return "", history

with gr.Blocks() as interface:
    with gr.Row():
        with gr.Column():
            history = gr.Chatbot(type='messages')
            msg = gr.Textbox(label="Mensagem")
            clear = gr.Button("Limpar")
        
        with gr.Column():
            system_prompt = gr.Textbox(
                label="Prompt do Sistema",
                value="Você é um assistente inteligente treinado para responder exclusivamente com base nas informações fornecidas nos documentos anexados (armazenados na base vetorial).\nNunca forneça respostas baseadas em conhecimento próprio, conhecimento geral, ou treinamento anterior.\nSe a resposta à pergunta não estiver clara ou presente nos documentos fornecidos, responda educadamente que você não tem essa informação.\n",
                lines=3,
                info="Define o comportamento base do assistente"
            )
            model = gr.Dropdown(
                choices=["gpt-4.1", "GPT-4.1-mini", "GPT-4.1-nano"],
                value="gpt-4.1",
                label="Modelo",
                info="Selecione o modelo de linguagem"
            )
            temperature = gr.Slider(
                minimum=0.0,
                maximum=2.0,
                value=1.0,
                step=0.1,
                label="Temperatura",
                info="Controla a aleatoriedade das respostas (0=focado, 2=criativo)"
            )
            max_tokens = gr.Slider(
                minimum=256,
                maximum=4096,
                value=4096,
                step=256,
                label="Tokens máximos",
                info="Limite máximo de tokens na resposta"
            )
            top_p = gr.Slider(
                minimum=0.0,
                maximum=1.0,
                value=1.0,
                step=0.1,
                label="Top P",
                info="Controla a diversidade das respostas"
            )
    
    msg.submit(process_message, 
              [msg, history, temperature, max_tokens, top_p, model, system_prompt], 
              [msg, history])
    # clear.click(lambda: None, None, history, queue=False)

if __name__ == "__main__": 
    interface.launch(auth=(USUARIO, SENHA))