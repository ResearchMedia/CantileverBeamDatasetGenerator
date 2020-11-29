#
# @Author: Philippe Wyder (pmw2125)
# @Description: Utilities for data generation including generatePolygon, clip, getimg
#
#

# imports for generatePolygon
import math, random
#imports for getimg
from PIL import Image, ImageDraw



###
# Polygon Generator
# (Source: https://stackoverflow.com/questions/8997099/algorithm-to-generate-random-2d-polygon)
###
def generatePolygon( ctrX, ctrY, aveRadius, irregularity, spikiness, numVerts ) :
    '''
    Start with the centre of the polygon at ctrX, ctrY, 
    then creates the polygon by sampling points on a circle around the centre. 
    Randon noise is added by varying the angular spacing between sequential points,
    and by varying the radial distance of each point from the centre.

    Params:
    ctrX, ctrY - coordinates of the "centre" of the polygon
    aveRadius - in px, the average radius of this polygon, this roughly controls how large the polygon is, really only useful for order of magnitude.
    irregularity - [0,1] indicating how much variance there is in the angular spacing of vertices. [0,1] will map to [0, 2pi/numberOfVerts]
    spikiness - [0,1] indicating how much variance there is in each vertex from the circle of radius aveRadius. [0,1] will map to [0, aveRadius]
    numVerts - self-explanatory

    Returns a list of vertices, in CCW order.
    '''

    irregularity = clip( irregularity, 0,1 ) * 2*math.pi / numVerts
    spikiness = clip( spikiness, 0,1 ) * aveRadius

    # generate n angle steps
    angleSteps = []
    lower = (2*math.pi / numVerts) - irregularity
    upper = (2*math.pi / numVerts) + irregularity
    sum = 0
    for i in range(numVerts) :
        tmp = random.uniform(lower, upper)
        angleSteps.append( tmp )
        sum = sum + tmp

    # normalize the steps so that point 0 and point n+1 are the same
    k = sum / (2*math.pi)
    for i in range(numVerts) :
        angleSteps[i] = angleSteps[i] / k

    # now generate the points
    points = []
    angle = random.uniform(0, 2*math.pi)
    for i in range(numVerts) :
        r_i = clip( random.gauss(aveRadius, spikiness), 0, aveRadius )
        x = ctrX + r_i*math.cos(angle)
        y = ctrY + r_i*math.sin(angle)
        points.append( (int(x),int(y)) )

        angle = angle + angleSteps[i]

    return points

def clip(x, min, max) :
    if( min > max ) :  return x    
    elif( x < min ) :  return min
    elif( x > max ) :  return max
    else :             return x

def getimg(verts, color, fill, img_max_x = 128, img_max_y = 128):
	if (color == 'grayscale'):
		c1 = (100,100,100)
		c2=(156,156,156)
	else:
		c1 = (0,0,0)
		c2=(255,255,255)
	im = Image.new('RGB', (img_max_x, img_max_y), c2)
	draw = ImageDraw.Draw(im)
	
	# either use .polygon(), if you want to fill the area with a solid colour
	if (fill):
		draw.polygon( verts, outline=c1,fill=c1 )
	else:
		draw.polygon( verts, outline=c1,fill=c2 )

	# Count Nr of pixels made up by cross-section
	nrpx = im.histogram()[c1[0]]

	# or .line() if you want to control the line thickness, or use both methods together!
	#draw.line( tupVerts+[tupVerts[0]], width=2, fill=black )
	return(im, nrpx)

'''
Functions to check for self intersection of polygons
'''
def ccw(a, b, c):
	return( (b[0]-a[0])*(c[1]-a[1])-(c[0]-a[0])*(b[1]-a[1]) )

def intersects(a,b,c,d):
	if (ccw(a, b, c)*ccw(a,b,d) >= 0):
		return False
	elif (ccw(c, d, a)*ccw(c,d,b) >= 0):
		return False
	else:
		return True

def isNonIntersecting(verts):
	for id1 in range(1, len(verts)+1):
		for id2 in range(1, len(verts)+1):
			if intersects(verts[id1-1],verts[id1%len(verts)], verts[id2-1], verts[id2%len(verts)]):
				return False
	return True
