"""Classe Orientacao: uma informação da base de conhecimento (um registro do JSON)."""

AVISO = "este assistente NÃO é um canal oficial."

# Campos que todo registro do JSON precisa ter, com o tipo esperado.
CAMPOS_OBRIGATORIOS = {
    "id": int,
    "categoria": str,
    "titulo": str,
    "palavras_chave": list,
    "resposta": str,
    "documentos": list,
    "onde": str,
    "fonte": str,
    "verificado_em": str,
}


class Orientacao:
    """Guarda os dados de uma orientação e sabe se exibir na tela."""

    def __init__(self, id, categoria, titulo, palavras_chave, resposta,
                 documentos, onde, fonte, verificado_em):
        self.id = id
        self.categoria = categoria
        self.titulo = titulo
        self.palavras_chave = palavras_chave
        self.resposta = resposta
        self.documentos = documentos
        self.onde = onde
        self.fonte = fonte
        self.verificado_em = verificado_em

    @staticmethod
    def registro_valido(registro):
        """Confere se um dicionário do JSON tem todos os campos com o tipo certo."""
        if not isinstance(registro, dict):
            return False
        for campo, tipo in CAMPOS_OBRIGATORIOS.items():
            valor = registro.get(campo)
            if not isinstance(valor, tipo) or isinstance(valor, bool):
                return False
            if tipo is str and not valor.strip():
                return False
        return True

    @classmethod
    def de_dicionario(cls, registro):
        """Cria um objeto Orientacao a partir de um dicionário do JSON."""
        return cls(
            registro["id"], registro["categoria"], registro["titulo"],
            registro["palavras_chave"], registro["resposta"],
            registro["documentos"], registro["onde"], registro["fonte"],
            registro["verificado_em"],
        )

    def exibir(self):
        """Mostra a orientação na tela, sempre com fonte, data e aviso."""
        print(f"\n>> {self.titulo}  [{self.categoria}]")
        print(self.resposta)
        print("Documentos necessários:")
        for documento in self.documentos:
            print(f"  - {documento}")
        print(f"Onde: {self.onde}")
        print(f"Fonte: {self.fonte} (verificado em {self.verificado_em})")
        print(f"Aviso: {AVISO}")
