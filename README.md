<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:002776,50:009c3b,100:ffdf00&height=200&section=header&text=🏛️%20Honestidade%20Políticos%20BR&fontSize=40&fontColor=ffffff&animation=twinkling&fontAlignY=35&desc=Índice%20de%20Transparência%20baseado%20em%20Dados%20Públicos&descAlignY=55&descSize=17&descColor=ffffff" width="100%"/>

<br/>

[![Stars](https://img.shields.io/github/stars/Ronbragaglia/honestidade-politicos-brasil?style=for-the-badge&color=ffdf00&logo=github&logoColor=black&label=⭐+Stars)](https://github.com/Ronbragaglia/honestidade-politicos-brasil/stargazers)
[![Forks](https://img.shields.io/github/forks/Ronbragaglia/honestidade-politicos-brasil?style=for-the-badge&color=009c3b&logo=git&logoColor=white&label=🍴+Forks)](https://github.com/Ronbragaglia/honestidade-politicos-brasil/network)
[![Issues](https://img.shields.io/github/issues/Ronbragaglia/honestidade-politicos-brasil?style=for-the-badge&color=e74c3c&logo=github&logoColor=white)](https://github.com/Ronbragaglia/honestidade-politicos-brasil/issues)
[![License](https://img.shields.io/badge/License-CC%20BY%204.0-blue?style=for-the-badge&logo=creative-commons&logoColor=white)](LICENSE)

<br/>

### 🚨 Sem viés partidário. Sem opinião. Apenas dados públicos documentados.

**18 senadores** · **20 deputados** · **27 governadores** · **4 presidentes** · **Atualizado Abr/2026**

</div>

---

## 🤔 Por que este projeto existe?

> **71% dos brasileiros** não sabem o que seu deputado vota. **83%** não acompanham gastos da cota parlamentar. Este projeto muda isso.

Nós coletamos dados de **fontes 100% oficiais** (TSE, STF, Portal da Transparência, APIs da Câmara/Senado) e transformamos em informação acessível para qualquer cidadão.

**Não somos de esquerda. Não somos de direita. Somos de dados.**

---

## 📊 Score de Transparência — Como funciona?

Cada político recebe um score de **0 a 100** baseado em critérios objetivos:

```
┌─────────────────────────────────────────────────────────┐
│  SCORE = Ficha Limpa (25%) + Coerência (20%)            │
│        + Presença (15%) + Patrimônio (15%)              │
│        + Produtividade (15%) + Ética Recursos (10%)     │
└─────────────────────────────────────────────────────────┘
```

| Score | Classificação | Significado |
|:---:|:---:|:---|
| 🟢 80-100 | **Excelente** | Ficha limpa, presente, produtivo, transparente |
| 🔵 60-79 | **Bom** | Atuação positiva com pontos de atenção |
| 🟡 40-59 | **Regular** | Desempenho mediano, inconsistências |
| 🟠 20-39 | **Ruim** | Problemas sérios documentados |
| 🔴 0-19 | **Péssimo** | Condenações, ausências graves, falta total de transparência |

👉 [Veja a metodologia completa →](metodologia/calculo-score.md)

---

## 🏛️ Rankings por Esfera

<table>
<tr>
<td width="50%" valign="top">

### 👔 [Presidentes](dados/presidentes.md)
Os 4 últimos presidentes com score de transparência, processos e patrimônio declarado.

**Preview:**
| Presidente | Score |
|---|:---:|
| Dilma Rousseff | 🟡 48 |
| Lula | 🟡 45 |
| Bolsonaro | 🟠 32 |
| Temer | 🟠 28 |

</td>
<td width="50%" valign="top">

### 🏛️ [Senadores](dados/senadores/_index.md)
Ranking de 18 senadores com presença, processos e produtividade legislativa.

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
Ranking de 20 deputados + análise por partido e gastos da cota parlamentar.

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

## 🛠️ Scripts de Coleta Automatizada

```bash
# Coletar dados de todos os deputados da legislatura atual
python3 scripts/coleta-camara.py --legislatura 57 --output dados/deputados-federais/

# Requer apenas: pip install requests
```

👉 [Ver script completo →](scripts/coleta-camara.py)

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

| Perfil | Como ajudar |
|:---:|:---|
| 🔬 **Pesquisador** | Adicione dados com fontes verificáveis via PR |
| 💻 **Desenvolvedor** | Melhore os scripts de coleta ou crie novos |
| 📰 **Jornalista** | Use os dados livremente (CC-BY-4.0, só atribuir) |
| 🗳️ **Cidadão** | Dê ⭐, compartilhe, abra Issues com sugestões |

### Regras

- ✅ Todo dado DEVE ter fonte oficial linkada
- ✅ Neutralidade jornalística absoluta
- ❌ Sem opinião pessoal ou linguagem pejorativa
- ❌ Sem dados de fontes não-oficiais para scoring

---

## 🌟 Dê uma estrela!

> Se você acredita que **transparência fortalece a democracia**, dê uma ⭐ neste repositório.
>
> Cada estrela ajuda mais brasileiros a encontrarem este projeto e cobrarem seus representantes com dados.

---

<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:ffdf00,50:009c3b,100:002776&height=100&section=footer&text=Dados%20públicos%2C%20para%20o%20público.&fontSize=16&fontColor=ffffff&fontAlignY=65" width="100%"/>

> *"A transparência é o melhor desinfetante."* — Louis Brandeis

**Mantido pela comunidade** · [Rone Bragaglia](https://github.com/Ronbragaglia) · **CC-BY-4.0**

</div>
