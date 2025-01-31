from pydantic import BaseModel, Field


class A(BaseModel):
    hey: str = Field(alias="h")
    ho: str
