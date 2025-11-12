from settings.database import get_db
from sqlalchemy.orm import Session
from fastapi import APIRouter, Request, Depends
from fastapi.responses import StreamingResponse
from .utils import GeoProc, TIFPicker, \
    RiskData, ImpactData, AdaptationData, \
    GlanceHazards, GlanceAdaptations
from api_layers.exceptions import LayerDataException
from fastapi.concurrency import run_in_threadpool


class LayerRouter:
    def __init__(self):
        self.router = APIRouter()
        self.router.add_api_route("/tif_picker", self.tif_picker, methods=["POST"])
        self.router.add_api_route("/geojson", self.geojson, methods=["POST"])
        self.router.add_api_route("/geojson/districts_c", self.geojson_districts_c, methods=["POST"])
        self.router.add_api_route("/geotiff", self.geotiff, methods=["POST"])
        self.router.add_api_route("/geotiff/raw", self.geotiff_raw, methods=["POST"])
        self.router.add_api_route("/legend", self.legend, methods=["POST"])
        self.router.add_api_route("/table", self.table, methods=["POST"])
        self.router.add_api_route("/hazards_glance", self.hazards_glance, methods=["POST"])
        self.router.add_api_route("/adaptations_glance", self.adaptations_glance, methods=["POST"])
        

    async def tif_picker(self, request: Request, db: Session=Depends(get_db)):
        request_body = await request.json()
        data = TIFPicker(
            db = db,
            layer_type = request_body.get("layer_type"),
            # common options - left pane
            analysis_scope_id = request_body.get("analysis_scope_id"),
            visualization_scale_id = request_body.get("visualization_scale_id"),
            commodity_id = request_body.get("commodity_id"),
            data_source_id = request_body.get("data_source_id"),
            # specific options
            risk_id = request_body.get("risk_id"),
            impact_id = request_body.get("impact_id"),
            adaptation_croptab_id = request_body.get("adaptation_croptab_id"),
            adaptation_id = request_body.get("adaptation_id")
        ).execute()
        return {"success": 1, "data": data}
    


    async def geojson(self, request: Request, db: Session = Depends(get_db)):
        request_body = await request.json()
        proc = GeoProc(
            db=db,
            admin_level=request_body.get("admin_level"),
            admin_level_id=request_body.get("admin_level_id"),
        )
        data = proc.prep_geojson()
        return {"success": 1, "data": data}
    

    async def geojson_districts_c(self, request: Request, db: Session = Depends(get_db)):
        request_body = await request.json()
        proc = GeoProc(
            db=db,
            admin_level=request_body.get("admin_level"),
            admin_level_id=request_body.get("admin_level_id"),
        )
        data = proc.prep_geojson_districts_c()
        return {"success": 1, "data": data}


    async def geotiff(self, request: Request, db: Session = Depends(get_db)):
        request_body = await request.json()
        proc = GeoProc(
            db=db,
            admin_level=request_body.get("admin_level"),
            admin_level_id=request_body.get("admin_level_id"),
            source_file=request_body.get("source_file"),
            color_ramp=request_body.get("color_ramp"),
        )
        # Offload CPU-heavy raster processing to threadpool - in-memory BytesIO
        memfile = await run_in_threadpool(proc.prep_geotiff)
        selected_region = "_".join(proc.get_region())
        tif_file_name = str(request_body.get("source_file")).split("/")[-1]
        download_filename = f"{selected_region}_{tif_file_name}".replace(" ", "_")
        return StreamingResponse(
            memfile,  # stream directly
            media_type="image/tiff",
            headers={
                "Content-Disposition": f'inline; filename="{download_filename}.tif"',
                "Access-Control-Expose-Headers": "Content-Disposition",
                "X-Accel-Buffering": "no"
            },
        )

    async def geotiff_raw(self, request: Request, db: Session = Depends(get_db)):
        request_body = await request.json()
        proc = GeoProc(
            db=db,
            admin_level=request_body.get("admin_level"),
            admin_level_id=request_body.get("admin_level_id"),
            source_file=request_body.get("source_file"),
        )
        memfile = await run_in_threadpool(proc.prep_raw_geotiff)
        selected_region = "_".join(proc.get_region())
        tif_file_name = str(request_body.get("source_file")).split("/")[-1]
        download_filename = f"{selected_region}_{tif_file_name}_Raw".replace(" ", "_")
        return StreamingResponse(
            memfile,
            media_type="image/tiff",
            headers={
                "Content-Disposition": f'inline; filename="{download_filename}.tif"',
                "Access-Control-Expose-Headers": "Content-Disposition",
                "X-Accel-Buffering": "no"
            },
        )

    async def legend(self, request: Request, db: Session=Depends(get_db)):
        request_body = await request.json()
        layer_type = request_body.get("layer_type")
        if layer_type not in ["risk", "impact", "adaptation"]:
            raise LayerDataException("Please choose an appropriate layer")
        data_class_index = {
            "risk": RiskData,
            "impact": ImpactData,
            "adaptation": AdaptationData,
        }
        LayerData = data_class_index[layer_type]
        data = LayerData(
            db=db,
            adaptation_croptab_id=request_body.get("adaptation_croptab_id"), # Only when crop commodity and layer_type="adaptation"
            commodity_id=request_body.get("commodity_id"),
            intensity_metric_id=request_body.get("intensity_metric_id"),
            visualization_scale_id=request_body.get("visualization_scale_id"),
            analysis_scope_id = request_body.get("analysis_scope_id"),
            climate_scenario_id=request_body.get("climate_scenario_id"),
            year=request_body.get("year"),
            change_metric_id=request_body.get("change_metric_id"),
            country_id=request_body.get("country_id"),
            state_id=request_body.get("state_id"),
            district_id=request_body.get("district_id"),
            layer_id=request_body.get("layer_id"),
        ).get_legend()
        return {"success": 1, "data": data}
    

    async def table(self, request: Request, db: Session=Depends(get_db)):
        request_body = await request.json()
        layer_type = request_body.get("layer_type")
        if layer_type not in ["risk", "impact", "adaptation"]:
            raise LayerDataException("Please choose an appropriate layer")
        data_class_index = {
            "risk": RiskData,
            "impact": ImpactData,
            "adaptation": AdaptationData,
        }
        LayerData = data_class_index[layer_type]
        layer_data = LayerData(
            db=db,
            adaptation_croptab_id=request_body.get("adaptation_croptab_id"),  # Only when crop commodity and layer_type="adaptation"
            commodity_id=request_body.get("commodity_id"),
            intensity_metric_id=request_body.get("intensity_metric_id"),
            visualization_scale_id=request_body.get("visualization_scale_id"),
            analysis_scope_id = request_body.get("analysis_scope_id"),
            climate_scenario_id=request_body.get("climate_scenario_id"),
            year=request_body.get("year"),
            change_metric_id=request_body.get("change_metric_id"),
            country_id=request_body.get("country_id"),
            state_id=request_body.get("state_id"),
            district_id=request_body.get("district_id"),
            layer_id=request_body.get("layer_id"),
        )
        memfile_obj = layer_data.get_table()
        memfile = memfile_obj.get("memfile")
        filename = memfile_obj.get("filename")
        return StreamingResponse(
            memfile,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"inline; filename={filename}.xlsx",
                "Access-Control-Expose-Headers": "Content-Disposition",
                "X-Accel-Buffering": "no"
            }
        )
    

    async def hazards_glance(self, request: Request, db: Session=Depends(get_db)):
        request_body = await request.json()
        data = GlanceHazards(
            db=db,
            commodity_id=request_body.get("commodity_id"),
        ).execute()
        return {"success": 1, "data": data}
    

    async def adaptations_glance(self, request: Request, db: Session=Depends(get_db)):
        request_body = await request.json()
        data = GlanceAdaptations(
            db=db,
            commodity_id=request_body.get("commodity_id"),
            adaptation_croptab_id=request_body.get("adaptation_croptab_id"),
        ).execute()
        return {"success": 1, "data": data}
    


layer_router = LayerRouter().router
