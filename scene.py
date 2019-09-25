import numpy as np
from OpenGL.GL import *
from OpenGL.arrays import vbo

POINT_SIZE = 10
#Hoang Ha Vu - hvuxx001 - GenCG ss 2019

class Scene:
    """ OpenGL 2D scene class """

    def __init__(self):
        self.k = 4 # Ordnung der Kurve
        self.m = 50 # Anzahl der Kurvenpunkte
        self.default_weight=1
        self.points = []
        self.curve = []
        self.points_with_weight =[]
        self.calcPoints = []
        self.curvePoints=[]
        self.kontroll = []
        self.found = False
        self.index = 0
        self.last_position = (0, 0)

    def deletePoints(self):
        self.points = []
        self.change()

    def makePoint(self, x, y):
        self.points_with_weight.append([x,y,1,self.default_weight])
        self.change()

    def pop_lastPoint(self):
        if len(self.points) != 0:
            self.points.pop()
            self.change()

    def changeWeight(self,position):

        if (self.found == False):
            self.findPoint(position[0], position[1])

        else:
            if (self.last_position[1] < position[1]):
                point = self.points_with_weight[self.index]
                print("Welcher Punkt ", self.index+1)
                print("alte Gewichtung:", point[3])
                oldvalue = point[3]
                if(oldvalue<10):
                    newvalue = oldvalue + 1
                    point[3] = newvalue
                    print("neue Gewichtung: ", point[3])
                self.points_with_weight[self.index] = point
                self.change()
            else:
                point = self.points_with_weight[self.index]
                print("Welcher Punkt ", self.index+1)
                print("alte Gewichtung:", point[3])
                oldvalue = point[3]
                if (oldvalue > 1):
                    newvalue = oldvalue - 1
                    point[3] = newvalue
                    print("neue Gewichtung: ", point[3])
                self.points_with_weight[self.index] = point
                self.change()

            self.last_position = position



    def findPoint(self,x,y):
        self.index=0
        for point in self.points:
            if(((x and point[0])>0 or (x and point[0])<0) and ((y and point[1])>0 or (y and point[1])<0) ):
                pxMrange = abs(point[0]) - 0.03
                pxPrange = abs(point[0]) + 0.03
                pyMrange = abs(point[1]) - 0.03
                pyPrange = abs(point[1]) + 0.03
                if (abs(x) > pxMrange and abs(x) < pxPrange and abs(y) > pyMrange and abs(y) < pyPrange):
                    self.found = True
                    self.last_position = (x, y)
                    return

            self.index+=1

    def draw(self):
        my_vbo = vbo.VBO(np.array(self.points, 'f'))
        my_vbo.bind()
        glEnableClientState(GL_VERTEX_ARRAY)
        glVertexPointer(2, GL_FLOAT, 0, my_vbo)
        # glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        glColor3fv([0, 0, 0])
        glPointSize(POINT_SIZE)
        glDrawArrays(GL_POINTS, 0, len(self.points))

        if len(self.points) > 1:
            glDrawArrays(GL_LINE_STRIP, 0, len(self.points))

        if len(self.curve)>1:
            line = vbo.VBO(np.array(self.curve, 'f'))
            line.bind()
            glColor3fv([1, 0, 0])
            glEnableClientState(GL_VERTEX_ARRAY)
            glVertexPointer(2, GL_FLOAT, 0, line)
            glPointSize(2)
            glDrawArrays(GL_POINTS, 0, len(self.curve))
            glDrawArrays(GL_LINE_STRIP, 0, len(self.curve))
            line.unbind()


        glDisableClientState(GL_VERTEX_ARRAY)
        my_vbo.unbind()

    def render(self):
        glClear(GL_COLOR_BUFFER_BIT)
        self.draw()
        glFlush()

    def deboor(self, j, i, degree, controlpoints, knotvector, t):
        if j == 0:
            if i == len(controlpoints):
                return controlpoints[i - 1]
            return controlpoints[i]

        a = (t - knotvector[i])
        b = (knotvector[i - j + degree] - knotvector[i])

        if b == 0:
            alpha = 0
        else:
            alpha = a / b

        left_term = self.deboor(j - 1, i - 1, degree, controlpoints, knotvector, t)
        right_term = self.deboor(j - 1, i, degree, controlpoints, knotvector, t)


        b1= (1 - alpha) * np.asarray(left_term) + alpha * np.asarray(right_term)

        return b1


    def calc_knotvector(self):
        countPoints = len(self.calcPoints)
        if countPoints < self.k:
            return None

        part1 = [0 for x in range(self.k)]
        part2 = [x for x in range(1, countPoints - (self.k - 2))]
        part3 = [countPoints - (self.k - 2) for x in range(self.k)]
        return part1 + part2 + part3

    def change(self):
        print("Ordnung der Kurve: {} Anzahl der Kurvenpunkte: {} Kontrollpunkte: {}".format(self.k,self.m,self.kontroll))
        self.calcPointList()
        self.calPoints()
        self.kontroll = self.calc_knotvector()
        if not self.kontroll:
            self.curvePoints.clear()
            return
        self.curvePoints=[]
        if self.m >0:
            for i in range(self.m + 1):
                t = max(self.kontroll) * (i / self.m)
                r = None
                for j in range(len(self.kontroll)):
                    if t == max(self.kontroll):
                        r = len(self.kontroll) - self.k - 1
                        break
                    if self.kontroll[j] <= t < self.kontroll[j + 1]:
                        r = j
                        break

                self.curvePoints.append(self.deboor(self.k - 1, r, self.k, self.calcPoints, self.kontroll, t))
            self.calcCurvePoints()


    def calPoints(self):
        self.points.clear()
        for x,y,w in self.calcPoints:
            self.points.append((x/w,y/w))

    def calcCurvePoints(self):
        self.curve.clear()
        for x,y,w in self.curvePoints:
            self.curve.append((x/w,y/w))


    def calcPointList(self):
        self.calcPoints.clear()
        for point in self.points_with_weight:
            self.calcPoints.append((point[0]*point[3],point[1]*point[3],point[2]*point[3]))

    def add_order(self):
        self.k += 1
        self.change()

    def remove_order(self):
        if self.k > 2:
            self.k -= 1
            self.change()

    def add_curvePoint(self):
        self.m += 10
        self.change()

    def remove_curvePoint(self):
        if self.m > 0:
            self.m -= 10
            self.change()


