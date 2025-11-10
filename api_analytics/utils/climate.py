from api_lookups.models import (
    LkpCountry, LkpState,
    LkpAnalyticsScenario, LkpClimateDataModel, LkpAnalyticsParam
)
from ..models import (
    TblStAnalyticsPrec, TblStAnalyticsTmax, TblStAnalyticsTmin
)
from sqlalchemy import func
from ..exceptions import AnalyticsDataException


class ClimateAnalyticsUtil:
    def __init__(self, **kwargs):
        self.state_level_models = {
            1: TblStAnalyticsPrec,
            2: TblStAnalyticsTmax,
            3: TblStAnalyticsTmin
        }
        self.db = kwargs.get("db")
        self.admin_level = kwargs.get("admin_level")
        self.admin_level_id = kwargs.get("admin_level_id")
        self.analytics_param_id = kwargs.get("analytics_param_id")
        self.camelcase = lambda s: " ".join(word.capitalize() for word in s.split())

    def execute(self):
        param_obj = self.db.query(LkpAnalyticsParam).get(self.analytics_param_id)
        TblAnalytics = self.state_level_models[self.analytics_param_id]

        if self.admin_level == "state":
            state_obj = self.db.query(LkpState).get(self.admin_level_id)
            if not state_obj:
                raise AnalyticsDataException("Please choose a valid state")
            location = f"{self.camelcase(state_obj.state)}, {state_obj.country.country}"
            queryset = (
                self.db.query(
                    TblAnalytics.year,
                    LkpAnalyticsScenario.scenario,
                    func.min(TblAnalytics.value).label("min_value"),
                    func.max(TblAnalytics.value).label("max_value"),
                    func.avg(TblAnalytics.value).label("mean_value"),
                )
                .join(LkpAnalyticsScenario, TblAnalytics.climate_scenario_id == LkpAnalyticsScenario.id)
                .filter(TblAnalytics.country_id == state_obj.country_id)
                .filter(TblAnalytics.state_id == self.admin_level_id)
                .group_by(TblAnalytics.year, TblAnalytics.climate_scenario_id)
                .order_by(TblAnalytics.climate_scenario_id, TblAnalytics.year)
            ).all()

        elif self.admin_level == "country":
            country_obj = self.db.query(LkpCountry).get(self.admin_level_id)
            if not country_obj:
                raise AnalyticsDataException("Please choose a valid country")
            location = country_obj.country
            queryset = (
                self.db.query(
                    TblAnalytics.year,
                    LkpAnalyticsScenario.scenario,
                    func.min(TblAnalytics.value).label("min_value"),
                    func.max(TblAnalytics.value).label("max_value"),
                    func.avg(TblAnalytics.value).label("mean_value"),
                )
                .join(LkpAnalyticsScenario, TblAnalytics.climate_scenario_id == LkpAnalyticsScenario.id)
                .filter(TblAnalytics.country_id == self.admin_level_id)
                .filter(TblAnalytics.state_id == None)
                .group_by(TblAnalytics.year, TblAnalytics.climate_scenario_id)
                .order_by(TblAnalytics.climate_scenario_id, TblAnalytics.year)
            ).all()

        elif self.admin_level == "total":
            location = "South Asia"
            queryset = (
                self.db.query(
                    TblAnalytics.year,
                    LkpAnalyticsScenario.scenario,
                    func.min(TblAnalytics.value).label("min_value"),
                    func.max(TblAnalytics.value).label("max_value"),
                    func.avg(TblAnalytics.value).label("mean_value"),
                )
                .join(LkpAnalyticsScenario, TblAnalytics.climate_scenario_id == LkpAnalyticsScenario.id)
                .filter(TblAnalytics.country_id == None)
                .filter(TblAnalytics.state_id == None)
                .group_by(TblAnalytics.year, TblAnalytics.climate_scenario_id)
                .order_by(TblAnalytics.climate_scenario_id, TblAnalytics.year)
            ).all()

        chart_data = [{
            "year": r.year,
            "scenario": r.scenario,
            "min": r.min_value,
            "max": r.max_value,
            "mean": r.mean_value,
        } for r in queryset]

        return {
            "location": location,
            "parameter": param_obj.param,
            "units": param_obj.units,
            "chart_data": chart_data
        }
