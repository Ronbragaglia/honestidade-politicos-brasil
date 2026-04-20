# 🇧🇷 Índice de Honestidade dos Políticos do Brasil

> Plataforma colaborativa de transparência política baseada em dados públicos. Sem viés partidário — apenas fatos documentados.

## 📊 O que este projeto rastreia

| Métrica | Fonte |
|---------|-------|
| Processos criminais | TSE, STF, STJ, TJs |
| Patrimônio declarado vs. evolução | Declarações ao TSE |
| Votações vs. promessas de campanha | Câmara/Senado API |
| Presença em sessões | Portal da Câmara / Senado |
| Uso da cota parlamentar | Portal da Transparência |
| Projetos de lei apresentados | Câmara/Senado |
| Condenações em 2ª instância | Tribunais |
| Mudanças de partido | TSE |

## 🏛️ Índice por Esfera

- [Presidentes](dados/presidentes.md)
- [Senadores](dados/senadores/)
- [Deputados Federais](dados/deputados-federais/)
- [Governadores](dados/governadores/)

## 📈 Metodologia de Score

Cada político recebe um **Score de Transparência (0-100)** baseado em:

| Critério | Peso | Como mede |
|----------|------|-----------|
| Ficha Limpa | 25% | Condenações em órgão colegiado |
| Coerência | 20% | Votações alinhadas às promessas |
| Presença | 15% | % de sessões que participou |
| Transparência patrimonial | 15% | Consistência da evolução patrimonial |
| Produtividade legislativa | 15% | Projetos apresentados e aprovados |
| Uso ético de recursos | 10% | Gastos da cota dentro do razoável |

### Classificação

| Score | Classificação | Cor |
|-------|--------------|-----|
| 80-100 | Excelente | 🟢 |
| 60-79 | Bom | 🔵 |
| 40-59 | Regular | 🟡 |
| 20-39 | Ruim | 🟠 |
| 0-19 | Péssimo | 🔴 |

## 📂 Estrutura do Projeto

```
dados/
├── presidentes.md
├── senadores/
│   ├── _index.md          # ranking geral
│   └── nome-sobrenome.md  # ficha individual
├── deputados-federais/
│   ├── _index.md
│   └── nome-sobrenome.md
├── governadores/
│   ├── _index.md
│   └── nome-sobrenome.md
metodologia/
├── fontes.md              # todas as fontes oficiais usadas
├── calculo-score.md       # fórmula detalhada
└── limitacoes.md          # o que NÃO conseguimos medir
scripts/
├── coleta-tse.py          # scraper dados TSE
├── coleta-camara.py       # API Câmara dos Deputados
└── coleta-senado.py       # API Senado Federal
```

## 🔍 Fontes Oficiais

| Fonte | URL | Dados |
|-------|-----|-------|
| TSE | dados.tse.jus.br | Candidaturas, patrimônio, partidos |
| Câmara | dadosabertos.camara.leg.br | Votações, presença, gastos |
| Senado | www12.senado.leg.br/dados-abertos | Votações, projetos |
| Portal Transparência | portaldatransparencia.gov.br | Cota parlamentar |
| STF | portal.stf.jus.br | Processos |
| CNJ | cnj.jus.br | Consulta processual |

## 🤝 Como Contribuir

1. **Pesquisadores**: adicione dados com fontes verificáveis
2. **Desenvolvedores**: melhore os scripts de coleta
3. **Jornalistas**: use os dados livremente (CC-BY-4.0)

### Regras de Contribuição

- Todo dado DEVE ter fonte oficial linkada
- Sem opinião pessoal — apenas fatos documentados
- Sem linguagem pejorativa — neutralidade jornalística
- Pull Requests passam por revisão de fontes antes de merge

## ⚖️ Princípios

1. **Apartidarismo** — não favorecemos nenhum partido ou espectro político
2. **Verificabilidade** — todo dado tem fonte pública rastreável
3. **Atualização** — dados desatualizados são marcados com ⚠️
4. **Presunção de inocência** — réus sem condenação em 2ª instância não perdem pontos na "Ficha Limpa"
5. **Direito de resposta** — políticos podem abrir Issues contestando dados com evidências

## 📜 Licença

[Creative Commons Attribution 4.0 (CC-BY-4.0)](LICENSE) — use livremente com atribuição.

---

> "A transparência é o melhor desinfetante." — Louis Brandeis

*Projeto mantido pela comunidade. Dados públicos, para o público.*
