import DTCurrentPlot

# import data
plot = DTCurrentPlot.DTCurrentPlot('fills/3992/')

# show some sample plots
plot.draw_slope_2d(format=None)
#plot.draw_current_vs_lumi(wheel=0, station=4, sector=4, format=None)
#plot.draw_slope_vs_sector_superlayers(wheel=0, station=4, format=None)
#plot.draw_slope_vs_sector_wheels(station=4, format=None)
#plot.draw_slope_vs_wheel(station=4, sector=4, format=None)

#plot.plot_data()