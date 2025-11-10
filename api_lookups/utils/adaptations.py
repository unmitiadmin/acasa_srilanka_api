from ..models import LkpCommodity, LkpCommodityType, \
    LkpAdaptGroup, LkpAdapt
from sqlalchemy import and_, or_


class LkpAdaptUtil:
    def __init__(self, **kwargs):
        self.db = kwargs.get("db")
        self.commodity_id = kwargs.get("commodity_id")


    def get_crops(self):
        adaptations = self.db.query(LkpAdapt).filter(
            and_(
                LkpAdapt.commodity_type_id == self.commodity_obj.type.id,
                or_(
                    LkpAdapt.commodity_id == self.commodity_id,
                    LkpAdapt.commodity_id == None
                )    
            )
        ).order_by(LkpAdapt.id).all()
        options_list = [{
            "group_id": i.group_id,
            "group": None if not i.group_id else self.groups[i.group_id],
            "adaptation_id": i.id,
            "adaptation": i.adaptation,
            "description": i.description,
            "analytics_param_id": i.analytics_param_id,
            "status": bool(i.status),
        } for i in adaptations]
        return options_list


    def get_livestock(self):
        adaptations = self.db.query(LkpAdapt).filter(
            and_(
                LkpAdapt.commodity_type_id == self.commodity_obj.type.id,
                LkpAdapt.commodity_id == self.commodity_id  
            )
        ).order_by(LkpAdapt.id).all()
        options_list = [{
            "group_id": i.group_id,
            "group": None if not i.group_id else self.groups[i.group_id],
            "adaptation_id": i.id,
            "adaptation": i.adaptation,
            "description": i.description,
            "analytics_param_id": i.analytics_param_id,
            "status": bool(i.status),
        } for i in adaptations]
        return options_list


    def get_data(self):
        self.commodity_obj = self.db.query(LkpCommodity).filter(LkpCommodity.id == self.commodity_id).first()
        groups_queryset = self.db.query(LkpAdaptGroup).filter(LkpAdaptGroup.commodity_type_id == self.commodity_obj.type.id).all()
        self.groups = {i.id: i.group for i in groups_queryset}
        commodity_types = {
            "Crops": self.get_crops,
            "Livestock": self.get_livestock,
        }
        return commodity_types[self.commodity_obj.type.type]()
        

