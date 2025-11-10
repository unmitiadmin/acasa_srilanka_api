from settings.database import get_db
from sqlalchemy.orm import Session
from fastapi import APIRouter, Request, Depends
from api_analytics.exceptions import AnalyticsDataException
from .utils import ClimateAnalyticsUtil



class AnalyticsRouter:
    def __init__(self):
        self.router = APIRouter()
        self.router.add_api_route("/climate", self.climate, methods=["POST"])
    

    async def climate(self, request: Request, db: Session=Depends(get_db)):
        request_body = await request.json()
        admin_level = request_body.get("admin_level")
        admin_level_id = request_body.get("admin_level_id")
        analytics_param_id = request_body.get("analytics_param_id")
        if analytics_param_id not in [1, 2, 3]:
            raise AnalyticsDataException("Please choose the right climate parameter to view data")
        data = ClimateAnalyticsUtil(
            db=db,
            admin_level=admin_level,
            admin_level_id=admin_level_id,
            analytics_param_id=analytics_param_id,
        ).execute()
        return {"success": 1, "data": data}


analytics_router = AnalyticsRouter().router
