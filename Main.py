import numpy as np
from matplotlib import pyplot as plt
from MeshVisual import MeshVisual


class Rigid:
    def __init__(self, position):
        self.pos = np.asarray(position, dtype=float)
        self.forces = np.zeros(3, dtype=float)
        self.connections = []

    def attach(self, spring):
        self.connections.append(spring)


class PointMass(Rigid):
    def __init__(self, position, mass):
        super().__init__(position)
        self.initial_pos = np.asarray(position, dtype=float)
        self.vel = np.zeros(3, dtype=float)
        self.acc = np.zeros(3, dtype=float)
        self.mass = mass

    def react(self, t):
        self.acc = self.forces / self.mass
        self.vel = self.vel + self.acc * t
        self.pos = self.pos + self.vel * t
        return 0.5 * self.mass * ((np.linalg.norm(self.vel))**2)


class Anchor(Rigid):
    def __init__(self, position):
        super().__init__(position)

    def react(self, t):
        return 0


class Spring:

    def __init__(self, rigid_n, rigid_p, natural_length, k, dim):
        self.k = k
        self.natural_length = natural_length
        self.rigids = [rigid_n, rigid_p]
        self.dim = dim

    def find_forces(self):
        distance = self.rigids[1].pos - self.rigids[0].pos
        length = np.linalg.norm(distance)
        force_vector = (-1 * (length - self.natural_length) * self.k) * distance / length
        potential_e = 0.5 * self.k * ((length - self.natural_length) ** 2)
        return force_vector, potential_e


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
        self.m[tuple(slot_n)].attach(self.spring_list[-1])
        self.m[tuple(slot_p)].attach(self.spring_list[-1])


class Instance:

    def __init__(self, mesh, tick_size, length_of_time):
        self.mesh = mesh
        self.t = tick_size
        self.extent = length_of_time
        self.time_axis = np.arange(0, self.extent, self.t)
        self.recorder = None
        self.te = [0]
        self.pe = [0]
        self.ke = [0]

        self.visual = MeshVisual(mesh)

    def simple_initiate(self, starting_objects_locs, displacements, recording_object_locs, recording_axis):
        self.recorder = np.zeros([len(recording_object_locs), int(self.extent / self.t)])
        recording_objects = [self.mesh.m[tuple(loc)] for loc in recording_object_locs]
        for i, axis in enumerate(recording_axis):
            self.recorder[i, 0] = recording_objects[i].pos[axis-1]

        for loc, disp in zip(starting_objects_locs, displacements):
            starting_object = self.mesh.m[tuple(loc)]
            starting_object.pos = starting_object.pos + disp

        self.simulate(recording_objects, recording_axis)

    def simulate(self, recording_objects, recording_axis):
        for tick in np.arange(self.t, self.extent, self.t):
            potential_e = 0
            for spring in self.mesh.spring_list:
                force_applicator, e = spring.find_forces()
                potential_e = potential_e + e
                spring.rigids[1].forces = spring.rigids[1].forces + force_applicator
                spring.rigids[0].forces = spring.rigids[0].forces + -1 * force_applicator

            kinetic_e = 0
            for rigid in np.nditer(self.mesh.m, flags=["refs_ok"]):
                rigid = rigid.item()
                e = rigid.react(self.t)
                kinetic_e = e + kinetic_e
                rigid.forces = np.zeros(3, dtype=float)

            for i, (rigid, axis) in enumerate(zip(recording_objects, recording_axis)):
                self.recorder[i, int(np.rint(tick / self.t))] = rigid.pos[axis-1]

            total_energy = potential_e + kinetic_e
            print(potential_e)
            print(kinetic_e)
            print(total_energy)
            self.pe.append(potential_e)
            self.ke.append(kinetic_e)
            self.te.append(total_energy)

            self.visual.update()

        #plt.plot(self.time_axis, self.pe, self.time_axis, self.ke, self.time_axis, self.te)
        plt.plot(self.time_axis, self.recorder[0, :], self.time_axis, self.recorder[1, :])
        plt.show()


TrialMesh = Mesh([1, 3, 2])

TrialMesh.create_anchor([0, 0, 0], [0, 0, 0])
TrialMesh.create_anchor([0, 0, 1], [0, 0, 1])

TrialMesh.create_pointmass([0, 1, 1], [0, 1, 1], 1)
TrialMesh.create_pointmass([0, 1, 0], [0, 1, 0], 1)
TrialMesh.create_pointmass([0, 2, 1], [0, 2, 1], 1)
TrialMesh.create_pointmass([0, 2, 0], [0, 2, 0], 1)

TrialMesh.create_spring([0, 0, 1], [0, 1, 1], 1, 1)
TrialMesh.create_spring([0, 0, 0], [0, 1, 0], 1, 1)
TrialMesh.create_spring([0, 1, 1], [0, 1, 0], 1, 1)

TrialMesh.create_spring([0, 1, 1], [0, 2, 1], 1, 1)
TrialMesh.create_spring([0, 1, 0], [0, 2, 0], 1, 1)
TrialMesh.create_spring([0, 2, 1], [0, 2, 0], 1, 1)

Instance1 = Instance(TrialMesh, 0.01, 100)
Instance1.simple_initiate([[0, 1, 0], [0, 1, 1]], [[0, 0, -0.2], [0, 0, 0.2]], [[0, 1, 0], [0, 2, 0]], [2, 2])
