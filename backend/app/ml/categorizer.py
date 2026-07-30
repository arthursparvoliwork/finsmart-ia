"""
categorizer.py — Modelo de Machine Learning para categorização.

🎓 COMO funciona o ML aqui (passo a passo):

1. PIPELINE: encadeamos duas etapas que rodam juntas:
   - TfidfVectorizer: transforma texto → números (vetor TF-IDF)
   - LogisticRegression: classificador que aprende padrões

2. TREINO: passamos o dataset (descrições + categorias) pro modelo.
   Ele "estuda" quais palavras indicam cada categoria.

3. PREDIÇÃO: damos uma descrição nova ("iFood hamburguer") e ele
   devolve a categoria mais provável ("Alimentação") + uma confiança (0 a 1).

4. PERSISTÊNCIA: depois de treinar, SALVAMOS o modelo num arquivo .pkl
   (joblib). Assim não precisamos retreinar toda vez que o servidor sobe.

🎓 POR QUE LogisticRegression e não algo mais fancy?
- Texto curto + categorias claras = Logistic Regression funciona muito bem
- Rápido pra treinar (<1s) e pra prever (<1ms)
- Interpretável (dá pra saber quais palavras pesam pra cada categoria)
- Não precisa de GPU
- Overkill usar rede neural aqui.

SOLID 'S': esta classe SÓ sabe treinar e prever categorias. Nada de banco/HTTP.
"""
import re
import unicodedata
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import cross_val_score

import joblib

from app.ml.training_data import DADOS_TREINO, CATEGORIAS_VALIDAS


# Caminho onde o modelo treinado será salvo (.pkl)
MODELO_PATH = Path(__file__).parent / "modelo_categorizacao.pkl"


def _preprocessar_texto(texto: str) -> str:
    """
    Limpa o texto ANTES da vetorização.
    - remove acentos ( café -> cafe )
    - lowercase
    - remove números e pontuação

    Por que remover acentos? Porque "café" e "cafe" deveriam ser tratados
    como a mesma palavra. O TF-IDF por padrão é case-sensitive e acentuado.
    """
    if not texto:
        return ""

    # Remove acentos: café → cafe
    texto_sem_acento = "".join(
        c for c in unicodedata.normalize("NFKD", texto)
        if not unicodedata.combining(c)
    )
    # lowercase + remove tudo que não é letra ou espaço
    texto_limpo = re.sub(r"[^a-zA-Z\s]", " ", texto_sem_acento.lower())
    # remove espaços múltiplos
    return re.sub(r"\s+", " ", texto_limpo).strip()


class CategorizerService:
    """
    Serviço que treina e usa o modelo de categorização.

    Padrão Singleton: carrega o modelo UMA vez e reutiliza em todas as
    requisições (treinar toda hora seria caro).
    """

    _instancia: "CategorizerService | None" = None  # cache singleton

    def __init__(self):
        # Pipeline: vetoriza o texto → classifica
        # ngram_range=(1,2): considera palavras isoladas E pares ("ifood" e "ifood restaurante")
        # min_df=1: aceita palavras que aparecem pelo menos 1 vez
        self._pipeline = Pipeline([
            ("tfidf", TfidfVectorizer(
                preprocessor=_preprocessar_texto,
                ngram_range=(1, 2),
                min_df=1,
            )),
            ("clf", LogisticRegression(
                max_iter=1000,
                C=10,  # C alto = modelo se ajusta mais aos dados
                class_weight="balanced",  # equilibra categorias com poucos exemplos
            )),
        ])
        self._treinado = False

    @classmethod
    def obter(cls) -> "CategorizerService":
        """Padrão Singleton: sempre retorna a MESMA instância."""
        if cls._instancia is None:
            cls._instancia = cls()
            cls._instancia.carregar_ou_treinar()
        return cls._instancia

    def carregar_ou_treinar(self) -> None:
        """
        Se já existe modelo salvo (.pkl), carrega. Senão, treina e salva.
        """
        if MODELO_PATH.exists():
            try:
                self._pipeline = joblib.load(MODELO_PATH)
                self._treinado = True
                print(f"[ML] Modelo carregado de {MODELO_PATH.name}")
                return
            except Exception as err:
                print(f"[ML] Aviso: falha ao carregar ({err}). Retreinando...")

        self.treinar()

    def treinar(self) -> dict:
        """
        Treina o modelo com DADOS_TREINO.
        Retorna métricas de qualidade do modelo (acurácia).
        """
        # Separa X (textos) e y (categorias)
        textos = [descricao for descricao, _ in DADOS_TREINO]
        categorias = [cat for _, cat in DADOS_TREINO]

        # Treina (fit = "ajustar" os pesos do modelo aos dados)
        self._pipeline.fit(textos, categorias)
        self._treinado = True

        # Validação cruzada: divide os dados em 5 partes, treina em 4,
        # testa em 1, repete. Mede quão bem generaliza pra dados NÃO vistos.
        scores = cross_val_score(
            self._pipeline, textos, categorias, cv=min(5, len(textos))
        )

        # Salva o modelo treinado no disco (.pkl)
        joblib.dump(self._pipeline, MODELO_PATH)

        return {
            "acuracia_media": float(scores.mean()),
            "desvio_padrao": float(scores.std()),
            "amostras_treino": len(textos),
            "categorias": len(set(categorias)),
        }

    def prever(self, descricao: str) -> dict:
        """
        Prediz a categoria de uma descrição nova.
        Retorna { categoria, confianca }.
        """
        if not self._treinado:
            raise RuntimeError("Modelo não treinado. Chame .treinar() antes.")

        # predict_proba retorna a probabilidade de cada categoria
        probabilidades = self._pipeline.predict_proba([descricao])[0]
        # classes_ tem a ordem das categorias correspondentes às probabilidades
        indice_max = probabilidades.argmax()
        categoria = self._pipeline.classes_[indice_max]
        confianca = float(probabilidades[indice_max])

        return {"categoria": categoria, "confianca": confianca}

    def prever_lote(self, descricoes: list[str]) -> list[dict]:
        """Prediz a categoria de várias descrições de uma vez (mais rápido)."""
        if not self._treinado:
            raise RuntimeError("Modelo não treinado.")
        if not descricoes:
            return []
        probabilidades = self._pipeline.predict_proba(descricoes)
        resultados = []
        for probs in probabilidades:
            idx = probs.argmax()
            resultados.append({
                "categoria": self._pipeline.classes_[idx],
                "confianca": float(probs[idx]),
            })
        return resultados

    @property
    def categorias_disponiveis(self) -> list[str]:
        return list(CATEGORIAS_VALIDAS)
