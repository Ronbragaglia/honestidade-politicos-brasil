"""
Coleta de dados da API do Senado Federal
https://legis.senado.leg.br/dadosabertos/

Uso: python3 coleta-senado.py [--output dados/senadores/] [--limit 10] [--json]
"""

import requests
import json
import time
import argparse
import sys
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

BASE_URL = "https://legis.senado.leg.br/dadosabertos"
HEADERS = {"Accept": "application/json"}
RATE_LIMIT_DELAY = 1.0  # API do Senado e mais restritiva


def progresso(atual, total, prefixo=""):
    """Exibe barra de progresso no terminal."""
    largura = 30
    pct = atual / total if total > 0 else 0
    preenchido = int(largura * pct)
    barra = "#" * preenchido + "-" * (largura - preenchido)
    sys.stdout.write(f"\r{prefixo} [{barra}] {pct*100:.1f}% ({atual}/{total})")
    sys.stdout.flush()
    if atual == total:
        print()


def get_senadores_atuais() -> list:
    """
    Busca todos os senadores em exercicio atualmente.
    Endpoint: GET /senador/lista/atual
    """
    url = f"{BASE_URL}/senador/lista/atual"

    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()

    data = response.json()

    # A estrutura da API do Senado varia; navegar ate a lista
    try:
        parlamentares = data["ListaParlamentarEmExercicio"]["Parlamentares"]["Parlamentar"]
    except (KeyError, TypeError):
        # Tentar estrutura alternativa
        try:
            parlamentares = data.get("ListaParlamentarEmExercicio", {}).get("Parlamentares", {}).get("Parlamentar", [])
        except (KeyError, TypeError, AttributeError):
            print("AVISO: Estrutura da API diferente do esperado. Tentando parsing alternativo...")
            parlamentares = []

    if not isinstance(parlamentares, list):
        parlamentares = [parlamentares] if parlamentares else []

    # Extrair dados relevantes de cada parlamentar
    senadores = []
    for p in parlamentares:
        ident = p.get("IdentificacaoParlamentar", {})
        mandato = p.get("Mandato", {})

        senador = {
            "codigo": ident.get("CodigoParlamentar", ""),
            "nome": ident.get("NomeParlamentar", ident.get("NomeCompletoParlamentar", "?")),
            "nome_completo": ident.get("NomeCompletoParlamentar", ""),
            "partido": ident.get("SiglaPartidoParlamentar", "?"),
            "uf": ident.get("UfParlamentar", "?"),
            "sexo": ident.get("SexoParlamentar", ""),
            "foto_url": ident.get("UrlFotoParlamentar", ""),
            "pagina_url": ident.get("UrlPaginaParlamentar", ""),
            "email": ident.get("EmailParlamentar", ""),
        }
        senadores.append(senador)

    return senadores


def get_votacoes_senador(codigo: str) -> list:
    """
    Busca votacoes de um senador.
    Endpoint: GET /senador/{codigo}/votacoes
    """
    url = f"{BASE_URL}/senador/{codigo}/votacoes"

    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        data = response.json()

        # Navegar na estrutura da resposta
        votacoes_wrap = data.get("VotacaoParlamentar", {})
        parlamentar = votacoes_wrap.get("Parlamentar", {})
        votacoes_obj = parlamentar.get("Votacoes", {})

        if not votacoes_obj:
            return []

        votacoes = votacoes_obj.get("Votacao", [])
        if not isinstance(votacoes, list):
            votacoes = [votacoes] if votacoes else []

        return votacoes

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return []
        raise
    except (json.JSONDecodeError, ValueError):
        return []


def get_autorias_senador(codigo: str) -> list:
    """
    Busca projetos de autoria de um senador.
    Endpoint: GET /senador/{codigo}/autorias
    """
    url = f"{BASE_URL}/senador/{codigo}/autorias"

    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        data = response.json()

        # Navegar na estrutura
        autorias_wrap = data.get("AutoriaParlamentar", {})
        parlamentar = autorias_wrap.get("Parlamentar", {})
        autorias_obj = parlamentar.get("Autorias", {})

        if not autorias_obj:
            return []

        autorias = autorias_obj.get("Autoria", [])
        if not isinstance(autorias, list):
            autorias = [autorias] if autorias else []

        return autorias

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return []
        raise
    except (json.JSONDecodeError, ValueError):
        return []


def calcular_score_votacoes(votacoes: list) -> int:
    """Calcula score baseado em participacao em votacoes (0-100)."""
    n = len(votacoes)
    if n >= 100:
        return 100
    elif n >= 60:
        return 80
    elif n >= 30:
        return 60
    elif n >= 10:
        return 40
    else:
        return 20


def calcular_score_autorias(autorias: list) -> int:
    """Calcula score de produtividade legislativa (0-100)."""
    n = len(autorias)
    if n >= 50:
        return 100
    elif n >= 30:
        return 80
    elif n >= 15:
        return 60
    elif n >= 5:
        return 40
    else:
        return 20


def calcular_score_total(score_votacoes: int, score_autorias: int) -> int:
    """
    Calcula score total ponderado.

    Pesos:
    - Participacao em votacoes: 55%
    - Produtividade (autorias): 45%

    Nota: criterios como Ficha Limpa, Presenca e Patrimonio requerem
    fontes externas e serao integrados futuramente.
    """
    score = score_votacoes * 0.55 + score_autorias * 0.45
    return round(score)


def classificar_score(score: int) -> str:
    """Retorna classificacao baseada no score."""
    if score >= 80:
        return "Excelente"
    elif score >= 65:
        return "Bom"
    elif score >= 45:
        return "Regular"
    elif score >= 25:
        return "Ruim"
    else:
        return "Pessimo"


def emoji_score(score: int) -> str:
    """Retorna emoji colorido para o score."""
    if score >= 80:
        return "🟢"
    elif score >= 65:
        return "🔵"
    elif score >= 45:
        return "🟡"
    elif score >= 25:
        return "🟠"
    else:
        return "🔴"


def gerar_ficha(senador: dict, votacoes: list, autorias: list,
                score_vot: int, score_aut: int, score_total: int) -> str:
    """Gera ficha markdown de um senador com score calculado."""
    nome = senador["nome"]
    partido = senador["partido"]
    uf = senador["uf"]
    classificacao = classificar_score(score_total)
    emoji = emoji_score(score_total)

    # Contar tipos de autorias
    tipos_autoria = {}
    for a in autorias:
        materia = a.get("Materia", a.get("IdentificacaoMateria", {}))
        if isinstance(materia, dict):
            tipo = materia.get("SiglaSubtipoMateria", materia.get("DescricaoSubtipoMateria", "Outros"))
        else:
            tipo = "Outros"
        tipos_autoria[tipo] = tipos_autoria.get(tipo, 0) + 1

    autorias_detalhe = ""
    if tipos_autoria:
        for tipo, qtd in sorted(tipos_autoria.items(), key=lambda x: -x[1])[:5]:
            autorias_detalhe += f"  - {tipo}: {qtd}\n"

    # Ultimas votacoes para referencia
    ultimas_votacoes = ""
    for v in votacoes[:5]:
        sessao = v.get("SessaoPlenaria", v.get("DescricaoVotacao", {}))
        if isinstance(sessao, dict):
            data_sessao = sessao.get("DataSessao", "?")
            desc = v.get("DescricaoVotacao", "Votacao")
        else:
            data_sessao = "?"
            desc = str(v)[:60] if v else "Votacao"
        ultimas_votacoes += f"  - [{data_sessao}] {str(desc)[:80]}\n"

    ficha = f"""# {nome} ({partido}-{uf})

## Dados Gerais

| Info | Valor |
|------|-------|
| Partido | {partido} |
| Estado | {uf} |
| Codigo Senado | {senador['codigo']} |
| Nome completo | {senador.get('nome_completo', nome)} |

## Atividade Legislativa

### Votacoes
- **Total de votacoes registradas**: {len(votacoes)}
- **Score votacoes**: {score_vot}/100

### Autorias (Projetos de Lei)
- **Total de autorias**: {len(autorias)}
- **Score autorias**: {score_aut}/100

#### Tipos de autoria:
{autorias_detalhe if autorias_detalhe else "  - Nenhuma autoria registrada\n"}
## Score Final

| Criterio | Score | Peso |
|----------|-------|------|
| Participacao em Votacoes | {score_vot}/100 | 55% |
| Produtividade (Autorias) | {score_aut}/100 | 45% |
| **TOTAL** | **{emoji} {score_total}/100 — {classificacao}** | |

> Nota: Criterios adicionais (Ficha Limpa, Presenca, Patrimonio) serao integrados
> quando fontes externas estiverem disponiveis.

---

*Fonte: [API Senado Federal](https://legis.senado.leg.br/dadosabertos/)*
*Ultima coleta: {datetime.now().strftime('%Y-%m-%d')}*
"""
    return ficha


def main():
    parser = argparse.ArgumentParser(description="Coleta dados do Senado Federal")
    parser.add_argument("--output", type=str, default="dados/senadores", help="Diretorio de saida")
    parser.add_argument("--limit", type=int, default=10, help="Limite de senadores (para teste)")
    parser.add_argument("--json", action="store_true", help="Exportar tambem em formato JSON para stdout")
    args = parser.parse_args()

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    print("Buscando senadores em exercicio...")
    senadores = get_senadores_atuais()
    total = min(args.limit, len(senadores))
    print(f"Encontrados: {len(senadores)} senadores (processando {total})")

    if not senadores:
        print("ERRO: Nenhum senador encontrado. Verifique a conexao ou a API.")
        sys.exit(1)

    resumo = []
    erros = []

    for i, sen in enumerate(senadores[:args.limit]):
        progresso(i + 1, total, prefixo="Coletando")

        try:
            votacoes = get_votacoes_senador(sen["codigo"])
            time.sleep(RATE_LIMIT_DELAY)

            autorias = get_autorias_senador(sen["codigo"])
            time.sleep(RATE_LIMIT_DELAY)

            # Calcular scores
            score_vot = calcular_score_votacoes(votacoes)
            score_aut = calcular_score_autorias(autorias)
            score_total = calcular_score_total(score_vot, score_aut)

            # Gerar ficha markdown
            ficha = gerar_ficha(sen, votacoes, autorias, score_vot, score_aut, score_total)

            filename = sen["nome"].lower().replace(" ", "-") + ".md"
            filepath = output_dir / filename
            filepath.write_text(ficha, encoding="utf-8")

            # Adicionar ao resumo
            resumo.append({
                "codigo": sen["codigo"],
                "nome": sen["nome"],
                "nome_completo": sen.get("nome_completo", ""),
                "partido": sen["partido"],
                "uf": sen["uf"],
                "score_total": score_total,
                "score_votacoes": score_vot,
                "score_autorias": score_aut,
                "classificacao": classificar_score(score_total),
                "total_votacoes": len(votacoes),
                "total_autorias": len(autorias),
                "arquivo_md": filename,
                "data_coleta": datetime.now().strftime("%Y-%m-%d"),
            })

        except Exception as e:
            erros.append({"senador": sen["nome"], "erro": str(e)})
            continue

    # Ordenar resumo por score (maior primeiro)
    resumo.sort(key=lambda x: x["score_total"], reverse=True)

    # Exportar JSON resumo
    json_path = output_dir / "resumo.json"
    dados_export = {
        "data_coleta": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_coletados": len(resumo),
        "erros": len(erros),
        "senadores": resumo,
    }
    if erros:
        dados_export["detalhes_erros"] = erros

    json_path.write_text(json.dumps(dados_export, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Resumo JSON salvo em {json_path}")

    if args.json:
        print(json.dumps(dados_export, ensure_ascii=False, indent=2))

    # Relatorio final
    print(f"\n{'='*50}")
    print(f"COLETA FINALIZADA")
    print(f"{'='*50}")
    print(f"Fichas geradas: {len(resumo)}")
    print(f"Erros: {len(erros)}")
    if resumo:
        media = sum(d["score_total"] for d in resumo) / len(resumo)
        print(f"Score medio: {media:.1f}/100")
        print(f"Melhor: {resumo[0]['nome']} ({resumo[0]['score_total']}/100)")
        print(f"Pior: {resumo[-1]['nome']} ({resumo[-1]['score_total']}/100)")
    print(f"Arquivos em: {output_dir}/")

    if erros:
        print(f"\nSenadores com erro:")
        for e in erros:
            print(f"  - {e['senador']}: {e['erro']}")


if __name__ == "__main__":
    main()
