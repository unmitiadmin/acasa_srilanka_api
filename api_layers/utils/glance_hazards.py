import re
from pathlib import Path
from settings import env
from api_lookups.models import LkpCommodity, LkpVisualizationScale, \
    LkpClimateScenario, LkpIntensityMetric, LkpChangeMetric, \
    LkpRisk, LkpRiskColor



class GlanceHazards:
    def __init__(self, **kwargs):
        self.data_root_dir = Path(env.get("DATA_ROOT_DIR"))
        self.db = kwargs.get("db")
        self.commodity_id = kwargs.get("commodity_id")
        # associate objects
        self.commodity_obj = self.db.query(LkpCommodity).filter(LkpCommodity.id == self.commodity_id).first()
        self.lcase = lambda s: re.sub(r'[^a-zA-Z0-9]', '', s).lower()
        self.ucase = lambda s: re.sub(r'[^a-zA-Z0-9]', '', s).upper()
        

    def execute(self):
        # Hazards - Commodity/{INTENSITY-METRIC - I/IF}/{Scenario}/{District/Pixel}/{CHANGE-METRIC - abs/del}
        # dist_pfx = "" # Squeeze this later - {District/Pixel} on confirmation
        parent_folder = "Hazards-final-struc"
        intensity_metric_ids = [row.id for row in self.db.query(LkpIntensityMetric).filter(LkpIntensityMetric.status)]
        change_metric_ids = [row.id for row in self.db.query(LkpChangeMetric).filter(LkpChangeMetric.status)]
        visualization_scale_ids = [row.id for row in self.db.query(LkpVisualizationScale).filter(LkpVisualizationScale.status)]
        commodity = self.commodity_obj.commodity
        master_queryset = self.db.query(LkpRisk).filter(
            (LkpRisk.commodity_type_id == self.commodity_obj.type_id) &
            ((LkpRisk.commodity_id == None) | (LkpRisk.commodity_id == self.commodity_obj.id))
        )
        all_scenarios = self.db.query(LkpClimateScenario).all()
        raster_file_index = []
        hazard_index_obj = master_queryset.filter(LkpRisk.suffix == "Hazard Index").first()
        other_objs = (
            master_queryset.filter(LkpRisk.suffix != "Hazard Index").limit(6).all()
            if self.commodity_obj.type.type == "Crops"
            else master_queryset.filter(LkpRisk.ipcc_id == 2).limit(6).all()
        )
        all_hazards = [hazard_index_obj, *other_objs]
        
        for grid_sequence, hazard_obj in enumerate(all_hazards):
            ramp = self.db.query(LkpRiskColor).filter(LkpRiskColor.suffix == hazard_obj.suffix).first().ramp
            hazard_index = {
                "grid_sequence": grid_sequence,
                "layer_id": hazard_obj.id,
                "layer_type": "risk",
                "hazard_title": hazard_obj.risk, 
                "raster_files": [],
            }
            for scale_id in visualization_scale_ids:
                for scenario in all_scenarios:
                    for intensity_metric_id in intensity_metric_ids:
                        for change_metric_id in change_metric_ids:
                            intensity_metric_obj = self.db.query(LkpIntensityMetric).filter(LkpIntensityMetric.id == intensity_metric_id).first()
                            change_metric_obj = self.db.query(LkpChangeMetric).filter(LkpChangeMetric.id == change_metric_id).first()
                            visualization_scale_obj = self.db.query(LkpVisualizationScale).filter(LkpVisualizationScale.id == scale_id).first()
                            scale = str(visualization_scale_obj.scale).split(" ")[0]
                            if scenario.scenario == "Baseline":
                                if change_metric_id == 1:
                                    baseline_intm_folder = f"{commodity}/{intensity_metric_obj.metric}/{scale}/Baseline/{change_metric_obj.p}"
                                    baseline_file = f"Baseline_{change_metric_obj.p}_{commodity}_{hazard_obj.suffix}.tif"
                                    hazard_index["raster_files"].append({
                                        "year": None,
                                        "climate_scenario_id": scenario.id,
                                        "intensity_metric_id": intensity_metric_id,
                                        "change_metric_id": change_metric_id,
                                        "visualization_scale_id": scale_id,
                                        "climate_scenario": "Baseline",
                                        "intensity_metric": intensity_metric_obj.metric,
                                        "change_metric": change_metric_obj.metric,
                                        "visualization_scale": scale,
                                        "source_file": (Path(parent_folder)/ baseline_intm_folder / baseline_file).as_posix(),
                                        "exists": Path.exists(self.data_root_dir / parent_folder / baseline_intm_folder / baseline_file),
                                        "ramp": ramp,
                                    })
                            else:
                                delta_color_ramp = (
                                    ["#800000", "#FF6666", "#F5F5DC", "#87CEFA", "#4682B4"]
                                    if hazard_obj.ipcc.ipcc == "Climatology" and hazard_obj.suffix == "Seasonal Rainfall"
                                    else ["#4682B4", "#87CEFA", "#E7E6A8", "#FF6666", "#800000"]
                                )
                                scn = self.ucase(scenario.scenario)
                                for future in [2050, 2080]:
                                    scenario_intm_folder = f"{commodity}/{intensity_metric_obj.metric}/{scale}/{scn}/{change_metric_obj.p}"
                                    scenario_file = f"{future}_{scn}_{change_metric_obj.p}_{commodity}_{hazard_obj.suffix}.tif"
                                    hazard_index["raster_files"].append({
                                        "year": future,
                                        "climate_scenario_id": scenario.id,
                                        "intensity_metric_id": intensity_metric_id,
                                        "change_metric_id": change_metric_id,
                                        "visualization_scale_id": scale_id,
                                        "climate_scenario": f"{scenario.scenario} | {future}s",
                                        "intensity_metric": intensity_metric_obj.metric,
                                        "change_metric": change_metric_obj.metric,
                                        "visualization_scale": scale,
                                        "source_file": (Path(parent_folder)/ scenario_intm_folder / scenario_file).as_posix(),
                                        "exists": Path.exists(self.data_root_dir / parent_folder / scenario_intm_folder / scenario_file),
                                        "ramp": ramp if change_metric_id == 1 else delta_color_ramp,
                                    })
            raster_file_index.append(hazard_index)      
        return {
            "commodity": f"{self.commodity_obj.commodity_group}: {self.commodity_obj.commodity}",
            "raster_grids": raster_file_index
        }


    
    