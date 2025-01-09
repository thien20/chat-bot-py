from pydantic import BaseModel

class KBEntry(BaseModel):
    id: str
    title: str
    content: str
    metadata: dict
