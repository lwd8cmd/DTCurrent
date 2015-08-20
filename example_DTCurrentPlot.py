import DTCurrentPlot

# import data
plot = DTCurrentPlot.DTCurrentPlot('fills/3992/')

#plot.draw_slope_vs_sector_superlayers(wheel=-2, station=1, format=None)
#plot.draw_maxcurrent_vs_sector_superlayers(wheel=-2, station=1, cathode=False, format=None)

plot.draw_maxcurrent_vs_wheel_superlayers(station=4, sector=4, format=None)
#plot.draw_slope_vs_wheel(station=4, sector=4, format=None)

# show some sample plots
#plot.draw_slope_2d(format=None)
#plot.draw_current_vs_lumi(wheel=0, station=4, sector=4, format=None)
#plot.draw_slope_vs_sector_superlayers(wheel=0, station=4, format=None)
#plot.draw_slope_vs_sector_wheels(station=4, format=None)
#plot.draw_slope_vs_wheel(station=4, sector=4, format=None)

#plot.plot_data()