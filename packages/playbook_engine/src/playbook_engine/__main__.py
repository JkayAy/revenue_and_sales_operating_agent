from pathlib import Path

from playbook_engine import PlaybookEngine, load_playbook_config


def main() -> None:
    import sys

    path = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    cfg = load_playbook_config(path)
    engine = PlaybookEngine(cfg)
    sample = engine.evaluate_icp(employee_count=120, country="US", industry="software")
    print(f"ICP sample: {sample.code} — {sample.message}")


if __name__ == "__main__":
    main()
