import json
from pathlib import Path

from app.main import app
from app.openapi import build_gpt_dynasty_openapi, build_gpt_play_openapi, build_gpt_winter_openapi

DESTINATION = Path(__file__).resolve().parents[1] / "docs" / "openapi.json"
GPT_PLAY_DESTINATION = Path(__file__).resolve().parents[1] / "docs" / "openapi-gpt-play.json"
GPT_DYNASTY_DESTINATION = Path(__file__).resolve().parents[1] / "docs" / "openapi-gpt-dynasty.json"
GPT_WINTER_DESTINATION = Path(__file__).resolve().parents[1] / "docs" / "openapi-gpt-winter.json"


def main() -> None:
    DESTINATION.write_text(
        json.dumps(app.openapi(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"Exported {DESTINATION}")
    GPT_PLAY_DESTINATION.write_text(
        json.dumps(build_gpt_play_openapi(app), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"Exported {GPT_PLAY_DESTINATION}")
    GPT_DYNASTY_DESTINATION.write_text(
        json.dumps(build_gpt_dynasty_openapi(app), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"Exported {GPT_DYNASTY_DESTINATION}")
    GPT_WINTER_DESTINATION.write_text(
        json.dumps(build_gpt_winter_openapi(app), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"Exported {GPT_WINTER_DESTINATION}")


if __name__ == "__main__":
    main()
