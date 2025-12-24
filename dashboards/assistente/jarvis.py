"""
Código do assistente de IA J.A.R.V.I.S. para o sistema S.H.I.E.L.D. Analytics.
"""
import json
import requests
import os
from dotenv import load_dotenv
from pathlib import Path


# Pega o caminho relativo à pasta deste arquivo
ENV_DIR = Path(__file__).parent / "gemini_api.env"

load_dotenv(ENV_DIR)

class AssistenteIA:
    """
    Classe para o assistente de IA J.A.R.V.I.S.
    """

    def __init__(self, id_conversa:str, prompt: str, historico: list = []):
        """
        :param id_conversa: id da conversa para controle de contexto
        :param prompt: prrompt para o asssitente J.A.R.V.I.S.
        :param api_key: chave da API para acesso ao modelo LLM
        :param historico: histórico de conversas anteriores
        """
        self.id_conversa = id_conversa
        self.prompt = Path("dashboards/assistente/prompt.md").read_text()
        self.api_key = os.getenv("API_KEY")
        self.historico = historico

        self.tools =  {
                "name": "buscar_banco_shield_query",
                "description": "Executa consultas SQL na base de dados do S.H.I.E.L.D. Analytics.",
                "parameters": {
                    "type": "object",
                    "required": ["query"],
                    "properties": {
                        "query": { "type": "string", "description": "A query deve seguir a sintaxe SQL padrão e todas as regras definidas." },
                    }
                }
            }

    def consultar_llm(self, consulta: str) -> str:
        """
        Consulta o modelo LLM/Gemini com a consulta do usuário.

        :param consulta: Consulta do usuário
        :return: Resposta gerada pelo modelo LLM
        """
        # Aqui você integraria com um modelo LLM/Gemini usando a API_KEY
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"

        headers = {
            "Content-Type": "application/json"
        }

        payload = {
            "system_instruction": {
            "parts": [
                        {"text": self.prompt}
                    ]
                },
                "contents": self.historico,
                "tools": [{"function_declarations":[self.tools]}],
                "tool_config": {
                    "function_calling_config": {
                        "mode": "AUTO"
                    }
                }
            }
        
        if not self.api_key:
            return {"text": "Chave de API não encontrada."}

        response = requests.post(
                f"{url}?key={self.api_key}",
                headers=headers,
                data=json.dumps(payload)
            )
        if response.status_code == 200:
            resposta = response.json()
            return resposta.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[-1]
        else:
            resposta = "Desculpe, não consegui processar sua consulta no momento."
            print(f"Erro na API LLM: {response.status_code} - {response.text}")
            return {"text": resposta}

    def guardar_historico(self, role: str, content: str):
        """
        Guarda a mensagem no histórico da conversa.

        :param role: Papel da mensagem (user/assistant)
        :param content: Conteúdo da mensagem
        """
        historico_formato = {
            "model":{
                "role": role,
                "parts": [
                    { "text": content }
                ]
            },
            "user":{
                "role": role,
                "parts": [
                    { "text": content }
                ]
            },
            "function":{
                "role": role,
                "parts": [
                    {
                        "functionResponse": {
                            "name": "buscar_banco_shield_query",
                            "response": {
                                "content": json.dumps(content)
                            }
                        }
                    }
                ]
            },
            "function_call":{
                "role": "model",
                'parts': [
                        {
                        'functionCall': {
                            'name': 'buscar_banco_shield_query',
                            'args': {
                            # O argumento que o Gemini teria gerado baseado no pedido do usuario
                            'query': content
                            }
                        }
                        }
                    ]
            }
        }

        self.historico.append(historico_formato.get(role, {}))

    def resetar_historico(self):
        """
        Reseta o histórico da conversa.
        """
        self.historico = []

