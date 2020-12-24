from pydantic import BaseModel
from typing import Optional, Union
from datetime import date


class OverdueItem(BaseModel):
	environment: str
	project_id: int
	period: str
	start_date: date
