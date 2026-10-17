#!/usr/bin/env python3
"""tool-census forwarder SHAPE check (tools/tool-census.mjs rule 9). Stdlib only; parses, never executes.

stdin: JSON [{"path": <file>, "tool": <pinned tool name>}]; stdout: JSON [null | "<why it is not a forwarder>"].
A file has the forwarder shape only if its Python AST passes every rule below (any failure = it stays a version):
  - statements: expression, assignment, return, if, for, try, raise, import, def, pass/break/continue only;
    no class, lambda, while, with, global/nonlocal, del, async, yield, walrus or comprehension; no decorators
    or default arguments; no dunder name except __name__/__file__ and no dunder attribute at all;
  - imports: os, sys, subprocess; from pathlib import Path; from __future__ import annotations (no aliases);
  - calls: the builtins in NAMES, functions the file defines, the exact dotted names in DOTTED, or a method in
    METHODS on a non-module object -- so no open/exec/eval/getattr/os.system/Popen/write/unlink;
  - no assignment to an attribute or into a container that is not a local name; f-string fields are bare names;
  - every subprocess.run takes a list literal and only the keywords in RUN_KW, and is either
    [sys.executable, <flags in PY_FLAGS>, <RUNNER>, "run", "<tool>", "--", ...] where RUNNER is a name bound
    ONLY by assignments holding the literals "factory-pins" and "pin-runner.py", or a constant
    ["git", <options>, "rev-parse", ...] read-only query;
  - at least one such runner call exists, and every list naming "run", "<x>" names this tool.
What the shape cannot prove (the file's byte cap and pins check in tool-census.mjs bound it): that every path
reaches the runner. A forwarder may still return early, but it cannot read or write a file, run anything but
the pinned tool and git rev-parse, or import anything beyond os/sys/subprocess/pathlib.
"""
import ast
import json
import sys

MODS = {"os": None, "sys": None, "subprocess": None, "pathlib": {"Path"}, "__future__": {"annotations"}}
NAMES = {"print", "str", "len", "dict", "list", "tuple", "enumerate", "range", "isinstance", "SystemExit", "Path"}
DOTTED = {"subprocess.run", "sys.exit", "os.path.join", "os.path.dirname", "os.path.abspath", "os.path.isfile",
          "os.path.exists", "os.environ.get", "sys.stdout.flush", "sys.stderr.flush"}
METHODS = {"join", "resolve", "is_file", "exists", "append", "startswith", "endswith", "split", "strip", "rstrip",
           "lstrip", "splitlines", "reconfigure", "get", "flush"}
RUN_KW = {"cwd", "env", "stdout", "stderr", "stdin", "encoding", "errors", "capture_output", "text", "timeout", "check"}
STMTS = (ast.Expr, ast.Assign, ast.AnnAssign, ast.AugAssign, ast.Return, ast.If, ast.For, ast.Try, ast.Raise,
         ast.Import, ast.ImportFrom, ast.FunctionDef, ast.Pass, ast.Break, ast.Continue)
BANNED = (ast.ClassDef, ast.AsyncFunctionDef, ast.Lambda, ast.Global, ast.Nonlocal, ast.Delete, ast.With,
          ast.AsyncWith, ast.While, ast.Yield, ast.YieldFrom, ast.Await, ast.NamedExpr, ast.ListComp, ast.SetComp,
          ast.DictComp, ast.GeneratorExp, ast.AsyncFor)
DUNDER_OK = {"__name__", "__file__"}
PY_FLAGS = {"-I", "-E", "-s", "-S", "-B", "-u"}


def dotted(n):
    parts = []
    while isinstance(n, ast.Attribute):
        parts.append(n.attr)
        n = n.value
    if isinstance(n, ast.Name):
        parts.append(n.id)
        return ".".join(reversed(parts))
    return None


def const_str(n):
    return n.value if isinstance(n, ast.Constant) and isinstance(n.value, str) else None


def check(src, tool):
    try:
        tree = ast.parse(src)
    except SyntaxError as e:
        return f"not parseable Python ({e.msg})"
    funcs = {n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}
    # The runner path: a name every binding of which is an assignment whose value holds the literals
    # "factory-pins" and "pin-runner.py" (the vendored runner beside the pins file), never rebound otherwise.
    good, bad = set(), set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Assign):
            for t in n.targets:
                pairs = list(zip(t.elts, n.value.elts)) if isinstance(t, ast.Tuple) and isinstance(n.value, ast.Tuple)                     and len(t.elts) == len(n.value.elts) else [(t, n.value)]
                for tg, val in pairs:
                    lits = {const_str(c) for c in ast.walk(val)}
                    for x in ast.walk(tg):
                        if isinstance(x, ast.Name):
                            (good if isinstance(tg, ast.Name) and {"factory-pins", "pin-runner.py"} <= lits else bad).add(x.id)
        elif isinstance(n, (ast.AugAssign, ast.AnnAssign, ast.For)):
            bad.update(x.id for x in ast.walk(n.target) if isinstance(x, ast.Name))
        elif isinstance(n, ast.arg):
            bad.add(n.arg)
        elif isinstance(n, ast.ExceptHandler) and n.name:
            bad.add(n.name)
    runner_names = good - bad
    if not runner_names:
        return "no name is bound only to the factory-pins/pin-runner.py path"
    for n in ast.walk(tree):
        if isinstance(n, ast.stmt) and not isinstance(n, STMTS):
            return f"statement {type(n).__name__} is not allowed in a forwarder (line {n.lineno})"
        if isinstance(n, BANNED):
            return f"{type(n).__name__} is not allowed in a forwarder (line {n.lineno})"
        if isinstance(n, ast.FunctionDef) and (n.decorator_list or n.args.defaults or n.args.kw_defaults):
            return f"function {n.name}: decorators and default arguments are not allowed"
        if isinstance(n, ast.Name) and n.id.startswith("__") and n.id not in DUNDER_OK:
            return f"dunder name {n.id} (line {n.lineno})"
        if isinstance(n, ast.Attribute) and n.attr.startswith("__"):
            return f"dunder attribute {n.attr} (line {n.lineno})"
        if isinstance(n, ast.Import):
            for a in n.names:
                if a.name not in MODS or MODS[a.name] is not None or a.asname:
                    return f"import {a.name} is not allowed"
        if isinstance(n, ast.ImportFrom):
            allowed = MODS.get(n.module or "")
            if n.level or allowed is None or any(a.name not in allowed or a.asname for a in n.names):
                return f"from {n.module} import ... is not allowed"
        if isinstance(n, (ast.Assign, ast.AugAssign, ast.AnnAssign)):
            for t in (n.targets if isinstance(n, ast.Assign) else [n.target]):
                for x in ast.walk(t):
                    if isinstance(x, ast.Attribute):
                        return f"assignment to an attribute (line {n.lineno})"
                    if isinstance(x, ast.Subscript) and not isinstance(x.value, ast.Name):
                        return f"assignment into a non-local container (line {n.lineno})"
        if isinstance(n, ast.JoinedStr):
            for v in n.values:
                if isinstance(v, ast.FormattedValue) and not (dotted(v.value) and (v.format_spec is None)):
                    return f"f-string field is not a bare name (line {n.lineno})"
        if isinstance(n, ast.Call):
            f, d = n.func, dotted(n.func)
            if isinstance(f, ast.Name):
                if f.id not in NAMES and f.id not in funcs:
                    return f"call to {f.id}() is not allowed (line {n.lineno})"
            elif isinstance(f, ast.Attribute):
                root = d.split(".")[0] if d else None
                if root in MODS or root in ("os", "sys", "subprocess", "pathlib"):
                    if d not in DOTTED:
                        return f"call to {d}() is not allowed (line {n.lineno})"
                elif f.attr not in METHODS:
                    return f"call to method .{f.attr}() is not allowed (line {n.lineno})"
            else:
                return f"call through a computed callee (line {n.lineno})"
    # Every list that names a pin-runner subcommand names THIS tool.
    runner_calls = 0
    for n in ast.walk(tree):
        if isinstance(n, ast.List):
            vals = [const_str(e) for e in n.elts]
            for i, v in enumerate(vals[:-1]):
                if v == "run" and vals[i + 1] is not None and vals[i + 1] != tool:
                    return f"runs pinned tool {vals[i + 1]!r}, not {tool!r}"
        if isinstance(n, ast.Call) and dotted(n.func) == "subprocess.run":
            for k in n.keywords:
                if k.arg not in RUN_KW:
                    return f"subprocess.run keyword {k.arg!r} is not allowed (line {n.lineno})"
            if len(n.args) != 1 or not isinstance(n.args[0], ast.List):
                return f"subprocess.run argv is not a list literal (line {n.lineno})"
            el = n.args[0].elts
            vals = [const_str(e) for e in el]
            if vals and vals[0] == "git":
                words = [v for v in vals[1:] if v is None or not v.startswith("-")]
                if None in vals or not words or words[0] != "rev-parse":
                    return f"the only other command allowed is a constant 'git rev-parse' (line {n.lineno})"
                continue
            if dotted(el[0]) != "sys.executable" if el else True:
                return f"subprocess.run is neither the pin runner nor git rev-parse (line {n.lineno})"
            try:
                i = vals.index("run")
            except ValueError:
                return f"subprocess.run of the interpreter without 'run <tool>' (line {n.lineno})"
            if i + 1 >= len(vals) or vals[i + 1] != tool:
                return f"pin-runner call names {vals[i + 1] if i + 1 < len(vals) else None!r}, not the constant {tool!r} (line {n.lineno})"
            head = el[1:i]
            flags = [const_str(e) for e in head if const_str(e) is not None]
            if any(f not in PY_FLAGS for f in flags):
                return f"interpreter flag(s) {[f for f in flags if f not in PY_FLAGS]} not allowed (line {n.lineno})"
            paths = [e for e in head if const_str(e) is None]
            def is_runner(e):
                if isinstance(e, ast.Call) and isinstance(e.func, ast.Name) and e.func.id == "str" and len(e.args) == 1:
                    e = e.args[0]
                return isinstance(e, ast.Name) and e.id in runner_names
            if len(paths) != 1 or not is_runner(paths[0]):
                return f"the interpreter's script is not the pin-runner.py path (line {n.lineno})"
            if i + 2 < len(vals) and vals[i + 2] != "--":
                return f"'run {tool}' is not followed by '--' (line {n.lineno})"
            runner_calls += 1
    if runner_calls == 0:
        return f"no subprocess.run of 'pin-runner.py run {tool}'"
    return None


out = []
for item in json.load(sys.stdin):
    try:
        src = open(item["path"], encoding="utf-8").read()
        out.append(check(src, item["tool"]))
    except Exception as e:  # noqa: BLE001 - any failure is "not a forwarder"
        out.append(f"checker error: {type(e).__name__}: {e}")
print(json.dumps(out))
