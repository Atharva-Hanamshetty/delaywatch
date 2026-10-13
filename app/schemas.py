from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class ReportCreate(BaseModel):
    train_number: str = Field(min_length=4, max_length=5)
    station_code: str = Field(min_length=2, max_length=5)
    delay_minutes: int = Field(ge=0, le=720)

    @field_validator("train_number")
    @classmethod
    def train_number_digits_only(cls, v: str) -> str:
        v = v.strip()
        if not v.isdigit():
            raise ValueError("train_number must contain digits only")
        return v

    @field_validator("station_code")
    @classmethod
    def station_code_uppercase(cls, v: str) -> str:
        return v.strip().upper()


class ReportOut(BaseModel):
    id: int
    train_number: str
    station_code: str
    delay_minutes: int
    reported_at: datetime

    model_config = {"from_attributes": True}