"""
Coleta de dados da API da Camara dos Deputados.
https://dadosabertos.camara.leg.br/api/v2/

Mudancas (2026-05):
- Endpoint /deputados/{id}/votacoes foi descontinuado (retorna 405).
- Migracao: agora listamos votacoes da legislatura uma vez e cruzamos com
  /votacoes/{id}/votos (cache global). Mais eficiente: ~200 requests fixos
  + 1 por deputado para detalhes, em vez de N requests N+1.
- Adicionado retry com backoff exponencial via urllib3.Retry.
- Logging estruturado em vez de prints soltos.
- Type hints completos.

Uso:
    python3 coleta-camara.py [--legislatura 57] [--ano 2026]
                             [--limit 20] [--output dados/deputados-federais]
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

BASE_URL = "https://dadosabertos.camara.leg.br/api/v2"
HEADERS = {"Accept": "application/json", "User-Agent": "honestidade-politicos-brasil/2.0"}
RATE_LIMIT_DELAY = 0.4  # segundos entre requests fora do retry
TIMEOUT = 30  # segundos por request
MEDIA_ANUAL_COTA = 120_000  # estimativa em R$

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
    stream=sys.stderr,
)
logger = logging.getLogger("coleta-camara")


# ---------------------------------------------------------------------------
# Sessao HTTP com retry/backoff exponencial
# ---------------------------------------------------------------------------


def make_session() -> requests.Session:
    """Cria sessao com retry para 429/5xx (tempo total ate ~46s no pior caso)."""
    session = requests.Session()
    retry = Retry(
        total=5,
        backoff_factor=1.5,   # delays: 0, 1.5, 3, 6, 12, 24
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset(["GET"]),
        respect_retry_after_header=True,
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry, pool_connections=10, pool_maxsize=20)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    session.headers.update(HEADERS)
    return session


SESSION = make_session()
_VOTOS_CACHE: dict[str, list[dict[str, Any]]] = {}


def _get_json(url: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    """GET com tratamento uniforme. Levanta para 4xx/5xx finais."""
    response = SESSION.get(url, params=params, timeout=TIMEOUT)
    if response.status_code >= 400:
        logger.warning("HTTP %s em %s params=%s", response.status_code, url, params)
        response.raise_for_status()
    return response.json()


# ---------------------------------------------------------------------------
# UI helpers
# ---------------------------------------------------------------------------


def progresso(atual: int, total: int, prefixo: str = "") -> None:
    largura = 30
    pct = atual / total if total > 0 else 0
    preenchido = int(largura * pct)
    barra = "#" * preenchido + "-" * (largura - preenchido)
    sys.stdout.write(f"\r{prefixo} [{barra}] {pct*100:.1f}% ({atual}/{total})")
    sys.stdout.flush()
    if atual == total:
        sys.stdout.write("\n")
        sys.stdout.flush()


# ---------------------------------------------------------------------------
# Coleta
# ---------------------------------------------------------------------------


def get_deputados(legislatura: int = 57) -> list[dict[str, Any]]:
    """Busca todos os deputados de uma legislatura."""
    url = f"{BASE_URL}/deputados"
    params = {
        "idLegislatura": legislatura,
        "itens": 513,
        "ordem": "ASC",
        "ordenarPor": "nome",
    }
    return _get_json(url, params=params)["dados"]


def get_despesas(deputado_id: int, ano: int | None = None) -> list[dict[str, Any]]:
    """Busca despesas da cota parlamentar de um deputado (paginado)."""
    url = f"{BASE_URL}/deputados/{deputado_id}/despesas"
    params: dict[str, Any] = {
        "itens": 100,
        "ordem": "DESC",
        "ordenarPor": "dataDocumento",
    }
    if ano:
        params["ano"] = ano

    all_despesas: list[dict[str, Any]] = []
    page = 1

    while True:
        params["pagina"] = page
        try:
            data = _get_json(url, params=params)["dados"]
        except requests.HTTPError as exc:
            logger.warning("despesas dep=%s pag=%s falhou: %s", deputado_id, page, exc)
            break

        if not data:
            break
        all_despesas.extend(data)
        page += 1
        time.sleep(RATE_LIMIT_DELAY)

    return all_despesas


def listar_votacoes_legislatura(ano_inicio: int, limite: int = 100) -> list[dict[str, Any]]:
    """Lista votacoes recentes da Camara a partir do ano inicial."""
    url = f"{BASE_URL}/votacoes"
    params: dict[str, Any] = {
        "dataInicio": f"{ano_inicio}-01-01",
        "ordem": "DESC",
        "ordenarPor": "dataHoraRegistro",
        "itens": 100,
    }
    all_votacoes: list[dict[str, Any]] = []
    page = 1
    while len(all_votacoes) < limite:
        params["pagina"] = page
        try:
            data = _get_json(url, params=params)["dados"]
        except requests.HTTPError as exc:
            logger.warning("listar votacoes pag=%s falhou: %s", page, exc)
            break
        if not data:
            break
        all_votacoes.extend(data)
        page += 1
        time.sleep(RATE_LIMIT_DELAY)
        if page > 5:
            break
    all_votacoes = all_votacoes[:limite]
    logger.info("Carregadas %s votacoes da legislatura.", len(all_votacoes))
    return all_votacoes


def prefetch_votos(votacoes: list[dict[str, Any]]) -> None:
    """Pre-busca todos os votos individuais ANTES do loop de deputados.

    Isso faz com que get_votos() vire O(1) in-memory durante o processing,
    eliminando sleeps no hot path.
    """
    n = len(votacoes)
    logger.info("Pre-buscando votos de %s votacoes...", n)
    for i, votacao in enumerate(votacoes, start=1):
        id_vot = str(votacao.get("id", ""))
        if not id_vot or id_vot in _VOTOS_CACHE:
            continue
        url = f"{BASE_URL}/votacoes/{id_vot}/votos"
        try:
            data = _get_json(url, params={"itens": 600})["dados"]
        except requests.HTTPError as exc:
            logger.warning("votos votacao=%s falhou: %s", id_vot, exc)
            data = []
        _VOTOS_CACHE[id_vot] = data
        if i % 20 == 0:
            logger.info("  prefetch: %s/%s", i, n)
        time.sleep(RATE_LIMIT_DELAY)
    logger.info("Prefetch completo: %s votacoes em cache.", len(_VOTOS_CACHE))


def get_votacoes_deputado(
    deputado_id: int, votacoes_legislatura: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Conta participacao do deputado iterando puramente o cache (sem I/O)."""
    participacoes: list[dict[str, Any]] = []
    for votacao in votacoes_legislatura:
        id_vot = str(votacao.get("id", ""))
        if not id_vot:
            continue
        votos = _VOTOS_CACHE.get(id_vot, [])
        for v in votos:
            dep_ref = v.get("deputado_") or v.get("deputado") or {}
            if dep_ref.get("id") == deputado_id:
                participacoes.append({
                    "idVotacao": id_vot,
                    "voto": v.get("tipoVoto"),
                    "data": votacao.get("dataHoraRegistro"),
                })
                break
    return participacoes


def get_presenca(deputado_id: int) -> dict[str, Any]:
    """
    Estima presenca em eventos a partir de /deputados/{id}/eventos.

    A API nao expoe presenca diretamente. Heuristica:
    - Eventos cuja data ja passou + situacao Encerrada/Realizada/Em andamento.
    - Se sem campo situacao, todos os passados sao contados.
    """
    url = f"{BASE_URL}/deputados/{deputado_id}/eventos"
    params: dict[str, Any] = {
        "itens": 100,
        "ordem": "DESC",
        "ordenarPor": "dataHoraInicio",
    }
    all_eventos: list[dict[str, Any]] = []
    page = 1
    while True:
        params["pagina"] = page
        try:
            data = _get_json(url, params=params)["dados"]
        except requests.HTTPError as exc:
            logger.warning("eventos dep=%s pag=%s falhou: %s", deputado_id, page, exc)
            break
        if not data:
            break
        all_eventos.extend(data)
        page += 1
        time.sleep(RATE_LIMIT_DELAY)
        if page > 3:
            break

    agora = datetime.now().isoformat()
    passados = [e for e in all_eventos if e.get("dataHoraInicio", "") < agora]
    total = len(passados)
    situacoes_presenca = {"encerrada", "realizada", "em andamento", "finalizada"}
    presentes = sum(
        1
        for e in passados
        if (e.get("situacao") or "").strip().lower() in situacoes_presenca
    )
    if presentes == 0 and total > 0:
        presentes = total
    return {
        "total_sessoes": total,
        "presencas": presentes,
        "percentual": round((presentes / total * 100), 1) if total > 0 else 0,
    }


# ---------------------------------------------------------------------------
# Scoring (mantida a logica original)
# ---------------------------------------------------------------------------


def calcular_score_despesas(despesas: list[dict[str, Any]], media: float = MEDIA_ANUAL_COTA) -> int:
    if not despesas:
        return 100
    total = sum(d.get("valorDocumento", 0) for d in despesas if d.get("valorDocumento", 0) > 0)
    if total <= media:
        return 100
    if total <= media * 1.5:
        return 70
    if total <= media * 2:
        return 50
    return 30


def calcular_score_presenca(presenca: dict[str, Any]) -> int:
    return min(100, int(presenca.get("percentual", 0)))


def calcular_score_produtividade(votacoes: list[dict[str, Any]]) -> int:
    n = len(votacoes)
    if n >= 80:
        return 100
    if n >= 50:
        return 80
    if n >= 30:
        return 60
    if n >= 10:
        return 40
    return 20


def calcular_score_total(despesas: int, presenca: int, produtividade: int) -> int:
    return round(presenca * 0.35 + despesas * 0.35 + produtividade * 0.30)


def classificar_score(score: int) -> str:
    if score >= 80:
        return "Excelente"
    if score >= 65:
        return "Bom"
    if score >= 45:
        return "Regular"
    if score >= 25:
        return "Ruim"
    return "Pessimo"


def emoji_score(score: int) -> str:
    return (
        "🟢" if score >= 80
        else "🔵" if score >= 65
        else "🟡" if score >= 45
        else "🟠" if score >= 25
        else "🔴"
    )


def gerar_ficha(
    deputado: dict[str, Any],
    despesas: list[dict[str, Any]],
    votacoes: list[dict[str, Any]],
    presenca: dict[str, Any],
    score_despesas: int,
    score_presenca: int,
    score_produtividade: int,
    score_total: int,
) -> str:
    nome = deputado["nome"]
    partido = deputado.get("siglaPartido", "?")
    uf = deputado.get("siglaUf", "?")
    total_gasto = sum(d.get("valorDocumento", 0) for d in despesas if d.get("valorDocumento", 0) > 0)
    classificacao = classificar_score(score_total)
    emoji = emoji_score(score_total)

    return f"""# {nome} ({partido}-{uf})

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

- **Votacoes participadas**: {len(votacoes)}
- **Score produtividade**: {score_produtividade}/100

## Score Final

| Criterio | Score | Peso |
|----------|-------|------|
| Presenca | {score_presenca}/100 | 35% |
| Uso de Recursos | {score_despesas}/100 | 35% |
| Produtividade | {score_produtividade}/100 | 30% |
| **TOTAL** | **{emoji} {score_total}/100 - {classificacao}** | |

> Nota: Criterios adicionais (Ficha Limpa, Coerencia, Patrimonio) serao integrados
> quando fontes externas estiverem disponiveis.

---

*Fonte: [API Camara dos Deputados](https://dadosabertos.camara.leg.br)*
*Ultima coleta: {datetime.now().strftime('%Y-%m-%d')}*
"""


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(description="Coleta dados da Camara dos Deputados")
    parser.add_argument("--legislatura", type=int, default=57)
    parser.add_argument("--output", type=str, default="dados/deputados-federais")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--json", action="store_true", help="Tambem ecoa JSON em stdout")
    parser.add_argument("--ano", type=int, default=None)
    args = parser.parse_args()

    ano = args.ano or datetime.now().year
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    logger.info("Buscando deputados da %sa legislatura...", args.legislatura)
    deputados = get_deputados(args.legislatura)
    total = min(args.limit, len(deputados))
    logger.info("Encontrados: %s deputados (processando %s)", len(deputados), total)

    logger.info("Carregando votacoes da legislatura (cache global)...")
    votacoes_legis = listar_votacoes_legislatura(ano_inicio=ano, limite=100)
    prefetch_votos(votacoes_legis)

    resumo: list[dict[str, Any]] = []
    erros: list[dict[str, str]] = []

    for i, dep in enumerate(deputados[:args.limit]):
        progresso(i + 1, total, prefixo="Coletando")
        try:
            despesas = get_despesas(dep["id"], ano=ano)
            time.sleep(RATE_LIMIT_DELAY)
            votacoes = get_votacoes_deputado(dep["id"], votacoes_legis)
            presenca = get_presenca(dep["id"])
            time.sleep(RATE_LIMIT_DELAY)

            score_desp = calcular_score_despesas(despesas)
            score_pres = calcular_score_presenca(presenca)
            score_prod = calcular_score_produtividade(votacoes)
            score_total = calcular_score_total(score_desp, score_pres, score_prod)

            total_gasto = sum(
                d.get("valorDocumento", 0) for d in despesas if d.get("valorDocumento", 0) > 0
            )

            ficha = gerar_ficha(
                dep, despesas, votacoes, presenca,
                score_desp, score_pres, score_prod, score_total,
            )

            filename = dep["nome"].lower().replace(" ", "-") + ".md"
            (output_dir / filename).write_text(ficha, encoding="utf-8")

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
        except Exception as exc:
            logger.exception("Erro processando %s", dep.get("nome"))
            erros.append({"deputado": dep.get("nome", "?"), "erro": str(exc)})
            continue

    resumo.sort(key=lambda x: x["score_total"], reverse=True)

    dados_export = {
        "legislatura": args.legislatura,
        "data_coleta": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_coletados": len(resumo),
        "erros": len(erros),
        "deputados": resumo,
    }
    if erros:
        dados_export["detalhes_erros"] = erros

    json_path = output_dir / "resumo.json"
    json_path.write_text(json.dumps(dados_export, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info("Resumo JSON salvo em %s", json_path)

    if args.json:
        sys.stdout.write(json.dumps(dados_export, ensure_ascii=False, indent=2) + "\n")

    logger.info("Fichas geradas: %s | Erros: %s", len(resumo), len(erros))
    if resumo:
        media = sum(d["score_total"] for d in resumo) / len(resumo)
        logger.info("Score medio: %.1f/100", media)
        logger.info("Melhor: %s (%s/100)", resumo[0]["nome"], resumo[0]["score_total"])
        logger.info("Pior:   %s (%s/100)", resumo[-1]["nome"], resumo[-1]["score_total"])

    return 0 if not erros else 1


if __name__ == "__main__":
    sys.exit(main())
