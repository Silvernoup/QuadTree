from java.util import ArrayList

from collections import defaultdict
from java.awt.event import KeyEvent
from java.lang.reflect import Modifier

key_names = defaultdict(lambda: 'UNKNOWN')
for f in KeyEvent.getDeclaredFields():
    if Modifier.isStatic(f.getModifiers()):
        name = f.getName()
        if name.startswith("VK_"):
            key_names[f.getInt(None)] = name[3:]


#############################################################################################################
#############################################################################################################
############################################                      ###########################################
############################################         MAIN         ###########################################
############################################                      ###########################################
#############################################################################################################
#############################################################################################################

######## Constants ###

# Screen dimensions
screen_w = 950
screen_h = 1040
# Width of mouse zone
rect_w = 150
# Variance distribution
variance = 20
# QuadTree Capacity
capa = 4

######## 

def setup():
    
    size(screen_w,screen_h)
    global quadT
    quadT = QuadTree(capa, Boundary([screen_w/2, screen_h/2], [screen_w/2, screen_h/2]))
    
    global points 
    points = ArrayList()


def draw(): 
    
    background(50)

    quadT = QuadTree(capa, Boundary([screen_w/2, screen_h/2], [screen_w/2, screen_h/2]))
    for p in points:
        quadT.insertPoint(p)

    quadT.show()
    #print(quadT.pArray)
    drawMouseZone(rect_w)

    pointsInMouseRect = 0
    if quadT.queryRange(Boundary([mouseX, mouseY], [rect_w/2, rect_w/2])):
        
        for p in quadT.queryRange(Boundary([mouseX, mouseY], [rect_w/2, rect_w/2])):
            p.researched = True
            pointsInMouseRect += 1


    textSize(16)
    fill(255)
    text(str(frameRate), 10, 20)
    text(str(pointsInMouseRect), 10, 40)



#############################################################################################################
#############################################################################################################
############################################                        #########################################
############################################         CLASSES        #########################################
############################################                        #########################################
#############################################################################################################
#############################################################################################################

class Point():
    
    global max_count 
    max_count = 5

    def __init__(self, center, radius):
        
        # center
        self.center = center
        # radius
        self.radius = radius
        # Point moves
        self.moving = True
        # Moving coefficient
        self.move_coef = 3
        # Moving counter
        self.count = 0
        # colors
        self.researched = False
        self.c = [150, 150, 150, 140]
        self.c_focus = [255, 0, 0, 140]

        

    def show(self):
        
        # Moving point
        if self.moving:
            self.move()
        
        # Draw point
        if self.researched:
            fill(self.c_focus[0], self.c_focus[1],self.c_focus[2],self.c_focus[3])
            stroke(self.c_focus[0], self.c_focus[1],self.c_focus[2],self.c_focus[3])
        else:
            fill(self.c[0], self.c[1],self.c[2],self.c[3])
            stroke(50)

        circle(self.center[0], self.center[1], self.radius)
        self.researched = False
        
    def move(self):

        self.count += 1
        if self.count == max_count:
            self.count = 0
            # Update position
            self.center[0] += self.move_coef * random(-1, 1)
            self.center[1] += self.move_coef * random(-1, 1)
        
        
class Boundary():
    
    def __init__(self, center, halfDimension):
        # Center of boundary
        self.center = center
        # Dimensions of boundary
        self.halfDimension = halfDimension
        
    def containsPoint(self, p):
        return (self.center[0] - self.halfDimension[0]) < p.center[0] < (self.center[0] + self.halfDimension[0]) \
                and (self.center[1] - self.halfDimension[1]) < p.center[1] < (self.center[1] + self.halfDimension[1])

    def intersects(self, bound):
        dist_x = abs(self.center[0] - bound.center[0])
        dist_y = abs(self.center[1] - bound.center[1])
        max_dist_x = self.halfDimension[0] + bound.halfDimension[0]
        max_dist_y = self.halfDimension[1] + bound.halfDimension[1]
        return(dist_x < max_dist_x, dist_y < max_dist_y)


    def drawLine(self):
        # Draw lines
        stroke(230)
        line(self.center[0] - self.halfDimension[0], self.center[1], self.center[0] + self.halfDimension[0], self.center[1])
        line(self.center[0], self.center[1] - self.halfDimension[1], self.center[0], self.center[1] + self.halfDimension[1])

    
class QuadTree():
    
    def __init__(self, capacity, boundary):
        # Maximum capacity of quadtree
        self.capacity = capacity
        # Boundary
        self.boundary = boundary
        # Array of points
        self.pArray = ArrayList()
        # Does QuadTree have child
        self.child = False
        
    def subdivide(self):
        new_center = [self.boundary.center[0], self.boundary.center[1]]
        self.northWest = QuadTree(self.capacity, Boundary([self.boundary.center[0] - self.boundary.halfDimension[0]/2, self.boundary.center[1] - self.boundary.halfDimension[1]/2], [self.boundary.halfDimension[0]/2, self.boundary.halfDimension[1]/2]))
        self.northEast = QuadTree(self.capacity, Boundary([self.boundary.center[0] + self.boundary.halfDimension[0]/2, self.boundary.center[1] - self.boundary.halfDimension[1]/2], [self.boundary.halfDimension[0]/2, self.boundary.halfDimension[1]/2]))
        self.southWest = QuadTree(self.capacity, Boundary([self.boundary.center[0] - self.boundary.halfDimension[0]/2, self.boundary.center[1] + self.boundary.halfDimension[1]/2], [self.boundary.halfDimension[0]/2, self.boundary.halfDimension[1]/2]))
        self.southEast = QuadTree(self.capacity, Boundary([self.boundary.center[0] + self.boundary.halfDimension[0]/2, self.boundary.center[1] + self.boundary.halfDimension[1]/2], [self.boundary.halfDimension[0]/2, self.boundary.halfDimension[1]/2]))
        
        self.child = True


    def insertPoint(self, p):
        
        # Ignore points outside boundary
        if not self.boundary.containsPoint(p):
            return False
        # 
        if len(self.pArray) < self.capacity:
            self.pArray.add(p)
            return True
        else:
            if not self.child:
                try:
                    self.northWest == None
                except:
                    self.subdivide()
            
            if (self.northWest.boundary.containsPoint(p)):
                self.northWest.insertPoint(p)
                return True
            if (self.northEast.boundary.containsPoint(p)):
                self.northEast.insertPoint(p)
                return True
            if (self.southWest.boundary.containsPoint(p)):
                self.southWest.insertPoint(p)
                return True
            if (self.southEast.boundary.containsPoint(p)):
                self.southEast.insertPoint(p)
                return True
        
    def show(self):
        
        for p in self.pArray:
            p.show()
            
        if self.child == True:
            self.northEast.show()
            self.northWest.show()
            self.southEast.show()
            self.southWest.show()
            self.boundary.drawLine()
    
    def queryRange(self, bound):
        # init array
        pointsInRange = ArrayList()
        # QuadTree is not in bound
        if not(self.boundary.intersects(bound)):
            return pointsInRange
        # adding points to array
        for p in self.pArray:
            if bound.containsPoint(p):
                pointsInRange.add(p)
        # no children
        if not self.child:
            return pointsInRange
        # recursive call of function
        else:
            pointsInRange += self.northEast.queryRange(bound)
            pointsInRange += self.northWest.queryRange(bound)
            pointsInRange += self.southEast.queryRange(bound)
            pointsInRange += self.southWest.queryRange(bound)

        return pointsInRange
    
    def queryTotalPoints(self):
        total = 0
        total += len(self.pArray)
        if self.child:
            total += self.northEast.queryTotalPoints()
            total += self.northWest.queryTotalPoints()
            total += self.southEast.queryTotalPoints()
            total += self.southWest.queryTotalPoints()
        return total


#############################################################################################################
#############################################################################################################
############################################                        #########################################
############################################        FONCTIONS       #########################################
############################################                        #########################################
#############################################################################################################
#############################################################################################################

def drawMouseZone(w):

        
    noFill()
    stroke(255, 255, 0)
    rect(mouseX - rect_w/2 , mouseY - rect_w/2, rect_w, rect_w)


def mousePressed():
    if mouseButton == LEFT:
        for i in range(50):
            points.add(Point([random(screen_w), random(screen_h)], random(20, 30)))

    if mouseButton == RIGHT:
        print("Number of points : ", quadT.queryTotalPoints())


def keyPressed():
    if key == 'r':
        global points
        points = ArrayList()

    if key == 'u':
        print(quadT.queryRange(Boundary([mouseX, mouseY], [rect_w/2, rect_w/2])))

    if key == 'i':
        print(quadT.pArray)
    