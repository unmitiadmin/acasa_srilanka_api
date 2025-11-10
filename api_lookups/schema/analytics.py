from pydantic import BaseModel, Field
from typing import Optional


class LkpAnalyticsScenarioOut(BaseModel):
    id: int = Field(alias="scenario_id")
    scenario: str
    description: str
    status: bool

    class Config:
        from_attributes = True
        validate_by_name = True


class LkpClimateDataModelOut(BaseModel):
    id: int = Field(alias="data_model_id")
    model: str
    description: Optional[str]
    status: bool

    class Config:
        from_attributes = True
        validate_by_name = True


