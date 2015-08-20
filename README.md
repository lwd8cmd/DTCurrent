# DTCurrent

Python classes for importing DT currents data files and plotting

# DTCurrentData usage

## subtitle
```python
import DTCurrentData
import matplotlib.pyplot as plt

data = DTCurrentData.DTCurrentData('fills/2984/')

# get average wire currents vs luminosity
xs, ys = data.current_vs_lumi()
plt.plot(xs, ys, '.')
plt.show()
```

available filters
```python
xs, ys = data.current_vs_lumi(wheel=2, station=4, sector=4, superlayer=1, layer=1, wire='w0')
```

Extract slopes:

```python
# slope d(current)/d(luminosity) vs wheel
xs, ys = data.slope_vs_wheel()
plt.plot(xs, ys, 'o')
plt.show()

# slope d(current)/d(luminosity) vs station
xs, ys = data.slope_vs_station()
plt.plot(xs, ys, 'o')
plt.show()

# slope d(current)/d(luminosity) vs sector
xs, ys = data.slope_vs_sector()
plt.plot(xs, ys, 'o')
plt.show()
```