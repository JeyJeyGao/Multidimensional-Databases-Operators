from pandas import DataFrame
from bokeh.io import show
from bokeh.models import ColumnDataSource, HoverTool, PanTool, WheelZoomTool, SaveTool, ResetTool, DataTable
from bokeh.plotting import figure
from bokeh.tile_providers import CARTODBPOSITRON, get_provider
import math


def show_map(cube: DataFrame, element: DataFrame):
    print("Showing map.")
    if not ("latitude" in cube.columns and "longitude" in cube.columns):
        raise Exception("Must contain dimensions: 'latitude' and 'longitude'.")
    if "date" in cube.columns or "DATE" in cube.columns:
        show_interactive_map(cube, element)
        return
    else:
        show_static_map(cube, element)


def show_static_map(cube: DataFrame, element: DataFrame):
    cube_copy = cube.copy()
    cube_copy[["longitude", "latitude"]] = [to_merc(x, y) for x, y in zip(cube_copy["longitude"], cube_copy["latitude"])]

    # TODO: hard coded now
    # cube_copy["__size__"] = [math.log(x, 2) * 2 + 3 if x > 0 else 0 for x in cube_copy["confirmed"]]
    cube_copy["__size__"] = 10

    source = ColumnDataSource(cube_copy)
    source.from_df(element)

    tile_provider = get_provider(CARTODBPOSITRON)
    p = figure(x_range=(-19000000, 21000000), y_range=(-5000000, 9000000),
               x_axis_type="mercator", y_axis_type="mercator")

    p.plot_width = 1100
    p.plot_height = 650

    hover = HoverTool(tooltips=[(col, "@" + col) for col in cube_copy.columns if col != "longitude" and col != "latitude" and col != "__size__"])
    wheel_zoom = WheelZoomTool()
    p.tools = [PanTool(), wheel_zoom, SaveTool(), ResetTool(), hover]
    p.toolbar.active_scroll = wheel_zoom
    p.add_tile(tile_provider)
    p.axis.visible = False
    p.toolbar.logo = None

    p.circle(x="longitude", y="latitude", size="__size__", alpha=0.5, source=source)
    show(p)


def to_merc(long, lat):
    k = 6378137
    x = k * math.radians(long)
    scale = x / long
    y = 180 / math.pi * math.log(math.tan(math.pi / 4 + lat * (math.pi / 180) / 2)) * scale
    return x, y


def show_interactive_map(cube: DataFrame, element: DataFrame):
    pass


def show_cube(cube: DataFrame, element: DataFrame):
    print("Showing cube.")
    pass


def show_table(cube: DataFrame, element: DataFrame):
    print("Showing table.")
    pass