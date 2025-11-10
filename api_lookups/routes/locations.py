from typing import List
from fastapi import APIRouter, Request, Depends
from settings.database import get_db
from settings.responses import SuccessResponse
from sqlalchemy.orm import Session
from ..models import LkpCountry, LkpState, LkpDistrict
from ..schema import LkpCountryOut, LkpStateOut, LkpDistrictOut
from sqlalchemy import and_, or_


class LkpLocationRouter:
    def __init__(self):
        self.router = APIRouter()
        self.router.add_api_route(
            "/countries", self.countries,  
            methods=["GET"], response_model=SuccessResponse[List[LkpCountryOut]]
        )
        self.router.add_api_route(
            "/states", self.states,  
            methods=["GET"], response_model=SuccessResponse[List[LkpStateOut]]
        )
        self.router.add_api_route(
            "/districts", self.districts,  
            methods=["GET"], response_model=SuccessResponse[List[LkpDistrictOut]]
        )


    def countries(self, db: Session=Depends(get_db)):
        data =  db.query(LkpCountry).all()
        return {"success": 1, "data": data}


    def states(self, request: Request, db: Session=Depends(get_db)):
        country_id = request.query_params.get("country_id")
        data = db.query(LkpState).filter(LkpState.country_id == country_id).all()
        return {"success": 1, "data": data}
    
    
    def districts(self, request: Request, db: Session=Depends(get_db)):
        country_id = request.query_params.get("country_id")
        state_id = request.query_params.get("state_id")
        data = db.query(LkpDistrict).filter(
            and_(LkpDistrict.country_id == country_id, LkpDistrict.state_id == state_id)
        ).all()
        return {"success": 1, "data": data}



lkp_location_router = LkpLocationRouter().router
