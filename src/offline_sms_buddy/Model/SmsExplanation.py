from pydantic import BaseModel

class SmsExplanation(BaseModel):
    """The three answers the model must give. Ollama forces this JSON shape."""

    meaning: str
    what_to_do: str
    be_careful: str