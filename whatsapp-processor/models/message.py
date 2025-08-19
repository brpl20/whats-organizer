"""
Message data models
"""
from dataclasses import dataclass, field
from typing import List, Literal, TypedDict, Union

StrOrFalse = Union[Literal[False], str]

class MessageData(TypedDict):
    """Structure for a WhatsApp message"""
    Name: str
    ID: int
    Date: str
    Time: str
    Message: str
    FileAttached: StrOrFalse
    IsApple: bool

@dataclass
class MessagesStore:
    """Store for WhatsApp messages"""
    messages: List[MessageData] = field(
        init=False,
        default_factory=list
    )
    required_fields: tuple = field(
        init=False,
        default=(
            'Name',
            'ID',
            'Date',
            'Time',
            'Message',
            'FileAttached',
            'IsApple'
        )
    )
    
    def add_message(self, message: MessageData) -> None:
        """Add a message to the store"""
        self.messages.append(message)
    
    def get_messages(self) -> List[MessageData]:
        """Get all messages"""
        return self.messages
    
    def clear(self) -> None:
        """Clear all messages"""
        self.messages.clear()
    
    def __len__(self) -> int:
        """Get the number of messages"""
        return len(self.messages)