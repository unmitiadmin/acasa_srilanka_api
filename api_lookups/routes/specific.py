from typing import List
from fastapi import APIRouter, Request, Depends
from settings.database import get_db
from settings.responses import SuccessResponse
from sqlalchemy.orm import Session
from ..models import LkpImpact, LkpAdaptCropColor
from ..schema import LkpImpactOut, LkpAdaptCropTabOut
from ..utils import LkpRiskUtil, LkpAdaptUtil


class LkpSpecificRouter:
    def __init__(self):
        self.router = APIRouter()
        self.router.add_api_route("/impacts", self.get_impacts, methods=["GET"], response_model=SuccessResponse[List[LkpImpactOut]])
        self.router.add_api_route("/risks", self.get_risks, methods=["GET"])
        self.router.add_api_route("/adaptation_croptabs", self.get_adaptation_croptabs, methods=["GET"], response_model=SuccessResponse[List[LkpAdaptCropTabOut]])
        self.router.add_api_route("/adaptations", self.get_adaptations, methods=["GET"])


    def get_risks(self, request: Request, db: Session=Depends(get_db)):
        commodity_id = request.query_params.get("commodity_id")
        data = LkpRiskUtil(db=db, commodity_id=commodity_id).get_data()
        return {"success": 1, "data": data}


    def get_impacts(self, db: Session=Depends(get_db)):
        data =  db.query(LkpImpact).all()
        return {"success": 1, "data": data}

    
    def get_adaptation_croptabs(self, db: Session=Depends(get_db)):
        data = db.query(LkpAdaptCropColor).all()
        return {"success": 1, "data": data}
    

    def get_adaptations(self, request: Request, db: Session=Depends(get_db)):
        commodity_id = request.query_params.get("commodity_id")
        data = LkpAdaptUtil(db=db, commodity_id=commodity_id).get_data()
        return {"success": 1, "data": data}


lkp_specific_router = LkpSpecificRouter().router
