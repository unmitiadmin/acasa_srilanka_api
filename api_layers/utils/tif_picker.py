import re
from pathlib import Path
from settings import env
from api_lookups.models import (
    LkpAnalysisScope, LkpVisualizationScale, LkpCommodity, LkpDataSource, LkpClimateScenario,
    LkpImpact, LkpImpactColor, LkpRisk, LkpRiskColor, 
    LkpAdaptCropColor, LkpAdaptLivestockColor, LkpAdapt,
    LkpIntensityMetric, LkpChangeMetric # Currently specific only for hazards
)
from ..exceptions import LayerDataException
import inflect

class TIFPicker:
    def __init__(self, **kwargs):
        self.data_root_dir = Path(env.get("DATA_ROOT_DIR"))
        self.valid_layer_types = ["commodity", "risk", "impact", "adaptation"]
        self.layer_type = kwargs.get("layer_type")
        # common options - left pane
        self.analysis_scope_id = kwargs.get("analysis_scope_id")
        self.visualization_scale_id = kwargs.get("visualization_scale_id")
        self.commodity_id = kwargs.get("commodity_id")
        self.data_source_id = kwargs.get("data_source_id")
        # specific options (based on commodity)
        self.risk_id = kwargs.get("risk_id")
        self.impact_id = kwargs.get("impact_id")
        self.adaptation_croptab_id = kwargs.get("adaptation_croptab_id") # only for crops
        self.adaptation_id = kwargs.get("adaptation_id")
        # Database-connector object
        self.db = kwargs.get("db")
        # Index objects - common options
        self.commodity_obj = self.db.query(LkpCommodity).filter(LkpCommodity.id == self.commodity_id).first()
        self.data_source_obj = self.db.query(LkpDataSource).filter(LkpDataSource.id == self.data_source_id).first()
        self.analysis_scope_obj = self.db.query(LkpAnalysisScope).filter(LkpAnalysisScope.id == self.analysis_scope_id).first()
        self.visualization_scale_obj = self.db.query(LkpVisualizationScale).filter(LkpVisualizationScale.id == self.visualization_scale_id).first()        
        # index objects - specific options
        self.risk_obj = None
        self.impact_obj = self.db.query(LkpImpact).filter(LkpImpact.id == self.impact_id).first()
        self.lcase = lambda s: re.sub(r'[^a-zA-Z0-9]', '', s).lower()
        self.ucase = lambda s: re.sub(r'[^a-zA-Z0-9]', '', s).upper()
        self.p = inflect.engine()
        self.irregulars = {
            "Indices": "Index",
        }
        self.singular = lambda s: self.irregulars.get(s, self.p.singular_noun(s) or s)
 

    
    def pick_commodity_raster(self):
        # Currently has only baseline (Jul 2025)
        # public> Crop Masks > Extent > {activeCrop}.tif
        parent_folder = "Crop Masks/Extent"
        common_color_ramp = ["#FFFFCC", "#FFE680", "#FFCC33", "#FF9933", "#CC6600"] # <---- change this if commodity specific ramp
        return {
            "level": self.visualization_scale_obj.scale,
            "commodity": f"{self.commodity_obj.commodity_group}: {self.commodity_obj.commodity}",
            "scenario": "Baseline",
            "model": self.data_source_obj.source,
            "mask": "commodity",
            "raster_files": [{
                "climate_scenario_id": 1,
                "climate_scenario": "Baseline",
                "source_file": (Path(parent_folder) / f"{self.commodity_obj.commodity}.tif").as_posix(),
                "exists": Path.exists( self.data_root_dir / parent_folder / f"{self.commodity_obj.commodity}.tif"),
                "ramp": common_color_ramp,
            }]
        }
    

    def pick_risk_raster(self):
        parent_folder = "Hazards-final-struc" # temporarily moving from Hazards (Aug 2025)
        commodity = (
            "Regional" if self.analysis_scope_id == 2
            else self.commodity_obj.commodity
        )
        scale = str(self.visualization_scale_obj.scale).split(" ")[0]
        risk_obj = self.db.query(LkpRisk).filter(LkpRisk.id == self.risk_id).first()
        ramp = self.db.query(LkpRiskColor).filter(LkpRiskColor.suffix == risk_obj.suffix).first().ramp
        raster_file_index = []
        intensity_metric_ids = [row.id for row in self.db.query(LkpIntensityMetric).filter(LkpIntensityMetric.status)]
        change_metric_ids = [row.id for row in self.db.query(LkpChangeMetric).filter(LkpChangeMetric.status)]
        # Baseline
        for intensity_metric_id in intensity_metric_ids:
            for change_metric_id in [change_metric_ids[0]]: # no delta for baseline
                intensity_metric_obj = self.db.query(LkpIntensityMetric).filter(LkpIntensityMetric.id == intensity_metric_id).first()
                change_metric_obj = self.db.query(LkpChangeMetric).filter(LkpChangeMetric.id == change_metric_id).first()
                # FOLDERPATH: {Commodity}/{Intensity|IntensityFrequency}/{District|Pixel}/Baseline/{abs|del}
                baseline_intm_folder = f"{commodity}/{intensity_metric_obj.metric}/{scale}/Baseline/{change_metric_obj.p}"
                # FILENAME EXAMPLE: Baseline_abs_Barley_Agricultural GDP.tif
                baseline_file = f"Baseline_{change_metric_obj.p}_{commodity}_{risk_obj.suffix}.tif"
                raster_file_index.append({
                    "layer_type": "risk",
                    "layer_id": risk_obj.id,
                    "year": None,
                    "climate_scenario_id": 1,
                    "intensity_metric_id": intensity_metric_id,
                    "change_metric_id": change_metric_id,
                    "climate_scenario": "Baseline",
                    "intensity_metric": intensity_metric_obj.metric,
                    "change_metric": change_metric_obj.metric,
                    "source_file": (Path(parent_folder)/ baseline_intm_folder / baseline_file).as_posix(),
                    "exists": Path.exists(self.data_root_dir / parent_folder / baseline_intm_folder / baseline_file),
                    "ramp": ramp,
                })
        # Future scenarios
        ipcc = risk_obj.ipcc.ipcc
        def append_non_baseline_risk(future, nonbaseline_scenario_id, intensity_metric_id, change_metric_id):
            delta_color_ramp = (
                ["#800000", "#FF6666", "#F5F5DC", "#87CEFA", "#4682B4"] 
                if ipcc == "Climatology" and risk_obj.suffix == "Seasonal Rainfall"
                else ["#4682B4", "#87CEFA", "#E7E6A8", "#FF6666", "#800000"]
            )
            nonbaseline_scenario_obj = self.db.query(LkpClimateScenario).get(nonbaseline_scenario_id)
            scenario = self.ucase(nonbaseline_scenario_obj.scenario)
            intensity_metric_obj = self.db.query(LkpIntensityMetric).filter(LkpIntensityMetric.id == intensity_metric_id).first()
            change_metric_obj = self.db.query(LkpChangeMetric).filter(LkpChangeMetric.id == change_metric_id).first()
            # FOLDERPATH: {Commodity}/{Intensity|IntensityFrequency}/{District|Pixel}/{Scenario}/{abs|del}
            intm_folder = f"{commodity}/{intensity_metric_obj.metric}/{scale}/{scenario}/{change_metric_obj.p}"
            # FILENAME EXAMPLE: 2050_SSP245_abs_Barley_Agricultural GDP.tif
            scenario_file = f"{future}_{scenario}_{change_metric_obj.p}_{commodity}_{risk_obj.suffix}.tif"
            raster_file_index.append({
                "layer_type": "risk",
                "layer_id": risk_obj.id,
                "year": future,
                "climate_scenario_id": nonbaseline_scenario_id,
                "intensity_metric_id": intensity_metric_id,
                "change_metric_id": change_metric_id,
                "climate_scenario": f"{nonbaseline_scenario_obj.scenario} | {future}s",
                "intensity_metric": intensity_metric_obj.metric,
                "change_metric": change_metric_obj.metric,
                "source_file": (Path(parent_folder)/ intm_folder / scenario_file).as_posix(),
                "exists": Path.exists(self.data_root_dir / parent_folder / intm_folder / scenario_file),
                "ramp": ramp if change_metric_id == 1 else delta_color_ramp
            })
        nonbaseline_scenario_ids = [row.id for row in self.db.query(LkpClimateScenario.id).filter(LkpClimateScenario.scenario != "Baseline").all()]
        for future in [2050, 2080]:
            for nonbaseline_scenario_id in nonbaseline_scenario_ids:
                for intensity_metric_id in intensity_metric_ids:
                    for change_metric_id in change_metric_ids:
                        append_non_baseline_risk(future, nonbaseline_scenario_id, intensity_metric_id, change_metric_id)
        return {
            "level": self.visualization_scale_obj.scale,
            "commodity": (
                "Regional Analysis" if self.analysis_scope_id == 2
                else f"{self.commodity_obj.commodity_group}: {commodity}"
            ),
            "mask": (
                risk_obj.suffix if self.analysis_scope_id == 2
                else f"{self.singular(ipcc)}: {risk_obj.risk}"
            ),
            "default_change_metric_id": 1,
            "default_intensity_metric_id": 2,
            "toggle_change_metric": ipcc in ["Climatology", "Hazards"],
            "toggle_intensity_metric": ipcc in ["Hazards"],
            "raster_files": raster_file_index
        }


    def pick_impact_raster(self):
        parent_folder = "Impact-final-struc" # temporarily moving from Impact (Aug 2025)
        commodity = self.commodity_obj.commodity
        scale = str(self.visualization_scale_obj.scale).split(" ")[0]
        impact_obj = self.db.query(LkpImpact).filter(LkpImpact.id == self.impact_id).first()
        # ramp will be scenario specific
        raster_file_index = []
        intensity_metric_ids = [row.id for row in self.db.query(LkpIntensityMetric).filter(LkpIntensityMetric.status)]
        change_metric_ids = [row.id for row in self.db.query(LkpChangeMetric).filter(LkpChangeMetric.status)]
        # Baseline
        baseline_ramp = self.db.query(LkpImpactColor).filter(LkpImpactColor.suffix == f"{impact_obj.optcode}_baseline").first().ramp
        for intensity_metric_id in intensity_metric_ids:
            for change_metric_id in [change_metric_ids[0]]: # no delta for baseline
                intensity_metric_obj = self.db.query(LkpIntensityMetric).filter(LkpIntensityMetric.id == intensity_metric_id).first()
                change_metric_obj = self.db.query(LkpChangeMetric).filter(LkpChangeMetric.id == change_metric_id).first()
                # FOLDERPATH: {Commodity}/{Intensity|IntensityFrequency}/{District|Pixel}/Baseline/{abs|del}
                baseline_intm_folder = f"{commodity}/{intensity_metric_obj.metric}/{scale}/Baseline/{change_metric_obj.p}"
                # FILENAME EXAMPLE: Baseline_abs_Maize_CV.tif
                baseline_file = f"Baseline_{change_metric_obj.p}_{commodity}_{impact_obj.optcode}.tif"
                raster_file_index.append({
                    "layer_type": "impact",
                    "layer_id": impact_obj.id,
                    "year": None,
                    "climate_scenario_id": 1,
                    "intensity_metric_id": intensity_metric_id,
                    "change_metric_id": change_metric_id,
                    "climate_scenario": "Baseline",
                    "intensity_metric": intensity_metric_obj.metric,
                    "change_metric": change_metric_obj.metric,
                    "source_file": (Path(parent_folder)/ baseline_intm_folder / baseline_file).as_posix(),
                    "exists": Path.exists(self.data_root_dir / parent_folder / baseline_intm_folder / baseline_file),
                    "ramp": baseline_ramp,
                })
        # Future scenarios
        def append_non_baseline_impact(future, nonbaseline_scenario_id, intensity_metric_id, change_metric_id):
            nonbaseline_scenario_obj = self.db.query(LkpClimateScenario).get(nonbaseline_scenario_id)
            scenario_ucase = self.ucase(nonbaseline_scenario_obj.scenario)
            scenario_lcase = self.lcase(nonbaseline_scenario_obj.scenario)
            scn_ramp = self.db.query(LkpImpactColor).filter(LkpImpactColor.suffix == f"{impact_obj.optcode}_{scenario_lcase}").first().ramp
            intensity_metric_obj = self.db.query(LkpIntensityMetric).filter(LkpIntensityMetric.id == intensity_metric_id).first()
            change_metric_obj = self.db.query(LkpChangeMetric).filter(LkpChangeMetric.id == change_metric_id).first()
            # FOLDERPATH: {Commodity}/{Intensity|IntensityFrequency}/{District|Pixel}/{scenario_ucase}/{abs|del}
            intm_folder = f"{commodity}/{intensity_metric_obj.metric}/{scale}/{scenario_ucase}/{change_metric_obj.p}"
            # FILENAME EXAMPLE: Baseline_abs_Maize_CV.tif
            scenario_file = f"{future}_{scenario_ucase}_{change_metric_obj.p}_{commodity}_{impact_obj.optcode}.tif"
            raster_file_index.append({
                "layer_type": "impact",
                "layer_id": impact_obj.id,
                "year": future,
                "climate_scenario_id": nonbaseline_scenario_id,
                "intensity_metric_id": intensity_metric_id,
                "change_metric_id": change_metric_id,
                "climate_scenario": f"{nonbaseline_scenario_obj.scenario} | {future}s",
                "intensity_metric": intensity_metric_obj.metric,
                "change_metric": change_metric_obj.metric,
                "source_file": (Path(parent_folder)/ intm_folder / scenario_file).as_posix(),
                "exists": Path.exists(self.data_root_dir / parent_folder / intm_folder / scenario_file),
                "ramp": scn_ramp
            })
        nonbaseline_scenario_ids = [row.id for row in self.db.query(LkpClimateScenario.id).filter(LkpClimateScenario.scenario != "Baseline").all()]
        for future in [2050, 2080]:
            for nonbaseline_scenario_id in nonbaseline_scenario_ids:
                for intensity_metric_id in intensity_metric_ids:
                    for change_metric_id in change_metric_ids:
                        append_non_baseline_impact(future, nonbaseline_scenario_id, intensity_metric_id, change_metric_id)
        return {
            "level": self.visualization_scale_obj.scale,
            "commodity": f"{self.commodity_obj.commodity_group}: {commodity}",
            "mask": f"Impact: {impact_obj.impact}",
            "default_change_metric_id": 1,
            "default_intensity_metric_id": 2,
            "toggle_change_metric": False,
            "toggle_intensity_metric": False,
            "raster_files": raster_file_index
        }



    def pick_adaptation_raster(self):
        commodity_type_dict = {
            "Crops": self.pick_adapt_crop_raster,
            "Livestock": self.pick_adapt_livestock_raster,
        }
        return commodity_type_dict[self.commodity_obj.type.type]()
    

    def pick_adapt_crop_raster(self):
        parent_folder = "Adap-final-struc" # temporarily moving from Adap (Aug 2025)
        commodity = self.commodity_obj.commodity
        scale = str(self.visualization_scale_obj.scale).split(" ")[0]
        cpfx_obj = self.db.query(LkpAdaptCropColor).get(self.adaptation_croptab_id)
        adap_obj = self.db.query(LkpAdapt).get(self.adaptation_id)
        raster_file_index = []
        intensity_metric_ids = [row.id for row in self.db.query(LkpIntensityMetric).filter(LkpIntensityMetric.status)]
        change_metric_ids = [row.id for row in self.db.query(LkpChangeMetric).filter(LkpChangeMetric.status)]
        # Baseline
        for intensity_metric_id in intensity_metric_ids:
            for change_metric_id in [change_metric_ids[0]]: # no delta for baseline
                intensity_metric_obj = self.db.query(LkpIntensityMetric).filter(LkpIntensityMetric.id == intensity_metric_id).first()
                change_metric_obj = self.db.query(LkpChangeMetric).filter(LkpChangeMetric.id == change_metric_id).first()
                # FOLDERPATH: {Commodity}/{Intensity|IntensityFrequency}/{District|Pixel}/Baseline/{abs|del}
                baseline_intm_folder = f"{commodity}/{intensity_metric_obj.metric}/{scale}/Baseline/{change_metric_obj.p}"
                if cpfx_obj.tab_name == "Adaptation Benefits":
                    impact_parent_folder = "Impact-final-struc"
                    # FILENAME EXAMPLE: Baseline_abs_Maize_Productivity.tif
                    baseline_file = f"Baseline_{change_metric_obj.p}_{commodity}_Productivity.tif"
                    raster_file_index.append({
                        "layer_type": "impact",
                        "layer_id": 1,
                        "year": None,
                        "climate_scenario_id": 1,
                        "intensity_metric_id": intensity_metric_id,
                        "change_metric_id": change_metric_id,
                        "climate_scenario": "Baseline",
                        "intensity_metric": intensity_metric_obj.metric,
                        "change_metric": change_metric_obj.metric,
                        "source_file": (Path(impact_parent_folder)/ baseline_intm_folder / baseline_file).as_posix(),
                        "exists": Path.exists(self.data_root_dir / impact_parent_folder / baseline_intm_folder / baseline_file),
                        "ramp": self.db.query(LkpImpactColor).filter(LkpImpactColor.suffix == "Productivity_baseline").first().ramp,
                    })
                else:
                    # FILENAME EXAMPLE: Gender_Barley_BBFIB_baseline.tif
                    baseline_file = f"{cpfx_obj.prefix}_{commodity}_{adap_obj.optcode}_baseline.tif"
                    raster_file_index.append({
                        "layer_type": "adaptation",
                        "layer_id": adap_obj.id,
                        "year": None,
                        "climate_scenario_id": 1,
                        "intensity_metric_id": intensity_metric_id,
                        "change_metric_id": change_metric_id,
                        "climate_scenario": "Baseline",
                        "intensity_metric": intensity_metric_obj.metric,
                        "change_metric": change_metric_obj.metric,
                        "source_file": (Path(parent_folder)/ baseline_intm_folder / baseline_file).as_posix(),
                        "exists": Path.exists(self.data_root_dir / parent_folder / baseline_intm_folder / baseline_file),
                        "ramp": cpfx_obj.ramp,
                    })
        # Future scenarios
        def append_non_baseline_adaptations(future, nonbaseline_scenario_id, intensity_metric_id, change_metric_id):
            nonbaseline_scenario_obj = self.db.query(LkpClimateScenario).get(nonbaseline_scenario_id)
            scenario_ucase = self.ucase(nonbaseline_scenario_obj.scenario)
            scenario_lcase = self.lcase(nonbaseline_scenario_obj.scenario)
            intensity_metric_obj = self.db.query(LkpIntensityMetric).filter(LkpIntensityMetric.id == intensity_metric_id).first()
            change_metric_obj = self.db.query(LkpChangeMetric).filter(LkpChangeMetric.id == change_metric_id).first()
            # FOLDERPATH: {Commodity}/{Intensity|IntensityFrequency}/{District|Pixel}/{scenario_ucase}/{abs|del}
            intm_folder = f"{commodity}/{intensity_metric_obj.metric}/{scale}/{scenario_ucase}/{change_metric_obj.p}"
            # FILENAME EXAMPLE: Cultivator_Wheat_ADPTI_2050_ssp245.tif
            scenario_file = f"{cpfx_obj.prefix}_{commodity}_{adap_obj.optcode}_{future}_{scenario_lcase}.tif"
            raster_file_index.append({
                "layer_type": "adaptation",
                "layer_id": adap_obj.id,
                "year": future,
                "climate_scenario_id": nonbaseline_scenario_id,
                "intensity_metric_id": intensity_metric_id,
                "change_metric_id": change_metric_id,
                "climate_scenario": f"{nonbaseline_scenario_obj.scenario} | {future}s",
                "intensity_metric": intensity_metric_obj.metric,
                "change_metric": change_metric_obj.metric,
                "source_file": (Path(parent_folder)/ intm_folder / scenario_file).as_posix(),
                "exists": Path.exists(self.data_root_dir / parent_folder / intm_folder / scenario_file),
                "ramp": cpfx_obj.ramp,
            })
        nonbaseline_scenario_ids = [row.id for row in self.db.query(LkpClimateScenario.id).filter(LkpClimateScenario.scenario != "Baseline").all()]
        for future in [2050, 2080]:
            for nonbaseline_scenario_id in nonbaseline_scenario_ids:
                for intensity_metric_id in intensity_metric_ids:
                    for change_metric_id in change_metric_ids:
                        append_non_baseline_adaptations(future, nonbaseline_scenario_id, intensity_metric_id, change_metric_id)  
        return {
            "level": self.visualization_scale_obj.scale,
            "commodity": f"{self.commodity_obj.commodity_group}: {commodity}",
            "mask": f"{cpfx_obj.tab_name} - {adap_obj.adaptation}",
            "default_change_metric_id": 1,
            "default_intensity_metric_id": 2,
            "toggle_change_metric": False,
            "toggle_intensity_metric": False,
            "raster_files": raster_file_index
        }



    def pick_adapt_livestock_raster(self):
        parent_folder = "Adap-final-struc" # temporarily moving from Adap (Aug 2025)
        commodity = self.commodity_obj.commodity
        scale = str(self.visualization_scale_obj.scale).split(" ")[0]
        adap_obj = self.db.query(LkpAdapt).get(self.adaptation_id)
        lsufx_obj = self.db.query(LkpAdaptLivestockColor).filter(LkpAdaptLivestockColor.suffix == adap_obj.optcode).first()
        raster_file_index = []
        intensity_metric_ids = [row.id for row in self.db.query(LkpIntensityMetric).filter(LkpIntensityMetric.status)]
        change_metric_ids = [row.id for row in self.db.query(LkpChangeMetric).filter(LkpChangeMetric.status)]
        # Baseline
        for intensity_metric_id in intensity_metric_ids:
            for change_metric_id in [change_metric_ids[0]]: # no delta for baseline
                intensity_metric_obj = self.db.query(LkpIntensityMetric).filter(LkpIntensityMetric.id == intensity_metric_id).first()
                change_metric_obj = self.db.query(LkpChangeMetric).filter(LkpChangeMetric.id == change_metric_id).first()
                # FOLDERPATH: {Commodity}/{Intensity|IntensityFrequency}/{District|Pixel}/Baseline/{abs|del}
                baseline_intm_folder = f"{commodity}/{intensity_metric_obj.metric}/{scale}/Baseline/{change_metric_obj.p}"
                # FILENAME EXAMPLE: Baseline_abs_Chicken_Vaccination.tif
                baseline_file = f"Baseline_{change_metric_obj.p}_{commodity}_{lsufx_obj.suffix}.tif"
                raster_file_index.append({
                    "layer_type": "adaptation",
                    "layer_id": adap_obj.id,
                    "year": None,
                    "climate_scenario_id": 1,
                    "intensity_metric_id": intensity_metric_id,
                    "change_metric_id": change_metric_id,
                    "climate_scenario": "Baseline",
                    "intensity_metric": intensity_metric_obj.metric,
                    "change_metric": change_metric_obj.metric,
                    "source_file": (Path(parent_folder)/ baseline_intm_folder / baseline_file).as_posix(),
                    "exists": Path.exists(self.data_root_dir / parent_folder / baseline_intm_folder / baseline_file),
                    "ramp": lsufx_obj.ramp,
                })
        # Future scenarios
        def append_non_baseline_adaptations(future, nonbaseline_scenario_id, intensity_metric_id, change_metric_id):
            nonbaseline_scenario_obj = self.db.query(LkpClimateScenario).get(nonbaseline_scenario_id)
            scenario_ucase = self.ucase(nonbaseline_scenario_obj.scenario)
            intensity_metric_obj = self.db.query(LkpIntensityMetric).filter(LkpIntensityMetric.id == intensity_metric_id).first()
            change_metric_obj = self.db.query(LkpChangeMetric).filter(LkpChangeMetric.id == change_metric_id).first()
            # FOLDERPATH: {Commodity}/{Intensity|IntensityFrequency}/{District|Pixel}/{scenario_ucase}/{abs|del}
            intm_folder = f"{commodity}/{intensity_metric_obj.metric}/{scale}/{scenario_ucase}/{change_metric_obj.p}"
            # EXAMPLE FILENAME: 2050_SSP245_abs_Chicken_Adoption of climate resilient breeds.tif
            scenario_file = f"{future}_{scenario_ucase}_{change_metric_obj.p}_{commodity}_{lsufx_obj.suffix}.tif"
            raster_file_index.append({
                "layer_type": "adaptation",
                "layer_id": adap_obj.id,
                "year": future,
                "climate_scenario_id": nonbaseline_scenario_id,
                "intensity_metric_id": intensity_metric_id,
                "change_metric_id": change_metric_id,
                "climate_scenario": f"{nonbaseline_scenario_obj.scenario} | {future}s",
                "intensity_metric": intensity_metric_obj.metric,
                "change_metric": change_metric_obj.metric,
                "source_file": (Path(parent_folder)/ intm_folder / scenario_file).as_posix(),
                "exists": Path.exists(self.data_root_dir / parent_folder / intm_folder / scenario_file),
                "ramp": lsufx_obj.ramp,
            })
        nonbaseline_scenario_ids = [row.id for row in self.db.query(LkpClimateScenario.id).filter(LkpClimateScenario.scenario != "Baseline").all()]
        for future in [2050, 2080]:
            for nonbaseline_scenario_id in nonbaseline_scenario_ids:
                for intensity_metric_id in intensity_metric_ids:
                    for change_metric_id in change_metric_ids:
                        append_non_baseline_adaptations(future, nonbaseline_scenario_id, intensity_metric_id, change_metric_id)
        return {
            "level": self.visualization_scale_obj.scale,
            "commodity": f"{self.commodity_obj.commodity_group}: {commodity}",
            "mask": f"{adap_obj.adaptation}",
            "default_change_metric_id": 1,
            "default_intensity_metric_id": 2,
            "toggle_change_metric": False,
            "toggle_intensity_metric": False,
            "raster_files": raster_file_index
        }


    def execute(self):
        if self.layer_type not in self.valid_layer_types:
            raise LayerDataException("Please ensure to choose one of Commodities/Risk/Impact/Adaptation options for viewing")
        if (self.layer_type == "adaptation"and 
            self.commodity_obj.type.type == "Crops" and 
            not self.adaptation_croptab_id):
            raise LayerDataException("Please choose an appropriate adaptation indicator for the chosen crop")
        picker = {
            "commodity": self.pick_commodity_raster,
            "risk": self.pick_risk_raster,
            "impact": self.pick_impact_raster,
            "adaptation": self.pick_adaptation_raster,
        }
        return picker[self.layer_type]()
        

