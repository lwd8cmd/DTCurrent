# DTCurrent

Python classes for importing DT currents data files and plotting

# DTCurrentData

Imports txt files and returns data in a nicer format.

## Usage
```python
import DTCurrentData
import matplotlib.pyplot as plt

data = DTCurrentData.DTCurrentData('fills/2984/')

# get average wire currents vs luminosity
xs, ys = data.current_vs_lumi()
plt.plot(xs, ys, '.')
plt.show()
```

Returned xs and ys arrays can be directly passed to matplotlib or ROOT plotting methods.

## Filters

Without filters DTCurrentData class returns mean current (averages over all chambers, layers, wires)

Optional arguments can be passed to get values only from selected locations.

* wheel = -2 | -1 | 0 | 1 | 2 | None
* station = 1 | 2 | 3 | 4 | None
* sector = 1 | 2 | ... | 12 | None
* superlayer = 1 | 2 | 3 | None
* layer = 1 | 2 | 3 | 4
* wire = 'wire0' | 'wire1' | 'wires' | 'cathode'

NB! None means filter is not present.

Example:

```python
xs, ys = data.current_vs_lumi(wheel=2, station=4, sector=4, superlayer=1, layer=1, wire='wire0')
```

## Available methods:

* slope(**filters) -> float slope
* maxcurrent(**filters) -> float maximum_current
* current_vs_lumi(**filters) -> tuple (float[] luminosity, float[] current)
* current_vs_lumi_fit(**filters) -> tuple (float[] luminosity, float[] fitted_current)
* slope_vs_wheel(**filters) -> tuple (int[] wheel, float[] slope)
* maxcurrent_vs_wheel(**filters) -> tuple (int[] wheel, float[] maximum_current)
* slope_vs_station(**filters) -> tuple (int[] station, float[] slope)
* maxcurrent_vs_station(**filters) -> tuple (int[] station, float[] maximum_current)
* slope_vs_sector(**filters) -> tuple (int[] sector, float[] slope)
* maxcurrent_vs_sector(**filters) -> tuple (int[] sector, float[] maximum_current)

# DTCurrentPlot

Plots data with titles, axes, labels and shows plot on screen or saves in the data directory.

## Usage

```python
import DTCurrentPlot

# load data
plot = DTCurrentPlot.DTCurrentPlot('fills/3992/')

# show some plots on the screen
plot.draw(y='current', x='luminosity', series='superlayer', wheel=1, station=4, sector=4, format=None)
plot.draw(y='slope', x='wheel', series='superlayer', station=4, format=None)
plot.draw_slope_2d(station=4, format=None)

# save several plots in the data directory with predefined options
plot.plot_data()
```

## Plot types

* Current vs luminosity: scatter plot with fitted line

draw(y='current', x='luminosity')

* Slope or maximum current: scatter plot

draw(y='slope')

draw(y='maxcurrent')

* 2D imagemap with slopes

draw_slope_2d()

## Available xaxis and series types in scatter plot (when y is slope or maxcurrent)

wheel, station, sector, superlayer, layer, wire

Usage:

```python
# show only one series
plot.draw(y='slope', x='wheel')
plot.draw(y='slope', x='station')

# show multiple series with legend
plot.draw(y='slope', x='wheel', series='superlayer')
plot.draw(y='slope', x='sector', series='layer')
```

## Filters

See filters information in DTCurrentData.

Usage:
```python
plot.draw(y='slope', x='sector', wheel=0)
plot.draw(y='slope', x='wheel', series='superlayer', station=4)
plot.draw(y='slope', x='sector', station=4, sector=4, wire='cathode')
```

## Saving options

format = 'png' | 'pdf' | 'eps' | 'svg' | None

Saves plot with defined format (png/pdf/eps/svg) or shows on screen (format=None).