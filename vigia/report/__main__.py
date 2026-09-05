"""Entry point: ``python3 -m vigia.report <bundle.json> [options]``.

Renders audience reports for one sealed bundle and writes them as sibling
files (or prints a single variant to stdout). Exit codes:

  0  reports written (or printed)
  1  bundle unreadable, or a target refused by the evidence boundary
  2  usage error (argparse), including ``--stdout`` with more than one variant
"""

from __future__ import annotations

import argparse
import os
import sys

from vigia.report import AUDIENCES, LANGS, REPORT_VERSION


def _expand(value: str, universe: tuple[str, ...]) -> tuple[str, ...]:
    return universe if value == "all" else (value,)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="python3 -m vigia.report",
        description=(
            "Audience-tailored presentations of a sealed VIGÍA bundle (viewer only: "
            "nothing is computed, nothing is written inside the bundle)."
        ),
        epilog=(
            "Outputs are <stem>_report_<audience>_<lang>.md next to the bundle, or under "
            "--output-dir. Targets inside VIGIA_EVIDENCE_DIR are refused."
        ),
    )
    p.add_argument("bundle", help="path to a sealed bundle JSON file")
    p.add_argument("--audience", choices=AUDIENCES + ("all",), default="all",
                   help="junior SOC analyst, expert examiner, or both (default: all)")
    p.add_argument("--lang", choices=LANGS + ("all",), default="all",
                   help="report language (default: all)")
    p.add_argument("--output-dir", default=None,
                   help="write reports here instead of next to the bundle")
    p.add_argument("--stdout", action="store_true",
                   help="print one variant instead of writing; requires a single "
                        "--audience and a single --lang")
    p.add_argument("--version", action="version", version=f"vigia.report {REPORT_VERSION}")
    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    audiences = _expand(args.audience, AUDIENCES)
    langs = _expand(args.lang, LANGS)

    if args.stdout and (len(audiences) != 1 or len(langs) != 1):
        parser.error("--stdout needs exactly one --audience and one --lang")

    # Imported here so `--help` and argument errors never touch the bundle
    # machinery, and so a failing import is reported as a real error.
    from vigia.report.adapter import load_view
    from vigia.report.renderers import render
    from vigia.report.writer import write_all

    try:
        if args.stdout:
            with open(args.bundle, "rb") as fh:
                raw = fh.read()
            view = load_view(raw, source_name=os.path.basename(args.bundle))
            sys.stdout.write(render(view, audiences[0], langs[0]))
            return 0
        written = write_all(args.bundle, audiences, langs, args.output_dir)
    except (OSError, ValueError) as exc:
        print(f"[vigia.report] cannot read bundle: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # noqa: BLE001 — SecurityError and any writer failure
        if type(exc).__name__ == "SecurityError":
            print(f"[vigia.report] refused: {exc}", file=sys.stderr)
            return 1
        raise
    for path in written:
        print(path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
