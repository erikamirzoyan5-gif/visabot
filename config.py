import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    bot_token: str
    manager_chat_id: str | None
    admin_ids: set[int]


def parse_admin_ids(value: str | None) -> set[int]:
    if not value:
        return set()
    result: set[int] = set()
    for item in value.split(","):
        item = item.strip()
        if item.isdigit():
            result.add(int(item))
    return result


def load_settings() -> Settings:
    token = os.getenv("BOT_TOKEN", "").strip()
    if not token or token == "PASTE_YOUR_BOT_TOKEN_HERE":
        raise RuntimeError(
            "BOT_TOKEN is missing. Create .env from .env.example and paste your token from @BotFather."
        )

    manager_chat_id = os.getenv("MANAGER_CHAT_ID", "").strip() or None
    admin_ids = parse_admin_ids(os.getenv("ADMIN_IDS"))

    return Settings(
        bot_token=token,
        manager_chat_id=manager_chat_id,
        admin_ids=admin_ids,
    )


settings = load_settings()
