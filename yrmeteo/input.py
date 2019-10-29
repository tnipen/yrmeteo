import netCDF4
import numpy as np


import verif.util


import met2verif.fcstinput


variables = ["air_temperature",
        "precipitation_amount",
        "cloud_area_fraction",
        "wind_speed",
        "wind_direction",
        "precipitation_amount_max",
        "precipitation_amount_min",
        "probability_of_precipitation",
        "air_temperature_lower",
        "air_temperature_upper",
        "wind_gust"]


class Input(object):
    def __init__(self, filename, config):
        self.filename = filename
        print(0)
        self.input = met2verif.fcstinput.Netcdf(self.filename)
        self.file = netCDF4.Dataset(self.filename, 'r')
        self.config = config

    def get(self, lat, lon, variable, members=[0], hood=0):
        if variable not in variables:
            verif.util.error("Unrecognized variable '%s'" % variable)

        variable_name = None
        add = 0
        multiply = 1
        if variable in self.config["variables"] and "name" in self.config["variables"][variable]:
            variable_name = self.config["variables"][variable]["name"]
            if "add" in self.config["variables"][variable]:
                add = float(self.config["variables"][variable]["add"])
            if "multiply" in self.config["variables"][variable]:
                multiply = float(self.config["variables"][variable]["multiply"])
        else:
            # Diagnose variable name
            potential_variables = list()
            if variable == "air_temperature":
                potential_variables += ["air_temperature_2m"]
                add = -273.15
            elif variable == "precipitation_amount":
                potential_variables += ["precipitation_amount"]
            elif variable == "wind_speed":
                potential_variables += ["wind_speed_10m"]
            elif variable == "wind_direction":
                potential_variables += ["wind_direction_10m"]
            elif variable == "wind_gust":
                potential_variables += ["wind_speed_of_gust"]
            else:
                potential_variables += [variable]

            print(potential_variables)
            # Find the right variable
            for potential_variable in potential_variables:
                if potential_variable in self.file.variables:
                    variable_name = potential_variable
                    break
        if variable_name is None:
            # Diagnose variables
            if variable == "wind_speed":
                if "x_wind_10m" in self.file.variables:
                    xname = "x_wind_10m"
                elif "wind_speed" in config.variables and "x" in config.variables["wind_speed"]:
                    xname = config.variables["wind_speed"]["x"]
                if "y_wind_10m" in self.file.variables:
                    yname = "y_wind_10m"
                elif "wind_speed" in config.variables and "y" in config.variables["wind_speed"]:
                    yname = config.variables["wind_speed"]["y"]
                x = self.input.extract([lat], [lon], xname, members, hood)
                y = self.input.extract([lat], [lon], yname, members, hood)
                data = np.sqrt(x**2 + y**2)
            elif variable == "wind_direction":
                data = None
            else:
                verif.util.error("Could not determine NetCDF variable name for '%s'" % variable)
        else:
            data = self.input.extract([lat], [lon], variable_name, members, hood)
        return data[:, 0, ] * multiply + add

    def get_times(self, tz=0):
        times = self.file.variables["time"][:]
        times = np.array([verif.util.unixtime_to_datenum(time) for time in times])
        times = times+tz/24
        return times

    def get_leadtimes(self):
        times = self.file.variables["time"][:]
        leadtimes = (times - times[0]) / 3600
        return leadtimes