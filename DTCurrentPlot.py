import DTCurrentData
import matplotlib.pyplot as plt
import numpy as np

# makes plots from DT current files.
# usage:
# DTCurrentPlot('pathname/')

path = 'augustfills/3992/'

class DTCurrentPlot(object):
	def __init__(self, path=''):
		self.path = path
		self.load_data()
		self.plot_data()
	
	# load files
	def load_data(self):
		self.data = DTCurrentData.DTCurrentData(self.path)
		
	# plot data
	def plot_data(self):
		for cathode in [False, True]:
			for station in self.data.stationes:
				self.draw_slope_vs_sector_wheels(station=station, cathode=cathode)
				self.draw_maxcurrent_vs_sector_wheels(station=station, cathode=cathode)
				for wheel in self.data.wheels:
					self.draw_slope_vs_sector_superlayers(wheel=wheel, station=station, cathode=cathode)
					self.draw_maxcurrent_vs_sector_superlayers(wheel=wheel, station=station, cathode=cathode)
					for sector in self.data.sectors:
						self.draw_current_vs_lumi(wheel=wheel, station=station, sector=sector, cathode=cathode)
		self.draw_slope_vs_wheel(station=4, sector=4)
		self.draw_maxcurrent_vs_wheel(station=4, sector=4)
		
	# draw line plot: luminosity on x-axis, current on y-axis. With linear regression
	def draw_current_vs_lumi(self, wheel=0, station=1, sector=1, cathode=False, save=True):
		colors = 'rgb'
		plots = 0
		ymax = 0
		for superlayer in self.data.valid_superlayers:
			# filter data
			kwargs = dict(wheel=wheel, station=station, sector=sector, superlayer=superlayer, wire=("cha" if cathode else "wires"))
			
			slope = self.data.slope(**kwargs)
			if slope == 0:# unavailable data or constant values
				continue
			
			plots += 1
			xs, ys = self.data.current_vs_lumi(**kwargs)
			_ymax = ys.max()
			ymax = max(ymax, _ymax)
			# plot data
			plt.plot(xs, ys, '.', c=colors[superlayer-1], label='SL{}w'.format(superlayer))
			
			# plot fit
			xs, ys = self.data.current_vs_lumi_fit(**kwargs)
			plt.plot(xs, ys, '--', c=colors[superlayer-1], label='{:.2f} pA/Lumi'.format(slope*1e6))
		
		if plots == 0:
			return
			
		# limits
		plt.xlim(xmin=0)
		plt.ylim(ymin=0, ymax=ymax*1.3)
		plt.grid()
		
		# plot labels
		plt.title('Average {place} Current vs Luminosity\nFill {fill} YB{wheel:+d} MB{station}S{sector:02d}' \
			.format(place=("Cathode" if cathode else "Wire"), fill=self.data.fill, **kwargs))
		plt.xlabel(r'Instantaneous Luminosity ($\mu barn^{-1} \cdot s^{-1}$)')
		plt.ylabel(r'Current ($\mu A$)')
		
		plt.legend(loc='upper center', ncol=plots, frameon=False, numpoints=1)
		
		# save plot
		filename = 'current_vs_lumi_{place}_YB{wheel:+d}_MB{station}S{sector:02d}.png' \
			.format(place=("cathode" if cathode else "wires"), **kwargs)
		self.plot_end(filename=filename, save=save)
		
	# draw scatter plot: sector on x-axis, d(current)/d(luminosity) on y-axis for each superlayer
	def draw_slope_vs_sector_superlayers(self, station=1, wheel=0, cathode=False, save=True):
		plots = 0
		xss = []
		for superlayer in self.data.valid_superlayers:
			xs, ys = self.data.slope_vs_sector(wheel=wheel, station=station, superlayer=superlayer, wire=("cha" if cathode else "wires"))
			if len(ys) == 0 or ys.max() == 0:# unavailable data
				continue
				
			xss.extend(xs)
			plt.plot(xs, ys*1e6, 'o', label='SL{}w'.format(superlayer))
			plots += 1
		
		if plots == 0:
			return
			
		# axes limits, ticks
		plt.xlim(xmin=0.5, xmax=12.5)
		plt.grid()
		
		# labels
		plt.title('Average {place} Current vs Luminosity\nFill {fill} YB{wheel:+d} MB{station}' \
			.format(place=("Cathode" if cathode else "Wire"), fill=self.data.fill, wheel=wheel, station=station))
		plt.ylabel(r'$pA / Lumi$')
		plt.xticks(self.data.valid_sectors, [('S{:02d}'.format(sector) if sector in xss else '') for sector in self.data.valid_sectors])
		plt.legend(loc='upper center', numpoints=1)
		
		# save plot
		filename = 'slope_vs_sector_{place}_YB{wheel:+d}_MB{station}.png' \
			.format(place=("cathode" if cathode else "wires"), wheel=wheel, station=station)
		self.plot_end(filename=filename, save=save)
		
	# draw scatter plot: sector on x-axis, d(current)/d(luminosity) on y-axis for each wheel	
	def draw_slope_vs_sector_wheels(self, station=1, cathode=False, save=True):
		plots = 0
		xss = []
		for wheel in self.data.wheels:
			xs, ys = self.data.slope_vs_sector(wheel=wheel, station=station, wire=("cha" if cathode else "wires"))
			if ys.max() == 0:# unavailable data
				continue
			xss.extend(xs)
			plt.plot(xs, ys*1e6, 'o', label='YB{:+d}'.format(wheel))
			plots += 1
		
		if plots == 0:
			return
			
		# axes limits
		plt.xlim(xmin=self.data.valid_sectors[0]-0.5, xmax=self.data.valid_sectors[-1]+0.5)
		plt.grid()
		
		# labels
		plt.title('Average {place} Current vs Luminosity\nFill {fill} MB{station}' \
			.format(place=("Cathode" if cathode else "Wire"), fill=self.data.fill, station=station))
		plt.ylabel(r'$pA / Lumi$')
		plt.xticks(self.data.valid_sectors, [('S{:02d}'.format(sector) if sector in xss else '') for sector in self.data.valid_sectors])
		plt.legend(loc='best', numpoints=1)
		
		# save plot
		filename = 'slope_vs_sector_{place}_MB{station}.png' \
			.format(place=("cathode" if cathode else "wires"), station=station)
		self.plot_end(filename=filename, save=save)
			
	# draw scatter plot: wheel on x-axis, d(current)/d(luminosity) on y-axis
	def draw_slope_vs_wheel(self, station=4, sector=4, cathode=False, save=True):
		xs, ys = self.data.slope_vs_wheel(station=station, sector=sector, wire=("cha" if cathode else "wires"))
		if ys.max() == 0:# unavailable data
			return
		
		plt.plot(xs, ys*1e6, 'o')
		
		# labels
		plt.title('Average {place} Current vs Luminosity\nFill {fill} MB{station}S{sector:02d}' \
			.format(place=("Cathode" if cathode else "Wire"), fill=self.data.fill, station=station, sector=sector))
		plt.ylabel(r'$pA / Lumi$')
		plt.xlim(xmin=self.data.valid_wheels[0]-0.5, xmax=self.data.valid_wheels[-1]+0.5)
		plt.xticks(self.data.valid_wheels, [('YB{:+d}'.format(wheel) if wheel in xs else '') for wheel in self.data.valid_wheels])
		plt.grid()
		
		# save plot
		filename = 'slope_vs_wheel_{place}_MB{station}S{sector:02d}.png' \
				.format(place=("cathode" if cathode else "wires"), station=station, sector=sector)
		self.plot_end(filename=filename, save=save)
		
	# draw scatter plot: sector on x-axis, max current on y-axis for each superlayer
	def draw_maxcurrent_vs_sector_superlayers(self, station=1, wheel=0, cathode=False, save=True):
		plots = 0
		xss = []
		for superlayer in self.data.valid_superlayers:
			xs, ys = self.data.maxcurrent_vs_sector(wheel=wheel, station=station, superlayer=superlayer, wire=("cha" if cathode else "wires"))
			if len(ys) == 0 or ys.max() == 0:# unavailable data
				continue
				
			xss.extend(xs)
			plt.plot(xs, ys, 'o', label='SL{}w'.format(superlayer))
			plots += 1
		
		if plots == 0:
			return
			
		# axes limits
		plt.xlim(xmin=0.5, xmax=12.5)
		plt.grid()
		
		# labels
		plt.title('Maximum {place} Current\nFill {fill} YB{wheel:+d} MB{station}' \
			.format(place=("Cathode" if cathode else "Wire"), fill=self.data.fill, wheel=wheel, station=station))
		plt.ylabel(r'$\mu A$')
		plt.xticks(self.data.valid_sectors, [('S{:02d}'.format(sector) if sector in xss else '') for sector in self.data.valid_sectors])
		plt.legend(loc='upper center', numpoints=1)
		
		# save plot
		filename = 'maxcurrent_vs_sector_{place}_YB{wheel:+d}_MB{station}.png' \
			.format(place=("cathode" if cathode else "wires"), wheel=wheel, station=station)
		self.plot_end(filename=filename, save=save)
				
	# draw scatter plot: sector on x-axis, max current on y-axis for each wheel
	def draw_maxcurrent_vs_sector_wheels(self, station=1, cathode=False, save=True):
		plots = 0
		xss = []
		for wheel in self.data.wheels:
			xs, ys = self.data.maxcurrent_vs_sector(wheel=wheel, station=station, wire=("cha" if cathode else "wires"))
			if ys.max() == 0:# data unavailable
				continue
			xss.extend(xs)
			plt.plot(xs, ys, 'o', label='YB{:+d}'.format(wheel))
			plots += 1
		
		if plots == 0:
			return
		# axes limits
		plt.xlim(xmin=self.data.valid_sectors[0]-0.5, xmax=self.data.valid_sectors[-1]+0.5)
		plt.grid()
		
		# labels
		plt.title('Maximum {place} Current\nFill {fill} MB{station}'.format(place=("Cathode" if cathode else "Wire"), fill=self.data.fill, station=station))
		plt.ylabel(r'$\mu A$')
		plt.xticks(self.data.valid_sectors, [('S{:02d}'.format(sector) if sector in xss else '') for sector in self.data.valid_sectors])
		plt.legend(loc='best', numpoints=1)
		
		# save plot
		filename = 'maxcurrent_vs_sector_{place}_MB{station}.png'.format(place=("cathode" if cathode else "wires"), station=station)
		self.plot_end(filename=filename, save=save)
			
	# draw scatter plot: wheel on x-axis, max current on y-axis
	def draw_maxcurrent_vs_wheel(self, station=4, sector=4, cathode=False, save=True):
		xs, ys = self.data.maxcurrent_vs_wheel(station=station, sector=sector, wire=("cha" if cathode else "wires"))
		if ys.max() == 0:# data unavailable
			return
		
		plt.plot(xs, ys, 'o')
		
		# labels
		plt.title('Maximum {place} Current\nFill {fill} MB{station}S{sector:02d}' \
			.format(place=("Cathode" if cathode else "Wire"), fill=self.data.fill, station=station, sector=sector))
		plt.ylabel(r'$\mu A$')
		plt.xlim(xmin=self.data.valid_wheels[0]-0.5, xmax=self.data.valid_wheels[-1]+0.5)
		plt.xticks(self.data.valid_wheels, [('YB{:+d}'.format(wheel) if wheel in xs else '') for wheel in self.data.valid_wheels])
		plt.grid()
		
		# save plot
		filename = 'maxcurrent_vs_wheel_{place}_MB{station}S{sector:02d}.png' \
				.format(place=("cathode" if cathode else "wires"), station=station, sector=sector)
		self.plot_end(filename=filename, save=save)
		
	# show or save plot
	def plot_end(self, filename='', save=True):
		plt.tight_layout()
		if save:
			plt.savefig(self.path + filename, bbox_inches='tight')
			print('Saved ' + filename)
		else:
			plt.show()
		plt.clf()
		
# load files and make plots
DTCurrentPlot(path)