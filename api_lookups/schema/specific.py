from pydantic import BaseModel, Field
from typing import Optional

class LkpImpactOut(BaseModel):
    id: int = Field(alias="impact_id")
    impact: str
    description: str
    analytics_param_id: Optional[int]
    status: bool

    class Config:
        from_attributes = True
        validate_by_name = True

class LkpRiskIpccOut(BaseModel):
    id: int = Field(alias="ipcc_id")
    ipcc: str
    c_label_sufx: bool
    c_label_info: Optional[str]
    status: bool

    class Config:
        from_attributes = True
        validate_by_name = True


class LkpAdaptCropTabOut(BaseModel):
    id: int = Field(alias="tab_id")
    tab_name: str
    status: bool

    class Config:
        from_attributes = True
        validate_by_name = True