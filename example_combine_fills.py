from DTCurrentPlot import *
import numpy as np

# import data
fill1 = DTCurrentPlot('fills/4364/')
fill2 = DTCurrentPlot('fills/4381/')

# combine luminosity and currents
fill2.data.luminosity = np.vstack((fill1.data.luminosity.reshape((-1,1)), fill2.data.luminosity.reshape((-1,1)))).flatten()
fill2.data.currents = np.ma.concatenate([fill1.data.currents, fill2.data.currents], axis=6)
fill2.data.background = np.ma.concatenate([fill1.data.background, fill2.data.background], axis=6)

# rename fill number (fill1+fill2) for plots
fill2.data.fill = '{} + {}'.format(fill1.data.fill, fill2.data.fill)


# save preconfigured plots
fill2.plot_data()