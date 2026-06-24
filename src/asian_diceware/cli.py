"""命令列進入點，串接六個 pipeline 階段。
Command-line entry point chaining the six pipeline stages.

    asian-diceware all --target 7776     # 完整建構 / full build end to end
    asian-diceware all --target 1296     # v0.1 方法論切片（4 顆骰）/ methodology slice (4 dice)
    asian-diceware collect|normalize|filter|prune|assemble|validate

`scripts/run_pipeline.sh` 封裝了 `all`。各階段讀寫 data/interim/，產物落在 output/。
`scripts/run_pipeline.sh` wraps `all`. Stages read/write data/interim/ and
outputs land in output/.
"""

from __future__ import annotations

import argparse
import sys

from . import assemble as _assemble
from . import collect as _collect
from . import filter_quality as _filter
from . import normalize as _normalize
from . import prune as _prune
from . import validate as _validate
from .common import output_dir


def _run_all(target: int, pool_size: int | None) -> int:
    print(f"[1/6] collect (pool_size={pool_size or 'all'})")
    _collect.collect(pool_size=pool_size)
    print("[2/6] normalize")
    _normalize.normalize()
    print("[3/6] filter_quality")
    _filter.filter_quality()
    print("[4/6] prune (prefix-free, pins protected)")
    _prune.prune()
    print(f"[5/6] assemble -> exactly {target} words")
    txt, dice = _assemble.assemble(target=target)
    print(f"        wrote {txt}")
    if dice:
        print(f"        wrote {dice}")
    print("[6/6] validate")
    report = _validate.validate(txt, target=target)
    print()
    print(_validate.format_report(report))
    return 0 if report["passed"] else 1


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="asian-diceware", description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)

    p_all = sub.add_parser("all", help="run the full pipeline end to end / 完整跑一遍")
    p_all.add_argument("--target", type=int, default=7776)
    p_all.add_argument("--pool-size", type=int, default=None)

    sub.add_parser("collect", help="stage 1")
    sub.add_parser("normalize", help="stage 2")
    sub.add_parser("filter", help="stage 3")
    sub.add_parser("prune", help="stage 4")
    p_asm = sub.add_parser("assemble", help="stage 5")
    p_asm.add_argument("--target", type=int, default=7776)
    p_val = sub.add_parser("validate", help="stage 6")
    p_val.add_argument("--target", type=int, default=7776)

    args = p.parse_args(argv)

    if args.cmd == "all":
        return _run_all(args.target, args.pool_size)
    if args.cmd == "collect":
        print(_collect.collect())
        return 0
    if args.cmd == "normalize":
        print(_normalize.normalize())
        return 0
    if args.cmd == "filter":
        print(_filter.filter_quality())
        return 0
    if args.cmd == "prune":
        print(_prune.prune())
        return 0
    if args.cmd == "assemble":
        txt, dice = _assemble.assemble(target=args.target)
        print(txt)
        if dice:
            print(dice)
        return 0
    if args.cmd == "validate":
        txt = output_dir() / f"asian_diceware_{args.target}.txt"
        report = _validate.validate(txt, target=args.target)
        print(_validate.format_report(report))
        return 0 if report["passed"] else 1
    return 2


if __name__ == "__main__":
    sys.exit(main())
