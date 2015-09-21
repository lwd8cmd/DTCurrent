import re
import time
import datetime
import numpy as np
from os import walk

# loads CMS DT current log files and returns average currents

class DTCurrentData(object):
	def __init__(self, path=''):
		# initial values filled during loading
		self.loaded = False
		self.path = ""
		self.dates = []
		self.times = []
		self.timestamps = []
		self.luminosity = []
		self.fill = ""
		self.currents = None
		self.background = None
		
		# valid filter options
		self.valid_wheels = np.array([-2,-1,0,1,2])
		self.valid_stations = np.array([1,2,3,4])
		self.valid_sectors = np.array([1,2,3,4,5,6,7,8,9,10,11,12])
		self.valid_superlayers = np.array([1,2,3])
		self.valid_layers = np.array([1,2,3,4])
		self.valid_wires = ["wire0", "wire1", "cathode"]
		
		# autoload data if path is specified
		if path:
			self.load_path(path)
	
	# look for files in dir
	def load_path(self, path):
		self.path = path.rstrip('/')+'/'
		
		_, _, files = walk(self.path).next()
		files_nr = 0
		for file in files:
			m = re.search("^W(M|0|P)([0-2])_MB([1-4])_S([0-9]{2})(L|)\.txt$", file)
			if not m:# filename is not in the correct form: eg WM2_MB1_S07.txt
				continue
			self.load_file(self.path + file)
			files_nr += 1
		
		print('Loaded {files} files from path {path}'.format(files=files_nr, path=path))
		self.loaded = True
			
		# check which wheels, stations and sectors files have been found
		wheels = []
		for wheel in self.valid_wheels:
			_r = self.get(wheel=wheel)
			if _r is not None and _r.max() > 0:
				wheels.append(wheel)
		self.wheels = np.array(wheels)
				
		stations = []
		for station in self.valid_stations:
			_r = self.get(station=station)
			if _r is not None and _r.max() > 0:
				stations.append(station)
		self.stations = np.array(stations)
				
		sectors = []
		for sector in self.valid_sectors:
			_r = self.get(sector=sector)
			if _r is not None and _r.max() > 0:
				sectors.append(sector)
		self.sectors = np.array(sectors)
			
	# load one txt file
	def load_file(self, filename):
		dates = []
		times = []
		timestamps = []
		luminosity = []
		currents = []
		
		# read file contents
		with open(filename) as fp:
			for line_nr, line in enumerate(fp):
				if line_nr == 0:
					# file header
					# File for chamber WP2_MB1_S10 for Fill 2984 created at 18-08-2012 09:35:21
					m = re.search("^File for chamber (.+?) for Fill ([0-9]+?) created at ([0-9\-]+?) ([0-9:]{8})", line)
					if not m:
						print("File header is in wrong format")
						return
					chamber, self.fill, _, _ = m.groups()
					
					# parse wheel, station and sector number from chamber name
					chamber_p = re.search("^W(M|0|P)([0-2])_MB([1-4])_S([0-9]{2})(L|)$", chamber)
					if not chamber_p:
						print("Unknown chamber syntax {chamber} in file {file}".format(chamber=chamber, file=filename))
						return
					mp0, wheel_abs, station_str, sector_str, _ = chamber_p.groups()
					wheel = int(wheel_abs) * (1 if mp0 is 'P' else -1)
					station = int(station_str)
					sector = int(sector_str)
				elif line_nr == 1:
					# tabs info
					#          Date     Time      State       Lumi   L1W0    L1W1   L1Cha   L2W0
					continue
				else:
					# data
					#    18-08-2012 09:35:21    STANDBY       0.65  0.000   0.000   0.000  0.000
					data = line.split()
					if not (data[2] == "ON"):# status is RAMPING or STANDBY
						continue
					dates.append(data[0])
					times.append(data[1])
					timestamps.append(datetime.datetime.strptime(data[0]+' '+data[1], "%d-%m-%Y %H:%M:%S"))
					luminosity.append(float(data[3]))
					currents.append([float(i) for i in data[4:]])
		
		# use numpy arrays (easier to manipulate)
		luminosity = np.array(luminosity)
		currents = np.array(currents)
		
		# calculate background current (bg=mean values where state=ON and luminosity<10 at the beginning)
		bgrows = np.argmax(luminosity > 10)
		background = currents[: bgrows].mean(0)
		
		# remove rows with small luminosity from the beginning (during ramping)
		imax = np.argmax(luminosity)
		currents = currents[imax:]
		luminosity = luminosity[imax:]
		
		# number of different options
		wheels = len(self.valid_wheels)
		stations = len(self.valid_stations)
		sectors = len(self.valid_sectors)
		superlayers = len(self.valid_superlayers)
		layers = len(self.valid_layers)
		wires = len(self.valid_wires)
		rows = len(currents)
		
		# create array to hold ALL files data
		if self.currents is None:
			shape = (wheels, stations, sectors, superlayers, layers, wires, rows)
			self.currents = np.ma.array(np.zeros(shape, dtype=np.float), mask=True)
			self.background = np.ma.array(np.zeros(shape, dtype=np.float), mask=True)
			self.luminosity = luminosity
			
		# insert this chamber data to global current data
		if station == 4:
			superlayers -= 1
		rows = min(rows, self.currents.shape[6])
		shape = (superlayers, layers, wires, rows)
		self.currents[wheel+2, station-1, sector-1, :superlayers, :, :, :rows] = currents[:rows].T.reshape(shape)
		self.background[wheel+2, station-1, sector-1, :superlayers, :, :, :rows] = np.tile(background, rows).reshape((-1,len(background))).T.reshape(shape)
		
	# get mean values using specified filters
	def get(self, wheel=None, station=None, sector=None, superlayer=None, layer=None, wire='wires', fit=None, get_slope=None, background=False):
		if not self.loaded:
			print("Data file is not loaded")
			return
		background=True	
		# subtract background (default) or use original values
		if background:
			c = self.currents
		else:
			c = self.currents - self.background
		
		# filter by wheel
		if wheel is None:
			c = c.mean(0)
		elif wheel in self.valid_wheels:
			c = c[wheel+2]
		else:
			print("wheel value should be " + '|'.join(map(str, self.valid_wheels)) + "|None")
			return
			
		# filter by station
		if station is None:
			c = c.mean(0)
		elif station in self.valid_stations:
			c = c[station-1]
		else:
			print("station value should be " + '|'.join(map(str, self.valid_stations)) + "|None")
			return
			
		# filter by sector
		if sector is None:
			c = c.mean(0)
		elif sector in self.valid_sectors:
			c = c[sector-1]
		else:
			print("sector value should be " + '|'.join(map(str, self.valid_sectors)) + "|None")
			return
			
		# filter by superlayer
		if superlayer is None:
			c = c.mean(0)
		elif superlayer in self.valid_superlayers:
			c = c[superlayer-1]
		else:
			print("superlayer value should be " + '|'.join(map(str, self.valid_superlayers)) + "|None")
			return
			
		# filter by layer
		if layer is None:
			c = c.mean(0)
		elif layer in self.valid_layers:
			c = c[layer-1]
		else:
			print("layer value should be " + '|'.join(map(str, self.valid_layers)) + "|None")
			return
			
		# filter by wire
		if wire=="wires":
			c = (c[0] + c[1]) * 0.5
		elif wire == "wire0":
			c = c[0]
		elif wire == "wire1":
			c = c[1]
		elif wire == "cathode":
			c = c[2]
		else:
			print("wire value should be wire0|wire1|wires|cathode")
			return
		
		# linear regression
		if fit or get_slope:
			# fit only values above 0 (useful in cathode plots, where current vs lumi goes like 0000001234)
			mask1 = c.data > 0
			
			# remove points that differs more than 0.02*3 from nearby values mean (outliers)
			mask2 = np.insert((c[1:-1]*2 - c[:-2] - c[2:]) < 0.02 * 3, [0, -1], [True, True])
			mask = mask1 * mask2 * ~c.mask
			
			intercept = 0
			if mask.sum() < 10:# less than 10 points after masking, dont fit
				slope = 0
			else:
				# current = slope * luminosity
				# slope, = np.linalg.lstsq(self.luminosity[:,np.newaxis], retval)[0]
				
				# current = slope * luminosity + intercept
				slope, intercept = np.linalg.lstsq(np.vstack([self.luminosity[mask], np.ones(len(self.luminosity[mask]))]).T, c[mask])[0]
			
			# return slope or fitted data?
			if get_slope:
				return slope
			
			return slope * self.luminosity + intercept
			
		return c
		
	# return slope: d(current)/d(luminosity)
	def slope(self, wheel=None, station=None, sector=None, superlayer=None, layer=None, wire='wires'):
		return self.get(wheel=wheel, station=station, sector=sector, superlayer=superlayer, layer=layer, wire=wire, get_slope=1)
		
	# return max current
	def maxcurrent(self, wheel=None, station=None, sector=None, superlayer=None, layer=None, wire='wires'):
		return self.get(wheel=wheel, station=station, sector=sector, superlayer=superlayer, layer=layer, wire=wire, background=True).max()
		
	# return current for each luminosity
	def current_vs_lumi(self, wheel=None, station=None, sector=None, superlayer=None, layer=None, wire='wires'):
		xs = self.luminosity
		ys = self.get(wheel=wheel, station=station, sector=sector, superlayer=superlayer, layer=layer, wire=wire)
		return (xs, ys)
		
	# return fitted current for each luminosity
	def current_vs_lumi_fit(self, wheel=None, station=None, sector=None, superlayer=None, layer=None, wire='wires'):
		xs = self.luminosity
		ys = self.get(wheel=wheel, station=station, sector=sector, superlayer=superlayer, layer=layer, wire=wire, fit=1)
		return (xs, ys)
		
	# return slope for each wheel
	def slope_vs_wheel(self, wheel=None, station=None, sector=None, superlayer=None, layer=None, wire='wires'):
		ys = [self.slope(wheel=wheel, station=station, sector=sector, superlayer=superlayer, layer=layer, wire=wire) for wheel in self.wheels]
		return (self.wheels, np.array(ys))
	
	# return max current for each wheel
	def maxcurrent_vs_wheel(self, wheel=None, station=None, sector=None, superlayer=None, layer=None, wire='wires'):
		ys = [self.maxcurrent(wheel=wheel, station=station, sector=sector, superlayer=superlayer, layer=layer, wire=wire) for wheel in self.wheels]
		return (self.wheels, np.array(ys))
		
	# return slope for each station
	def slope_vs_station(self, wheel=None, station=None, sector=None, superlayer=None, layer=None, wire='wires'):
		ys = [self.slope(wheel=wheel, station=station, sector=sector, superlayer=superlayer, layer=layer, wire=wire) for station in self.stations]
		return (self.stations, np.array(ys))
		
	# return max current for each station
	def maxcurrent_vs_station(self, wheel=None, station=None, sector=None, superlayer=None, layer=None, wire='wires'):
		ys = [self.maxcurrent(wheel=wheel, station=station, sector=sector, superlayer=superlayer, layer=layer, wire=wire) for station in self.stations]
		return (self.stations, np.array(ys))
		
	# return slope for each sector
	def slope_vs_sector(self, wheel=None, station=None, sector=None, superlayer=None, layer=None, wire='wires'):
		xs = []
		ys = []
		for sector in self.sectors:
			slope = self.slope(wheel=wheel, station=station, sector=sector, superlayer=superlayer, layer=layer, wire=wire)
			if slope > 0:
				xs.append(sector)
				ys.append(slope)
		return (np.array(xs), np.array(ys))
		
	# return max current for each sector
	def maxcurrent_vs_sector(self, wheel=None, station=None, sector=None, superlayer=None, layer=None, wire='wires'):
		xs = []
		ys = []
		for sector in self.sectors:
			maxcurrent = self.maxcurrent(wheel=wheel, station=station, sector=sector, superlayer=superlayer, layer=layer, wire=wire)
			if maxcurrent > 0:
				xs.append(sector)
				ys.append(maxcurrent)
		return (np.array(xs), np.array(ys))