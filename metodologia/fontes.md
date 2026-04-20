# 📚 Fontes Oficiais e Metodologia de Coleta

## APIs Públicas Utilizadas

### 1. Câmara dos Deputados
- **URL**: `https://dadosabertos.camara.leg.br/api/v2/`
- **Dados**: deputados, votações, proposições, despesas, eventos
- **Rate limit**: sem autenticação, 1000 req/hora
- **Formato**: JSON/XML/CSV

Endpoints principais:
```
GET /deputados — lista de deputados da legislatura
GET /deputados/{id}/despesas — gastos da cota
GET /deputados/{id}/votacoes — como votou
GET /votacoes/{id}/votos — votos individuais numa votação
GET /proposicoes — projetos de lei
```

### 2. Senado Federal
- **URL**: `https://legis.senado.leg.br/dadosabertos/`
- **Dados**: senadores, votações, matérias, presenças
- **Formato**: JSON/XML

### 3. TSE (Tribunal Superior Eleitoral)
- **URL**: `https://dadosabertos.tse.jus.br/`
- **Dados**: candidaturas, prestação de contas, patrimônio declarado
- **Formato**: CSV (bulk download por eleição)

### 4. Portal da Transparência
- **URL**: `https://api.portaldatransparencia.gov.br/`
- **Dados**: cota parlamentar, viagens, cartões corporativos
- **Autenticação**: necessita cadastro (gratuito)

### 5. IBGE
- **URL**: `https://servicodados.ibge.gov.br/api/`
- **Dados**: indicadores socioeconômicos (para contextualização)

## Periodicidade de Atualização

| Dado | Frequência | Método |
|------|-----------|--------|
| Votações | Semanal | API Câmara/Senado |
| Despesas cota | Mensal | API Transparência |
| Patrimônio | A cada eleição (4 anos) | TSE bulk |
| Processos | Trimestral | Consulta manual STF/STJ |
| Presença | Semanal | API Câmara/Senado |

## Limitações

- **Patrimônio**: apenas o declarado ao TSE — não inclui offshores, laranjas ou bens de familiares
- **Processos**: apenas os públicos — segredo de justiça não é contabilizado
- **Votações secretas**: quando o voto é secreto, não há como medir coerência
- **Lobby**: influência indireta não é mensurável por dados públicos
- **Contexto**: um voto "contra" a promessa pode ter justificativa legítima (mudança de cenário)

## Integridade dos Dados

- Todos os dados são coletados via APIs oficiais ou sites .gov.br/.jus.br
- Nenhum dado de fonte jornalística é usado para scoring (apenas para contexto)
- Divergências entre fontes são marcadas com ⚠️
- Hash SHA-256 dos datasets é mantido para auditabilidade
