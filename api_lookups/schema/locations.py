from pydantic import BaseModel, Field


class LkpCountryOut(BaseModel):
    id: int = Field(alias="country_id")
    country: str
    status: bool

    class Config:
        from_attributes = True
        validate_by_name = True


class LkpStateOut(BaseModel):
    id: int = Field(alias="state_id")
    state: str
    country_id: int
    status: bool

    class Config:
        from_attributes = True
        validate_by_name = True


class LkpDistrictOut(BaseModel):
    id: int = Field(alias="district_id")
    district: str
    country_id: int
    state_id: int
    status: bool

    class Config:
        from_attributes = True
        validate_by_name = True
