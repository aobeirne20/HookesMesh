import numpy as np
from matplotlib import pyplot as plt


class Connections:

    def __init__(self):
        self.matrix = np.empty(6, dtype=object)
        # Connections are stored in the following size 6 numpy array [+x, -x, +y, -y, +z, -z]
        # Therefore, +x = 1, -x = -1, +y = 2, -y = -2, +z = 3, -z = -3
        self.conn_dict = {1: 0, -1: 1, 2: 2, -2: 3, 3: 4, -3: 5}

    def attach(self, spring, side):
        if self.matrix[self.conn_dict[side]] is None:
            self.matrix[self.conn_dict[side]] = spring
        else:
            print(f"This mass is already connected at side {side}. Review setup and try again.")

    def check(self, side):
        if self.matrix[self.conn_dict[side]] is None:
            return 0
        else:
            return 1

    def select(self, side):
        return self.matrix[self.conn_dict[side]]


class PointMass:

    def __init__(self, mass, position):
        self.mass = mass
        #Position, velocity, and acceleration are handled as size 3 numpy array vectors
        #Positive x is to the right, positive y is up, positive z is into the screen
        self.initial_pos = np.asarray(position, dtype=float)
        self.pos = np.asarray(position, dtype=float)
        self.vel = np.zeros(3, dtype=float)
        self.acc = np.zeros(3, dtype=float)
        self.connections = Connections()
        self.conn_dict = {1: 0, -1: 1, 2: 2, -2: 3, 3: 4, -3: 5}

    def attach(self, spring, side):
        self.connections.attach(spring, side)

    def find_forces(self):
        temp_displace = self.pos - self.initial_pos
        force_v = np.array(6)
        for side in [1, 2, 3]:
            force_nside, force_pside = 0
            if self.connections.check(side) == 0 and self.connections.check(-1 * side) == 0:
                pass
            elif self.connections.check(side) == 1 and self.connections.check(-1 * side) == 1:
                force_pside = self.connections.select(side).react(temp_displace[side-1] * -1)
                force_nside = -1 * self.connections.select(side).react(temp_displace[side-1])
            elif self.connections.check(side) == 1 and self.connections.check(-1 * side) == 0:
                force_pside = self.connections.select(side).react(temp_displace[side-1] * -1)
            elif self.connections.check(side) == 0 and self.connections.check(-1 * side) == 1:
                force_nside = -1 * self.connections.select(side).react(temp_displace[side-1])
            else:
                print(f"This mass is not connected to any springs. Check setup")
            force_v[self.conn_dict[side]] =  force_pside
            force_v[self.conn_dict[side*-1]] = force_nside
        return force_v


class Anchor:

    def __init__(self, position):
        #See PointMass for information regarding position data
        self.pos = np.asarray(position, dtype=float)
        #A anchor should only ever have one connection, but will be stored as size 1 numpy array for consistency
        self.connection = np.empty(1, dtype=object)

    def attach(self, spring, placeholder_side):
        if self.connection[0] is None:
            self.connection[0] = spring
        else:
            print(f"This anchor is already connected.")

    def find_forces(self):
        return np.zeros(6)


class Spring:

    def __init__(self, k, natural_length):
        self.k = k
        self.natural_length = natural_length
        self.length = natural_length
        self.connections = np.empty(2, dtype=object)
        self.force = 0

    def connect(self, *rigids):
        #Connect allows masses and anchors to be attached individually or two at a time, using the [a, b] format
        if len(rigids) == 2:
            self.connections[0] = rigids[0]
            self.connections[1] = rigids[1]
        elif self.connections[0] is None:
            self.connections[0] = rigids
        else:
            self.connections[1] = rigids

    def jump(self, rigid):
        #Jump is a utility function that returns the rigid at the other end of the spring
        if rigid is self.connections[0]:
            return self.connections[1]
        elif rigid is self.connections[1]:
            return self.connections[0]
        else:
            print(f"That object is not attached to this spring")

    def react(self, stretch):
        self.length = self.length + stretch
        self.force = -1 * (self.length - self.natural_length) * self.k
        return self.force



class Mesh:

    def __init__(self, dim):
        self.m = np.empty(dim, dtype=object)

    def connect(self, rigid1, side1, spring, rigid2, side2):
        #Used when a spring is simultaneously connected to two rigids
        rigid1.attach(spring, side1)
        rigid2.attach(spring, side2)
        spring.connect([rigid1, rigid2])

    def attach(self, rigid, side, spring):
        #Used when a spring is attached to only one rigid
        rigid.attach(spring, side)
        spring.connect(rigid)



class Instance:

    def __init__(self, mesh, tick_size, length_of_time):
        self.mesh = mesh
        self.t = tick_size
        self.extent = length_of_time
        self.recorder = np.array((1, self.extent / self.tick_size))
        self.jump_dict = {1: [1, 0, 0], 2: [-1, 0, 0], 3: [0, 1, 0], 4: [0, -1, 0], 5: [0, 0, 1], 6: [0, 0 -1]}

    def simple_initiate(self, starting_object, displacement, recording_object, recording_axis):
        self.recorder[0] = recording_object.pos[recording_axis]
        starting_object.pos = starting_object.pos + displacement
        self.simulate(starting_object, recording_object, recording_axis)

    def simulate(self, starting_object, recording_object, recording_axis):

        def discover_forces(loc, rigid):
            side = 1
            for spring_force in force_matrix[-1, :]:
                if spring_force == 0:
                    pass
                    side += 1
                elif np.isin(self.mesh.m[self.jump_dict[side] + loc], object_list) is True:
                    pass
                    side += 1
                else:
                    next_rigid = self.mesh.m[self.jump_dict[side] + loc]
                    force_matrix.append([next_rigid.find_forces()], axis=0)
                    object_list.append(next_rigid)
                    discover_forces(self.mesh.m[self.jump_dict[side] + loc], next_rigid)

        for tick in range(self.t, self.extent, self.t):
            #This is the start of the recursive loop, which is performed semi-seperately at the beginning of every tick
            object_list = np.array(shape=0, dtype=object)
            force_matrix = np.array(shape=(0, 3))
            force_matrix.append([starting_object.find_forces()], axis=0)
            object_list.append(starting_object)

            discover_forces(starting_object, np.where(self.mesh.m == starting_object))