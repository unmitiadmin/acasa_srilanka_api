from ..models import LkpCommodity, LkpCommodityType, \
    LkpRiskIpcc, LkpRisk, LkpRiskCommoditySeason
from ..schema import LkpRiskIpccOut
from sqlalchemy import and_, or_


class LkpRiskUtil:
    def __init__(self, **kwargs):
        self.db = kwargs.get("db")
        self.commodity_id = kwargs.get("commodity_id")
        
    
    def get_data(self):
        ipcc_queryset = self.db.query(LkpRiskIpcc).filter(LkpRiskIpcc.status).all()
        if self.commodity_id:
            commodity_obj = self.db.query(LkpCommodity).filter(LkpCommodity.id == self.commodity_id).first()
            commodity = commodity_obj.commodity
            commodity_type = commodity_obj.type.type
            ipcc_dict = {int(i.id) : (
                f"Climate hazards of {commodity}" if i.id == 2 # Hazards
                else  (
                    f"{i.ipcc} (Area of {commodity})" if commodity_type == "Crops"
                    else f"Exposure (Number of {commodity} per grid)" if commodity_type == "Livestock"
                    else ""
                ) if i.id == 3 # Exposure
                else (
                    f"Vulnerability of {commodity} farming systems" if commodity_type == "Livestock"
                    else f"Vulnerability" if commodity_type == "Crops"
                    else ""
                ) if i.id == 4 # Vulnerability
                else i.ipcc # Indices or Climatology
            ) for i in ipcc_queryset} 
            print(ipcc_dict)
            c_queryset = self.db.query(LkpRisk).filter(
                and_(
                    LkpRisk.commodity_type_id == commodity_obj.type.id,
                    or_(
                        LkpRisk.commodity_id == self.commodity_id,
                        LkpRisk.commodity_id == None
                    )
                )
            ).all()
            risk_options = []
            for i in c_queryset:
                if not(i.risk == "Feed/Fodder" and commodity in ["Pig", "Chicken"]):
                    risk_options.append({
                        "ipcc_id": i.ipcc_id,
                        "ipcc": ipcc_dict[i.ipcc_id],
                        "risk_id": i.id,
                        "risk": i.risk,
                        "description": i.description,
                        "analytics_param_id": i.analytics_param_id,
                        "status": bool(i.status),
                    })
            risk_options = sorted(risk_options, key=lambda x: x.get("ipcc_id"))
            return risk_options
        else:
            ipcc_dict = {int(i.id): i.ipcc for i in ipcc_queryset }
            c_queryset = self.db.query(LkpRisk).filter(
                and_(
                    LkpRisk.commodity_type_id == None,
                    LkpRisk.commodity_id == None
                )
            )
            risk_options = []
            for i in c_queryset:
                risk_options.append({
                    "ipcc_id": i.ipcc_id,
                    "ipcc": ipcc_dict[i.ipcc_id],
                    "risk_id": i.id,
                    "risk": i.risk,
                    "description": i.description,
                    "analytics_param_id": i.analytics_param_id,
                    "status": bool(i.status),
                })

            risk_options = sorted(risk_options, key=lambda x: x.get("ipcc_id"))
            return risk_options
