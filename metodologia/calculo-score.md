# 📐 Cálculo do Score de Transparência

## Fórmula

```
Score = (FichaLimpa × 0.25) + (Coerencia × 0.20) + (Presenca × 0.15) 
      + (Patrimonio × 0.15) + (Produtividade × 0.15) + (Etica × 0.10)
```

## Detalhamento por Critério

### 1. Ficha Limpa (0-100, peso 25%)

| Situação | Pontos |
|----------|--------|
| Sem processos | 100 |
| Processos arquivados | 90 |
| Réu em 1ª instância (presumido inocente) | 70 |
| Condenado em 2ª instância | 30 |
| Condenado com trânsito em julgado | 10 |
| Inelegível (Lei da Ficha Limpa) | 0 |

### 2. Coerência Votações vs. Promessas (0-100, peso 20%)

Mapeamos as 10 principais promessas de campanha → votações relacionadas.

```
Coerencia = (votações alinhadas / votações relevantes) × 100
```

### 3. Presença em Sessões (0-100, peso 15%)

```
Presenca = (sessões presentes / sessões totais) × 100
```
- Licenças médicas documentadas não contam como ausência
- Missões oficiais não contam como ausência

### 4. Transparência Patrimonial (0-100, peso 15%)

| Situação | Pontos |
|----------|--------|
| Patrimônio compatível com rendimentos | 100 |
| Crescimento acima de 50% sem explicação | 60 |
| Crescimento acima de 200% sem explicação | 30 |
| Ocultação de bens comprovada | 0 |

### 5. Produtividade Legislativa (0-100, peso 15%)

```
Produtividade = min(100, (PLs apresentados × 5) + (PLs aprovados × 30) + (relatórios × 10))
```

### 6. Uso Ético de Recursos (0-100, peso 10%)

- Gastos da cota dentro da média: 100
- Gastos 50% acima da média: 70
- Gastos investigados pelo TCU: 40
- Gastos irregulares comprovados: 0

## Exemplo de Cálculo

```
Deputado Exemplo:
- Ficha Limpa: 70 (réu em 1ª instância)
- Coerência: 80 (8/10 votações alinhadas)
- Presença: 90 (90% das sessões)
- Patrimônio: 100 (compatível)
- Produtividade: 60 (3 PLs, 1 aprovado)
- Ética: 85 (gastos levemente acima)

Score = (70×0.25) + (80×0.20) + (90×0.15) + (100×0.15) + (60×0.15) + (85×0.10)
Score = 17.5 + 16 + 13.5 + 15 + 9 + 8.5
Score = 79.5 → 🔵 Bom
```
