import matplotlib.pylab as mpl
import numpy as np
import yrmeteo.symbol
import matplotlib.dates as mpldates
import matplotlib.colors
import matplotlib.image as mplimg
from pylab import rcParams
import copy
import scipy.interpolate

fig_size = [11, 3]
rcParams['figure.figsize'] = fig_size

# blue = matplotlib.colors.to_hex("00b9f2")
blue = "#00b9f2"
blue = "#68CFE8"
red = "#FF3333"
gray = [0.7,0.7,0.7]
darkblue = "#0059b3"


class Meteogram(object):

    def __init__(self):
        self.title = None
        self.ylim = None
        self.debug = False
        self.dpi = 150
        self.start_time_index = 0
        self.show_pop = True

    def adjust_xaxis(self, ax=None, show_tick_labels=True):
        if ax is None:
            ax = mpl.gca()
        xlim = ax.get_xlim()
        xlim = [xlim[0] + self.start_time_index/24.0, xlim[1]]
        ax.set_xlim(xlim)
        L = xlim[1] - xlim[0]
        if L <= 5:
            ax.xaxis.set_major_locator(mpldates.DayLocator(interval=1))
            ax.xaxis.set_minor_locator(mpldates.HourLocator(byhour=range(0,24,2)))
            if show_tick_labels:
                ax.xaxis.set_major_formatter(mpldates.DateFormatter('\n%a %d %b %Y'))
                ax.xaxis.set_minor_formatter(mpldates.DateFormatter('%H'))
            else:
                ax.xaxis.set_ticklabels([])
            ax.xaxis.grid(True, which='major', color=gray, zorder=3, linestyle='-', linewidth=1)
            ax.xaxis.grid(True, which='minor', color=gray, zorder=2, linestyle='-', lw=0.5)

            # Only show even numbered hours
            """
            print ax.get_xminorticklabels()[0]
            for n, tick in enumerate(ax.xaxis.get_minor_ticks()):
                offset = 0
                if (n+offset) % 2 == 0:
                    print "remove"
                    tick.label1.set_visible(False)
            """

            # Align labels. For some strange reason, this does not work if the code is placed outside
            # this if/else block...
            ticks = ax.xaxis.get_major_ticks()
            for n, tick in enumerate(ax.xaxis.get_major_ticks()):
                # Don't show the last label if it is unlikely to fit, because there aren't enough hours in
                # that day in the graph
                if n == len(ticks)-1 and (xlim[1] % 1) <= 0.42:
                    tick.label1.set_visible(False)
                else:
                    tick.label1.set_horizontalalignment("left")
        else:
            ax.xaxis.set_major_locator(mpldates.DayLocator(interval=1))
            ax.xaxis.set_minor_locator(mpldates.HourLocator(byhour=range(0,24,6)))
            if show_tick_labels:
                ax.xaxis.set_major_formatter(mpldates.DateFormatter('%a\n%b %d'))
                ax.xaxis.set_minor_formatter(mpldates.DateFormatter(''))
            else:
                ax.xaxis.set_ticklabels([])
            ax.xaxis.grid(True, which='major', color=gray, zorder=3, linestyle='-', linewidth=2)
            ax.xaxis.grid(True, which='minor', color=gray, zorder=2, linestyle='-', lw=1)

            # Align labels
            ticks = ax.xaxis.get_major_ticks()
            for n, tick in enumerate(ax.xaxis.get_major_ticks()):
                # Don't show the last label if it is unlikely to fit, because there aren't enough hours in
                # that day in the graph
                if n == len(ticks)-1 and (xlim[1] % 1) <= 0.42:
                    tick.label1.set_visible(False)
                else:
                    tick.label1.set_horizontalalignment("left")

    def adjust_yaxis(self, ax=None, show_tick_labels=True):
        if ax is None:
            ax = mpl.gca()
        xlim = ax.get_xlim()
        L = xlim[1] - xlim[0]
        if L <= 5:
            ax.yaxis.set_major_locator(matplotlib.ticker.MaxNLocator(10, integer=True))
            ax.yaxis.grid(True, which='major', color=gray, zorder=3, linestyle='-', lw=1)
        else:
            ax.yaxis.set_major_locator(matplotlib.ticker.MaxNLocator(10, integer=True))
            ax.yaxis.grid(True, which='major', color=gray, zorder=3, linestyle='-', lw=1)


    def plot(self, times, air_temperature, cloud_area_fraction, precipitation_amount,
            precipitation_amount_min=None, precipitation_amount_max=None,
            probability_of_precipitation=None, wind_speed=None, wind_direction=None,
            air_temperature_lower=None, air_temperature_upper=None, wind_gust=None,
            weather_symbol=None, weather_symbol_confidence_12h=None):
        show_wind = wind_speed is not None and wind_direction is not None
        print(precipitation_amount_max.shape)
        q = np.zeros([len(precipitation_amount_max), 2])
        q[:, 0] = probability_of_precipitation*100
        q[:, 1] = precipitation_amount_max
        print(q)

        """
        Plot temperature
        """
        ax1 = mpl.gca() # fig.axes([0.125, 0.1, 0.8, 0.8])
        ax1.set_zorder(1)
        ax1.patch.set_alpha(0)
        ax1.set_position([0.05, 0.20, 0.9, 0.7])
        times_highres = np.linspace(np.min(times), np.max(times), 1000)
        f = scipy.interpolate.interp1d(times, air_temperature, kind='cubic')
        air_temperature_highres = f(times_highres)
        Iwarm = np.where(air_temperature_highres >= 0)[0]
        Tcold = copy.deepcopy(air_temperature_highres)
        Tcold[Iwarm] = np.nan
        ax1.plot(times_highres, air_temperature_highres, '-', color=red, lw=2, zorder=3)
        ax1.plot(times_highres, Tcold, '-', color=darkblue, lw=2, zorder=3)
        ax1.set_xlim([ax1.get_xlim()[0], np.max(times)])
        ax1.set_xlim([np.min(times), np.max(times)])
        if air_temperature_lower is not None and air_temperature_upper is not None:
            # ax1.plot(times, air_temperature_lower, '-', color=red, lw=2, zorder=3)
            # ax1.plot(times, air_temperature_upper, '-', color=red, lw=2, zorder=3)
            I = np.where((np.isnan(air_temperature_lower) == 0) & (np.isnan(air_temperature_upper) == 0))[0]
            ax1.fill(np.concatenate((times[I], times[I[::-1]])), np.concatenate((air_temperature_lower[I], air_temperature_upper[I[::-1]])), color='r', alpha=0.2, linewidth=0)

        """
        Plot symbols
        """
        xlim = ax1.get_xlim()
        # xlim = [np.min(times), xlim[0]+2] # Only allow 48 hour forecasts
        ylim = ax1.get_ylim()
        dx = xlim[1] - xlim[0]
        dy = ylim[1] - ylim[0]
        ylim = [ylim[0], ylim[1] + dy/5.0]
        dy = ylim[1] - ylim[0]
        dlt = times[1]-times[0]
        for t in range(len(times)):
            if dlt > 2.0/24:
                It = np.argmin(np.abs(times_highres - (times[t] - dlt/2)))
            else:
                It = np.argmin(np.abs(times_highres - times[t]))
            if dlt >= 2.0/24 or (times[t] * 24) % 2 == 1:
                if not np.isnan(air_temperature[t]) and not np.isnan(precipitation_amount[t]) and not np.isnan(cloud_area_fraction[t]):
                    if weather_symbol is None:
                        symbol = yrmeteo.symbol.get(air_temperature[t], precipitation_amount[t], cloud_area_fraction[t])
                    else:
                        symbol0 = yrmeteo.symbol.get(air_temperature[t], precipitation_amount[t], cloud_area_fraction[t])
                        symbol = yrmeteo.symbol.get_image(int(weather_symbol[t]))
                        #if symbol0 != symbol:
                        #    print("Different symbols %s!=%s %d" % (symbol0, symbol,
                        #        weather_symbol[t]))
                        #    print(cloud_area_fraction[t], precipitation_amount[t], air_temperature[t])
                    image = mplimg.imread(symbol)
                    h = 0.7/5*dy/dx*2.75*dlt*24  # Icon height
                    dy1 = dy/12
                    if dlt <= 2.0/24:
                        extent = [times[t]-dlt,times[t]+dlt,air_temperature[t]+dy1, air_temperature[t]+dy1+h]
                    else:
                        # extent = [times[t]-dlt/2.0,times[t]+dlt/2.0,air_temperature[t]+dy1, air_temperature[t]+dy1+h/2.0]
                        extent = [times[t]-dlt,times[t],air_temperature_highres[It]+dy1, air_temperature_highres[It]+dy1+h/2.0]
                    ax1.imshow(image, aspect="auto", extent=extent, zorder=10)
                    if self.show_pop and probability_of_precipitation is not None:
                        pop = np.round(probability_of_precipitation[t],1)*100
                        pop = np.round(probability_of_precipitation[t],2)*100
                        #if pop == 10 and probability_of_precipitation[t] < 10:
                        #    pop = 9
                        if pop > 0:
                            adj = -3.0/24 * (dlt > 2.0/24)
                            ax1.text(times[t] + adj, air_temperature_highres[It] + dy/30, "%d%%" % (pop),
                            horizontalalignment='center', fontsize=10)
        self.adjust_xaxis(ax1, False)
        self.adjust_yaxis(ax1, False)

        if weather_symbol_confidence_12h is not None:
            colors = ['w', 'y', 'r']
            unique_timeofday = np.unique(times * 24 % 24)
            # Find the time of day that is closest to 18Z
            I = np.argmin(np.abs(unique_timeofday - 18))
            lookup_timeofday = unique_timeofday[I]
            print(lookup_timeofday)
            for i in range(3):
                I = np.where((weather_symbol_confidence_12h == i) & ((times * 24 % 24) == lookup_timeofday))[0]
                # Place the 18Z confidence at 12Z
                I0 = (I - 6/(24*dlt)).astype(int)
                print(i, I, dlt, I0, dy)
                ax1.plot(times[I0], air_temperature[I0], 'o', mfc=colors[i], mec='k', zorder=10)
                # ax1.plot(times, air_temperature, 'o', mec='k', zorder=10)


        # Freezing line
        ax1.plot(xlim, [0,0], '-', lw=2, color=gray)

        """
        Plot precipitation
        """
        ax2 = ax1.twinx()
        ax2.set_zorder(0)
        ax2.set_position(ax1.get_position())
        precipitation_amount[precipitation_amount < 0.1] = 0
        if precipitation_amount_max is not None:
            precipitation_amount_max[precipitation_amount_max < 0.1] = 0
            ax2.bar(times - dlt/2, precipitation_amount_max, 0.95*dlt, color="white", ec=blue, hatch="//////", lw=0, align='center', zorder=0)
            for t in range(len(times)):
                if not np.isnan(precipitation_amount_max[t]) and precipitation_amount_max[t] > 0.1 and precipitation_amount_max[t] < 10:
                     mpl.text(times[t] - dlt/2.0, precipitation_amount_max[t], "%0.1f" %
                             precipitation_amount_max[t], fontsize=6,
                           horizontalalignment="center", color="k")
                # if not np.isnan(precipitation_amount_max[t]):
                #     mpl.text(times[t] - dlt/2.0, precipitation_amount_max[t], "%.0f%%" %
                #             (probability_of_precipitation[t] * 100), fontsize=6,
                #           horizontalalignment="center", color="k")
        # print(np.sum((precipitation_amount_max > 0.1) & (probability_of_precipitation < 0.1)))
        # print(np.sum((precipitation_amount_max < 0.1) & (probability_of_precipitation > 0.1)))
        main_blue_bar = precipitation_amount
        if precipitation_amount_min is not None:
            main_blue_bar = precipitation_amount_min
        ax2.bar(times - dlt/2, main_blue_bar, 0.95*dlt, color=blue, lw=0, align='center', zorder=0)
        ax2.plot(times - dlt/2, precipitation_amount, '_', color="blue", ms=8, lw=0, zorder=10)
        #ax2.set_ylabel("Precipitation (mm)")
        #ax2.set_xticks([])
        lim = [0, 10]
        if dlt > 2.0/24:
            # Compress y axis for precip for longer accumulation periods
            lim = [0, 25]
        ax1.set_xlim(xlim)
        ax1.set_ylim(ylim)
        ax2.set_ylim(lim)
        self.adjust_xaxis(ax2, not show_wind)
        for t in range(len(times)):
            if not np.isnan(main_blue_bar[t]) and main_blue_bar[t] > 0.1:
                mpl.text(times[t] - dlt/2.0, 0, "%0.1f" % main_blue_bar[t], fontsize=6,
                      horizontalalignment="center", color="k")
        axlast = ax2

        """
        Plot winds
        """
        if show_wind:
            pos = ax1.get_position()
            ax_wind = mpl.axes([pos.x0, 0.05, pos.x1-pos.x0, 0.12])
            xlim = ax1.get_xlim()
            ax_wind.set_xlim(xlim)
            # s = (xlim[1] - xlim[0]) / fig_size[0] * (pos.x1-pos.x0) * (fig_size[1] * (0.05)) * 2 * 12
            # Don't deal with scale here. Just assume the axis is set up with the right aspect.
            max_y = 0.95*1.0 / 24 #(xlim[1] - xlim[0]) / fig_size[0] * (pos.x1-pos.x0) * (fig_size[1] * (0.05)) * 2 * 12
            ylim = [-max_y*2, max_y*1.2]
            ax_wind.set_ylim(ylim)
            if dlt <= 1.5/24:
                freq = 2
                start_time_index = 0
            else:
                freq = 1
                start_even_hour = int(times[0]*24) % freq == 0
                start_time_index = 2 - start_even_hour
            for i in range(start_time_index, len(times), freq):
                time = times[i]
                dir = wind_direction[i]
                dx = -max_y * np.sin(dir / 180 * 3.14159265)
                dy = -max_y * np.cos(dir / 180 * 3.14159265)
                hl = 0.0125
                # Arrow puts the head at the end of the line, so rescale the line to be slightly shorter
                hlx = (2.0/24 - hl)/(2.0/24)
                ax_wind.arrow(time - dx, -dy, 2*dx*hlx, 2*dy*hlx, head_width=0.01, head_length=hl, fc='k', ec='k', zorder=10)
                # ax_wind.arrow(time - dx, -dy, 2*dx-hl, 2*dy-hl, head_width=0.01, head_length=0, fc='k', ec='k', zorder=10)
                # ax_wind.plot([time - dx, time + dx], [-dy, dy], '.-', lw=1)
                if not np.isnan(wind_speed[i]):
                    if wind_gust is not None and not np.isnan(wind_gust[i]):
                        text = "%1.0f-%1.0f" % (wind_speed[i], wind_gust[i])
                    else:
                        text = "%0.1f" % wind_speed[i]
                    ax_wind.text(times[i], ylim[0]*0.95, text, fontsize=8, horizontalalignment="center", color="k", verticalalignment="bottom")

                self.adjust_xaxis(ax_wind)
                ax_wind.set_yticks([])
            axlast = ax_wind

        ax2.set_yticks([])

        labels = [u"%d\u00B0" % item for item in ax1.get_yticks()]
        ax1.set_yticklabels(labels)

        if self.title is not None:
            mpl.title(self.title)

        # mpl.gcf().subplots_adjust(bottom=0.15, top=0.9, left=0.05, right=0.95)
        if self.ylim is not None:
            ax1.set_ylim(self.ylim)

    def show(self):
        mpl.show()

    def save(self, filename):
        mpl.savefig(filename, bbox_inches='tight', dpi=self.dpi)
