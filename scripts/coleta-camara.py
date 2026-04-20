"""
Coleta de dados da API da Câmara dos Deputados
https://dadosabertos.camara.leg.br/api/v2/

Uso: python3 coleta-camara.py [--legislatura 57] [--output dados/deputados-federais/]
"""

import requests
import json
import time
import argparse
from datetime import datetime
from pathlib import Path

BASE_URL = "https://dadosabertos.camara.leg.br/api/v2"
HEADERS = {"Accept": "application/json"}
RATE_LIMIT_DELAY = 0.5  # segundos entre requests


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
    """Busca votações de um deputado na legislatura atual."""
    url = f"{BASE_URL}/deputados/{deputado_id}/votacoes"
    params = {"itens": 100, "ordem": "DESC", "ordenarPor": "dataHoraRegistro"}
    
    response = requests.get(url, params=params, headers=HEADERS)
    response.raise_for_status()
    return response.json()["dados"]


def get_presenca(deputado_id: int) -> dict:
    """Busca presença em sessões (eventos) de um deputado."""
    url = f"{BASE_URL}/deputados/{deputado_id}/eventos"
    params = {"itens": 100}
    
    response = requests.get(url, params=params, headers=HEADERS)
    response.raise_for_status()
    eventos = response.json()["dados"]
    
    total = len(eventos)
    presentes = sum(1 for e in eventos if e.get("presenca") == "Presença")
    
    return {
        "total_sessoes": total,
        "presencas": presentes,
        "percentual": round((presentes / total * 100), 1) if total > 0 else 0
    }


def calcular_score_despesas(despesas: list, media_anual: float = 120000) -> int:
    """Calcula score de ética no uso de recursos (0-100)."""
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


def gerar_ficha(deputado: dict, despesas: list, votacoes: list) -> str:
    """Gera ficha markdown de um deputado."""
    nome = deputado["nome"]
    partido = deputado.get("siglaPartido", "?")
    uf = deputado.get("siglaUf", "?")
    
    total_gasto = sum(d.get("valorDocumento", 0) for d in despesas if d.get("valorDocumento", 0) > 0)
    total_votacoes = len(votacoes)
    
    ficha = f"""# {nome} ({partido}-{uf})

## Dados Gerais

| Info | Valor |
|------|-------|
| Partido | {partido} |
| Estado | {uf} |
| Legislatura | 57ª (2023-2027) |
| ID Câmara | {deputado['id']} |

## Cota Parlamentar

- **Total gasto (período)**: R$ {total_gasto:,.2f}
- **Despesas registradas**: {len(despesas)}

## Atividade Legislativa

- **Votações participadas**: {total_votacoes}

## Score

> ⚠️ Score em cálculo — aguardando dados completos de processos e coerência.

---

*Fonte: [API Câmara dos Deputados](https://dadosabertos.camara.leg.br)*
*Última coleta: {datetime.now().strftime('%Y-%m-%d')}*
"""
    return ficha


def main():
    parser = argparse.ArgumentParser(description="Coleta dados da Câmara dos Deputados")
    parser.add_argument("--legislatura", type=int, default=57, help="Número da legislatura (default: 57)")
    parser.add_argument("--output", type=str, default="dados/deputados-federais", help="Diretório de saída")
    parser.add_argument("--limit", type=int, default=10, help="Limite de deputados (para teste)")
    args = parser.parse_args()
    
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Buscando deputados da {args.legislatura}ª legislatura...")
    deputados = get_deputados(args.legislatura)
    print(f"Encontrados: {len(deputados)} deputados")
    
    for i, dep in enumerate(deputados[:args.limit]):
        print(f"[{i+1}/{min(args.limit, len(deputados))}] {dep['nome']}...")
        
        try:
            despesas = get_despesas(dep["id"], ano=2025)
            time.sleep(RATE_LIMIT_DELAY)
            
            votacoes = get_votacoes(dep["id"])
            time.sleep(RATE_LIMIT_DELAY)
            
            ficha = gerar_ficha(dep, despesas, votacoes)
            
            filename = dep["nome"].lower().replace(" ", "-") + ".md"
            filepath = output_dir / filename
            filepath.write_text(ficha, encoding="utf-8")
            
        except Exception as e:
            print(f"  ERRO: {e}")
            continue
    
    print(f"\nFichas salvas em {output_dir}/")


if __name__ == "__main__":
    main()
