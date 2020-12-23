from pydantic import BaseModel
from typing import Optional
from datetime import date


class OverdueItem(BaseModel):
	environment: str
	project_id: int
	period: int
	start_date: date
