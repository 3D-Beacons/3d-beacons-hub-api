from pydantic import BaseModel


class Sequence(BaseModel):
    sequence: str
