from pandas import DataFrame
from bokeh.io import show
from bokeh.models import ColumnDataSource, HoverTool, PanTool, WheelZoomTool, SaveTool, ResetTool, Select, \
    Slider, FuncTickFormatter, DataTable, TableColumn, DateFormatter, Button, Axis, LabelSet
from bokeh.plotting import figure
from bokeh.tile_providers import CARTODBPOSITRON, get_provider
from bokeh.server.server import Server
from bokeh.layouts import column, row
import plotly.express as px
from time import mktime
import datetime
from copy import deepcopy
import math
import random
import string


class Visualization:
    port = [5006]

    def __init__(self, cube: DataFrame, element: DataFrame):
        self.element = element
        self.original_cube = cube
        self.cube = deepcopy(cube)
        if "longitude" in self.cube.columns and "latitude" in self.cube.columns:
            self.cube[["longitude", "latitude"]] = [self.to_merc(x, y) for x, y in zip(self.cube["longitude"], self.cube["latitude"])]
        for ind in element.columns:
            self.cube["ELEMENT_" + ind] = element[ind]
        self.cube_copy = deepcopy(self.cube)
        self.date = "date" in self.cube.columns and min(self.cube["date"]) != max(self.cube["date"])
        while True:
            try:
                self.server = Server({'/' + self.random_str(): self.bkapp}, port=self.port[0])
                break
            except:
                self.port[0] += 1
        self.tile_provider = get_provider(CARTODBPOSITRON)
        self.port[0] += 1

    def show_map(self):
        print("Showing map.")
        if not ("latitude" in self.cube.columns and "longitude" in self.cube.columns):
            raise Exception("Must contain dimensions: 'latitude' and 'longitude'.")
        self.show_interactive_map("date" in self.cube.columns)

    def show_interactive_map(self, date: bool):
        try:
            self.server.start()
            self.server.io_loop.add_callback(self.server.show, "/")
            print("Press Ctrl-C to continue.")
            self.server.io_loop.start()
        except KeyboardInterrupt:
            pass

    def bkapp(self, doc):
        def update(attr, old, new):
            layout.children[1] = create_figure()

        options = [x for x in self.cube_copy.columns if (isinstance(self.cube_copy[x][self.cube.index[0]], int) or
                                                         isinstance(self.cube_copy[x][self.cube.index[0]], float))
                   and x != "longitude" and x != "latitude" and x != "__size__"]
        select = Select(title="Circle Size (logarithm)", value=options[0], options=options)
        select.on_change("value", update)
        if self.date:
            start = mktime(min(self.cube_copy["date"]).timetuple())
            end = mktime(max(self.cube_copy["date"]).timetuple())
            delta = mktime(datetime.date(2020, 4, 6).timetuple()) - mktime(datetime.date(2020, 4, 5).timetuple())
            date_slider = Slider(title="Date", value=start, start=start, end=end, step=delta)
            date_slider.on_change("value", update)
            date_slider.format = FuncTickFormatter(code="""
                function to_date(timestamp) {
                    var date = new Date(timestamp * 1000);
                    return date.getFullYear() + '-' + (date.getMonth() + 1) + '-' + date.getDate();
                }
                return to_date(tick);
            """)
            button = Button(label='► Play', width=60)
            callback_id = None

            def animate():
                nonlocal callback_id
                if button.label == '► Play':
                    button.label = '❚❚ Pause'
                    callback_id = doc.add_periodic_callback(animate_update, 200)
                else:
                    button.label = '► Play'
                    doc.remove_periodic_callback(callback_id)

            def animate_update():
                date = date_slider.value + delta
                if date > end:
                    date = start
                date_slider.value = date
            button.on_click(animate)
            controls = column(select, date_slider, button, width=200)
        else:
            controls = column(select, width=200)

        def create_figure():
            if self.date:
                self.cube_copy = self.cube[self.cube["date"] == datetime.date.fromtimestamp(date_slider.value)]
            if select.value:
                self.cube_copy["__size__"] = [math.log(x, 2) * 2 + 3 if x > 0 else 0 for x in self.cube_copy[select.value]]
            else:
                self.cube_copy["__size__"] = 10

            source = ColumnDataSource(self.cube_copy)

            p = figure(x_range=(-19000000, 21000000), y_range=(-5000000, 9000000),
                       x_axis_type="mercator", y_axis_type="mercator")

            p.plot_width = 1100
            p.plot_height = 650

            hover = HoverTool(tooltips=[(col, "@" + col) for col in self.cube_copy.columns if col != "longitude" and
                                        col != "latitude" and col != "__size__" and col != "date"])
            wheel_zoom = WheelZoomTool()
            p.tools = [PanTool(), wheel_zoom, SaveTool(), ResetTool(), hover]
            p.toolbar.active_scroll = wheel_zoom
            p.add_tile(self.tile_provider)
            p.axis.visible = False
            p.toolbar.logo = None
            p.circle(x="longitude", y="latitude", size="__size__", alpha=0.5, source=source)
            return p

        layout = row(controls, create_figure())
        doc.add_root(layout)

    def to_merc(self, long, lat):
        k = 6378137
        x = k * math.radians(long)
        scale = x / long
        y = 180 / math.pi * math.log(math.tan(math.pi / 4 + lat * (math.pi / 180) / 2)) * scale
        return x, y

    def show_cube(self):
        print("Showing cube.")
        dim = len(self.original_cube.columns)
        if dim == 1:
            self.show_cube_1d()
        elif dim == 2:
            self.show_cube_2d()
        elif dim == 3:
            self.show_cube_3d()
        else:
            print("Cannot visualize cube of dimension {}".format(dim))

    def show_table(self):
        print("Showing table.")
        cube_copy = deepcopy(self.original_cube)
        for col in self.element.columns:
            cube_copy["ELEMENT_" + col] = self.element[col]
        source = ColumnDataSource(cube_copy)
        columns = [TableColumn(field=x, title=x) if "date" not in x else
                   TableColumn(field=x, title=x, formatter=DateFormatter()) for x in cube_copy.columns]
        dt = DataTable(source=source, columns=columns, width=len(columns) * 150, height=800, editable=True)

        show(dt)

    def show_cube_1d(self):
        cube = deepcopy(self.original_cube)
        d = cube.columns[0]
        f = figure(x_range=[str(x) if isinstance(x, datetime.date) else x for x in sorted(set(cube[d]))])
        f.xaxis.axis_label = d
        f.width = 900
        f.height = 200
        f.yaxis.visible = False

        # deal with datetime type
        for c in cube.columns:
            if isinstance(cube[c][cube.index[0]], datetime.date):
                cube[c] = [str(x) for x in cube[c]]

        cube["__label__"] = ["<{}>".format(", ".join([str(self.element[x][d])
                                                      for x in self.element.columns]))
                             for d in self.element.index]
        for col in self.element.columns:
            cube[col] = self.element[col]
        hover = HoverTool(tooltips=[(x, "@" + x) for x in cube.columns if "__" not in x])
        zoom_tool = WheelZoomTool()
        f.tools = [PanTool(), zoom_tool, SaveTool(), ResetTool(), hover]
        f.toolbar.active_scroll = zoom_tool
        f.toolbar.logo = None

        source = ColumnDataSource(cube)

        label = LabelSet(x=d, text="__label__", y_offset=5, source=source)
        f.circle(x=d, source=source, size=10)
        f.add_layout(label)
        show(f)

    def show_cube_2d(self):
        cube = deepcopy(self.original_cube)
        d1, d2 = cube.columns[0], cube.columns[1]
        f = figure(x_range=[str(x) if isinstance(x, datetime.date) else x for x in sorted(set(cube[d1]))],
                   y_range=[str(x) if isinstance(x, datetime.date) else x for x in sorted(set(cube[d2]))])
        f.width = 900
        f.xaxis.axis_label = d1
        f.yaxis.axis_label = d2

        # deal with datetime type
        for c in cube.columns:
            if isinstance(cube[c][cube.index[0]], datetime.date):
                cube[c] = [str(x) for x in cube[c]]

        cube["__label__"] = ["<{}>".format(", ".join([str(self.element[x][d])
                                                      for x in self.element.columns]))
                             for d in self.element.index]
        for col in self.element.columns:
            cube[col] = self.element[col]
        hover = HoverTool(tooltips=[(x, "@" + x) for x in cube.columns if "__" not in x])
        zoom_tool = WheelZoomTool()
        f.tools = [PanTool(), zoom_tool, SaveTool(), ResetTool(), hover]
        f.toolbar.active_scroll = zoom_tool
        f.toolbar.logo = None

        source = ColumnDataSource(cube)

        label = LabelSet(x=d1, y=d2, text="__label__", y_offset=5, source=source)
        f.circle(x=d1, y=d2, source=source, size=10)
        f.add_layout(label)
        show(f)

    def show_cube_3d(self):
        cube = deepcopy(self.original_cube)

        d1 = cube.columns[0]
        d2 = cube.columns[1]
        d3 = cube.columns[2]

        for col in self.element.columns:
            cube[col] = self.element[col]

        f = px.scatter_3d(cube, x=d1, y=d2, z=d3, category_orders={
            d1: sorted(set(cube[d1])), d2: sorted(set(cube[d2])), d3: sorted(set(cube[d3]))}, hover_data=cube)
        f.show()

    def random_str(self, length=7):
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for i in range(length))


def map_html(cube, value, tile_provider):
    from bokeh.embed import components
    element = cube.element
    cube = deepcopy(cube.cube)
    if "longitude" in cube.columns and "latitude" in cube.columns:
        cube[["longitude", "latitude"]] = [Visualization.to_merc(1, x, y) for x, y in zip(cube["longitude"], cube["latitude"])]
    for ind in element.columns:
        cube["ELEMENT_" + ind] = element[ind]

    cube_copy = deepcopy(cube)
    cube_copy["__size__"] = [math.log(x, 2) * 2 + 3 if x > 0 else 0 for x in cube_copy[value]]

    source = ColumnDataSource(cube_copy)

    p = figure(x_range=(-19000000, 21000000), y_range=(-5000000, 9000000),
               x_axis_type="mercator", y_axis_type="mercator")

    p.plot_width = 1100
    p.plot_height = 650

    hover = HoverTool(tooltips=[(col, "@" + col) for col in cube_copy.columns if col != "longitude" and
                                col != "latitude" and col != "__size__" and col != "date"])
    wheel_zoom = WheelZoomTool()
    p.tools = [PanTool(), wheel_zoom, SaveTool(), ResetTool(), hover]
    p.toolbar.active_scroll = wheel_zoom
    p.add_tile(tile_provider)
    p.axis.visible = False
    p.toolbar.logo = None
    p.circle(x="longitude", y="latitude", size="__size__", alpha=0.5, source=source)
    js, div = components(p)
    return '<script src="https://cdn.bokeh.org/bokeh/release/bokeh-2.0.0.min.js"></script>' + js + div
