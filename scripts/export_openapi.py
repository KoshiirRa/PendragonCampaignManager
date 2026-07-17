import json
from pathlib import Path

from app.main import app

DESTINATION = Path(__file__).resolve().parents[1] / "docs" / "openapi.json"


def main() -> None:
    DESTINATION.write_text(
        json.dumps(app.openapi(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"Exported {DESTINATION}")


if __name__ == "__main__":
    main()
