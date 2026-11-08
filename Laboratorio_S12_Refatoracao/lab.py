from __future__ import annotations

import argparse
import ast
import difflib
import importlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parent
CHECKOUT = ROOT / "src" / "checkout.py"
BASELINE = ROOT / "baseline" / "checkout_original.py"


def load_checkout():
    import src.checkout as checkout_module
    importlib.reload(checkout_module)
    return checkout_module.checkout


def scenarios():
    from src.models import Customer, Item, Order

    def make(name, plan, items):
        return Order(
            customer=Customer(name=name, plan=plan),
            items=tuple(Item(n, p, q) for n, p, q in items),
        )

    return {
        "regular-low": make("Ana", "REGULAR", [("Book", 100.0, 1)]),
        "silver-low": make("Bruno", "SILVER", [("Headset", 100.0, 1)]),
        "gold-low": make("Carla", "GOLD", [("Keyboard", 100.0, 1)]),
        "gold-free-shipping": make("Diego", "GOLD", [("Monitor", 200.0, 1)]),
        "shipping-boundary": make("Eva", "REGULAR", [("Chair", 150.0, 1)]),
        "multiple-items": make(
            "Fábio",
            "SILVER",
            [("Mouse", 50.0, 2), ("Cable", 25.0, 2)],
        ),
    }


def run_scenarios():
    checkout = load_checkout()
    output = {}
    for name, order in scenarios().items():
        output[name] = checkout(order)
    return output


def cmd_run(_args):
    data = run_scenarios()
    for name, result in data.items():
        print(f"\n[{name}]")
        for key, value in result.items():
            print(f"  {key}: {value}")


def cmd_snapshot(args):
    data = run_scenarios()
    path = Path(args.file)
    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True),
        encoding="utf-8",
    )
    print(f"Snapshot gravado em: {path}")


def cmd_compare(args):
    before = json.loads(Path(args.before).read_text(encoding="utf-8"))
    after = json.loads(Path(args.after).read_text(encoding="utf-8"))

    if before == after:
        print("OK: snapshots idênticos.")
        print("Os cenários observados preservaram exatamente as mesmas saídas.")
        return

    print("ATENÇÃO: há diferenças entre os snapshots.")
    keys = sorted(set(before) | set(after))
    for key in keys:
        if before.get(key) != after.get(key):
            print(f"\n[{key}]")
            print("  ANTES:", before.get(key))
            print("  DEPOIS:", after.get(key))


def function_metrics(source: str, function_name: str):
    tree = ast.parse(source)
    lines = source.splitlines()
    target = None
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == function_name:
            target = node
            break
    if target is None:
        raise SystemExit(f"Função {function_name!r} não encontrada.")

    end = getattr(target, "end_lineno", target.lineno)
    src_lines = lines[target.lineno - 1:end]
    nonblank = sum(1 for line in src_lines if line.strip())

    decisions = 0
    loops = 0
    returns = 0
    calls = []
    for node in ast.walk(target):
        if isinstance(node, ast.If):
            decisions += 1
        elif isinstance(node, (ast.For, ast.While)):
            loops += 1
        elif isinstance(node, ast.Return):
            returns += 1
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            calls.append(node.func.id)

    helpers = sorted(
        {
            n.name
            for n in tree.body
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
            and n.name != function_name
            and n.name in calls
        }
    )

    return {
        "source_lines": end - target.lineno + 1,
        "nonblank_lines": nonblank,
        "ifs": decisions,
        "loops": loops,
        "returns": returns,
        "local_helpers_called": helpers,
    }


def cmd_inspect(_args):
    source = CHECKOUT.read_text(encoding="utf-8")
    m = function_metrics(source, "checkout")
    print("Estrutura observada em src/checkout.py")
    print("-------------------------------------")
    print(f"Linhas da função checkout(): {m['source_lines']}")
    print(f"Linhas não vazias:           {m['nonblank_lines']}")
    print(f"Comandos if:                 {m['ifs']}")
    print(f"Laços:                       {m['loops']}")
    print(f"Returns:                     {m['returns']}")
    helpers = ", ".join(m["local_helpers_called"]) if m["local_helpers_called"] else "(nenhum)"
    print(f"Helpers locais chamados:     {helpers}")
    print()
    print("Observação: estes números descrevem estrutura; não são, sozinhos,")
    print("uma medida de qualidade nem prova de que a dívida foi tratada.")


def cmd_diff(_args):
    original = BASELINE.read_text(encoding="utf-8").splitlines(keepends=True)
    current = CHECKOUT.read_text(encoding="utf-8").splitlines(keepends=True)
    diff = difflib.unified_diff(
        original,
        current,
        fromfile="baseline/checkout_original.py",
        tofile="src/checkout.py",
    )
    text = "".join(diff)
    print(text if text else "Nenhuma diferença em relação ao baseline.")


def cmd_reset(_args):
    shutil.copyfile(BASELINE, CHECKOUT)
    cache = ROOT / "src" / "__pycache__"
    if cache.exists():
        shutil.rmtree(cache)
    print("src/checkout.py restaurado para a versão original.")


def build_parser():
    parser = argparse.ArgumentParser(
        description="Laboratório S12 — refactoring e preservação de comportamento."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("run", help="Executa os cenários de checkout.")
    p.set_defaults(func=cmd_run)

    p = sub.add_parser("snapshot", help="Grava as saídas observadas em JSON.")
    p.add_argument("file")
    p.set_defaults(func=cmd_snapshot)

    p = sub.add_parser("compare", help="Compara dois snapshots JSON.")
    p.add_argument("before")
    p.add_argument("after")
    p.set_defaults(func=cmd_compare)

    p = sub.add_parser("inspect", help="Mostra medidas estruturais simples de checkout().")
    p.set_defaults(func=cmd_inspect)

    p = sub.add_parser("diff", help="Mostra o diff entre o baseline e o código atual.")
    p.set_defaults(func=cmd_diff)

    p = sub.add_parser("reset", help="Restaura src/checkout.py para o baseline.")
    p.set_defaults(func=cmd_reset)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
