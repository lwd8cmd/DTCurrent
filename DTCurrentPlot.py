import DTCurrentData
import matplotlib.pyplot as plt
import numpy as np

# makes plots from DT current files.
# usage:
# DTCurrentPlot('pathname/')

class DTCurrentPlot(object):
	def __init__(self, path=''):
		self.load_data(path)
		
		#self.plot_data()
	
	# load files
	def load_data(self, path):
		self.path = path.rstrip('/')+'/'
		self.data = DTCurrentData.DTCurrentData(self.path)
		self.args = {'luminosity': [1], 'wheel': self.data.wheels, 'station': self.data.stations, 'sector': self.data.sectors, 'superlayer': self.data.valid_superlayers, 'layer': self.data.valid_layers, 'wire': self.data.valid_wires}
		self.labels = {'wheel': 'YB{:+d}', 'station': 'MB{}', 'sector': 'S{:02d}', 'superlayer': 'SL{}', 'layer': 'L{}', 'wire': '{}'}
		self.keywords = ['wheel', 'station', 'sector', 'superlayer', 'layer', 'wire']
		
	# plot data
	def plot_data(self):
		for wire in ['wires', 'cathode']:
			for station in self.data.stations:
				self.draw(y='slope', x='sector', series='wheel', station=station, wire=wire)
				self.draw(y='maxcurrent', x='sector', series='wheel', station=station, wire=wire)
				for wheel in self.data.wheels:
					self.draw(y='slope', x='sector', series='superlayer', wheel=wheel, station=station, wire=wire)
					self.draw(y='maxcurrent', x='sector', series='superlayer', wheel=wheel, station=station, wire=wire)
					for sector in self.data.sectors:
						self.draw(y='current', x='luminosity', series='superlayer', wheel=wheel, station=station, sector=sector, wire=wire)
		self.draw(y='slope', x='wheel', series='superlayer', station=station, sector=4)
		self.draw(y='maxcurrent', x='wheel', series='superlayer', station=station, sector=4)
		self.draw_slope_2d(station=4)
		
	def build_filterargs(self, filters={}):
		return dict(
			wheel=filters['wheel'] if 'wheel' in filters else None, \
			station=filters['station'] if 'station' in filters else None, \
			sector=filters['sector'] if 'sector' in filters else None, \
			superlayer=filters['superlayer'] if 'superlayer' in filters else None, \
			layer=filters['layer'] if 'layer' in filters else None, \
			wire=filters['wire'] if 'wire' in filters else 'wires')
		
	def getdata(self, x, y, filters={}):
		func = {'slope': self.data.slope, 'maxcurrent': self.data.maxcurrent}

		xs = []
		ys = []
		
		for arg in self.args[x]:
			filters[x] = arg
			val = func[y](**self.build_filterargs(filters))
				
			if val > 0:
				xs.append(arg)
				ys.append(val)
				
		return (np.array(xs), np.array(ys)*(1e6 if y=='slope' else 1))
		
	def draw(self, x='sector', y='slope', series=None, format='png', wheel=None, station=None, sector=None, superlayer=None, layer=None, wire='wires'):	
		filters = {'wheel':wheel, 'station':station, 'sector':sector, 'superlayer':superlayer, 'layer':layer, 'wire':wire}
		colors = 'rgbcymk'
		
		xss = []
		plots = 0
		if series is None:
			if y == 'current':
				kwargs = self.build_filterargs(filters)
					
				slope = self.data.slope(**kwargs)
				if slope == 0:# unavailable data or constant values
					print('unavailable data, args: ', kwargs)
					return
				
				xs, ys = self.data.current_vs_lumi(**kwargs)
				plt.plot(xs, ys, '.', c=colors[0], label='current')
				
				xs, ys = self.data.current_vs_lumi_fit(**kwargs)
				plt.plot(xs, ys, '--', c=colors[0], label='{:.2f} pA/Lumi'.format(slope*1e6))
				
				plt.legend(loc='upper center', ncol=1, frameon=False, numpoints=1)
			else:
				xs, ys = self.getdata(x=x, y=y, filters=filters)
			
				if len(xs) == 0:
					print('unavailable data, args: ', x, y, filters)
					return
				
				xss = xs
				plt.plot(xs, ys, 'o')
		else:
			for arg_nr, arg in enumerate(self.args[series]):
				filters[series] = arg
				
				if y == 'current':
					kwargs = self.build_filterargs(filters)
					
					slope = self.data.slope(**kwargs)
					if slope == 0:# unavailable data or constant values
						continue
					
					xs, ys = self.data.current_vs_lumi(**kwargs)
					plt.plot(xs, ys, '.', c=colors[arg_nr], label=self.labels[series].format(arg))
					
					xs, ys = self.data.current_vs_lumi_fit(**kwargs)
					plt.plot(xs, ys, '--', c=colors[arg_nr], label='{:.2f} pA/Lumi'.format(slope*1e6))
				else:
					xs, ys = self.getdata(x=x, y=y, filters=filters)
						
					if len(ys) == 0 or ys.max() == 0:# unavailable data
						continue
						
					xss.extend(xs)
					plt.plot(xs, ys, 'o', label=self.labels[series].format(arg))
				plots += 1
			
			if plots == 0:
				print('Unavailable data')
				return
				
			xss = np.unique(xss)
			if y == 'current':
				plt.legend(loc='upper center', ncol=plots, frameon=False, numpoints=1)
			else:
				plt.legend(loc='best', numpoints=1)
			
		# filename
		filename = y + '_vs_' + x
		if series is not None:
			filename += '_every_' + series
		
		# labels
		if y == 'slope':
			title = 'Average {place} Current vs Luminosity'.format(place=wire)
		elif y == 'maxcurrent':
			title = r'Maximum {place} Current ($\mu A$)'.format(place=wire)
		elif y == 'current':
			title = 'Average {place} Current vs Luminosity'.format(place=wire)
		title += '\nFill {fill}'.format(fill=self.data.fill)
		
		# build filename and labels based on a filter
		for keyword in self.keywords:
			if not (x==keyword or y==keyword or series==keyword) and filters[keyword] is not None:
				title += ' ' + self.labels[keyword].format(filters[keyword])
				filename += '_' + self.labels[keyword].format(filters[keyword])
		
		plt.title(title)
		
		# axes labels
		if y == 'slope':
			plt.ylabel(r'$pA / Lumi$')
		elif y == 'current':
			plt.xlabel(r'Instantaneous Luminosity ($\mu barn^{-1} \cdot s^{-1}$)')
			plt.ylabel(r'Current ($\mu A$)')
		
		if x is not 'luminosity':
			plt.xlim(xmin=xss.min()-0.5, xmax=xss.max()+0.5)
			plt.xticks(xss, [self.labels[x].format(_x) for _x in xss])
		
		plt.grid()
		
		# save plot
		self.plot_end(filename=filename, format=format)
		
	# draw 2d plot with colormap: 	
	def draw_slope_2d(self, station=4, wire='wires', format='png'):
		values = []
		for wheel in self.data.wheels:
			values.append([self.data.slope(wheel=wheel, sector=sector, wire=wire) for sector in self.data.sectors])
		values = np.array(values) * 1e6
		
		fig, ax = plt.subplots()
		
		im = ax.pcolor(values[::-1], cmap='OrRd', edgecolor='black', linestyle=':', lw=1)
		fig.colorbar(im)
		
		# labels
		ax.xaxis.set(ticks=np.arange(len(self.data.sectors))+0.5, ticklabels=[self.labels['sector'].format(sector) for sector in self.data.sectors])
		ax.yaxis.set(ticks=np.arange(len(self.data.wheels))+0.5, ticklabels=[self.labels['wheel'].format(wheel) for wheel in self.data.wheels][::-1])
		#plt.xlabel('Sector')
		#plt.ylabel('Wheel')
		plt.title(r'Fill {fill} MB{station} slope $pA \cdot \mu barn \cdot s$'.format(fill=self.data.fill, station=station))
		
		# save plot
		filename = 'slope2d_{wire}_MB{station}' \
				.format(wire=wire, station=station)
		self.plot_end(filename=filename, format=format)
		
	# show or save plot
	def plot_end(self, filename='', format='png'):
		plt.tight_layout()
		if format is None:
			plt.show()
		else:
			filename += '.' + format
			plt.savefig(self.path + filename, bbox_inches='tight')
			print('Saved ' + filename)
		plt.clf()