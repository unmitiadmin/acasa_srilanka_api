from typing import List
from fastapi import APIRouter, Request, Depends
from settings.database import get_db
from settings.responses import SuccessResponse
from sqlalchemy.orm import Session
from ..models import LkpAnalysisScope, LkpVisualizationScale, \
    LkpDataSource, LkpClimateScenario, LkpCommodityType, LkpCommodity, \
    LkpIntensityMetric, LkpChangeMetric
from ..schema import LkpAnalysisScopeOut, LkpVisualizationScaleOut, \
    LkpDataSourceOut, LkpClimateScenarioOut, LkpCommodityTypeOut, LkpCommodityOut, \
    LkpIntensityMetricOut, LkpChangeMetricOut
from sqlalchemy import and_, or_



class LkpCommonRouter:
    def __init__(self):
        self.router = APIRouter()
        self.router.add_api_route(
            "/analysis_scopes", self.get_analysis_scopes,
            methods=["GET"], response_model=SuccessResponse[List[LkpAnalysisScopeOut]]
        )
        self.router.add_api_route(
            "/visualization_scales", self.get_visualization_scales,
            methods=["GET"], response_model=SuccessResponse[List[LkpVisualizationScaleOut]]
        )
        self.router.add_api_route(
            "/data_sources", self.get_data_sources,
            methods=["GET"], response_model=SuccessResponse[List[LkpDataSourceOut]]
        )
        self.router.add_api_route(
            "/climate_scenarios", self.get_climate_scenarios,
            methods=["GET"], response_model=SuccessResponse[List[LkpClimateScenarioOut]]
        )
        self.router.add_api_route(
            "/commodity_types", self.get_commodity_types,
            methods=["GET"], response_model=SuccessResponse[List[LkpCommodityTypeOut]]
        )
        self.router.add_api_route(
            "/commodities", self.get_commodities,
            methods=["GET"], response_model=SuccessResponse[List[LkpCommodityOut]]
        )
        self.router.add_api_route(
            "/intensity_metrics", self.get_intensity_metrics,
            methods=["GET"], response_model=SuccessResponse[List[LkpIntensityMetricOut]]
        )
        self.router.add_api_route(
            "/change_metrics", self.get_change_metrics,
            methods=["GET"], response_model=SuccessResponse[List[LkpChangeMetricOut]]
        )
        
    
    def get_analysis_scopes(self, db: Session=Depends(get_db)):
        data = db.query(LkpAnalysisScope).all()
        return {"success": 1, "data": data}


    def get_visualization_scales(self, db: Session=Depends(get_db)):
        data = db.query(LkpVisualizationScale).all()
        return {"success": 1, "data": data}
    

    def get_data_sources(self, db: Session=Depends(get_db)):
        data = db.query(LkpDataSource).all()
        return {"success": 1, "data": data}
    

    def get_climate_scenarios(self, db: Session=Depends(get_db)):
        data = db.query(LkpClimateScenario).all()
        return {"success": 1, "data": data}
    

    def get_commodity_types(self, db: Session=Depends(get_db)):
        data = db.query(LkpCommodityType).all()
        return {"success": 1, "data": data}
    

    def get_commodities(self, db: Session=Depends(get_db)):
        data = db.query(LkpCommodity).all()
        return {"success": 1, "data": data}


    def get_intensity_metrics(self, db: Session=Depends(get_db)):
        data = db.query(LkpIntensityMetric).all()
        return {"success": 1, "data": data}
    

    def get_change_metrics(self, db: Session=Depends(get_db)):
        data = db.query(LkpChangeMetric).all()
        return {"success": 1, "data": data}


lkp_common_router = LkpCommonRouter().router
