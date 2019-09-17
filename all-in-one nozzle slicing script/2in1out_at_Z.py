#Name:2in1out at Z(ratio) QQ group:118582381
#Info: default: 0.95 at bottom and 0.05 at top
#Depend: GCode
#Type: postprocess
#Param: Z_ratio(float:0.5) height ratio (0.0-1.0)
#Param: extrude_ratio(float:0.5) E1 ratio(0.05-0.95)
#Param: b_gradient(int:1) 1:gradient(default)  0:don't gradient

# #__copyright__ = "Copyright@yiyu:QQ296721137 "
import re
import copy

def getValue(line, key, default=None):
	if not key in line:
		return default
	subPart = line[line.find(key) + len(key):]
	m = re.search('^[0-9]+\.?[0-9]*', subPart)
	if m is None:
		return default
	try:
		return float(m.group(0))
	except:
		return default


def getHeight(file_lines):
	try:
		layer = -1
		height = 1.0
		for line in file_lines:
			if line.startswith(';Layer count: '):
				layer = int(getValue(line, ';Layer count: ', layer))
			elif line.startswith(';End GCode'):
				break
			elif line.startswith(';LAYER:'):
				if int(getValue(line, ';LAYER:', 0)) == layer - 1:
					break;
			else:
				code = getValue(line, 'G', None)
				if code == 1 or code == 0:
					height = getValue(line, 'Z', height)
		return float(height)
	except Exception as e:
		print e
		return 1.0
		
with open(filename, "r") as f:
	lines = f.readlines()
	
height = 0.0

for line in lines:
	if ';MAX_Z_HEIGHT:' in line:  # checks for state change comment
			height = getValue(line, ';MAX_Z_HEIGHT:', height)
	break;
	
if height == 0.0:
	height = getHeight(lines)
print height
	
height_list = []
ratio_list = []
b_gradient_list = []
for line in lines:  # ;DUAL_IN_ONE_OUT:ratio:0.3 height_ratio:0.3 /height:34
	if ';DUAL_IN_ONE_OUT:' in line:  # checks for state change comment
			ratio_list.append(getValue(line, 'ratio:', 0.0))
			b_gradient_list.append(int(getValue(line, 'gradient:', 0)))
			height_ratio = getValue(line, 'height_ratio:', -1)
			if height_ratio != -1:
				height_list.append(height * height_ratio)
			else:
				height_list.append(getValue(line, 'height:', 0))
	
print "----------list start----------------------"
print height_list
print ratio_list
print b_gradient
print "-----------list start---------------------"
def item_in_list(list, item):
	try:
		return list.index(item) >= 0
	except:
		return 0

if(item_in_list(height_list, Z_ratio * height) == 0):
	height_list.append(Z_ratio * height)
	ratio_list.append(extrude_ratio)
	b_gradient_list.append(int(b_gradient))
else:
	ratio_list[height_list.index(Z_ratio * height)] = extrude_ratio
	b_gradient_list[height_list.index(Z_ratio * height)] = int(b_gradient)

if(item_in_list(height_list, 0.0) == 0):
	height_list.append(0.0)
	ratio_list.append(1.0)
	b_gradient_list.append(int(1))
if(item_in_list(height_list, height) == 0):
	height_list.append(height)
	ratio_list.append(0.0)
	b_gradient_list.append(int(1))

	
mapped_height_list = copy.deepcopy(height_list)
mapped_height_list.sort()
mapped_ratio_list = []
mapped_gradient_list = []
mapped_ratio_step = []
for h in mapped_height_list:
	t_ratio = ratio_list[height_list.index(h)]
	if t_ratio < 0.05:
		t_ratio = 0.05
	if t_ratio > 0.95:
		t_ratio = 0.95
	mapped_ratio_list.append(t_ratio)
	mapped_gradient_list.append(b_gradient_list[height_list.index(h)])

	
for h in mapped_height_list:
	index = mapped_height_list.index(h)
	if index != len(mapped_height_list) - 1 and mapped_height_list[index] != mapped_height_list[index + 1] :
		mapped_ratio_step.append((mapped_ratio_list[index + 1] - mapped_ratio_list[index]) / (mapped_height_list[index + 1] - mapped_height_list[index]))
	else:
		mapped_ratio_step.append(0.0)
		
print "----------map list start----------------------"
print 	mapped_height_list
print 	mapped_ratio_list
print 	mapped_ratio_step
print 	mapped_gradient_list
print "----------map list end----------------------"

with open(filename, "w") as f:
	layer_init = 0
	f.write(";MAX_Z_HEIGHT:%f\n" % (height))
	for line in lines:
		if line.startswith(';MAX_Z_HEIGHT:'):
			continue
		elif layer_init == 0:
			if line.startswith('M117 Printing'):
				layer_init = 1
		elif line.startswith('M6050'):
			continue
		elif(len(mapped_height_list) > 0):
			if line.startswith('G') and (getValue(line, 'G', None) == 1 or getValue(line, 'G', None) == 0):
				Z = getValue(line, 'Z', None)
				if Z != None and Z >= mapped_height_list[0]:
					curr_step = 0.0
					if mapped_gradient_list[0] == 1:
						curr_step = mapped_ratio_step[0]
					curr_ratio = mapped_ratio_list[0] + mapped_ratio_step[0] * (Z - mapped_height_list[0])
					f.write("M6050 S%f P%f Z%f;DUAL_IN_ONE_OUT:ratio:%f height:%f gradient:%d\n" % (curr_ratio, curr_step, mapped_height_list[0], mapped_ratio_list[0], mapped_height_list[0],mapped_gradient_list[0]))
					del mapped_height_list[0]
					del mapped_ratio_list[0]
					del mapped_ratio_step[0]
					del mapped_gradient_list[0]
		f.write(line)
			
