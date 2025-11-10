from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from settings.database import engine
from api_lookups.routes import lkp_location_router, lkp_common_router, lkp_specific_router, lkp_analytics_router
from api_layers.routes import layer_router
from api_analytics.routes import analytics_router
import traceback
from api_layers.exceptions import NoRasterDataException, LayerDataException, RasterFileNotFoundException
from api_analytics.exceptions import AnalyticsDataException



app = FastAPI(root_path="/acasa_srilanka_api")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(lkp_location_router, prefix="/lkp/locations")
app.include_router(lkp_common_router, prefix="/lkp/common")
app.include_router(lkp_specific_router, prefix="/lkp/specific")
app.include_router(lkp_analytics_router, prefix="/lkp/analytics")
app.include_router(layer_router, prefix="/layers")
app.include_router(analytics_router, prefix="/analytics")


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "success": 0,
            "message": "Validation failed. Please check your input.",
            "errors": jsonable_encoder(exc.errors()),
        },
    )


@app.exception_handler(NoRasterDataException)
async def handle_raster_data_error(request: Request, exc: NoRasterDataException):
    return JSONResponse(
        status_code=200,
        content={
            "success": 0,
            "message": str(exc),
            # "trace": traceback.format_exc() # dev-local
        },
    )


@app.exception_handler(LayerDataException)
async def handle_layer_type_error(request: Request, exc: LayerDataException):
    return JSONResponse(
        status_code=200,
        content={
            "success": 0,
            "message": str(exc),
            # "trace": traceback.format_exc() # dev-local
        },
    )


@app.exception_handler(RasterFileNotFoundException)
async def handle_tif_unavailable_error(request: Request, exc: RasterFileNotFoundException):
    return JSONResponse(
        status_code=200,
        content={
            "success": 0,
            "message": str(exc),
            # "trace": traceback.format_exc() # dev-local
        },
    )


@app.exception_handler(AnalyticsDataException)
async def handle_analytics_error(request: Request, exc: AnalyticsDataException):
    return JSONResponse(
        status_code=200,
        content={
            "success": 0,
            "message": str(exc),
            # "trace": traceback.format_exc() # dev-local
        },
    )
