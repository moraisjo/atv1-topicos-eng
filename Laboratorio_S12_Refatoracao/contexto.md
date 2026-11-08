# Contexto do laboratório

Você integra uma equipe responsável por um pequeno sistema de vendas.

A equipe registrou três itens de Dívida Técnica.

## TDI-01 — checkout.py
- A função `checkout()` concentra subtotal, desconto, frete, imposto e mensagem.
- O arquivo recebeu 18 alterações nos últimos três meses.
- Uma nova regra para clientes PLATINUM está prevista para o próximo sprint.
- Existem testes de regressão para os cenários atuais.
- A equipe relata que mudanças nessa função exigem releitura frequente de toda a rotina.

## TDI-02 — legacy_export.py
- O código é difícil de ler e possui responsabilidades misturadas.
- Não recebe mudança funcional há 14 meses.
- O exportador será desativado em aproximadamente oito semanas.
- Não há incidentes recentes associados a ele.
- A cobertura de testes é baixa.

## TDI-03 — integração fiscal externa
- A integração usa uma versão antiga de uma API de um fornecedor.
- A migração depende de uma versão do SDK que o fornecedor ainda não liberou.
- O componente é crítico para faturamento.
- A equipe adicionou monitoramento e testes de contrato para detectar mudanças do fornecedor.
- A substituição completa não pode ser executada agora.

Antes de alterar qualquer código, escolha a resposta que considera mais adequada para
cada TDI: eliminar, reduzir, mitigar, aceitar ou postergar. Uma mesma situação pode
combinar mais de uma ação; indique a principal e justifique.
