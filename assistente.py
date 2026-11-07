"""Classe Assistente: conversa com o cidadão, guarda o histórico e calcula indicadores."""

import csv
import json
import os
import time
from datetime import datetime

from base_conhecimento import LIMITE_MEDIA, BaseConhecimento, normalizar
from orientacao import AVISO

CAMPOS_CSV = ["data", "sessao", "origem", "pergunta", "orientacao_id",
              "encontrou", "ajudou", "tentativas", "tempo_s", "nota_facilidade"]

MSG_DADO_PESSOAL = "Atenção: não digite CPF, telefone ou e-mail. Reescreva."


class Assistente:
    """Quem conversa com o cidadão. Usa uma BaseConhecimento (composição)."""

    def __init__(self, nome, base, caminho_historico="data/historico.json",
                 caminho_csv="data/atendimentos.csv"):
        self.nome = nome
        self.base = base                      # objeto BaseConhecimento
        self.caminho_historico = caminho_historico
        self.caminho_csv = caminho_csv
        self.sessao = datetime.now().strftime("%Y%m%d-%H%M%S")
        self.historico = []                   # lista de dicionários (atendimentos)
        self._carregar_historico()

    # ------------------------------------------------------------------
    # Entrada de dados segura: nada aqui encerra o programa
    # ------------------------------------------------------------------
    @staticmethod
    def _ler(mensagem):
        return input(mensagem).strip()

    def _ler_opcao(self, mensagem, minimo, maximo):
        """Pede um número entre minimo e maximo até receber um valor válido."""
        while True:
            texto = self._ler(mensagem)
            if texto.isdecimal() and minimo <= int(texto) <= maximo:
                return int(texto)
            print(f"Opção inválida. Digite um número de {minimo} a {maximo}.")

    def _ler_sim_nao(self, mensagem):
        """Pede s/n até receber uma resposta válida. Devolve True para 's'."""
        while True:
            texto = self._ler(mensagem).lower()
            if texto in ("s", "sim"):
                return True
            if texto in ("n", "nao", "não"):
                return False
            print("Resposta inválida. Digite apenas s (sim) ou n (não).")

    @staticmethod
    def contem_dado_pessoal(texto):
        """8 ou mais dígitos (CPF, telefone...) ou o símbolo @ (e-mail)."""
        digitos = sum(1 for letra in texto if letra.isdigit())
        return digitos >= 8 or "@" in texto

    # ------------------------------------------------------------------
    # Histórico (data/historico.json)
    # ------------------------------------------------------------------
    def _carregar_historico(self):
        try:
            with open(self.caminho_historico, "r", encoding="utf-8") as arquivo:
                dados = json.load(arquivo)
            if isinstance(dados, list):
                self.historico = [d for d in dados if isinstance(d, dict)]
            else:
                raise ValueError("histórico não é uma lista")
        except FileNotFoundError:
            self.historico = []
        except (json.JSONDecodeError, ValueError, OSError):
            print("Aviso: o histórico estava corrompido; começando um novo.")
            self.historico = []
            try:   # guarda uma cópia do arquivo ruim em vez de apagá-lo
                os.replace(self.caminho_historico, self.caminho_historico + ".corrompido")
            except OSError:
                pass

    def _salvar_historico(self):
        try:
            pasta = os.path.dirname(self.caminho_historico)
            if pasta:
                os.makedirs(pasta, exist_ok=True)
            with open(self.caminho_historico, "w", encoding="utf-8") as arquivo:
                json.dump(self.historico, arquivo, ensure_ascii=False, indent=2)
        except OSError:
            print("Aviso: não consegui salvar o histórico neste momento.")

    def registrar(self, origem, pergunta, orientacao_id, encontrou, ajudou,
                  tentativas, tempo_s):
        """Guarda um atendimento no histórico e no arquivo JSON."""
        atendimento = {
            "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "sessao": self.sessao,
            "origem": origem,                  # "pergunta" ou "categoria"
            "pergunta": pergunta,
            "orientacao_id": orientacao_id,
            "encontrou": encontrou,
            "ajudou": ajudou,
            "tentativas": tentativas,
            "tempo_s": tempo_s,
            "nota_facilidade": None,           # preenchida ao sair
        }
        self.historico.append(atendimento)
        self._salvar_historico()

    # ------------------------------------------------------------------
    # Atendimento por pergunta (texto livre)
    # ------------------------------------------------------------------
    def perguntar(self):
        """Atende dúvidas em texto livre usando base.buscar() e orientacao.exibir()."""
        if not self.base.orientacoes:
            print("A base de conhecimento está indisponível no momento.")
            return

        inicio = time.time()
        tentativas = 0
        ultima_pergunta = ""
        ultimo_id = None
        encontrou = False

        while True:
            texto = self._ler("\nDigite sua dúvida (0 para voltar): ")

            if texto == "0":
                if tentativas > 0:   # a pessoa desistiu sem a dúvida resolvida
                    self.registrar("pergunta", ultima_pergunta, ultimo_id, encontrou,
                                   False, tentativas, round(time.time() - inicio, 1))
                return
            if not texto or not normalizar(texto).strip():
                print("Atenção: escreva sua dúvida com palavras, ou digite 0 para voltar.")
                continue
            if self.contem_dado_pessoal(texto):
                print(MSG_DADO_PESSOAL)   # recusada e NUNCA registrada
                continue

            tentativas += 1
            ultima_pergunta = texto
            resultados = self.base.buscar(texto)
            nivel = None
            if resultados:
                pontos, melhor = resultados[0]
                nivel = BaseConhecimento.nivel_confianca(pontos)

            if nivel is None:
                encontrou = False
                ultimo_id = None
                self._mostrar_nao_encontrei()
                continue

            encontrou = True
            ultimo_id = melhor.id
            print(f"\nConfiança da resposta: {nivel} ({pontos} pontos)")
            melhor.exibir()
            self._mostrar_alternativas(resultados[1:3])

            if self._ler_sim_nao("\nEssa orientação respondeu sua dúvida? (s/n): "):
                self.registrar("pergunta", texto, melhor.id, True, True,
                               tentativas, round(time.time() - inicio, 1))
                print("Que bom que ajudou!")
                return
            print("Tente escrever a dúvida com outras palavras, ou digite 0 para voltar.")

    def _mostrar_nao_encontrei(self):
        print("\nNão encontrei uma orientação para essa dúvida.")
        print("Tente outras palavras (ex.: 'cartão SUS', 'vacina', 'ônibus', 'INSS')")
        print("ou use a opção 'Navegar por categorias' no menu principal.")

    @staticmethod
    def _mostrar_alternativas(alternativas):
        """Mostra até duas outras orientações com pontuação suficiente."""
        validas = [(p, o) for p, o in alternativas if p >= LIMITE_MEDIA]
        if validas:
            print("\nOutras orientações que podem interessar:")
            for pontos, o in validas:
                print(f"  - {o.titulo}  [{o.categoria}] ({pontos} pontos)")

    # ------------------------------------------------------------------
    # Atendimento por categorias
    # ------------------------------------------------------------------
    def navegar(self):
        """Lista categorias e orientações numeradas, com 0 para voltar."""
        categorias = self.base.categorias()
        if not categorias:
            print("A base de conhecimento está indisponível no momento.")
            return
        while True:
            print("\n=== Categorias ===")
            for i, categoria in enumerate(categorias, start=1):
                total = len(self.base.por_categoria(categoria))
                print(f"{i}. {categoria} ({total} orientações)")
            print("0. Voltar")
            opcao = self._ler_opcao("Escolha uma categoria: ", 0, len(categorias))
            if opcao == 0:
                return
            self._navegar_categoria(categorias[opcao - 1])

    def _navegar_categoria(self, categoria):
        orientacoes = self.base.por_categoria(categoria)
        while True:
            inicio = time.time()
            print(f"\n=== {categoria} ===")
            for i, o in enumerate(orientacoes, start=1):
                print(f"{i}. {o.titulo}")
            print("0. Voltar")
            opcao = self._ler_opcao("Escolha uma orientação: ", 0, len(orientacoes))
            if opcao == 0:
                return
            escolhida = orientacoes[opcao - 1]
            escolhida.exibir()
            ajudou = self._ler_sim_nao("\nEssa orientação respondeu sua dúvida? (s/n): ")
            self.registrar("categoria", f"{categoria}: {escolhida.titulo}", escolhida.id,
                           True, ajudou, 1, round(time.time() - inicio, 1))

    # ------------------------------------------------------------------
    # Indicadores e CSV
    # ------------------------------------------------------------------
    @staticmethod
    def _media(valores):
        return sum(valores) / len(valores) if valores else 0.0

    @staticmethod
    def _numero(valor):
        try:
            return float(valor)
        except (TypeError, ValueError):
            return None

    def indicadores(self):
        """Calcula os indicadores a partir do histórico e devolve um dicionário."""
        h = self.historico
        total = len(h)
        encontrados = [a for a in h if a.get("encontrou") is True]
        ajudaram = [a for a in h if a.get("ajudou") is True]

        tempos = [self._numero(a.get("tempo_s")) for a in encontrados]
        tempos = [t for t in tempos if t is not None]
        tentativas = [self._numero(a.get("tentativas")) for a in h]
        tentativas = [t for t in tentativas if t is not None]

        # uma nota por sessão (todos os atendimentos da sessão têm a mesma nota)
        notas_por_sessao = {}
        for a in h:
            nota = self._numero(a.get("nota_facilidade"))
            if nota is not None:
                notas_por_sessao[a.get("sessao")] = nota

        sem_solucao = []
        for a in h:
            if a.get("origem") == "pergunta" and a.get("ajudou") is not True:
                pergunta = a.get("pergunta", "")
                if pergunta and pergunta not in sem_solucao:
                    sem_solucao.append(pergunta)

        return {
            "total": total,
            "encontrada_pct": 100 * len(encontrados) / total if total else 0.0,
            "acerto_pct": 100 * len(ajudaram) / total if total else 0.0,
            "tempo_medio": self._media(tempos),
            "tentativas_media": self._media(tentativas),
            "facilidade": self._media(list(notas_por_sessao.values())),
            "sessoes_avaliadas": len(notas_por_sessao),
            "sem_solucao": sem_solucao,
        }

    def mostrar_indicadores(self):
        i = self.indicadores()
        print("\n=== Indicadores ===")
        if i["total"] == 0:
            print("Ainda não há atendimentos registrados.")
            return
        print(f"Atendimentos registrados: {i['total']}")
        print(f"Resposta encontrada (%):     {i['encontrada_pct']:.1f}")
        print(f"Taxa de acerto: ajudou (%):  {i['acerto_pct']:.1f}")
        print(f"Tempo médio para encontrar:  {i['tempo_medio']:.1f} s")
        print(f"Tentativas por atendimento:  {i['tentativas_media']:.1f}")
        if i["sessoes_avaliadas"]:
            n = i["sessoes_avaliadas"]
            print(f"Facilidade de uso (1 a 5):   {i['facilidade']:.1f} "
                  f"({n} {'avaliação' if n == 1 else 'avaliações'})")
        else:
            print("Facilidade de uso (1 a 5):   sem avaliações ainda")
        if i["sem_solucao"]:
            print("Dúvidas sem solução:")
            for pergunta in i["sem_solucao"]:
                print(f"  - {pergunta}")
        else:
            print("Dúvidas sem solução: nenhuma")

    def exportar_csv(self):
        """Exporta os atendimentos para data/atendimentos.csv com csv.DictWriter."""
        try:
            pasta = os.path.dirname(self.caminho_csv)
            if pasta:
                os.makedirs(pasta, exist_ok=True)
            with open(self.caminho_csv, "w", newline="", encoding="utf-8") as arquivo:
                escritor = csv.DictWriter(arquivo, fieldnames=CAMPOS_CSV,
                                          extrasaction="ignore")
                escritor.writeheader()
                for atendimento in self.historico:
                    escritor.writerow(atendimento)
        except OSError:
            print("Aviso: não consegui criar o arquivo CSV.")
            return False
        print(f"CSV exportado: {self.caminho_csv} ({len(self.historico)} atendimentos)")
        return True

    # ------------------------------------------------------------------
    # Menu principal
    # ------------------------------------------------------------------
    def menu(self):
        print(f"\n===== {self.nome} =====")
        print("Orientações para pessoas idosas, com base em fontes oficiais.")
        print(f"Aviso: {AVISO}")
        print("Não digite CPF, telefone ou e-mail. Eu nunca peço esses dados.")
        if not self.base.orientacoes:
            print(f"\nAtenção: a base de conhecimento não foi carregada ({self.base.erro}).")

        while True:
            print("\n--- Menu principal ---")
            print("1. Fazer uma pergunta")
            print("2. Navegar por categorias")
            print("3. Ver indicadores")
            print("4. Exportar atendimentos para CSV")
            print("0. Sair")
            opcao = self._ler_opcao("Escolha uma opção: ", 0, 4)
            if opcao == 1:
                self.perguntar()
            elif opcao == 2:
                self.navegar()
            elif opcao == 3:
                self.mostrar_indicadores()
            elif opcao == 4:
                self.exportar_csv()
            else:
                self.encerrar()
                return

    def encerrar(self, pedir_nota=True):
        """Pede a nota de facilidade (1 a 5), salva, mostra indicadores e exporta."""
        da_sessao = [a for a in self.historico if a.get("sessao") == self.sessao]
        if pedir_nota and da_sessao:
            nota = self._ler_opcao("\nDe 1 a 5, qual a facilidade de usar o assistente? ", 1, 5)
            for atendimento in da_sessao:
                atendimento["nota_facilidade"] = nota
            self._salvar_historico()
        self.mostrar_indicadores()
        self.exportar_csv()
        print("\nObrigado por usar o Citizen Assist AI. Até logo!")
