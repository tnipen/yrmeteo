import sys
import numpy as np
import yaml
import argparse
import time


import verif.util


import yrmeteo.input
import yrmeteo.meteogram


def main():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('file', help='', nargs="?")
    parser.add_argument('--config', help='')
    parser.add_argument('-hood', default=0, type=int, help="Neighbourhood radius (in grid points)")
    parser.add_argument('-f', type=str, default=None, help="Output filename", dest="output_filename")
    parser.add_argument('-lt', type=verif.util.parse_ints, help="Leadtimes", dest="leadtimes")
    parser.add_argument('-lat', default=59.9423, type=float, help="Latitude in degrees")
    parser.add_argument('-lon', default=10.72, type=float, help="Longitude in degrees")
    parser.add_argument('--debug', help="Show debug info", action="store_true")
    parser.add_argument('-tz', type=int, default=0, help="Timezone (0 UTC, 1 CET)")

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()

    with open(args.config) as cfile:
        config = yaml.load(cfile)

    if args.file is None:
        unixtime = time.time() - 3600*2
        date = verif.util.unixtime_to_date(unixtime)
        hour = (unixtime % 86400) / 3600
        filename = "/lustre/storeB/project/metproduction/products/yr_nordic/%08d%02d/yr_nordic_%08d%02d.nc" % (date, hour, date, hour)
    else:
        filename = args.file
    input = yrmeteo.input.Input(filename, config.get("input", {}))
    data = dict()
    variables = yrmeteo.input.variables
    for variable in variables:
        data[variable] = input.get(args.lat, args.lon,variable, [0], args.hood)
    times = input.get_times(tz=args.tz)

    leadtimes = input.get_leadtimes()

    for key in data:
        if data[key] is not None:
            if args.leadtimes is not None:
                Ileadtimes = [i for i in range(len(leadtimes)) if leadtimes[i] in args.leadtimes]
                data[key] = data[key][Ileadtimes, :]
            data[key] = data[key][:, 0]
    if args.leadtimes is not None:
        Ileadtimes = [i for i in range(len(leadtimes)) if leadtimes[i] in args.leadtimes]
        times = times[Ileadtimes]
        leadtimes = leadtimes[Ileadtimes]

    meteo = yrmeteo.meteogram.Meteogram()
    meteo.plot(times, **data)
    if args.output_filename:
        meteo.save(args.output_filename)
    else:
        meteo.show()


if __name__ == '__main__':
    main()
