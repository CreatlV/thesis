from dataclasses import dataclass

@dataclass
class Message:
    role: str
    content: str


@dataclass
class Choice:
    message: Message
    finish_reason: str
    index: int


@dataclass
class Usage:
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


@dataclass
class APIResponse:
    id: str
    object: str
    created: int
    model: str
    usage: Usage
    choices: list[Choice]
