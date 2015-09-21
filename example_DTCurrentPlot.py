from DTCurrentPlot import *

# import data
plot = DTCurrentPlot('fills/3992/')

# draw plots
plot.draw(y='current', x='luminosity', series='superlayer', wheel=1, station=4, sector=4, format=None)
plot.draw(y='slope', x='wheel', series='superlayer', station=4, format=None)
plot.draw(y='maxcurrent', x='sector', station=4, format=None)
plot.draw_slope_2d(station=4, format=None)

# save in pdf
plot.draw(y='slope', x='wheel', format='svg')

# save preconfigured plots
plot.plot_data()