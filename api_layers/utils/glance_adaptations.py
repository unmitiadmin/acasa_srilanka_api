import re
from pathlib import Path
from settings import env
from api_lookups.models import (
    LkpCommodity,LkpClimateScenario, LkpIntensityMetric, LkpChangeMetric, LkpVisualizationScale,
    LkpImpact, LkpImpactColor, # Crop sequence 0
    LkpRisk, LkpRiskColor, # Livestock sequence 0
    LkpAdapt, LkpAdaptCropColor, LkpAdaptLivestockColor, LkpAdaptGroup
)
from api_layers.exceptions import LayerDataException

class GlanceAdaptations:
    def __init__(self, **kwargs):
        self.data_root_dir = Path(env.get("DATA_ROOT_DIR"))
        self.db = kwargs.get("db")
        # associate objects
        self.commodity_id = kwargs.get("commodity_id")
        self.commodity_obj = self.db.query(LkpCommodity).filter(LkpCommodity.id == self.commodity_id).first()
        self.adaptation_croptab_id = kwargs.get("adaptation_croptab_id")
        self.lcase = lambda s: re.sub(r'[^a-zA-Z0-9]', '', s).lower()
        self.ucase = lambda s: re.sub(r'[^a-zA-Z0-9]', '', s).upper()

    
    def crop_sequence_zero(self):
        parent_folder = "Impact-final-struc" # temporarily moving from Impact (Aug 2025)
        commodity = self.commodity_obj.commodity
        impact_obj = self.db.query(LkpImpact).get(1) # IMPACT ON PRODUCTIVITY
        # ramp will be scenario specific
        raster_file_index = []
        intensity_metric_ids = [row.id for row in self.db.query(LkpIntensityMetric).filter(LkpIntensityMetric.status)]
        change_metric_ids = [row.id for row in self.db.query(LkpChangeMetric).filter(LkpChangeMetric.status)]
        visualization_scale_ids = [row.id for row in self.db.query(LkpVisualizationScale).filter(LkpVisualizationScale.status)]
        # Baseline
        baseline_ramp = self.db.query(LkpImpactColor).filter(LkpImpactColor.suffix == f"{impact_obj.optcode}_baseline").first().ramp
        for scale_id in visualization_scale_ids:
            for intensity_metric_id in intensity_metric_ids:
                for change_metric_id in [change_metric_ids[0]]: # no delta for baseline
                    intensity_metric_obj = self.db.query(LkpIntensityMetric).filter(LkpIntensityMetric.id == intensity_metric_id).first()
                    change_metric_obj = self.db.query(LkpChangeMetric).filter(LkpChangeMetric.id == change_metric_id).first()
                    scale_obj = self.db.query(LkpVisualizationScale).filter(LkpVisualizationScale.id == scale_id).first()
                    scale = str(scale_obj.scale).split(" ")[0]
                    # FOLDERPATH: {Commodity}/{Intensity|IntensityFrequency}/{District|Pixel}/Baseline/{abs|del}
                    baseline_intm_folder = f"{commodity}/{intensity_metric_obj.metric}/{scale}/Baseline/{change_metric_obj.p}"
                    # FILENAME EXAMPLE: Baseline_abs_Maize_CV.tif
                    baseline_file = f"Baseline_{change_metric_obj.p}_{commodity}_{impact_obj.optcode}.tif"
                    raster_file_index.append({
                        "year": None,
                        "impact_id": impact_obj.id,
                        "climate_scenario_id": 1,
                        "intensity_metric_id": intensity_metric_id,
                        "change_metric_id": change_metric_id,
                        "visualization_scale_id": scale_id,
                        "climate_scenario": "Baseline",
                        "intensity_metric": intensity_metric_obj.metric,
                        "change_metric": change_metric_obj.metric,
                        "visualization_scale": scale,
                        "source_file": (Path(parent_folder)/ baseline_intm_folder / baseline_file).as_posix(),
                        "exists": Path.exists(self.data_root_dir / parent_folder / baseline_intm_folder / baseline_file),
                        "ramp": baseline_ramp,
                    })
        # Future scenarios
        def append_non_baseline_impact(future, nonbaseline_scenario_id, intensity_metric_id, change_metric_id, scale_id):
            nonbaseline_scenario_obj = self.db.query(LkpClimateScenario).get(nonbaseline_scenario_id)
            scenario_ucase = self.ucase(nonbaseline_scenario_obj.scenario)
            scenario_lcase = self.lcase(nonbaseline_scenario_obj.scenario)
            scn_ramp = self.db.query(LkpImpactColor).filter(LkpImpactColor.suffix == f"{impact_obj.optcode}_{scenario_lcase}").first().ramp
            intensity_metric_obj = self.db.query(LkpIntensityMetric).filter(LkpIntensityMetric.id == intensity_metric_id).first()
            change_metric_obj = self.db.query(LkpChangeMetric).filter(LkpChangeMetric.id == change_metric_id).first()
            scale_obj = self.db.query(LkpVisualizationScale).filter(LkpVisualizationScale.id == scale_id).first()
            scale = str(scale_obj.scale).split(" ")[0]
            # FOLDERPATH: {Commodity}/{Intensity|IntensityFrequency}/{District|Pixel}/{scenario_ucase}/{abs|del}
            intm_folder = f"{commodity}/{intensity_metric_obj.metric}/{scale}/{scenario_ucase}/{change_metric_obj.p}"
            # FILENAME EXAMPLE: Baseline_abs_Maize_CV.tif
            scenario_file = f"{future}_{scenario_ucase}_{change_metric_obj.p}_{commodity}_{impact_obj.optcode}.tif"
            raster_file_index.append({
                "year": future,
                "impact_id": impact_obj.id,
                "climate_scenario_id": nonbaseline_scenario_id,
                "intensity_metric_id": intensity_metric_id,
                "change_metric_id": change_metric_id,
                "visualization_scale_id": scale_id,
                "climate_scenario": nonbaseline_scenario_obj.scenario,
                "intensity_metric": intensity_metric_obj.metric,
                "change_metric": change_metric_obj.metric,
                "visualization_scale": scale,
                "source_file": (Path(parent_folder)/ intm_folder / scenario_file).as_posix(),
                "exists": Path.exists(self.data_root_dir / parent_folder / intm_folder / scenario_file),
                "ramp": scn_ramp
            })
        nonbaseline_scenario_ids = [row.id for row in self.db.query(LkpClimateScenario.id).filter(LkpClimateScenario.scenario != "Baseline").all()]
        for future in [2050, 2080]:
            for scale_id in visualization_scale_ids:
                for nonbaseline_scenario_id in nonbaseline_scenario_ids:
                    for intensity_metric_id in intensity_metric_ids:
                        for change_metric_id in change_metric_ids:
                            append_non_baseline_impact(future, nonbaseline_scenario_id, intensity_metric_id, change_metric_id, scale_id)
        return raster_file_index


    def prep_crops(self):
        parent_folder = "Adap-final-struc"
        intensity_metric_ids = [row.id for row in self.db.query(LkpIntensityMetric).filter(LkpIntensityMetric.status)]
        change_metric_ids = [row.id for row in self.db.query(LkpChangeMetric).filter(LkpChangeMetric.status)]
        visualization_scale_ids = [row.id for row in self.db.query(LkpVisualizationScale).filter(LkpVisualizationScale.status)]
        commodity = self.commodity_obj.commodity
        all_scenarios = self.db.query(LkpClimateScenario).all()
        raster_file_index = []
        raster_file_index.append({
            "grid_sequence": None,
            "layer_type": "impact",
            "layer_id": 1,
            "grid_sequence_title": "Impact on productivity",
            "raster_files": self.crop_sequence_zero()
        })
        master_queryset = self.db.query(LkpAdapt).filter(
            (LkpAdapt.commodity_type_id == 1) &
            ((LkpAdapt.commodity_id == self.commodity_id) | (LkpAdapt.commodity_id == None))
        )
        all_adaptations = master_queryset.all()
        cpfx_obj = self.db.query(LkpAdaptCropColor).get(self.adaptation_croptab_id)
        for grid_sequence, adap_obj in enumerate(all_adaptations):
            adap_index = {
                "grid_sequence": grid_sequence + 1,
                "layer_type": "adaptation",
                "layer_id": adap_obj.id,
                "grid_sequence_title": None,
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
                                    # FOLDERPATH: {Commodity}/{Intensity|IntensityFrequency}/{District|Pixel}/Baseline/{abs|del}
                                    baseline_intm_folder = f"{commodity}/{intensity_metric_obj.metric}/{scale}/Baseline/{change_metric_obj.p}"
                                    # FILENAME EXAMPLE: Gender_Barley_BBFIB_baseline.tif
                                    baseline_file = f"{cpfx_obj.prefix}_{commodity}_{adap_obj.optcode}_baseline.tif"
                                    adap_index["raster_files"].append({
                                        "year": None,
                                        "adaptation_id": adap_obj.id,
                                        "climate_scenario_id": 1,
                                        "intensity_metric_id": intensity_metric_id,
                                        "change_metric_id": change_metric_id,
                                        "visualization_scale_id": scale_id,
                                        "climate_scenario": "Baseline",
                                        "intensity_metric": intensity_metric_obj.metric,
                                        "change_metric": change_metric_obj.metric,
                                        "visualization_scale": scale,
                                        "source_file": (Path(parent_folder)/ baseline_intm_folder / baseline_file).as_posix(),
                                        "exists": Path.exists(self.data_root_dir / parent_folder / baseline_intm_folder / baseline_file),
                                        "ramp": cpfx_obj.ramp,
                                    })
                            else:
                                scn_ucase = self.ucase(scenario.scenario)
                                scn_lcase = self.lcase(scenario.scenario)
                                for future in [2050, 2080]:
                                    # FOLDERPATH: {Commodity}/{Intensity|IntensityFrequency}/{District|Pixel}/{scn_ucase}/{abs|del}
                                    scenario_intm_folder = f"{commodity}/{intensity_metric_obj.metric}/{scale}/{scn_ucase}/{change_metric_obj.p}"
                                    # FILENAME EXAMPLE: Cultivator_Wheat_ADPTI_2050_ssp245.tif
                                    scenario_file = f"{cpfx_obj.prefix}_{commodity}_{adap_obj.optcode}_{future}_{scn_lcase}.tif"
                                    adap_index["raster_files"].append({
                                        "year": future,
                                        "adaptation_id": adap_obj.id,
                                        "climate_scenario_id": 1,
                                        "intensity_metric_id": intensity_metric_id,
                                        "change_metric_id": change_metric_id,
                                        "visualization_scale_id": scale_id,
                                        "climate_scenario": "Baseline",
                                        "intensity_metric": intensity_metric_obj.metric,
                                        "change_metric": change_metric_obj.metric,
                                        "visualization_scale": scale,
                                        "source_file": (Path(parent_folder)/ scenario_intm_folder / scenario_file).as_posix(),
                                        "exists": Path.exists(self.data_root_dir / parent_folder / scenario_intm_folder / scenario_file),
                                        "ramp": cpfx_obj.ramp,
                                    })
            

            raster_file_index.append(adap_index)

            for i, entry in enumerate(raster_file_index, start=0):
                entry["grid_sequence"] = i

        return {
            "commodity": f"{self.commodity_obj.commodity_group}: {self.commodity_obj.commodity}",
            "raster_grids": raster_file_index[:7]
        }


    def livestock_sequence_zero(self):
        parent_folder = "Hazards-final-struc" # temporarily moving from Impact (Aug 2025)
        commodity = self.commodity_obj.commodity
        risk_obj = self.db.query(LkpRisk).get(25) # HAZARD INDEX
        ramp = self.db.query(LkpRiskColor).filter(LkpRiskColor.suffix == risk_obj.suffix).first().ramp
        raster_file_index = []
        intensity_metric_ids = [row.id for row in self.db.query(LkpIntensityMetric).filter(LkpIntensityMetric.status)]
        change_metric_ids = [row.id for row in self.db.query(LkpChangeMetric).filter(LkpChangeMetric.status)]
        visualization_scale_ids = [row.id for row in self.db.query(LkpVisualizationScale).filter(LkpVisualizationScale.status)]
        # Baseline
        for scale_id in visualization_scale_ids:
            for intensity_metric_id in intensity_metric_ids:
                for change_metric_id in [change_metric_ids[0]]: # no delta for baseline
                    intensity_metric_obj = self.db.query(LkpIntensityMetric).filter(LkpIntensityMetric.id == intensity_metric_id).first()
                    change_metric_obj = self.db.query(LkpChangeMetric).filter(LkpChangeMetric.id == change_metric_id).first()
                    scale_obj = self.db.query(LkpVisualizationScale).filter(LkpVisualizationScale.id == scale_id).first()
                    scale = str(scale_obj.scale).split(" ")[0]
                    # FOLDERPATH: {Commodity}/{Intensity|IntensityFrequency}/{District|Pixel}/Baseline/{abs|del}
                    baseline_intm_folder = f"{commodity}/{intensity_metric_obj.metric}/{scale}/Baseline/{change_metric_obj.p}"
                    # FILENAME EXAMPLE: Baseline_abs_Barley_Agricultural GDP.tif
                    baseline_file = f"Baseline_{change_metric_obj.p}_{commodity}_{risk_obj.suffix}.tif"
                    raster_file_index.append({
                        "year": None,
                        "risk_id": risk_obj.id,
                        "climate_scenario_id": 1,
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
        # Future scenarios
        def append_non_baseline_risk(future, nonbaseline_scenario_id, intensity_metric_id, change_metric_id, scale_id):
            nonbaseline_scenario_obj = self.db.query(LkpClimateScenario).get(nonbaseline_scenario_id)
            scenario = self.ucase(nonbaseline_scenario_obj.scenario)
            intensity_metric_obj = self.db.query(LkpIntensityMetric).filter(LkpIntensityMetric.id == intensity_metric_id).first()
            change_metric_obj = self.db.query(LkpChangeMetric).filter(LkpChangeMetric.id == change_metric_id).first()
            scale_obj = self.db.query(LkpVisualizationScale).filter(LkpVisualizationScale.id == scale_id).first()
            scale = str(scale_obj.scale).split(" ")[0]
            # FOLDERPATH: {Commodity}/{Intensity|IntensityFrequency}/{District|Pixel}/{Scenario}/{abs|del}
            intm_folder = f"{commodity}/{intensity_metric_obj.metric}/{scale}/{scenario}/{change_metric_obj.p}"
            # FILENAME EXAMPLE: 2050_SSP245_abs_Barley_Agricultural GDP.tif
            scenario_file = f"{future}_{scenario}_{change_metric_obj.p}_{commodity}_{risk_obj.suffix}.tif"
            raster_file_index.append({
                "year": future,
                "risk_id": risk_obj.id,
                "climate_scenario_id": nonbaseline_scenario_id,
                "intensity_metric_id": intensity_metric_id,
                "change_metric_id": change_metric_id,
                "visualization_scale_id": scale_id,
                "climate_scenario": f"{nonbaseline_scenario_obj.scenario} | {future}s",
                "intensity_metric": intensity_metric_obj.metric,
                "change_metric": change_metric_obj.metric,
                "visualization_scale": scale,
                "source_file": (Path(parent_folder)/ intm_folder / scenario_file).as_posix(),
                "exists": Path.exists(self.data_root_dir / parent_folder / intm_folder / scenario_file),
                "ramp": ramp
            })
        nonbaseline_scenario_ids = [row.id for row in self.db.query(LkpClimateScenario.id).filter(LkpClimateScenario.scenario != "Baseline").all()]
        for future in [2050, 2080]:
            for scale_id in visualization_scale_ids:
                for nonbaseline_scenario_id in nonbaseline_scenario_ids:
                    for intensity_metric_id in intensity_metric_ids:
                        for change_metric_id in change_metric_ids:
                            append_non_baseline_risk(future, nonbaseline_scenario_id, intensity_metric_id, change_metric_id, scale_id)
        return raster_file_index



    def prep_livestock(self):
        parent_folder = "Adap-final-struc"
        intensity_metric_ids = [row.id for row in self.db.query(LkpIntensityMetric).filter(LkpIntensityMetric.status)]
        change_metric_ids = [row.id for row in self.db.query(LkpChangeMetric).filter(LkpChangeMetric.status)]
        visualization_scale_ids = [row.id for row in self.db.query(LkpVisualizationScale).filter(LkpVisualizationScale.status)]
        commodity = self.commodity_obj.commodity
        all_scenarios = self.db.query(LkpClimateScenario).all()
        raster_file_index = []
        raster_file_index.append({
            "grid_sequence": 0,
            "layer_type": "risk",
            "layer_id": 25,
            "grid_sequence_title": "Hazard Index",
            "raster_files": self.livestock_sequence_zero()
        })
        master_queryset = self.db.query(LkpAdapt).filter(
            (LkpAdapt.commodity_type_id == 2) &
            ((LkpAdapt.commodity_id == self.commodity_id) | (LkpAdapt.commodity_id == None))
        )
        all_adaptations = master_queryset.limit(6).all()
        for grid_sequence, adap_obj in enumerate(all_adaptations):
            lsufx_obj = self.db.query(LkpAdaptLivestockColor).filter(LkpAdaptLivestockColor.suffix == adap_obj.optcode).first()
            adap_index = {
                "grid_sequence": grid_sequence + 1,
                "layer_type": "adaptation",
                "layer_id": adap_obj.id,
                "grid_sequence_title": None,
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
                                    # FOLDERPATH: {Commodity}/{Intensity|IntensityFrequency}/{District|Pixel}/Baseline/{abs|del}
                                    baseline_intm_folder = f"{commodity}/{intensity_metric_obj.metric}/{scale}/Baseline/{change_metric_obj.p}"
                                    # FILENAME EXAMPLE: Baseline_abs_Chicken_Vaccination.tif
                                    baseline_file = f"Baseline_{change_metric_obj.p}_{commodity}_{lsufx_obj.suffix}.tif"
                                    adap_index["raster_files"].append({
                                        "year": None,
                                        "adaptation_id": lsufx_obj.id,
                                        "climate_scenario_id": 1,
                                        "intensity_metric_id": intensity_metric_id,
                                        "change_metric_id": change_metric_id,
                                        "visualization_scale_id": scale_id,
                                        "climate_scenario": "Baseline",
                                        "intensity_metric": intensity_metric_obj.metric,
                                        "change_metric": change_metric_obj.metric,
                                        "source_file": (Path(parent_folder)/ baseline_intm_folder / baseline_file).as_posix(),
                                        "exists": Path.exists(self.data_root_dir / parent_folder / baseline_intm_folder / baseline_file),
                                        "ramp": lsufx_obj.ramp,
                                    })
                            else:
                                scn_ucase = self.ucase(scenario.scenario)
                                scn_lcase = self.lcase(scenario.scenario)
                                for future in [2050, 2080]:
                                    # FOLDERPATH: {Commodity}/{Intensity|IntensityFrequency}/{District|Pixel}/{scn_ucase}/{abs|del}
                                    scenario_intm_folder = f"{commodity}/{intensity_metric_obj.metric}/{scale}/{scn_ucase}/{change_metric_obj.p}"
                                    # EXAMPLE FILENAME: 2050_SSP245_abs_Chicken_Adoption of climate resilient breeds.tif
                                    scenario_file = f"{future}_{scn_ucase}_{change_metric_obj.p}_{commodity}_{lsufx_obj.suffix}.tif"
                                    adap_index["raster_files"].append({
                                        "year": future,
                                        "adaptation_id": lsufx_obj.id,
                                        "climate_scenario_id": 1,
                                        "intensity_metric_id": intensity_metric_id,
                                        "change_metric_id": change_metric_id,
                                        "visualization_scale_id": scale_id,
                                        "climate_scenario": "Baseline",
                                        "intensity_metric": intensity_metric_obj.metric,
                                        "change_metric": change_metric_obj.metric,
                                        "visualization_scale": scale,
                                        "source_file": (Path(parent_folder)/ scenario_intm_folder / scenario_file).as_posix(),
                                        "exists": Path.exists(self.data_root_dir / parent_folder / scenario_intm_folder / scenario_file),
                                        "ramp": lsufx_obj.ramp,
                                    })
            raster_file_index.append(adap_index)

        return {
            "commodity": f"{self.commodity_obj.commodity_group}: {self.commodity_obj.commodity}",
            "raster_grids": raster_file_index
        }
                        


    def execute(self):
        if self.commodity_obj.type.type == "Crops":
            if not self.adaptation_croptab_id:
                raise LayerDataException("Please choose an appropriate adaptation indicator for the chosen crop")
            return self.prep_crops()
        if self.commodity_obj.type.type == "Livestock":
            return self.prep_livestock()
