from pydantic import BaseModel, Field, field_serializer
from typing import Optional


class LkpAnalysisScopeOut(BaseModel):
    id: int = Field(alias="scope_id")
    scope: str
    description: str
    status: bool

    class Config:
        from_attributes = True
        validate_by_name = True


class LkpVisualizationScaleOut(BaseModel):
    id: int = Field(alias="scale_id")
    scale: str
    description: str
    status: bool

    class Config:
        from_attributes = True
        validate_by_name = True


class LkpCommodityTypeOut(BaseModel):
    id: int = Field(alias="commodity_type_id")
    type: str = Field(alias="commodity_type")
    status: bool

    class Config:
        from_attributes = True
        validate_by_name = True


class LkpCommodityOut(BaseModel):
    id: int = Field(alias="commodity_id")
    type_id: int = Field(alias="commodity_type_id")
    commodity_group: str
    commodity: str
    analytics_param_id: Optional[int]
    status: bool

    @field_serializer("commodity")
    def rename_mustard(self, v: str, _info):
        return "Rapeseed/Mustard" if v == "Mustard" else v
    class Config:
        from_attributes = True
        validate_by_name = True



class LkpDataSourceOut(BaseModel):
    id: int = Field(alias="data_source_id")
    source: str
    description: str
    status: bool

    class Config:
        from_attributes = True
        validate_by_name = True


class LkpClimateScenarioOut(BaseModel):
    id: int = Field(alias="scenario_id")
    scenario: str
    description: str
    status: bool

    class Config:
        from_attributes = True
        validate_by_name = True



class LkpIntensityMetricOut(BaseModel):
    id: int = Field(alias="intensity_metric_id")
    metric: str
    status: bool

    class Config:
        from_attributes = True
        validate_by_name = True


class LkpChangeMetricOut(BaseModel):
    id: int = Field(alias="change_metric_id")
    metric: str
    status: bool

    class Config:
        from_attributes = True
        validate_by_name = True