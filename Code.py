from PIL import Image
import numpy as np
from random import randint

def zbuffer_clipper(obj_file, image : Image):

    class point:
        def __init__(self, xyz : tuple[int,int,int]):
            self.x = xyz[0]
            self.y = xyz[1]
            self.z = xyz[2]
        

    class plane:
        def __init__(self, p: tuple[point,point,point], color):
            
            self.p = p
            self.color = color

            Arr = np.array((
                [   -p[0].x,    -p[0].y,     -p[0].z  ],
                [   p[1].x - p[0].x,    p[1].y - p[0].y,     p[1].z - p[0].z  ],
                [   p[2].x - p[0].x,    p[2].y - p[0].y,     p[2].z - p[0].z  ],
            ))


            self.A = np.linalg.det(np.array((
                [Arr[1][1], Arr[1][2]],
                [Arr[2][1], Arr[2][2]],
                )))
            self.B = np.linalg.det(np.array((
                [Arr[1][0], Arr[1][2]],
                [Arr[2][0], Arr[2][2]],
                )))
            self.C = np.linalg.det(np.array((
                [Arr[1][0], Arr[1][1]],
                [Arr[2][0], Arr[2][1]],
                )))
            self.D = np.linalg.det(Arr)

        def in_plane_xy(self, xy : tuple[int,int]) -> bool: 

            abV = tuple([(self.p[1].x - self.p[0].x), (self.p[1].y - self.p[0].y)])
            bcV = tuple([(self.p[2].x - self.p[1].x), (self.p[2].y - self.p[1].y)])
            caV = tuple([(self.p[0].x - self.p[2].x), (self.p[0].y - self.p[2].y)])

            Nab = tuple([abV[1], -abV[0]])
            Nbc = tuple([bcV[1], -bcV[0]])
            Nca = tuple([caV[1], -caV[0]])

            atV = tuple([xy[0] - self.p[0].x, xy[1] - self.p[0].y])
            btV = tuple([xy[0] - self.p[1].x, xy[1] - self.p[1].y])
            ctV = tuple([xy[0] - self.p[2].x, xy[1] - self.p[2].y])


            if ((
                (Nab[0]*atV[0] + Nab[1]*atV[1] >= 0) and 
                (Nbc[0]*btV[0] + Nbc[1]*btV[1] >= 0) and 
                (Nca[0]*ctV[0] + Nca[1]*ctV[1] >= 0)
                )

                or

                (
                (Nab[0]*atV[0] + Nab[1]*atV[1] < 0) and 
                (Nbc[0]*btV[0] + Nbc[1]*btV[1] < 0) and 
                (Nca[0]*ctV[0] + Nca[1]*ctV[1] < 0)
                )):
                
                return True

            return False
        def get_z(self, xy : tuple[int, int]) -> int:
            return -(self.D + self.A * xy[0] + self.B * xy[1]) / self.C
        

    dots = list()
    planes = list()

    with open(obj_file) as file:
        info = file.read().split('\n')

    for line in info:
        if (line.find("v") == 0):
            _, *line = line.split()
            if (len(line) == 3):
                x = (int(line[0]))
                y = (int(line[1]))
                z = (int(line[2]))

                (x,y,z) = scale_3D((x,y,z),(300, 400, 400))
                (x,y,z) = shift_3D((x,y,z),(500,500,0))

                (x,y,z) = rotateY_3D((x,y,z), 20)

                (x,y,z) = rotateX_3D((x,y,z), 34)

                dots.append(point((x, y, z)))

        elif (line.find("f") == 0):
            _, *line = line.split()
            if (len(line) == 3):
                p0 = dots[int(line[0]) - 1]
                p1 = dots[int(line[1]) - 1]
                p2 = dots[int(line[2]) - 1]
                planes.append(plane((p0, p1, p2), randint(100, 255)))

    
    for i in range(image.size[0]):
        for j in range(image.size[1]):
          
          z_max = planes[0].get_z((i,j))

          for p in planes:
              if(p.in_plane_xy((i, j))):
                  z = p.get_z((i,j))
                  if (z > z_max):
                      z_max = z
                      image.putpixel((i,j), p.color)  
