"""
Gerador de dashboard consolidado a partir dos dados coletados.

Le arquivos JSON de dados/ e gera DASHBOARD.md na raiz do repositorio
com estatisticas, graficos ASCII, rankings e analise por partido/regiao.

Uso: python3 gerar-dashboard.py [--dados-dir dados/] [--output DASHBOARD.md]
"""

import json
import argparse
import sys
from datetime import datetime
from pathlib import Path
from collections import defaultdict


# Mapeamento UF -> Regiao
UF_REGIAO = {
    "AC": "Norte", "AP": "Norte", "AM": "Norte", "PA": "Norte",
    "RO": "Norte", "RR": "Norte", "TO": "Norte",
    "AL": "Nordeste", "BA": "Nordeste", "CE": "Nordeste", "MA": "Nordeste",
    "PB": "Nordeste", "PE": "Nordeste", "PI": "Nordeste", "RN": "Nordeste",
    "SE": "Nordeste",
    "DF": "Centro-Oeste", "GO": "Centro-Oeste", "MT": "Centro-Oeste",
    "MS": "Centro-Oeste",
    "ES": "Sudeste", "MG": "Sudeste", "RJ": "Sudeste", "SP": "Sudeste",
    "PR": "Sul", "RS": "Sul", "SC": "Sul",
}


def carregar_dados(dados_dir: Path) -> list:
    """Carrega todos os arquivos resumo.json encontrados em dados/."""
    todos = []
    fontes = []

    for json_file in dados_dir.rglob("resumo.json"):
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Identificar esfera pelo diretorio
            esfera = json_file.parent.name
            data_coleta = data.get("data_coleta", "?")
            fontes.append({"esfera": esfera, "arquivo": str(json_file), "data_coleta": data_coleta})

            # Extrair lista de politicos (pode ser 'deputados' ou 'senadores')
            for chave in ["deputados", "senadores", "politicos", "governadores", "prefeitos"]:
                if chave in data:
                    for p in data[chave]:
                        p["esfera"] = esfera
                        todos.append(p)
                    break

        except (json.JSONDecodeError, IOError) as e:
            print(f"AVISO: Erro ao ler {json_file}: {e}")

    return todos, fontes


def barra_ascii(valor, maximo=100, largura=25):
    """Gera barra ASCII proporcional."""
    if maximo == 0:
        return ""
    preenchido = int((valor / maximo) * largura)
    preenchido = min(preenchido, largura)
    return "█" * preenchido + "░" * (largura - preenchido)


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
    """Retorna emoji para o score."""
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


def gerar_estatisticas_gerais(politicos: list) -> str:
    """Gera secao de estatisticas gerais."""
    if not politicos:
        return "> Nenhum dado encontrado.\n"

    total = len(politicos)
    scores = [p.get("score_total", 0) for p in politicos]
    media = sum(scores) / total
    maximo = max(scores)
    minimo = min(scores)

    # Distribuicao por classificacao
    dist = defaultdict(int)
    for s in scores:
        dist[classificar_score(s)] += 1

    # Esferas
    esferas = defaultdict(int)
    for p in politicos:
        esferas[p.get("esfera", "?")] += 1

    txt = f"""## Estatisticas Gerais

| Metrica | Valor |
|---------|-------|
| Total de politicos | {total} |
| Score medio | {media:.1f}/100 |
| Maior score | {maximo}/100 |
| Menor score | {minimo}/100 |
| Mediana | {sorted(scores)[total//2]}/100 |

### Por Esfera

"""
    for esfera, qtd in sorted(esferas.items()):
        txt += f"- **{esfera}**: {qtd} politicos\n"

    txt += f"""
### Distribuicao por Classificacao

| Classificacao | Qtd | Grafico |
|---------------|-----|---------|
| 🟢 Excelente (80-100) | {dist.get('Excelente', 0)} | {barra_ascii(dist.get('Excelente', 0), max(dist.values()) if dist else 1, 20)} |
| 🔵 Bom (65-79) | {dist.get('Bom', 0)} | {barra_ascii(dist.get('Bom', 0), max(dist.values()) if dist else 1, 20)} |
| 🟡 Regular (45-64) | {dist.get('Regular', 0)} | {barra_ascii(dist.get('Regular', 0), max(dist.values()) if dist else 1, 20)} |
| 🟠 Ruim (25-44) | {dist.get('Ruim', 0)} | {barra_ascii(dist.get('Ruim', 0), max(dist.values()) if dist else 1, 20)} |
| 🔴 Pessimo (0-24) | {dist.get('Pessimo', 0)} | {barra_ascii(dist.get('Pessimo', 0), max(dist.values()) if dist else 1, 20)} |

### Distribuicao de Scores (grafico)

```
100 |
 90 |{' ' + '█' * len([s for s in scores if 90 <= s <= 100]) + f' ({len([s for s in scores if 90 <= s <= 100])})' if len([s for s in scores if 90 <= s <= 100]) > 0 else ''}
 80 |{' ' + '█' * len([s for s in scores if 80 <= s < 90]) + f' ({len([s for s in scores if 80 <= s < 90])})' if len([s for s in scores if 80 <= s < 90]) > 0 else ''}
 70 |{' ' + '█' * len([s for s in scores if 70 <= s < 80]) + f' ({len([s for s in scores if 70 <= s < 80])})' if len([s for s in scores if 70 <= s < 80]) > 0 else ''}
 60 |{' ' + '█' * len([s for s in scores if 60 <= s < 70]) + f' ({len([s for s in scores if 60 <= s < 70])})' if len([s for s in scores if 60 <= s < 70]) > 0 else ''}
 50 |{' ' + '█' * len([s for s in scores if 50 <= s < 60]) + f' ({len([s for s in scores if 50 <= s < 60])})' if len([s for s in scores if 50 <= s < 60]) > 0 else ''}
 40 |{' ' + '█' * len([s for s in scores if 40 <= s < 50]) + f' ({len([s for s in scores if 40 <= s < 50])})' if len([s for s in scores if 40 <= s < 50]) > 0 else ''}
 30 |{' ' + '█' * len([s for s in scores if 30 <= s < 40]) + f' ({len([s for s in scores if 30 <= s < 40])})' if len([s for s in scores if 30 <= s < 40]) > 0 else ''}
 20 |{' ' + '█' * len([s for s in scores if 20 <= s < 30]) + f' ({len([s for s in scores if 20 <= s < 30])})' if len([s for s in scores if 20 <= s < 30]) > 0 else ''}
 10 |{' ' + '█' * len([s for s in scores if 10 <= s < 20]) + f' ({len([s for s in scores if 10 <= s < 20])})' if len([s for s in scores if 10 <= s < 20]) > 0 else ''}
  0 |{' ' + '█' * len([s for s in scores if 0 <= s < 10]) + f' ({len([s for s in scores if 0 <= s < 10])})' if len([s for s in scores if 0 <= s < 10]) > 0 else ''}
    +{'─' * 40}
     Cada █ = 1 politico
```
"""
    return txt


def gerar_ranking(politicos: list) -> str:
    """Gera secao Top 10 e Bottom 10."""
    if not politicos:
        return ""

    ordenados = sorted(politicos, key=lambda x: x.get("score_total", 0), reverse=True)

    txt = "## Top 10 — Melhores Scores\n\n"
    txt += "| # | Nome | Partido | UF | Esfera | Score | Class. |\n"
    txt += "|---|------|---------|----|----|-------|--------|\n"

    for i, p in enumerate(ordenados[:10]):
        s = p.get("score_total", 0)
        txt += (
            f"| {i+1} | {p.get('nome', '?')} | {p.get('partido', '?')} | "
            f"{p.get('uf', '?')} | {p.get('esfera', '?')} | "
            f"{emoji_score(s)} {s} | {classificar_score(s)} |\n"
        )

    txt += "\n## Bottom 10 — Piores Scores\n\n"
    txt += "| # | Nome | Partido | UF | Esfera | Score | Class. |\n"
    txt += "|---|------|---------|----|----|-------|--------|\n"

    bottom = ordenados[-10:] if len(ordenados) >= 10 else ordenados
    bottom_sorted = sorted(bottom, key=lambda x: x.get("score_total", 0))

    for i, p in enumerate(bottom_sorted[:10]):
        s = p.get("score_total", 0)
        txt += (
            f"| {i+1} | {p.get('nome', '?')} | {p.get('partido', '?')} | "
            f"{p.get('uf', '?')} | {p.get('esfera', '?')} | "
            f"{emoji_score(s)} {s} | {classificar_score(s)} |\n"
        )

    return txt


def gerar_analise_partidos(politicos: list) -> str:
    """Gera tabela comparativa por partido."""
    if not politicos:
        return ""

    partidos = defaultdict(list)
    for p in politicos:
        partido = p.get("partido", "?")
        partidos[partido].append(p.get("score_total", 0))

    # Ordenar por score medio descendente
    ranking = []
    for partido, scores in partidos.items():
        media = sum(scores) / len(scores)
        ranking.append({
            "partido": partido,
            "qtd": len(scores),
            "media": round(media, 1),
            "melhor": max(scores),
            "pior": min(scores),
        })

    ranking.sort(key=lambda x: x["media"], reverse=True)

    txt = "## Comparacao por Partido\n\n"
    txt += "| Partido | Politicos | Score Medio | Melhor | Pior | Grafico |\n"
    txt += "|---------|-----------|-------------|--------|------|--------|\n"

    for r in ranking:
        txt += (
            f"| {r['partido']} | {r['qtd']} | "
            f"{emoji_score(int(r['media']))} {r['media']} | "
            f"{r['melhor']} | {r['pior']} | "
            f"{barra_ascii(r['media'], 100, 15)} |\n"
        )

    return txt


def gerar_analise_regional(politicos: list) -> str:
    """Gera analise por regiao do Brasil."""
    if not politicos:
        return ""

    regioes = defaultdict(list)
    for p in politicos:
        uf = p.get("uf", "?")
        regiao = UF_REGIAO.get(uf, "Outro")
        regioes[regiao].append(p.get("score_total", 0))

    txt = "## Analise Regional\n\n"
    txt += "| Regiao | Politicos | Score Medio | Melhor | Pior | Grafico |\n"
    txt += "|--------|-----------|-------------|--------|------|--------|\n"

    for regiao in ["Norte", "Nordeste", "Centro-Oeste", "Sudeste", "Sul", "Outro"]:
        scores = regioes.get(regiao, [])
        if not scores:
            continue
        media = sum(scores) / len(scores)
        txt += (
            f"| {regiao} | {len(scores)} | "
            f"{emoji_score(int(media))} {media:.1f} | "
            f"{max(scores)} | {min(scores)} | "
            f"{barra_ascii(media, 100, 15)} |\n"
        )

    # Detalhamento por UF
    txt += "\n### Por Estado (UF)\n\n"
    ufs = defaultdict(list)
    for p in politicos:
        ufs[p.get("uf", "?")].append(p.get("score_total", 0))

    uf_ranking = []
    for uf, scores in ufs.items():
        uf_ranking.append({"uf": uf, "qtd": len(scores), "media": sum(scores)/len(scores)})

    uf_ranking.sort(key=lambda x: x["media"], reverse=True)

    txt += "| UF | Politicos | Score Medio | Grafico |\n"
    txt += "|----|-----------|-------------|--------|\n"

    for r in uf_ranking:
        txt += (
            f"| {r['uf']} | {r['qtd']} | "
            f"{emoji_score(int(r['media']))} {r['media']:.1f} | "
            f"{barra_ascii(r['media'], 100, 15)} |\n"
        )

    return txt


def gerar_timeline(fontes: list) -> str:
    """Gera timeline de atualizacoes dos dados."""
    if not fontes:
        return ""

    txt = "## Timeline de Atualizacoes\n\n"
    txt += "| Data | Esfera | Arquivo |\n"
    txt += "|------|--------|--------|\n"

    for f in sorted(fontes, key=lambda x: x.get("data_coleta", ""), reverse=True):
        txt += f"| {f.get('data_coleta', '?')} | {f.get('esfera', '?')} | `{f.get('arquivo', '?')}` |\n"

    return txt


def main():
    parser = argparse.ArgumentParser(description="Gera dashboard consolidado")
    parser.add_argument("--dados-dir", type=str, default="dados", help="Diretorio com dados coletados")
    parser.add_argument("--output", type=str, default="DASHBOARD.md", help="Arquivo de saida")
    args = parser.parse_args()

    dados_dir = Path(args.dados_dir)

    if not dados_dir.exists():
        print(f"ERRO: Diretorio {dados_dir} nao encontrado.")
        sys.exit(1)

    print(f"Carregando dados de {dados_dir}/...")
    politicos, fontes = carregar_dados(dados_dir)
    print(f"Total de politicos carregados: {len(politicos)}")
    print(f"Fontes de dados: {len(fontes)}")

    if not politicos:
        print("AVISO: Nenhum dado encontrado. Execute os scripts de coleta primeiro.")
        print("  python3 scripts/coleta-camara.py")
        print("  python3 scripts/coleta-senado.py")
        sys.exit(0)

    # Gerar dashboard
    dashboard = f"""# Dashboard — Honestidade Politicos Brasil

> Relatorio consolidado gerado automaticamente em {datetime.now().strftime('%Y-%m-%d %H:%M')}.
> Dados coletados de APIs publicas (Camara dos Deputados, Senado Federal).

---

{gerar_estatisticas_gerais(politicos)}

---

{gerar_ranking(politicos)}

---

{gerar_analise_partidos(politicos)}

---

{gerar_analise_regional(politicos)}

---

{gerar_timeline(fontes)}

---

## Metodologia

Os scores sao calculados com base nos dados disponiveis via APIs publicas:
- **Deputados Federais**: Presenca (35%) + Uso de Recursos (35%) + Produtividade (30%)
- **Senadores**: Participacao em Votacoes (55%) + Autorias (45%)

Criterios adicionais (Ficha Limpa, Coerencia, Patrimonio) serao integrados
quando fontes externas estiverem disponiveis. Veja [metodologia completa](metodologia/calculo-score.md).

---

*Gerado por `scripts/gerar-dashboard.py` | Projeto [Honestidade Politicos Brasil](https://github.com/)*
*Ultima atualizacao: {datetime.now().strftime('%Y-%m-%d')}*
"""

    output_path = Path(args.output)
    output_path.write_text(dashboard, encoding="utf-8")
    print(f"\nDashboard gerado: {output_path}")
    print(f"Total de politicos: {len(politicos)}")


if __name__ == "__main__":
    main()
