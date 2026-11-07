"""Citizen Assist AI: assistente de orientação ao cidadão (público: pessoas idosas).

Execute com:  python main.py
"""

import os

from assistente import Assistente
from base_conhecimento import BaseConhecimento

# Os caminhos partem da pasta deste arquivo, então funciona de qualquer lugar.
PASTA = os.path.dirname(os.path.abspath(__file__))


def main():
    base = BaseConhecimento(os.path.join(PASTA, "data", "base_conhecimento.json"))
    base.carregar()   # lê o JSON e cria os objetos Orientacao (não trava se falhar)

    assistente = Assistente(
        "Citizen Assist AI", base,
        caminho_historico=os.path.join(PASTA, "data", "historico.json"),
        caminho_csv=os.path.join(PASTA, "data", "atendimentos.csv"),
    )
    try:
        assistente.menu()
    except (KeyboardInterrupt, EOFError):
        print("\n\nEncerrando...")
        assistente.encerrar(pedir_nota=False)


if __name__ == "__main__":
    main()
