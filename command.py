import asyncio
from typing import Optional
from dataclasses import dataclass
from openai import OpenAI
from telethon import events


@dataclass
class MessageContext:
    is_reply: bool
    is_own_message: bool
    replied_text: Optional[str]
    relationship_label: str


class Command:
    def __init__(
        self,
        prefix: str,
        system_prompt: str,
        default_message: str,
        model: str,
        openai_client: OpenAI,
        interlocutor_label: str = "собеседник"
    ):
        if not prefix.startswith("!"):
            raise ValueError(f"Command prefix must start with '!', got: {prefix}")
        
        self.prefix = prefix
        self.system_prompt = system_prompt
        self.default_message = default_message
        self.model = model
        self.openai_client = openai_client
        self.interlocutor_label = interlocutor_label
    
    async def get_message_context(self, event: events.NewMessage.Event) -> MessageContext:
        is_reply = event.is_reply
        is_own_message = False
        replied_text = None
        
        if is_reply:
            replied_msg = await event.get_reply_message()
            replied_text = replied_msg.text
            is_own_message = replied_msg.out
        
        return MessageContext(
            is_reply=is_reply,
            is_own_message=is_own_message,
            replied_text=replied_text,
            relationship_label=self.interlocutor_label
        )
    
    def build_prompt(self, user_prompt: str, context: MessageContext) -> str:
        if not context.is_reply:
            return user_prompt
        
        if context.is_own_message:
            context_note = f"[Ранее персонаж уже говорил: '{context.replied_text}']\n\n"
        else:
            context_note = f"[{context.relationship_label.capitalize()} сказал персонажу: '{context.replied_text}']\n\n"
        
        return context_note + user_prompt
    
    async def generate_response(self, user_prompt: str, context: MessageContext) -> str:
        full_prompt = self.build_prompt(user_prompt, context)
        
        completion = await asyncio.to_thread(
            self.openai_client.chat.completions.create,
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": full_prompt},
            ],
        )
        
        return completion.choices[0].message.content
    
    async def execute(self, event: events.NewMessage.Event) -> None:
        user_prompt = event.text[len(self.prefix):].strip()
        
        if not user_prompt:
            return
        
        try:
            await event.edit(self.default_message)
            
            context = await self.get_message_context(event)
            
            response_text = await self.generate_response(user_prompt, context)
            
            await event.edit(response_text)
            
        except Exception as e:
            error_message = f"Произошла ошибка:\n\n`{e}`"
            await event.edit(error_message)
    
    def get_pattern(self) -> str:
        return f'^{self.prefix}.*'
