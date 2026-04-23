"""
Validador de dados do projeto Honestidade Politicos Brasil.

Verifica integridade dos arquivos .md e .json em dados/:
- Scores no range 0-100
- Siglas de partido validas
- Entradas duplicadas
- URLs de fonte bem formatadas
- Estrutura dos arquivos JSON

Uso: python3 validar-dados.py [--dados-dir dados/]
Retorna exit code 1 se encontrar erros (util para CI).
"""

import json
import re
import sys
import argparse
from pathlib import Path
from collections import defaultdict


# Partidos brasileiros registrados no TSE (atualizado 2026)
PARTIDOS_VALIDOS = {
    "MDB", "PT", "PSDB", "PP", "PDT", "PTB", "DEM", "PL", "PSB", "PCdoB",
    "PSD", "PSOL", "PSC", "Avante", "Podemos", "Cidadania", "NOVO", "Novo",
    "REDE", "Rede", "PV", "PMN", "DC", "PCB", "PCO", "PSTU", "UP",
    "Republicanos", "Solidariedade", "PROS", "Patriota",
    "União", "Uniao", "União Brasil",
    # Siglas alternativas comuns
    "SD", "PR", "PRB", "PPS", "PPL", "PMB", "PRTB", "PTC", "PHS",
    "AGIR", "Agir",
    # Formato com maiusculas
    "AVANTE", "PODEMOS", "CIDADANIA", "SOLIDARIEDADE", "REPUBLICANOS",
    "?",  # Desconhecido (aceito)
}

# Regex para URLs
URL_PATTERN = re.compile(
    r'https?://'
    r'(?:[\w-]+\.)+[\w-]+'
    r'(?:/[\w.~:/?#\[\]@!$&\'()*+,;=%-]*)?'
)

# Regex para extrair scores de markdown
SCORE_PATTERN = re.compile(r'\b(\d{1,3})/100\b')
SCORE_EMOJI_PATTERN = re.compile(r'[🟢🔵🟡🟠🔴]\s*(\d{1,3})')


class Validador:
    """Validador de dados do projeto."""

    def __init__(self, dados_dir: Path):
        self.dados_dir = dados_dir
        self.erros = []
        self.avisos = []
        self.stats = {
            "arquivos_md": 0,
            "arquivos_json": 0,
            "politicos_encontrados": 0,
            "scores_validados": 0,
            "urls_verificadas": 0,
        }

    def erro(self, arquivo: str, mensagem: str):
        """Registra um erro."""
        self.erros.append(f"[ERRO] {arquivo}: {mensagem}")

    def aviso(self, arquivo: str, mensagem: str):
        """Registra um aviso."""
        self.avisos.append(f"[AVISO] {arquivo}: {mensagem}")

    def validar_score(self, score, arquivo: str, contexto: str = ""):
        """Valida que um score esta no range 0-100."""
        self.stats["scores_validados"] += 1
        try:
            s = int(score) if not isinstance(score, int) else score
            if s < 0 or s > 100:
                self.erro(arquivo, f"Score fora do range 0-100: {s} {contexto}")
                return False
        except (ValueError, TypeError):
            self.erro(arquivo, f"Score invalido (nao numerico): {score} {contexto}")
            return False
        return True

    def validar_partido(self, partido: str, arquivo: str):
        """Valida sigla de partido."""
        if not partido or partido.strip() == "":
            self.erro(arquivo, "Partido vazio")
            return False
        if partido not in PARTIDOS_VALIDOS:
            self.aviso(arquivo, f"Partido nao reconhecido: '{partido}' (pode ser novo/alterado)")
        return True

    def validar_urls_markdown(self, conteudo: str, arquivo: str):
        """Valida URLs encontradas no markdown."""
        # Encontrar links markdown [texto](url)
        links = re.findall(r'\[.*?\]\((https?://[^)]+)\)', conteudo)
        for url in links:
            self.stats["urls_verificadas"] += 1
            if not URL_PATTERN.match(url):
                self.erro(arquivo, f"URL malformada: {url}")
            # Verificar dominios conhecidos
            if "dadosabertos.camara.leg.br" not in url and \
               "legis.senado.leg.br" not in url and \
               "portal.stf.jus.br" not in url and \
               "portaldatransparencia.gov.br" not in url and \
               "tse.jus.br" not in url and \
               "planalto.gov.br" not in url and \
               "github.com" not in url and \
               "senado.leg.br" not in url:
                self.aviso(arquivo, f"URL de fonte nao reconhecida: {url}")

    def validar_arquivo_md(self, filepath: Path):
        """Valida um arquivo markdown individual."""
        self.stats["arquivos_md"] += 1

        try:
            conteudo = filepath.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            self.erro(str(filepath), "Erro de encoding (esperado UTF-8)")
            return

        if not conteudo.strip():
            self.erro(str(filepath), "Arquivo vazio")
            return

        # Ignorar arquivos _index.md (sao manuais)
        if filepath.name == "_index.md":
            return

        # Verificar se tem titulo
        if not conteudo.startswith("#"):
            self.aviso(str(filepath), "Arquivo nao comeca com titulo (#)")

        # Extrair e validar scores
        scores = SCORE_PATTERN.findall(conteudo)
        for s in scores:
            self.validar_score(int(s), str(filepath), contexto=f"(encontrado no texto: {s}/100)")

        scores_emoji = SCORE_EMOJI_PATTERN.findall(conteudo)
        for s in scores_emoji:
            self.validar_score(int(s), str(filepath), contexto=f"(score com emoji)")

        # Validar URLs
        self.validar_urls_markdown(conteudo, str(filepath))

        # Extrair partido do titulo (formato: "Nome (PARTIDO-UF)")
        titulo_match = re.search(r'^#\s+.+\((\w+)-(\w{2})\)', conteudo)
        if titulo_match:
            partido = titulo_match.group(1)
            uf = titulo_match.group(2)
            self.validar_partido(partido, str(filepath))

            ufs_validas = {
                "AC", "AL", "AM", "AP", "BA", "CE", "DF", "ES", "GO",
                "MA", "MG", "MS", "MT", "PA", "PB", "PE", "PI", "PR",
                "RJ", "RN", "RO", "RR", "RS", "SC", "SE", "SP", "TO"
            }
            if uf not in ufs_validas:
                self.erro(str(filepath), f"UF invalida: {uf}")

    def validar_arquivo_json(self, filepath: Path):
        """Valida um arquivo JSON de resumo."""
        self.stats["arquivos_json"] += 1

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            self.erro(str(filepath), f"JSON invalido: {e}")
            return
        except UnicodeDecodeError:
            self.erro(str(filepath), "Erro de encoding (esperado UTF-8)")
            return

        if not isinstance(data, dict):
            self.erro(str(filepath), "JSON raiz deve ser um objeto/dict")
            return

        # Verificar campos esperados
        if "data_coleta" not in data:
            self.aviso(str(filepath), "Campo 'data_coleta' ausente")

        # Validar lista de politicos
        for chave in ["deputados", "senadores", "politicos"]:
            if chave in data:
                lista = data[chave]
                if not isinstance(lista, list):
                    self.erro(str(filepath), f"Campo '{chave}' deve ser uma lista")
                    continue

                self.stats["politicos_encontrados"] += len(lista)

                for item in lista:
                    nome = item.get("nome", "?")

                    # Validar score
                    if "score_total" in item:
                        self.validar_score(
                            item["score_total"], str(filepath),
                            contexto=f"(politico: {nome})"
                        )

                    # Validar partido
                    if "partido" in item:
                        self.validar_partido(item["partido"], str(filepath))

                    # Validar sub-scores
                    for sub in ["score_despesas", "score_presenca", "score_produtividade",
                                "score_votacoes", "score_autorias"]:
                        if sub in item:
                            self.validar_score(
                                item[sub], str(filepath),
                                contexto=f"({sub} de {nome})"
                            )

    def verificar_duplicatas(self, dados_dir: Path):
        """Verifica entradas duplicadas entre arquivos."""
        nomes_vistos = defaultdict(list)

        for json_file in dados_dir.rglob("resumo.json"):
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    data = json.load(f)

                for chave in ["deputados", "senadores", "politicos"]:
                    if chave in data:
                        for item in data[chave]:
                            nome = item.get("nome", "?")
                            esfera = json_file.parent.name
                            chave_unica = f"{nome}|{esfera}"
                            nomes_vistos[chave_unica].append(str(json_file))
            except (json.JSONDecodeError, IOError):
                continue

        for chave, arquivos in nomes_vistos.items():
            if len(arquivos) > 1:
                nome = chave.split("|")[0]
                self.erro(
                    "duplicatas",
                    f"Politico duplicado: '{nome}' encontrado em {len(arquivos)} arquivos: {', '.join(arquivos)}"
                )

    def executar(self):
        """Executa todas as validacoes."""
        print(f"Validando dados em {self.dados_dir}/...\n")

        if not self.dados_dir.exists():
            print(f"ERRO: Diretorio {self.dados_dir} nao encontrado.")
            return False

        # Validar arquivos markdown
        for md_file in self.dados_dir.rglob("*.md"):
            self.validar_arquivo_md(md_file)

        # Validar arquivos JSON
        for json_file in self.dados_dir.rglob("*.json"):
            self.validar_arquivo_json(json_file)

        # Verificar duplicatas
        self.verificar_duplicatas(self.dados_dir)

        return len(self.erros) == 0

    def relatorio(self) -> str:
        """Gera relatorio de validacao."""
        linhas = []
        linhas.append("=" * 55)
        linhas.append("  RELATORIO DE VALIDACAO — Honestidade Politicos Brasil")
        linhas.append("=" * 55)
        linhas.append("")

        linhas.append("Estatisticas:")
        linhas.append(f"  Arquivos .md analisados:  {self.stats['arquivos_md']}")
        linhas.append(f"  Arquivos .json analisados: {self.stats['arquivos_json']}")
        linhas.append(f"  Politicos encontrados:     {self.stats['politicos_encontrados']}")
        linhas.append(f"  Scores validados:          {self.stats['scores_validados']}")
        linhas.append(f"  URLs verificadas:          {self.stats['urls_verificadas']}")
        linhas.append("")

        if self.erros:
            linhas.append(f"ERROS ({len(self.erros)}):")
            linhas.append("-" * 40)
            for e in self.erros:
                linhas.append(f"  {e}")
            linhas.append("")

        if self.avisos:
            linhas.append(f"AVISOS ({len(self.avisos)}):")
            linhas.append("-" * 40)
            for a in self.avisos:
                linhas.append(f"  {a}")
            linhas.append("")

        if not self.erros and not self.avisos:
            linhas.append("Nenhum problema encontrado!")
            linhas.append("")

        status = "FALHOU" if self.erros else "OK"
        linhas.append(f"Resultado: {status}")
        linhas.append(f"  {len(self.erros)} erro(s), {len(self.avisos)} aviso(s)")

        return "\n".join(linhas)


def main():
    parser = argparse.ArgumentParser(description="Valida dados do projeto")
    parser.add_argument("--dados-dir", type=str, default="dados", help="Diretorio com dados")
    args = parser.parse_args()

    validador = Validador(Path(args.dados_dir))
    sucesso = validador.executar()

    print(validador.relatorio())

    if not sucesso:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
