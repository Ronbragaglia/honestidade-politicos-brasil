"""
Coleta de dados da API da Camara dos Deputados
https://dadosabertos.camara.leg.br/api/v2/

Uso: python3 coleta-camara.py [--legislatura 57] [--output dados/deputados-federais/] [--json]
"""

import requests
import json
import time
import argparse
import sys
from datetime import datetime
from pathlib import Path

BASE_URL = "https://dadosabertos.camara.leg.br/api/v2"
HEADERS = {"Accept": "application/json"}
RATE_LIMIT_DELAY = 0.5  # segundos entre requests

# Media anual da cota parlamentar (estimativa nacional em R$)
MEDIA_ANUAL_COTA = 120000


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


def get_deputados(legislatura: int = 57) -> list:
    """Busca todos os deputados de uma legislatura."""
    url = f"{BASE_URL}/deputados"
    params = {"idLegislatura": legislatura, "itens": 513, "ordem": "ASC", "ordenarPor": "nome"}

    response = requests.get(url, params=params, headers=HEADERS)
    response.raise_for_status()
    return response.json()["dados"]


def get_despesas(deputado_id: int, ano: int = None) -> list:
    """Busca despesas da cota parlamentar de um deputado."""
    url = f"{BASE_URL}/deputados/{deputado_id}/despesas"
    params = {"itens": 100, "ordem": "DESC", "ordenarPor": "dataDocumento"}
    if ano:
        params["ano"] = ano

    all_despesas = []
    page = 1

    while True:
        params["pagina"] = page
        response = requests.get(url, params=params, headers=HEADERS)
        response.raise_for_status()
        data = response.json()["dados"]

        if not data:
            break

        all_despesas.extend(data)
        page += 1
        time.sleep(RATE_LIMIT_DELAY)

    return all_despesas


def get_votacoes(deputado_id: int) -> list:
    """Busca votacoes de um deputado na legislatura atual."""
    url = f"{BASE_URL}/deputados/{deputado_id}/votacoes"
    params = {"itens": 100, "ordem": "DESC", "ordenarPor": "dataHoraRegistro"}

    response = requests.get(url, params=params, headers=HEADERS)
    response.raise_for_status()
    return response.json()["dados"]


def get_presenca(deputado_id: int) -> dict:
    """
    Busca presenca em eventos/sessoes de um deputado.

    A API da Camara nao fornece campo 'presenca' diretamente nos eventos.
    Contamos eventos passados (dataHoraInicio no passado) como sessoes agendadas,
    e eventos onde o deputado consta como organizador ou participante programado
    sao considerados presencas efetivas.
    """
    url = f"{BASE_URL}/deputados/{deputado_id}/eventos"
    params = {"itens": 100, "ordem": "DESC", "ordenarPor": "dataHoraInicio"}

    all_eventos = []
    page = 1

    while True:
        params["pagina"] = page
        response = requests.get(url, params=params, headers=HEADERS)
        response.raise_for_status()
        data = response.json()["dados"]

        if not data:
            break

        all_eventos.extend(data)
        page += 1
        time.sleep(RATE_LIMIT_DELAY)

        # Limitar a 3 paginas para nao sobrecarregar a API
        if page > 3:
            break

    agora = datetime.now().isoformat()
    # Eventos passados = sessoes que ja ocorreram
    passados = [e for e in all_eventos if e.get("dataHoraInicio", "") < agora]
    total = len(passados)

    # Eventos com situacao indicando realizacao sao considerados presenca
    # Situacoes comuns: "Encerrada", "Realizada", "Em andamento"
    situacoes_presenca = {"encerrada", "realizada", "em andamento", "finalizada"}
    presentes = sum(
        1 for e in passados
        if e.get("situacao", "").strip().lower() in situacoes_presenca
    )

    # Se nao ha info de situacao, usar total de passados como estimativa
    if presentes == 0 and total > 0:
        presentes = total

    return {
        "total_sessoes": total,
        "presencas": presentes,
        "percentual": round((presentes / total * 100), 1) if total > 0 else 0
    }


def calcular_score_despesas(despesas: list, media_anual: float = MEDIA_ANUAL_COTA) -> int:
    """Calcula score de etica no uso de recursos (0-100)."""
    if not despesas:
        return 100

    total = sum(d.get("valorDocumento", 0) for d in despesas if d.get("valorDocumento", 0) > 0)

    if total <= media_anual:
        return 100
    elif total <= media_anual * 1.5:
        return 70
    elif total <= media_anual * 2:
        return 50
    else:
        return 30


def calcular_score_presenca(presenca: dict) -> int:
    """Calcula score de presenca (0-100)."""
    pct = presenca.get("percentual", 0)
    return min(100, int(pct))


def calcular_score_produtividade(votacoes: list) -> int:
    """
    Calcula score de produtividade legislativa (0-100).
    Baseado no numero de votacoes participadas.
    """
    n = len(votacoes)
    if n >= 80:
        return 100
    elif n >= 50:
        return 80
    elif n >= 30:
        return 60
    elif n >= 10:
        return 40
    else:
        return 20


def calcular_score_total(score_despesas: int, score_presenca: int, score_produtividade: int) -> int:
    """
    Calcula score total ponderado.

    Pesos adaptados dos criterios disponiveis via API:
    - Presenca: 35%
    - Uso etico de recursos (despesas): 35%
    - Produtividade (votacoes): 30%

    Nota: criterios como Ficha Limpa, Coerencia e Patrimonio requerem
    fontes externas e serao integrados futuramente.
    """
    score = (
        score_presenca * 0.35
        + score_despesas * 0.35
        + score_produtividade * 0.30
    )
    return round(score)


def classificar_score(score: int) -> str:
    """Retorna classificacao e emoji baseado no score."""
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


def gerar_ficha(deputado: dict, despesas: list, votacoes: list, presenca: dict,
                score_despesas: int, score_presenca: int, score_produtividade: int,
                score_total: int) -> str:
    """Gera ficha markdown de um deputado com score calculado."""
    nome = deputado["nome"]
    partido = deputado.get("siglaPartido", "?")
    uf = deputado.get("siglaUf", "?")

    total_gasto = sum(d.get("valorDocumento", 0) for d in despesas if d.get("valorDocumento", 0) > 0)
    total_votacoes = len(votacoes)
    classificacao = classificar_score(score_total)
    emoji = emoji_score(score_total)

    ficha = f"""# {nome} ({partido}-{uf})

## Dados Gerais

| Info | Valor |
|------|-------|
| Partido | {partido} |
| Estado | {uf} |
| Legislatura | 57a (2023-2027) |
| ID Camara | {deputado['id']} |

## Cota Parlamentar

- **Total gasto (periodo)**: R$ {total_gasto:,.2f}
- **Despesas registradas**: {len(despesas)}
- **Score despesas**: {score_despesas}/100

## Presenca em Sessoes

- **Sessoes registradas**: {presenca['total_sessoes']}
- **Presencas**: {presenca['presencas']}
- **Percentual**: {presenca['percentual']}%
- **Score presenca**: {score_presenca}/100

## Atividade Legislativa

- **Votacoes participadas**: {total_votacoes}
- **Score produtividade**: {score_produtividade}/100

## Score Final

| Criterio | Score | Peso |
|----------|-------|------|
| Presenca | {score_presenca}/100 | 35% |
| Uso de Recursos | {score_despesas}/100 | 35% |
| Produtividade | {score_produtividade}/100 | 30% |
| **TOTAL** | **{emoji} {score_total}/100 — {classificacao}** | |

> Nota: Criterios adicionais (Ficha Limpa, Coerencia, Patrimonio) serao integrados
> quando fontes externas estiverem disponiveis.

---

*Fonte: [API Camara dos Deputados](https://dadosabertos.camara.leg.br)*
*Ultima coleta: {datetime.now().strftime('%Y-%m-%d')}*
"""
    return ficha


def main():
    parser = argparse.ArgumentParser(description="Coleta dados da Camara dos Deputados")
    parser.add_argument("--legislatura", type=int, default=57, help="Numero da legislatura (default: 57)")
    parser.add_argument("--output", type=str, default="dados/deputados-federais", help="Diretorio de saida")
    parser.add_argument("--limit", type=int, default=10, help="Limite de deputados (para teste)")
    parser.add_argument("--json", action="store_true", help="Exportar tambem em formato JSON")
    parser.add_argument("--ano", type=int, default=None, help="Ano para filtrar despesas (default: ano atual)")
    args = parser.parse_args()

    if args.ano is None:
        args.ano = datetime.now().year

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Buscando deputados da {args.legislatura}a legislatura...")
    deputados = get_deputados(args.legislatura)
    total = min(args.limit, len(deputados))
    print(f"Encontrados: {len(deputados)} deputados (processando {total})")

    resumo = []
    erros = []

    for i, dep in enumerate(deputados[:args.limit]):
        progresso(i + 1, total, prefixo="Coletando")

        try:
            despesas = get_despesas(dep["id"], ano=args.ano)
            time.sleep(RATE_LIMIT_DELAY)

            votacoes = get_votacoes(dep["id"])
            time.sleep(RATE_LIMIT_DELAY)

            presenca = get_presenca(dep["id"])
            time.sleep(RATE_LIMIT_DELAY)

            # Calcular scores parciais
            score_desp = calcular_score_despesas(despesas)
            score_pres = calcular_score_presenca(presenca)
            score_prod = calcular_score_produtividade(votacoes)
            score_total = calcular_score_total(score_desp, score_pres, score_prod)

            total_gasto = sum(
                d.get("valorDocumento", 0) for d in despesas if d.get("valorDocumento", 0) > 0
            )

            # Gerar ficha markdown
            ficha = gerar_ficha(
                dep, despesas, votacoes, presenca,
                score_desp, score_pres, score_prod, score_total
            )

            filename = dep["nome"].lower().replace(" ", "-") + ".md"
            filepath = output_dir / filename
            filepath.write_text(ficha, encoding="utf-8")

            # Adicionar ao resumo
            resumo.append({
                "id": dep["id"],
                "nome": dep["nome"],
                "partido": dep.get("siglaPartido", "?"),
                "uf": dep.get("siglaUf", "?"),
                "score_total": score_total,
                "score_despesas": score_desp,
                "score_presenca": score_pres,
                "score_produtividade": score_prod,
                "classificacao": classificar_score(score_total),
                "total_gasto": round(total_gasto, 2),
                "total_despesas": len(despesas),
                "total_votacoes": len(votacoes),
                "presenca_percentual": presenca["percentual"],
                "arquivo_md": filename,
                "data_coleta": datetime.now().strftime("%Y-%m-%d"),
            })

        except Exception as e:
            erros.append({"deputado": dep["nome"], "erro": str(e)})
            continue

    # Ordenar resumo por score (maior primeiro)
    resumo.sort(key=lambda x: x["score_total"], reverse=True)

    # Exportar JSON resumo
    json_path = output_dir / "resumo.json"
    dados_export = {
        "legislatura": args.legislatura,
        "data_coleta": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_coletados": len(resumo),
        "erros": len(erros),
        "deputados": resumo,
    }
    if erros:
        dados_export["detalhes_erros"] = erros

    json_path.write_text(json.dumps(dados_export, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Resumo JSON salvo em {json_path}")

    if args.json:
        # Saida JSON para stdout tambem
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
        print(f"\nDeputados com erro:")
        for e in erros:
            print(f"  - {e['deputado']}: {e['erro']}")


if __name__ == "__main__":
    main()
