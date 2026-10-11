import argparse
from pathlib import Path
import traceback


def main():
    parser = argparse.ArgumentParser(description="Darkness Lies Ahead")
    parser.add_argument("--smoke-test", action="store_true")
    parser.add_argument("--smoke-report", type=Path)
    args = parser.parse_args()
    if args.smoke_test:
        from game.checks import smoke

        try:
            result = smoke()
        except Exception:
            if args.smoke_report:
                args.smoke_report.write_text(traceback.format_exc(), encoding="utf-8")
            return 1
        if args.smoke_report:
            args.smoke_report.write_text(result, encoding="utf-8")
        return 0
    from game.ui import run

    run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
