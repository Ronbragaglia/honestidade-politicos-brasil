# Politica de Seguranca

## Reportar uma vulnerabilidade

**Nao** abra issue publica para vulnerabilidades.

Use o canal privado do GitHub:

* https://github.com/Ronbragaglia/honestidade-politicos-brasil/security/advisories/new

Inclua, se possivel:

* Descricao clara
* Passos para reproduzir
* Versao afetada
* Impacto estimado

Responderemos em ate **72 horas uteis**.

## Modelo de ameaca

Este projeto coleta dados publicos da Camara, Senado, TSE e STF. Ele:

* ✅ Nao armazena dados pessoais (apenas dados publicos de pessoas publicas)
* ✅ Nao requer autenticacao de usuario
* ✅ Nao executa codigo dinamico em runtime
* ✅ Dependencia unica de runtime: `requests`
* ✅ Workflows com `permissions` minimas e `harden-runner` ativo
* ✅ Actions externas pinadas por SHA (nao tag mutavel)
* ✅ CodeQL `security-and-quality` rodando em todo PR e semanalmente

## Sobre integridade dos dados

* Toda coleta e timestamped (campo `data_coleta`)
* Fonte da API original e citada nas fichas markdown
* Score e calculo determinístico baseado em criterios documentados em `metodologia/`

Obrigado por ajudar a manter o projeto seguro.
