import geopandas as gpd
import rasterio
from rasterio.mask import mask
from rasterio.io import MemoryFile
from rasterio.enums import Resampling
import numpy as np
from matplotlib.colors import to_rgba
from io import BytesIO
import json
from settings import ROOT_DIR, env
from pathlib import Path
from api_lookups.models import LkpCountry, LkpState
from api_layers.exceptions import NoRasterDataException, RasterFileNotFoundException


class GeoProc:
    def __init__(self, **kwargs):
        self.db = kwargs.get("db")
        self.geojson_data_dir = ROOT_DIR / "_assets/shapefiles_geojson"
        self.tif_data_dir = Path(env.get("DATA_ROOT_DIR"))
        self.admin_level = kwargs.get("admin_level")
        self.admin_level_id = kwargs.get("admin_level_id")
        self.raster_layer = kwargs.get("layer")
        self.geojson_index = {
            "total": "sa_outline.geojson",
            "country": f"sa_countries/country_{self.admin_level_id}.geojson",
            "state": f"sa_states/state_{self.admin_level_id}.geojson",
        }
        self.source_file = self.tif_data_dir / kwargs.get("source_file") if kwargs.get("source_file") else None
        self.color_ramp = kwargs.get("color_ramp")
        self.tcase = lambda s: ' '.join(word.capitalize() for word in s.split())


    def get_region(self):
        if self.admin_level == "total":
            return ["South Asia"]
        if self.admin_level == "country":
            return [self.db.query(LkpCountry).filter(LkpCountry.id == self.admin_level_id).first().country]
        if self.admin_level == "state":
            state_obj = self.db.query(LkpState).filter(LkpState.id == self.admin_level_id).first()
            return [self.tcase(state_obj.state), state_obj.country.country]


    def prep_geojson(self):
        geojson_file = self.geojson_data_dir / self.geojson_index[self.admin_level]
        gdf = gpd.read_file(geojson_file)
        return {
            "region": self.get_region(),
            "bbox": gdf.total_bounds.tolist(),
            "geojson": json.loads(gdf.to_json())
        }
    

    def prep_geojson_districts_c(self):
        geojson_file = self.geojson_data_dir / f"sa_districts_c/simplified/districts_c{self.admin_level_id}.json"
        gdf = gpd.read_file(geojson_file)
        return {
            "country": self.get_region()[0],
            "bbox": gdf.total_bounds.tolist(),
            "geojson": json.loads(gdf.to_json())
        }
    

    def handle_geotiff(self):
        vector_data = self.prep_geojson()
        geojson = vector_data.get("geojson")
        if not Path(self.source_file).exists():
            raise RasterFileNotFoundException("The requested raster data file is unavailable")
        with rasterio.open(self.source_file) as src:
            geoms = [feature["geometry"] for feature in geojson["features"]]
            out_image, out_transform = mask(src, geoms, crop=True)
            raster_band = out_image[0]
            raster_masked = np.ma.masked_where(np.isnan(raster_band) | (raster_band == 0), raster_band)
            if raster_masked.mask.all():
                selected_region = ", ".join(self.get_region())
                raise NoRasterDataException(f"No data available for the selected inputs in {selected_region}")
            return {
                "masked_band": raster_masked,
                "transform": out_transform,
                "raster_meta": src.meta.copy()
            }

    def prep_raw_geotiff(self):
        result = self.handle_geotiff()
        masked_band = result["masked_band"]
        transform = result["transform"]
        meta = result["raster_meta"].copy()

        # Update metadata
        meta.update({
            "count": 1,
            "dtype": "float64",
            "driver": "GTiff",
            "height": masked_band.shape[0],
            "width": masked_band.shape[1],
            "transform": transform,
            "tiled": True,
            "blockxsize": 256,
            "blockysize": 256,
            "compress": "deflate",
        })
        meta.pop("nodata", None) 

        memfile = MemoryFile()
        with memfile.open(**meta) as dst:
            dst.write(masked_band.filled(np.nan), 1)
            dst.build_overviews([2, 4, 8, 16], Resampling.nearest)
            dst.update_tags(ns="rio_overview", resampling="nearest")

        return BytesIO(memfile.read())

    def prep_geotiff(self):
        result = self.handle_geotiff()
        masked_band = result["masked_band"]
        transform = result["transform"]
        meta = result["raster_meta"]
        hex_colors = self.color_ramp 
        # RGBA array
        rgba = np.zeros((masked_band.shape[0], masked_band.shape[1], 4), dtype=np.uint8)
        unique_vals = np.unique(masked_band.compressed()).astype(int)
        for val in unique_vals:
            idx = val - 1
            if 0 <= idx < len(hex_colors):
                color = to_rgba(hex_colors[idx], 1.0) 
                rgba[masked_band == val] = (np.array(color) * 255).astype(np.uint8)
        rgba[masked_band.mask] = [0, 0, 0, 0]
        # Base metadata
        out_meta = meta.copy()
        out_meta.update({
            "count": 4,
            "driver": "GTiff",
            "dtype": "uint8",
            "height": rgba.shape[0],
            "width": rgba.shape[1],
            "transform": transform,
            "tiled": True,                # COG requirement
            "blockxsize": 256,            # tile width
            "blockysize": 256,            # tile height
            "compress": "deflate",        # or "lzw"
            "interleave": "pixel"         # bands interleaved
        })
        out_meta.pop("nodata", None)
        # Write to an in-memory GeoTIFF
        memfile = MemoryFile()
        with memfile.open(**out_meta) as dst:
            for i in range(4):
                dst.write(rgba[:, :, i], i + 1)
            # Build overviews (pyramids for faster reads at smaller scales)
            dst.build_overviews([2, 4, 8, 16], Resampling.nearest)
            dst.update_tags(ns="rio_overview", resampling="nearest")
        # Return BytesIO-like object for StreamingResponse
        return BytesIO(memfile.read())