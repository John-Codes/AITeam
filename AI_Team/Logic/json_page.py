# Define a new Pydantic model with field descriptions and tailored for Twitter.
from pydantic import BaseModel, Field
from typing import List

class ContentPage(BaseModel):
    title: str = Field(description="Title of the page.")
    header: str = Field(description="Header of the page.")
    description: str = Field(description="Description of the page.")
    keywords: List[str] = Field(description="Keywords of the page.")
    default_message: str = Field(description="Default message of the page.")
    list_items: List[dict] = Field(description="List items of the page.")