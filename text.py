from io import StringIO
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import xml.etree.ElementTree as ET

fid = StringIO()

# Data for plotting
t = np.arange(0.0, 2.0, 0.01)
s = 1 + np.sin(2 * np.pi * t)

fig, ax = plt.subplots()
ax.plot(t, s)

ax.set(xlabel='time (s)', ylabel='voltage (mV)',
       title='About as simple as it gets, folks')
ax.grid()

#fig.savefig("test.svg", format="svg", transparent=True)
fig.savefig(fid, format="svg", transparent=True)
fid.seek(0)

#with fid as f:
#	print(f.readlines())

tree = ET.parse(fid)
root = tree.getroot()
#print(root.attrib)

#or child in root:
#	print(child.tag, child.attrib)


for g in root.iter("{http://www.w3.org/2000/svg}g"):
	g_dict = g. attrib
	if "id" in g_dict and g_dict["id"] == "figure_1":
		g.set("inkscape:groupmode", "layer")
		g.set("inkscape:label", "mpl" )
	print(g.attrib)

#for child in root:
#	print(child.tag, child.attrib)

"""
with fid as f:
	svg_list = f.readlines()
	print(svg_list)
"""
#plt.show()
