<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:002776,50:009c3b,100:ffdf00&height=200&section=header&text=🏛️%20Honestidade%20Políticos%20BR&fontSize=40&fontColor=ffffff&animation=twinkling&fontAlignY=35&desc=Índice%20de%20Transparência%20baseado%20em%20Dados%20Públicos&descAlignY=55&descSize=17&descColor=ffffff" width="100%"/>

<br/>

[![Stars](https://img.shields.io/github/stars/Ronbragaglia/honestidade-politicos-brasil?style=for-the-badge&color=ffdf00&logo=github&logoColor=black&label=⭐+Stars)](https://github.com/Ronbragaglia/honestidade-politicos-brasil/stargazers)
[![Forks](https://img.shields.io/github/forks/Ronbragaglia/honestidade-politicos-brasil?style=for-the-badge&color=009c3b&logo=git&logoColor=white&label=🍴+Forks)](https://github.com/Ronbragaglia/honestidade-politicos-brasil/network)
[![Issues](https://img.shields.io/github/issues/Ronbragaglia/honestidade-politicos-brasil?style=for-the-badge&color=e74c3c&logo=github&logoColor=white)](https://github.com/Ronbragaglia/honestidade-politicos-brasil/issues)
[![License](https://img.shields.io/badge/License-CC%20BY%204.0-blue?style=for-the-badge&logo=creative-commons&logoColor=white)](LICENSE)

<br/>

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat-square&logo=python&logoColor=white)](scripts/)
[![GitHub Actions](https://img.shields.io/github/actions/workflow/status/Ronbragaglia/honestidade-politicos-brasil/validar-dados.yml?style=flat-square&logo=githubactions&logoColor=white&label=CI)](https://github.com/Ronbragaglia/honestidade-politicos-brasil/actions)
[![Last Commit](https://img.shields.io/github/last-commit/Ronbragaglia/honestidade-politicos-brasil?style=flat-square&color=009c3b)](https://github.com/Ronbragaglia/honestidade-politicos-brasil/commits)
[![Repo Size](https://img.shields.io/github/repo-size/Ronbragaglia/honestidade-politicos-brasil?style=flat-square&color=ffdf00)](https://github.com/Ronbragaglia/honestidade-politicos-brasil)

<br/>

### 🚨 Sem viés partidário. Sem opinião. Apenas dados públicos documentados.

</div>

<div align="center">

```
 ╔═══════════════════════════════════════════════════════════════════╗
 ║  📊 69 políticos avaliados · 4 esferas · 15 partidos · 6 fontes ║
 ║     Presidentes · Senadores · Deputados · Governadores           ║
 ║     Atualizado Abril/2026                                        ║
 ╚═══════════════════════════════════════════════════════════════════╝
```

</div>

---

## 🤔 Por que este projeto existe?

> **71% dos brasileiros** não sabem o que seu deputado vota.
> **83%** não acompanham gastos da cota parlamentar.
> **Este projeto muda isso.**

Nós coletamos dados de **fontes 100% oficiais** — TSE, STF, Portal da Transparência, APIs da Câmara e do Senado — e transformamos em informação acessível para qualquer cidadão.

Cada político recebe um **score de 0 a 100**, calculado com critérios transparentes e verificáveis. Sem achismo. Sem filtro ideológico. Sem editorial.

**Não somos de esquerda. Não somos de direita. Somos de dados.**

---

## ⚙️ Como Funciona — Pipeline

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│    Fontes     │    │   Scripts    │    │    Dados     │    │    Score     │    │   Rankings   │
│   Oficiais   │───▶│   Python     │───▶│    JSON/MD   │───▶│   0 — 100   │───▶│   Públicos   │
│ TSE/Câmara/  │    │ Automatizado │    │ Estruturado  │    │ Transparente │    │  Por Esfera  │
│  STF/Senado  │    │              │    │              │    │              │    │              │
└──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘
```

---

## 📊 Score de Transparência

Cada político recebe um score de **0 a 100** baseado em 6 critérios objetivos:

```
┌─────────────────────────────────────────────────────────────────┐
│  SCORE = Ficha Limpa (25%) + Coerência (20%) + Presença (15%)  │
│        + Patrimônio (15%) + Produtividade (15%) + Ética (10%)  │
└─────────────────────────────────────────────────────────────────┘
```

**Exemplo visual** — como ler o score:

```
  0        20        40        60        80       100
  ├─────────┼─────────┼─────────┼─────────┼─────────┤
  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░░░░░░░  Score: 78
  🔴 Péssimo  🟠 Ruim  🟡 Regular  🔵 Bom  🟢 Excelente
```

| Score | Classificação | Significado |
|:---:|:---:|:---|
| 🟢 80–100 | **Excelente** | Ficha limpa, presente, produtivo, transparente |
| 🔵 60–79 | **Bom** | Atuação positiva com pontos de atenção |
| 🟡 40–59 | **Regular** | Desempenho mediano, inconsistências |
| 🟠 20–39 | **Ruim** | Problemas sérios documentados |
| 🔴 0–19 | **Péssimo** | Condenações, ausências graves, falta total de transparência |

👉 [Veja a metodologia completa →](metodologia/calculo-score.md)

---

## 🏛️ Rankings por Esfera

<table>
<tr>
<td width="50%" valign="top">

### 👔 [Presidentes](dados/presidentes.md)
Os 4 últimos presidentes com score de transparência, processos e patrimônio declarado.

| Presidente | Score |
|---|:---:|
| Dilma Rousseff | 🟡 48 |
| Lula | 🟡 45 |
| Bolsonaro | 🟠 32 |
| Temer | 🟠 28 |

</td>
<td width="50%" valign="top">

### 🏛️ [Senadores](dados/senadores/_index.md)
18 senadores avaliados com presença, processos e produtividade legislativa.

**Top 3:**
| Senador | Score |
|---|:---:|
| Eduardo Girão (Novo-CE) | 🟢 82 |
| Sergio Moro (União-PR) | 🟢 80 |
| Eliziane Gama (PSD-MA) | 🔵 78 |

</td>
</tr>
<tr>
<td width="50%" valign="top">

### 🏛️ [Deputados Federais](dados/deputados-federais/_index.md)
20 deputados federais + análise por partido e gastos da cota parlamentar.

**Top 3:**
| Deputado | Score |
|---|:---:|
| Tábata Amaral (PSB-SP) | 🟢 85 |
| Adriana Ventura (Novo-SP) | 🟢 83 |
| Marcel van Hattem (Novo-RS) | 🟢 81 |

</td>
<td width="50%" valign="top">

### 🗺️ [Governadores](dados/governadores/_index.md)
Todos os 27 governadores dos estados brasileiros com score e processos.

**Top 3:**
| Governador | Score |
|---|:---:|
| Eduardo Leite (PSDB-RS) | 🟢 80 |
| Renato Casagrande (PSB-ES) | 🔵 77 |
| Raquel Lyra (PSDB-PE) | 🔵 75 |

</td>
</tr>
</table>

> 📈 **[Ver Dashboard completo com gráficos e estatísticas →](DASHBOARD.md)**

---

## 📡 Fontes Oficiais (100% dados públicos)

| Fonte | O que coletamos | URL |
|:---:|:---|:---|
| 🏛️ TSE | Candidaturas, patrimônio, partidos | [dados.tse.jus.br](https://dados.tse.jus.br) |
| 📋 Câmara | Votações, presença, despesas | [dadosabertos.camara.leg.br](https://dadosabertos.camara.leg.br) |
| 📋 Senado | Votações, projetos de lei | [legis.senado.leg.br](https://legis.senado.leg.br/dadosabertos) |
| 💰 Transparência | Cota parlamentar, viagens | [portaldatransparencia.gov.br](https://portaldatransparencia.gov.br) |
| ⚖️ STF | Processos criminais | [portal.stf.jus.br](https://portal.stf.jus.br) |
| ⚖️ CNJ | Consulta processual | [cnj.jus.br](https://www.cnj.jus.br) |

---

## 📁 Estrutura do Projeto

```
honestidade-politicos-brasil/
├── dados/                          # Dados dos políticos
│   ├── presidentes.md              #   4 presidentes recentes
│   ├── senadores/                  #   18 senadores com ranking
│   │   └── _index.md
│   ├── deputados-federais/         #   20 deputados federais
│   │   └── _index.md
│   └── governadores/               #   27 governadores estaduais
│       └── _index.md
├── metodologia/                    # Metodologia documentada
│   ├── calculo-score.md            #   Fórmula do score (pesos, critérios)
│   └── fontes.md                   #   APIs e fontes utilizadas
├── scripts/                        # Coleta automatizada
│   ├── coleta-camara.py            #   Coletor da API da Câmara
│   └── requirements.txt            #   Dependências Python
├── .github/
│   ├── workflows/                  #   CI/CD automatizado
│   └── ISSUE_TEMPLATE/             #   Template para contestações
│       └── contestacao.md
├── DASHBOARD.md                    # Resumo visual com gráficos
├── CONTRIBUTING.md                 # Guia de contribuição
├── LICENSE                         # CC-BY-4.0
└── README.md                       # Este arquivo
```

---

## 💻 Acesso aos Dados

Os dados estão disponíveis em Markdown estruturado. Você pode acessá-los diretamente ou processá-los programaticamente:

```python
# Exemplo: ler e processar dados do ranking
import json, re
from pathlib import Path

# Parsear dados do markdown
def extrair_scores(arquivo_md):
    """Extrai nomes e scores de um arquivo de ranking."""
    conteudo = Path(arquivo_md).read_text(encoding='utf-8')
    # Regex para capturar linhas da tabela com score
    padrao = r'\| .+? \| .+? \| .+? \| .+? \| [🟢🔵🟡🟠🔴] (\d+)'
    return re.findall(padrao, conteudo)

# Coletar dados frescos da API da Câmara
# python3 scripts/coleta-camara.py --legislatura 57 --output dados/deputados-federais/
```

```bash
# Coleta automatizada via CLI
pip install requests
python3 scripts/coleta-camara.py --legislatura 57 --limit 20

# Output: fichas individuais em dados/deputados-federais/
```

---

## 🤖 Automação (GitHub Actions)

O projeto utiliza GitHub Actions para manter os dados atualizados e garantir qualidade:

| Workflow | Frequência | O que faz |
|:---:|:---:|:---|
| Coleta Câmara | Semanal | Atualiza votações e despesas via API |
| Validação de PR | A cada PR | Verifica se fontes oficiais estão linkadas |
| Contestação | Manual | Template estruturado para políticos contestarem dados |

Políticos ou assessorias podem contestar dados abrindo uma [Issue de Contestação](https://github.com/Ronbragaglia/honestidade-politicos-brasil/issues/new?template=contestacao.md) com evidências documentais.

---

## ⚖️ Princípios Inegociáveis

| Princípio | Como aplicamos |
|:---:|:---|
| 🏳️ **Apartidarismo** | Avaliamos PT, PL, MDB, PSOL, Novo — todos pela mesma régua |
| 🔍 **Verificabilidade** | Todo dado tem link para fonte oficial (.gov.br / .jus.br) |
| ⚖️ **Presunção de inocência** | Réu sem condenação em 2ª instância NÃO perde pontos |
| 🗣️ **Direito de resposta** | Políticos podem abrir Issues contestando com evidências |
| 📅 **Atualização** | Dados desatualizados são marcados com ⚠️ |

---

## 🤝 Como Contribuir

<table>
<tr><th>Perfil</th><th>Como ajudar</th><th>Primeiros passos</th></tr>
<tr>
<td>🔬 <b>Pesquisador</b></td>
<td>Adicione dados com fontes verificáveis</td>
<td>

1. Fork → 2. Crie arquivo em `dados/` → 3. Link fonte .gov.br → 4. PR
</td>
</tr>
<tr>
<td>💻 <b>Desenvolvedor</b></td>
<td>Melhore scripts ou crie novos coletores</td>
<td>

1. Veja `scripts/` → 2. APIs em `metodologia/fontes.md` → 3. PR com testes
</td>
</tr>
<tr>
<td>📰 <b>Jornalista</b></td>
<td>Use os dados livremente (CC-BY-4.0)</td>
<td>

Cite como: *"Dados: Honestidade Políticos BR (CC-BY-4.0)"*
</td>
</tr>
<tr>
<td>🗳️ <b>Cidadão</b></td>
<td>Dê ⭐, compartilhe, abra Issues</td>
<td>

Encontrou erro? [Abra uma Issue](https://github.com/Ronbragaglia/honestidade-politicos-brasil/issues)
</td>
</tr>
</table>

### Regras para contribuições

- ✅ Todo dado **DEVE** ter fonte oficial linkada (.gov.br / .jus.br)
- ✅ Neutralidade jornalística absoluta — sem adjetivos, sem opinião
- ✅ PRs passam por revisão de fontes antes do merge
- ❌ Sem opinião pessoal ou linguagem pejorativa
- ❌ Sem dados de fontes não-oficiais para scoring

👉 [Guia completo de contribuição →](CONTRIBUTING.md)

---

## 🌟 Dê uma estrela!

> Se você acredita que **transparência fortalece a democracia**, dê uma ⭐ neste repositório.
>
> Cada estrela ajuda mais brasileiros a encontrarem este projeto e cobrarem seus representantes **com dados, não com achismo**.

---

<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:ffdf00,50:009c3b,100:002776&height=100&section=footer&text=Dados%20públicos%2C%20para%20o%20público.&fontSize=16&fontColor=ffffff&fontAlignY=65" width="100%"/>

> *"A transparência é o melhor desinfetante."* — Louis Brandeis

**Mantido pela comunidade** · [Rone Bragaglia](https://github.com/Ronbragaglia) · **CC-BY-4.0**

</div>
