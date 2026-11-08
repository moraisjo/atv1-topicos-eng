# A11 — Refatore sem mudar o comportamento

## 1. Estratégia para os três TDIs

Para o TDI-01, escolhi **reduzir** a dívida. A função `checkout()` recebia mudanças frequentes, uma nova regra para clientes PLATINUM estava prevista e a equipe precisava reler toda a rotina a cada alteração. Extraí responsabilidades para funções auxiliares, deixando a função pública menor e mais fácil de acompanhar. Isso reduz o custo de compreender e modificar o fluxo, mas não elimina toda a dívida: as regras continuam neste módulo e uma futura regra ainda exigirá uma mudança.

Para o TDI-02, escolhi **aceitar temporariamente** a dívida e postergar qualquer refatoração. Embora `legacy_export.py` seja difícil de ler, ele deve ser aposentado em aproximadamente oito semanas, não tem incidentes recentes e possui baixa cobertura. Uma intervenção agora teria pouco tempo para recuperar seu custo e evidência limitada de preservação. Para o TDI-03, escolhi **mitigar**: a integração fiscal é crítica e não pode ser substituída antes da liberação do SDK. O monitoramento e os testes de contrato reduzem o risco enquanto a dependência externa não está disponível.

## 2. Comportamento usado como baseline

Antes de alterar o código, executei os cenários do laboratório e os sete testes. Para um pedido de R$ 100,00, clientes REGULAR, SILVER e GOLD recebem, respectivamente, desconto de R$ 0,00, R$ 5,00 e R$ 10,00; os totais são R$ 132,16, R$ 126,26 e R$ 120,36. O cenário GOLD de R$ 200,00 resulta em frete grátis e total de R$ 212,40. O limite é inclusivo: uma compra REGULAR de R$ 150,00 já recebe frete grátis. Também considerei a acumulação de múltiplos itens, os valores de imposto e o texto das mensagens como comportamento observado. Salvei essas saídas em `before.json`.

## 3. Refatorações realizadas

Fiz três extrações pequenas em sequência, rodando todos os testes depois de cada uma. Primeiro, movi a acumulação e o arredondamento do subtotal para `_calculate_subtotal(order)`. Depois, extraí desconto, cálculo do frete, base tributável, imposto e total para `_calculate_checkout_amounts(subtotal, plan)`. Por fim, movi a escolha e a formatação da mensagem para `_format_checkout_message(customer_name, shipping, total)`. A interface pública continuou sendo `checkout(order)`, e o dicionário retornado manteve as mesmas chaves. Preservei a ordem das operações e os arredondamentos.

## 4. Evidências e limites

Os sete testes passaram antes da intervenção e após cada extração. Ao concluir, `python lab.py compare before.json after.json` informou que os snapshots são idênticos, portanto os seis cenários registrados produziram exatamente as mesmas saídas. O diff mostra somente a redistribuição do código para três helpers e as chamadas feitas por `checkout()`. Essas evidências cobrem os exemplos fornecidos pelos testes e pelo laboratório; não provam que todos os pedidos possíveis, valores extremos ou futuras regras terão o mesmo resultado. Por isso, a conclusão é de preservação nos cenários observados, não de prova completa para qualquer entrada.

## 5. Mudança observada em `inspect`

Antes, `checkout()` tinha 37 linhas, 31 não vazias, quatro comandos `if`, um laço, um `return` e nenhum helper local chamado. Depois, passou a ter 15 linhas, 14 não vazias, nenhum `if` ou laço, um `return` e chamadas aos três helpers extraídos. A função principal agora deixa mais visível a sequência do checkout. Essas métricas descrevem a estrutura, não a qualidade: reduzir linhas ou condicionais, isoladamente, não demonstra que os nomes, limites ou responsabilidades escolhidos são melhores. Essa avaliação depende da intenção das extrações e da manutenção do comportamento.

## 6. Situação do TDI-01

Considero o TDI-01 **reduzido**, não eliminado. A lógica de subtotal, valores e mensagem deixou de estar concentrada em um único corpo e foi separada em partes nomeadas. Isso facilita localizar e compreender uma mudança, mas não remove a necessidade de decidir como uma futura regra PLATINUM interage com descontos, frete e impostos. O experimento reorganizou responsabilidades com segurança observável; ele não redesenhou o domínio nem criou cobertura para cenários ainda inexistentes.

## 7. Critério de parada para `legacy_export.py`

Continuar em `legacy_export.py` ampliaria o escopo sem ajudar diretamente a preparar `checkout()` para mudanças próximas. Como o exportador será aposentado em breve, não há incidentes recentes e a cobertura é baixa, seria difícil justificar o investimento e demonstrar preservação do comportamento. Código imperfeito, por si só, não exige intervenção imediata. Parar após as extrações planejadas mantém a mudança proporcional ao risco e ao benefício esperado.

## Evidências finais

Saída de `python lab.py inspect`:

```text
Estrutura observada em src/checkout.py
-------------------------------------
Linhas da função checkout(): 15
Linhas não vazias:           14
Comandos if:                 0
Laços:                       0
Returns:                     1
Helpers locais chamados:     _calculate_checkout_amounts, _calculate_subtotal, _format_checkout_message

Observação: estes números descrevem estrutura; não são, sozinhos,
uma medida de qualidade nem prova de que a dívida foi tratada.
```

Saída de `python lab.py compare before.json after.json`:

```text
OK: snapshots idênticos.
Os cenários observados preservaram exatamente as mesmas saídas.
```

Saída de `python lab.py diff`:

```diff
--- baseline/checkout_original.py
+++ src/checkout.py
@@ -1,12 +1,14 @@
-def checkout(order):
+def _calculate_subtotal(order):
     subtotal = 0.0
     for item in order.items:
         subtotal += item.price * item.qty
-    subtotal = round(subtotal, 2)
+    return round(subtotal, 2)
 
-    if order.customer.plan == "GOLD":
+
+def _calculate_checkout_amounts(subtotal, plan):
+    if plan == "GOLD":
         discount = round(subtotal * 0.10, 2)
-    elif order.customer.plan == "SILVER":
+    elif plan == "SILVER":
         discount = round(subtotal * 0.05, 2)
     else:
         discount = 0.0
@@ -21,11 +23,21 @@
     taxable = round(after_discount + shipping, 2)
     tax = round(taxable * 0.18, 2)
     total = round(taxable + tax, 2)
+    return discount, shipping, tax, total
+
+
+def _format_checkout_message(customer_name, shipping, total):
     if shipping == 0.0:
-        message = f"{order.customer.name}: frete grátis | total R$ {total:.2f}"
-    else:
-        message = f"{order.customer.name}: frete R$ {shipping:.2f} | total R$ {total:.2f}"
+        return f"{customer_name}: frete grátis | total R$ {total:.2f}"
+    return f"{customer_name}: frete R$ {shipping:.2f} | total R$ {total:.2f}"
+
+
+def checkout(order):
+    subtotal = _calculate_subtotal(order)
+    discount, shipping, tax, total = _calculate_checkout_amounts(
+        subtotal, order.customer.plan
+    )
+    message = _format_checkout_message(order.customer.name, shipping, total)
 
     return {
         "subtotal": subtotal,
```
