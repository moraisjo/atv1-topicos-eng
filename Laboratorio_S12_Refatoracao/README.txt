LABORATÓRIO S12 — TRATAMENTO DA DÍVIDA TÉCNICA E REFATORAÇÃO

Requisito:
- Python 3.10 ou superior
- Nenhum pacote externo

Objetivo:
Refatorar uma função de checkout em pequenos passos, preservando o comportamento
observável e registrando evidências antes e depois da intervenção.

Comandos principais:
1. python lab.py run
2. python -m unittest discover -s tests -v
3. python lab.py inspect
4. python lab.py snapshot before.json

Depois de cada pequeno refactoring:
5. python -m unittest discover -s tests -v

Ao final:
6. python lab.py inspect
7. python lab.py snapshot after.json
8. python lab.py compare before.json after.json
9. python lab.py diff

Se precisar voltar ao código original:
10. python lab.py reset

Leia também contexto.md antes de começar.
