import asyncio
from enum import Enum
from typing import List, Optional

from g4f.Provider import OpenaiChat, Gemini
from g4f.client import AsyncClient
from pydantic import BaseModel, Field

from core.loggers.make_loggers import except_log
from core.utils import texts


class GPTRole(str, Enum):
    """
    Enum для определения возможных ролей отправителей сообщений в чат.

    - SYSTEM: Системное сообщение, используется для установки контекста или инструкций для модели.
    - USER: Сообщение от пользователя, содержит запрос или вводные данные.
    - ASSISTANT: Ответ от ассистента (модели), содержит сгенерированный текст.
    """
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class GPTMessage(BaseModel):
    """
    Модель сообщения для взаимодействия с OpenAI Chat API.

    Attributes:
        role (GPTRole): Роль отправителя сообщения. Может быть 'system', 'user' или 'assistant'.
        content (str): Текстовое содержимое сообщения.
        name (Optional[str]): Имя пользователя (опционально).
    """
    role: GPTRole = Field(..., description="Роль отправителя сообщения: 'system', 'user' или 'assistant'")
    content: str = Field(..., description="Текстовое содержимое сообщения")
    # name: Optional[str] = Field(None, description="Имя пользователя (опционально)")


class ChatGPTIntegration:
    """
    Класс для интеграции с OpenAI Chat API.

    Attributes:
        model (str): Модель OpenAI, например, 'gpt-4'.
        temperature (float): Параметр для управления креативностью ответов.
        max_tokens (int): Максимальное количество токенов в ответе.
        messages (List[GPTMessage]): История сообщений в разговоре.
    """

    def __init__(
            self,
            model: str = "gpt-4o-mini",
            max_tokens: int = 10000,
    ):
        """
        Инициализация ChatGPTIntegration.

        Args:
            model (str): Модель OpenAI.
            max_tokens (int): Максимальное количество токенов.
        """
        # openai.api_key = openai_cfg.TOKEN
        self.model = model
        self.max_tokens = max_tokens
        self.messages: list[GPTMessage] = []
        self.client =  AsyncClient()

    async def send_message(self, message: GPTMessage) -> Optional[str]:
        await self.add_message(message)
        try:
            print(self.messages)
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[m.dict() for m in self.messages],
                web_search=True
            )
            print(response)
            assistant_content = response.choices[0].message.content
            assistant_message = GPTMessage(
                role=GPTRole.ASSISTANT,
                content=assistant_content
            )
            await self.add_message(assistant_message)
            return assistant_content
        except Exception as e:
            except_log.exception(e)

    async def add_message(self, message: GPTMessage) -> None:
        """
        Добавляет сообщение в историю сообщений.

        Args:
            message (GPTMessage): Сообщение для добавления.
        """
        self.messages.append(message)

    async def clear_conversation(self) -> List[GPTMessage]:
        """
        Очищает историю сообщений.

        Returns:
            List[GPTMessage]: Пустой список сообщений.
        """
        self.messages = []
        return self.messages

    async def get_messages(self) -> List[GPTMessage]:
        """
        Возвращает историю сообщений.

        Returns:
            List[GPTMessage]: История сообщений.
        """
        return [msg.model_dump_json() for msg in self.messages]

    async def set_messages(self, messages: List[GPTMessage]) -> None:
        """
        Возвращает историю сообщений.

        Returns:
            List[GPTMessage]: История сообщений.
        """
        if messages is None:
            self.messages = []
        elif isinstance(messages[0], GPTMessage):
            self.messages = messages
        elif isinstance(messages[0], dict):
            self.messages = [GPTMessage(**msg) for msg in messages]
        elif isinstance(messages[0], str):
            self.messages = [GPTMessage.model_validate_json(msg) for msg in messages]


async def main():
    chatgpt = ChatGPTIntegration(model='gpt-4o-mini')
    await chatgpt.set_messages([GPTMessage(role=GPTRole.SYSTEM, content=texts.gpt_start_message)])
    await chatgpt.send_message(GPTMessage(role=GPTRole.USER, content='Привет'))
    answer = await chatgpt.send_message(GPTMessage(role=GPTRole.USER, content='Что такое Бады?'))
    print(answer)


if __name__ == '__main__':
    import asyncio

    asyncio.run(main())
