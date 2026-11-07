"""Classe BaseConhecimento: lê o JSON, lista categorias e busca a melhor orientação."""

import json

from orientacao import Orientacao

# ---------- Regras de pontuação (explicadas no README) ----------
PONTOS_PALAVRA_CHAVE = 3   # palavra-chave da orientação encontrada na pergunta
PONTOS_TITULO = 1          # palavra da pergunta (4+ letras) encontrada no título
LIMITE_ALTA = 6            # a partir daqui: confiança ALTA
LIMITE_MEDIA = 3           # de 3 a 5 pontos: confiança MÉDIA

# Palavras comuns que não ajudam a achar uma orientação. Sem elas, uma pergunta
# como "como posso fazer isso para mais anos" ganharia pontos só por coincidência.
PALAVRAS_IGNORADAS = {
    "como", "para", "onde", "qual", "quais", "quero", "preciso", "posso",
    "tenho", "pelo", "pela", "sobre", "isso", "esse", "essa", "mais",
    "muito", "quando", "porque", "anos", "ano", "uma", "minha", "meu",
}

ACENTOS = {"á": "a", "à": "a", "ã": "a", "â": "a", "é": "e", "è": "e",
           "ê": "e", "í": "i", "ì": "i", "ó": "o", "ò": "o", "õ": "o",
           "ô": "o", "ú": "u", "ù": "u", "ü": "u", "ç": "c"}


def normalizar(texto):
    """Minúsculas, sem acentos e sem pontuação, com um espaço em cada ponta.

    Os espaços nas pontas permitem procurar palavras inteiras com
    `" sus " in texto`, sem confundir "sus" com "susto".
    """
    texto = texto.lower().strip()
    for letra, troca in ACENTOS.items():
        texto = texto.replace(letra, troca)
    for sinal in "?!.,;:()-/\"'":
        texto = texto.replace(sinal, " ")
    return " " + " ".join(texto.split()) + " "


class BaseConhecimento:
    """O conjunto de todas as orientações (lista de objetos Orientacao)."""

    def __init__(self, caminho):
        self.caminho = caminho
        self.orientacoes = []
        self.erro = ""   # motivo da falha, se o JSON não pôde ser lido

    def carregar(self):
        """Lê o JSON e cria os objetos Orientacao. Nunca trava o programa.

        Devolve True se carregou pelo menos uma orientação válida.
        """
        self.orientacoes = []
        self.erro = ""
        try:
            with open(self.caminho, "r", encoding="utf-8") as arquivo:
                dados = json.load(arquivo)
        except FileNotFoundError:
            self.erro = f"arquivo não encontrado: {self.caminho}"
            return False
        except json.JSONDecodeError:
            self.erro = f"arquivo corrompido (JSON inválido): {self.caminho}"
            return False
        except OSError as e:
            self.erro = f"não foi possível abrir o arquivo ({e})"
            return False

        if not isinstance(dados, list):
            self.erro = "o JSON deve ser uma lista de orientações"
            return False

        ignorados = 0
        for registro in dados:
            if Orientacao.registro_valido(registro):
                self.orientacoes.append(Orientacao.de_dicionario(registro))
            else:
                ignorados += 1

        if ignorados:
            print(f"Aviso: {ignorados} registro(s) inválido(s) foram ignorados.")
        if not self.orientacoes:
            self.erro = "nenhuma orientação válida na base"
            return False
        return True

    def categorias(self):
        """Lista as categorias, sem repetir, na ordem em que aparecem."""
        lista = []
        for o in self.orientacoes:
            if o.categoria not in lista:
                lista.append(o.categoria)
        return lista

    def por_categoria(self, categoria):
        """Devolve as orientações de uma categoria."""
        return [o for o in self.orientacoes if o.categoria == categoria]

    def pontuar(self, pergunta, orientacao):
        """Calcula quantos pontos a orientação recebe para a pergunta."""
        texto = normalizar(pergunta)
        pontos = 0

        chaves = {normalizar(p) for p in orientacao.palavras_chave}
        for chave in chaves:
            if chave.strip() and chave in texto:
                pontos += PONTOS_PALAVRA_CHAVE

        titulo = normalizar(orientacao.titulo)
        for palavra in set(texto.split()):
            if (len(palavra) >= 4 and palavra not in PALAVRAS_IGNORADAS
                    and f" {palavra} " in titulo):
                pontos += PONTOS_TITULO
        return pontos

    def buscar(self, pergunta):
        """Devolve uma lista de tuplas (pontos, orientacao), da maior para a menor."""
        resultados = []
        for o in self.orientacoes:
            pontos = self.pontuar(pergunta, o)
            if pontos > 0:
                resultados.append((pontos, o))
        resultados.sort(key=lambda par: (-par[0], par[1].id))
        return resultados

    @staticmethod
    def nivel_confianca(pontos):
        """ALTA (6+), MÉDIA (3 a 5) ou None (menos de 3: 'não encontrei')."""
        if pontos >= LIMITE_ALTA:
            return "ALTA"
        if pontos >= LIMITE_MEDIA:
            return "MÉDIA"
        return None
