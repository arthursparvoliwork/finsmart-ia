"""
ai_service.py — Camada de serviços de IA.

SOLID 'S' (Single Responsibility):
- Esta camada sabe sobre IA (categorização), mas NÃO sabe sobre HTTP ou banco.
- As rotas chamam estas funções; estas funções chamam o modelo ML.

SOLID 'D' (Dependency Inversion):
- As rotas dependem desta abstração, não do modelo ML diretamente.
"""
from app.ml.categorizer import CategorizerService


class AIService:
    """
    Serviço de IA: orquestra chamadas aos modelos ML.
    """

    def __init__(self):
        # Obtém a instância Singleton do modelo
        self._categorizer = CategorizerService.obter()

    def categorizar(self, descricao: str) -> dict:
        """
        Recebe a descrição de uma transação e retorna a categoria prevista.

        Exemplo:
            input:  "iFood hamburguer"
            output: {"categoria": "Alimentação", "confianca": 0.62}
        """
        if not descricao or not descricao.strip():
            return {"categoria": None, "confianca": 0.0}

        return self._categorizer.prever(descricao.strip())

    def categorizar_lote(self, descricoes: list[str]) -> list[dict]:
        """Versão em lote: recebe várias descrições, retorna várias predições."""
        return self._categorizer.prever_lote(descricoes)

    def listar_categorias(self) -> list[str]:
        """Retorna todas as categorias que o modelo conhece."""
        return self._categorizer.categorias_disponiveis
