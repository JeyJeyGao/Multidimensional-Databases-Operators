from pandas import DataFrame
from bokeh.io import show
from bokeh.models import ColumnDataSource, HoverTool, PanTool, WheelZoomTool, SaveTool, ResetTool, Select, \
    Slider, FuncTickFormatter, DataTable, TableColumn, DateFormatter, Button
from bokeh.plotting import figure
from bokeh.tile_providers import CARTODBPOSITRON, get_provider
from bokeh.server.server import Server
from bokeh.layouts import column, row
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
        self.cube[["longitude", "latitude"]] = [self.to_merc(x, y) for x, y in zip(self.cube["longitude"], self.cube["latitude"])]
        for ind in element.columns:
            self.cube["ELEMENT_" + ind] = element[ind]
        self.cube_copy = deepcopy(self.cube)
        self.date = "date" in self.cube.columns and min(self.cube["date"]) != max(self.cube["date"])
        self.server = Server({'/' + self.random_str(): self.bkapp}, port=self.port[0])
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
        pass

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

    def random_str(self, length=7):
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for i in range(length))
