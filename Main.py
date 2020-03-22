import numpy as np
from matplotlib import pyplot as plt

class PointMass:

    def __init__(self, position, mass):
        self.mass = mass
        self.initial_pos = np.asarray(position, dtype=float)
        self.pos = np.asarray(position, dtype=float)
        self.vel = np.zeros(3, dtype=float)
        self.acc = np.zeros(3, dtype=float)
        self.forces = np.zeros(3, dtype=float)
        self.connections = [None] * 6

    def attach(self, spring, side):
        conn_dict = {1: 0, -1: 1, 2: 2, -2: 3, 3: 4, -3: 5}
        self.connections[conn_dict[side]] = spring

    def react(self, t):
        self.acc = self.forces / self.mass
        self.vel = self.vel + self.acc * t
        self.pos = self.pos + self.vel * t


class Anchor:

    def __init__(self, position):
        self.pos = np.asarray(position, dtype=float)
        self.initial_pos = self.pos
        self.connections = None
        self.forces = np.zeros(3, dtype=float)

    def attach(self, spring, placeholder_side):
        self.connections = spring

    def react(self, t):
        pass


class Spring:

    def __init__(self, rigid_n, rigid_p, natural_length, k, dim):
        self.k = k
        self.natural_length = natural_length
        self.length = natural_length
        self.rigids = [rigid_n, rigid_p]
        self.force = 0
        self.dim = dim

    def find_forces(self):
        pos_n = self.rigids[0].pos - self.rigids[0].initial_pos
        pos_p = self.rigids[1].pos - self.rigids[1].initial_pos
        self.length = pos_p[self.dim-1] - pos_n[self.dim-1]
        self.force = -1 * self.length * self.k
        force_applicator = np.zeros(3, dtype=float)
        force_applicator[self.dim - 1] = self.force
        self.rigids[1].forces = self.rigids[1].forces + force_applicator
        force_applicator[self.dim - 1] = -1 * self.force
        self.rigids[0].forces = self.rigids[0].forces + force_applicator
        force_applicator = None


class Mesh:

    def __init__(self, dim):
        self.m = np.empty(dim, dtype=object)
        self.spring_list = []

    def create_pointmass(self, slot, position, mass):
        self.m[tuple(slot)] = PointMass(position, mass)

    def create_anchor(self, slot, position):
        self.m[tuple(slot)] = Anchor(position)

    def create_spring(self, slot_n, slot_p, natural_length, k):
        slot_n = np.asarray(slot_n)
        slot_p = np.asarray(slot_p)
        side = ((np.argwhere(abs(slot_p - slot_n)))[0, 0] + 1) * sum(slot_p - slot_n)
        self.spring_list.append(Spring(self.m[tuple(slot_n)], self.m[tuple(slot_p)], natural_length, k, abs(side)))
        self.m[tuple(slot_n)].attach(self.spring_list[-1], side)
        self.m[tuple(slot_p)].attach(self.spring_list[-1], side * -1)


class Instance:

    def __init__(self, mesh, tick_size, length_of_time):
        self.mesh = mesh
        self.t = tick_size
        self.extent = length_of_time
        self.time_axis = np.arange(0, self.extent, self.t)
        self.recorder = np.zeros([int(self.extent / tick_size)])

    def simple_initiate(self, starting_object_loc, displacement, recording_object_loc, recording_axis):
        starting_object = self.mesh.m[tuple(starting_object_loc)]
        recording_object = self.mesh.m[tuple(recording_object_loc)]
        self.recorder[0] = recording_object.pos[recording_axis - 1]
        starting_object.pos = starting_object.pos + displacement
        self.simulate(recording_object, recording_axis)

    def simulate(self,recording_object, recording_axis):
        for tick in np.arange(self.t, self.extent, self.t):
            for spring in self.mesh.spring_list:
                spring.find_forces()

            for rigid in np.nditer(self.mesh.m, flags=["refs_ok"]):
                rigid = rigid.item()
                rigid.react(self.t)
                rigid.forces = np.zeros(3, dtype=float)

            self.recorder[int(np.rint(tick / self.t))] = recording_object.pos[recording_axis - 1]
        plt.plot(self.time_axis, self.recorder)
        plt.show()


TrialMesh = Mesh([1, 1, 4])
TrialMesh.create_anchor([0, 0, 0], [0, 0, 0])
TrialMesh.create_pointmass([0, 0, 1], [0, 0, 1], 1)
TrialMesh.create_pointmass([0, 0, 2], [0, 0, 2], 1)
TrialMesh.create_anchor([0, 0, 3], [0, 0, 3])
TrialMesh.create_spring([0, 0, 1], [0, 0, 0], 1, 2)
TrialMesh.create_spring([0, 0, 2], [0, 0, 1], 1, 2)
TrialMesh.create_spring([0, 0, 3], [0, 0, 2], 1, 2)

Instance1 = Instance(TrialMesh, 0.01, 20)
Instance1.simple_initiate([0, 0, 2], [0, 0, 0.5], [0, 0, 1], 3)










