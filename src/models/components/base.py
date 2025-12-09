from pydantic import BaseModel, ConfigDict

from abc import ABC
from typing import Optional

from src.models.enums import Position


class Component(ABC, BaseModel):

    identifier: str
    position: Optional[Position] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)
