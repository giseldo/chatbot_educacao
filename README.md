# Chatbot Educacional com RAG

Este projeto implementa um chatbot utilizando a API da OpenAI e a biblioteca Gradio para a interface gráfica. O chatbot é projetado para responder perguntas com base em um conjunto específico de documentos, utilizando a técnica de Retrieval-Augmented Generation (RAG) através de uma base vetorial (vector store) da OpenAI.

## Estrutura do Projeto

*   `.venv/`: Diretório do ambiente virtual (ignorado pelo Git).
*   `doc/`: Diretório para documentos (ignorado pelo Git).
*   `.env`: Arquivo para armazenar variáveis de ambiente (necessário criar manualmente).
*   `.gitignore`: Especifica arquivos e diretórios ignorados pelo Git.
*   `chatbot.py`: Script principal que executa a interface do Gradio e interage com a API da OpenAI.
*   `requirements.txt`: Lista as dependências Python do projeto.
*   `README.md`: Este arquivo.

## Configuração

1.  **Clone o repositório:**
    ```bash
    git clone <url-do-seu-repositorio>
    cd chatbot_educacao
    ```

2.  **Crie e ative um ambiente virtual:**
    ```bash
    python -m venv .venv
    # No Windows
    .\.venv\Scripts\activate
    # No macOS/Linux
    source .venv/bin/activate
    ```

3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Crie um arquivo `.env` na raiz do projeto:**
    Copie o conteúdo abaixo para o arquivo `.env` e substitua os valores pelos seus dados:
    ```env
    # Credenciais para autenticação no Gradio
    USUARIO=seu_usuario_gradio
    SENHA=sua_senha_gradio

    # Chave da API da OpenAI
    OPENAI_API_KEY=sua_chave_openai_api_key
    ```
    *Observação:* Certifique-se de que o ID da sua Vector Store (`vs_...`) esteja corretamente configurado dentro do script `chatbot.py` ou externalize-o para o `.env` se preferir.

## Uso

Execute o script principal a partir do diretório raiz do projeto:

```bash
python chatbot.py
```

A aplicação Gradio será iniciada e um link local será fornecido no terminal. Abra este link no seu navegador. Você precisará fornecer o `USUARIO` e `SENHA` definidos no arquivo `.env` para acessar a interface.

## Funcionalidades

*   Interface de chat interativa criada com Gradio.
*   Integração com a API da OpenAI.
*   Utilização de RAG com File Search da OpenAI para basear respostas em documentos específicos.
*   Configuração de parâmetros da API (Modelo, Temperatura, Máximo de Tokens, Top P).
*   Prompt de sistema customizável para definir o comportamento do assistente.
*   Autenticação básica para a interface Gradio.
