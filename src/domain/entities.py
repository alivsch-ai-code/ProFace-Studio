from dataclasses import dataclass


@dataclass
class UserProfile:
    user_id: int
    username: str | None
    selected_template: str | None = None
    stage: str = "await_template"
