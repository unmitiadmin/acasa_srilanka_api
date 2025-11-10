from typing import List
from fastapi import APIRouter, Request, Depends
from settings.database import get_db
from settings.responses import SuccessResponse
from sqlalchemy.orm import Session
from ..models import LkpClimateDataModel, LkpAnalyticsScenario
from ..schema import LkpClimateDataModelOut, LkpAnalyticsScenarioOut

class AnalyticsRouter:
    def __init__(self):
        self.router = APIRouter()
        self.router.add_api_route(
            "/climate_scenarios", self.climate_scenarios, methods=["GET"],
            response_model=SuccessResponse[List[LkpAnalyticsScenarioOut]]
        )
        self.router.add_api_route(
            "/climate_data_models", self.climate_data_models, methods=["GET"],
            response_model=SuccessResponse[List[LkpClimateDataModelOut]]
        )


    def climate_scenarios(self, db: Session=Depends(get_db)):
        data = db.query(LkpAnalyticsScenario)
        return {"success": 1, "data": data}
    

    def climate_data_models(self, db: Session=Depends(get_db)):
        data = db.query(LkpClimateDataModel)
        return {"success": 1, "data": data}


lkp_analytics_router = AnalyticsRouter().router
