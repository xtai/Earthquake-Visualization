# Earthquake Visualization
#
# Homework 05 for DMS 423 Fall 14
# by Xiaoyu Tai
#
# Input Data type: Geojson
# 
# "M ? - Papua, Indonesia, 1978-06-17 23:38:51.5" -> Mag=6.4
# http://comcat.cr.usgs.gov/earthquakes/eventpage/pde19780618033851500_86

import json, time, datetime, calendar#, urllib
from pyglet.gl import *

## App Settings:
window    = pyglet.window.Window(1024,576)
json_file = "1950-65.json"
speed     = 0.3
duration  = 2

## App is able to use online geojson file by import urllib and uncomment following lines:
# url       = "http://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/1.0_month.geojson"
# json_file = urllib.urlopen(url);

class EarthQuake:
	def __init__(self, longitude, latitude, dep, mag, time, title):
		self.longitude = longitude
		self.latitude  = latitude
		self.dep = dep
		self.mag = mag
		self.time = int(float(time)/1000)
		self.title = title
		self.alpha = 0.5
		self.loaded = 0
	def load(self):
		self.datetime  = datetime.datetime.fromtimestamp(int(self.time)/1000)
		self.vlist = pyglet.graphics.vertex_list(4, ("v2f",[-1,-1,1,-1,-1,1,1,1]), ('t2f', [0,0, 1,0, 0,1, 1,1]))
		self.x = self.longitude * 128/45
		self.y = self.latitude * 128/45 + 64
		self.green = float(self.dep)/720
		self.texture = quake_texture
		self.size = 2**(self.mag-3.3)
		self.loaded = 1
	def draw(self):
		if self.loaded:
			glEnable(GL_BLEND)
			glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
			if self.dep:
				glColor4f(1,self.green,0,self.alpha)
			else: # Some earthquakes' depth is unavailable
				glColor4f(1,1,1,self.alpha)
			glEnable(GL_TEXTURE_2D)
			glBindTexture(GL_TEXTURE_2D, self.texture.id)
			glPushMatrix()
			glTranslatef(self.x+512, self.y+256, 0)
			glScalef(self.size, self.size, self.size)
			self.vlist.draw(GL_TRIANGLE_STRIP)
			glPopMatrix()
			glBindTexture(GL_TEXTURE_2D, 0)
			glDisable(GL_TEXTURE_2D)
			glDisable(GL_BLEND)

class Background:
	def __init__(self, x,y, xoffset,yoffset, texturefile):
		self.texture = pyglet.image.load(texturefile).get_texture()
		self.vlist = pyglet.graphics.vertex_list(4, ('v2f', [xoffset,yoffset, xoffset+x,yoffset, xoffset,yoffset+y, xoffset+x,yoffset+y]), ('t2f', [0,0, 1,0, 0,1, 1,1]))
	def draw(self):
		glEnable(GL_BLEND)
		glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
		glColor3f(1,1,1)
		glEnable(GL_TEXTURE_2D)
		glBindTexture(GL_TEXTURE_2D, self.texture.id)
		glPushMatrix()
		self.vlist.draw(GL_TRIANGLE_STRIP)
		glPopMatrix()
		glBindTexture(GL_TEXTURE_2D, 0)
		glDisable(GL_TEXTURE_2D)
		glDisable(GL_BLEND)

# creating a initialization function so that the app can reset it self
def init():
	global all_quakes, onscreen_quakes, indicative_quakes, indicative_text
	global app_start_time, app_pause_time, app_wait_time, current_time
	global pause_holder, h_holder, year, quake_texture
	global last_quake_time, offset
	global background_map, background_banner, background_help
	global onqueue_first, onqueue_last
	all_quakes, onscreen_quakes, indicative_quakes, indicative_text = [], [], [], []
	app_start_time, app_pause_time, app_wait_time  = time.time(), 0, -1
	current_time = app_start_time
	pause_holder, h_holder = 1, 1
	j = open(json_file, "r")
	d = json.loads(j.read())
	year = 31556926
	quake_texture = pyglet.image.load("support/quake.png").get_texture()
	for e in d['features']:
		all_quakes.append(EarthQuake(e['geometry']['coordinates'][0],
			e['geometry']['coordinates'][1],e['geometry']['coordinates'][2],
			e['properties']['mag'],e['properties']['time'],e['properties']['title']))
	last_quake_time, offset = all_quakes[0].time, all_quakes[0].time
	indicative_quakes.append(EarthQuake(55,-100.95,10,7.6,time.time(),None))
	indicative_quakes.append(EarthQuake(70,-100.95,200,7.6,time.time(),None))
	indicative_quakes.append(EarthQuake(85,-100.95,700,7.6,time.time(),None))
	indicative_quakes.append(EarthQuake(100,-100.95,0,7.6,time.time(),None))
	indicative_text.append(pyglet.text.Label("Magnitude: 9   8 76", x=824, y=32, anchor_y="center", color=(255,255,255,200)))
	indicative_text.append(pyglet.text.Label("Depth (KM):    10     200    700    N/A", x=558, y=32, anchor_y="center", color=(255,255,255,200)))
	indicative_text.append(pyglet.text.Label("", x=13, y=43, anchor_y="center", color=(255,255,255,200)))
	indicative_text.append(pyglet.text.Label(json_file+" is loaded", x=13, y=21, anchor_y="center", color=(255,255,255,200)))
	indicative_text.append(pyglet.text.Label("", x=470, y=43, anchor_y="center", color=(255,255,255,100)))
	background_map    = Background(1024,512,0,64,"support/blue.jpg")
	background_banner = Background(1024,128,0,0,"support/banner.png")
	background_help   = Background(1024,512,0,32,"support/help.png")
	for o in indicative_quakes:
		o.load()
	onscreen_quakes.append(all_quakes[0])
	onscreen_quakes[-1].load()
	onqueue_last, onqueue_first = 0, 0

@window.event
def on_draw():
	glClear(GL_COLOR_BUFFER_BIT)
	background_map.draw()
	background_banner.draw()
	objects = indicative_quakes + onscreen_quakes + indicative_text
	for o in objects:
		o.draw()
	if h_holder:
		background_help.draw()

def update(dt):
	global last_quake_time
	update_pause()
	if last_quake_time >= all_quakes[-1].time:
		last_quake_time = all_quakes[-1].time
	else:
		last_quake_time = int((current_time-app_start_time)*year*speed + offset)
	update_quakes(last_quake_time, year*duration)
	update_text()

# when SPACE key is pressed
def update_pause():
	global app_start_time, app_wait_time, app_pause_time, current_time
	if pause_holder:
		if app_wait_time == -1:
			app_wait_time = time.time()
		else:
			app_pause_time = (time.time() - app_wait_time)
	else:
		if app_wait_time != -1:
			app_start_time += app_pause_time
			app_wait_time = -1
		current_time = time.time()

# update on-screen earthquakes time range and "should-be time"
def update_text():
	if len(onscreen_quakes):
		t1 = datetime.datetime.fromtimestamp(onscreen_quakes[0].time)
		t2 = datetime.datetime.fromtimestamp(onscreen_quakes[-1].time)
		t3 = datetime.datetime.fromtimestamp(last_quake_time)
		indicative_text[2].text = "On Screen: %d quakes from %s,%s to %s,%s (%d years)" % (len(onscreen_quakes), calendar.month_abbr[t1.month], t1.year, calendar.month_abbr[t2.month], t2.year, duration)
		indicative_text[4].text = "%s,%s" % (calendar.month_abbr[t3.month], t3.year)

# given last displayed time and time duration to update on screen earthquakes
def update_quakes(t, dt):
	global onscreen_quakes, onqueue_first, onqueue_last, pause_holder
	if len(onscreen_quakes):
		if onscreen_quakes[0].time < (t - dt):
			onscreen_quakes.pop(0)
			onqueue_first += 1
		if onscreen_quakes[-1].time > t:
			onscreen_quakes.pop()
			onqueue_last -= 1
	else:
		onqueue_last -= 1
		if onqueue_last < 0:
			onqueue_last = 0
	if onqueue_last+1 < len(all_quakes) and all_quakes[onqueue_last+1].time < t:
		onqueue_last += 1
		onscreen_quakes.append(all_quakes[onqueue_last])
		onscreen_quakes[-1].load()
		if onscreen_quakes[-1].mag > 7.8:
			update_title(onscreen_quakes[-1])
	if onqueue_first-1 > 0 and all_quakes[onqueue_first-1].time > t-dt:
		onqueue_first -= 1
		onscreen_quakes.insert(0, all_quakes[onqueue_first])
		onscreen_quakes[0].load()
		if onscreen_quakes[0].mag > 7.8:
			update_title(onscreen_quakes[-1])
	if onqueue_last+1 == len(all_quakes):
		pause_holder = 1

# update earthquake-describing text in bottom left corner
def update_title(q):
	global indicative_text
	d = datetime.datetime.fromtimestamp(q.time)
	t = str(q.dep)
	t += " KM - " + q.title
	if len(q.title) > 55:
		t = t[0:52] + "..."
	t += " - " + calendar.month_abbr[d.month] + " " + str(d.day) + ", " + str(d.year)
	indicative_text[3].text = t

# distance function for calculating distance between two dots
def distance(a, b):
	return (a[0] - b[0])**2 + (a[1] - b[1])**2

# detecting key:SPACE for pause
# key:LEFT/RIGHT for adjusting "should-be time"
# key:UP/DOWN for adjusting "duration time"
# key:R for reset and start over
# key:H for help infomation
@window.event
def on_key_press(symbol, modifiers):
	global pause_holder, h_holder, app_start_time, app_pause_time, last_quake_time, duration
	if symbol == pyglet.window.key.SPACE:
		pause_holder = not pause_holder
		if h_holder:
			h_holder = 0
	elif symbol == pyglet.window.key.RIGHT:
		if onqueue_last+1 != len(all_quakes):
			app_start_time -= 1/speed
			last_quake_time -= 1/speed
	elif symbol == pyglet.window.key.LEFT:
		if onqueue_first != 0:
			app_start_time += 1/speed
			last_quake_time += 1/speed
	elif symbol == pyglet.window.key.DOWN:
		duration -= 1
		if duration < 1:
			duration = 1
	elif symbol == pyglet.window.key.UP:
		duration += 1
		if duration > 20:
			duration = 20
	elif symbol == pyglet.window.key.R:
		init()
	elif symbol == pyglet.window.key.H:
		h_holder = not h_holder
		if not pause_holder:
			pause_holder = 1

# when mouse clicking, display the earthquake's information in bottom left corner 
@window.event
def on_mouse_press(x,y, dx,dy):
	for o in onscreen_quakes:
		if distance((o.x+512, o.y+256), (x,y)) <= o.size**2:
				update_title(o)

# during pause, hovering to an earthquake and bottom-left-corner will be updated for that quake
@window.event
def on_mouse_motion(x,y, dx,dy):
	if pause_holder:
		for o in onscreen_quakes:
			if distance((o.x+512, o.y+256), (x,y)) <= o.size**2:
				update_title(o)

init()
pyglet.clock.schedule_interval(update,1/200.0)
pyglet.app.run()