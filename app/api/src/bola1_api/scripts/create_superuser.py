import argparse
import getpass
import os

from dotenv import load_dotenv

from bola1_api.core.security import hash_password
from bola1_api.db.session import SessionLocal
from bola1_api.models import User
from bola1_api.repositories.users import get_user_by_email


def read_value(value: str | None, env_name: str, prompt: str, *, secret: bool = False) -> str:
    if value:
        return value
    env_value = os.getenv(env_name)
    if env_value:
        return env_value
    return getpass.getpass(prompt) if secret else input(prompt)


def create_superuser(*, email: str, password: str, nickname: str) -> None:
    db = SessionLocal()
    try:
        user = get_user_by_email(db, email)
        if user:
            user.is_active = True
            user.is_superuser = True
            user.nickname = nickname
            user.password_hash = hash_password(password)
            action = "Updated"
        else:
            user = User(
                email=email.lower(),
                password_hash=hash_password(password),
                nickname=nickname,
                is_active=True,
                is_superuser=True,
            )
            db.add(user)
            action = "Created"

        db.commit()
        print(f"{action} superuser {email.lower()}")
    finally:
        db.close()


def main() -> None:
    load_dotenv()
    parser = argparse.ArgumentParser(description="Create or promote the initial bola1 superuser.")
    parser.add_argument("--email")
    parser.add_argument("--password")
    parser.add_argument("--nickname")
    args = parser.parse_args()

    email = read_value(args.email, "BOLA1_SUPERUSER_EMAIL", "Email: ").strip().lower()
    password = read_value(args.password, "BOLA1_SUPERUSER_PASSWORD", "Password: ", secret=True)
    nickname = read_value(args.nickname, "BOLA1_SUPERUSER_NICKNAME", "Nickname: ").strip()

    if not email or not password or not nickname:
        raise SystemExit("email, password and nickname are required")

    create_superuser(email=email, password=password, nickname=nickname)


if __name__ == "__main__":
    main()
