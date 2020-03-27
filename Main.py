import numpy as np
from matplotlib import pyplot as plt
#from MeshVisual import MeshVisual
from vis2 import MeshVisual


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

    def get_kinetic(self):
        return 0.5 * self.mass * ((np.linalg.norm(self.vel))**2)


class Anchor(Rigid):
    def __init__(self, position):
        super().__init__(position)

    def react(self, t):
        pass

    def get_kinetic(self):
        return 0


class Spring:

    def __init__(self, rigid_n, rigid_p, natural_length, k):
        self.k = k
        self.natural_length = natural_length
        self.length = natural_length
        self.rigids = [rigid_n, rigid_p]

    def find_forces(self):
        length_vector = self.rigids[1].pos - self.rigids[0].pos
        self.length = np.linalg.norm(length_vector)
        return (-1 * (self.length - self.natural_length) * self.k) * length_vector / self.length

    def get_potential(self):
        return 0.5 * self.k * ((self.length - self.natural_length) ** 2)


class Mesh:

    def __init__(self, dim):
        self.m = np.empty(dim, dtype=object)
        self.spring_list = []

    def create_pointmass(self, slot, position, mass):
        self.m[tuple(slot)] = PointMass(position, mass)

    def create_anchor(self, slot, position):
        self.m[tuple(slot)] = Anchor(position)

    def create_rest_spring(self, slot_n, slot_p, k):
        rigid_n, rigid_p = self.m[tuple(slot_n)], self.m[tuple(slot_p)]
        self.spring_list.append(Spring(rigid_n, rigid_p, np.linalg.norm(rigid_p.pos - rigid_n.pos), k))
        rigid_n.attach(self.spring_list[-1])
        rigid_p.attach(self.spring_list[-1])


class Instance:

    def __init__(self, mesh, tick_size, length_of_time):
        self.mesh = mesh
        self.t = tick_size
        self.extent = length_of_time
        self.time_axis = np.arange(0, self.extent, self.t)
        self.tracked_objects = None
        self.tracked_axis = None
        self.motion_tracker = None
        self.energy_tracker = None
        self.visual = MeshVisual(mesh)

    def initialize_tracking(self, tracked_object_locs, tracked_axis):
        self.energy_tracker = np.zeros([int(self.extent / self.t), 3])
        for spring in self.mesh.spring_list:
            self.energy_tracker[0, 0] = self.energy_tracker[0, 0] + spring.get_potential()
        for rigid in np.nditer(self.mesh.m, flags=["refs_ok"]):
            rigid = rigid.item()
            self.energy_tracker[0, 1] = self.energy_tracker[0, 1] + rigid.get_kinetic()
        self.energy_tracker[0, 2] = self.energy_tracker[0, 0] + self.energy_tracker[0, 1]

        self.motion_tracker = np.zeros([int(self.extent / self.t), len(tracked_object_locs)])
        self.tracked_objects = [self.mesh.m[tuple(loc)] for loc in tracked_object_locs]
        self.tracked_axis = tracked_axis
        for i, axis in enumerate(self.tracked_axis):
            self.motion_tracker[0, i] = self.tracked_objects[i].pos[axis-1]

    def initialize_displacement(self, starting_objects_locs, displacements):
        for loc, disp in zip(starting_objects_locs, displacements):
            self.mesh.m[tuple(loc)].pos = self.mesh.m[tuple(loc)].pos + disp

    def simulate(self):
        for i, tick in enumerate(np.arange(self.t, self.extent, self.t)):
            for spring in self.mesh.spring_list:
                force_applicator = spring.find_forces()
                spring.rigids[1].forces = spring.rigids[1].forces + force_applicator
                spring.rigids[0].forces = spring.rigids[0].forces + -1 * force_applicator
                self.energy_tracker[i+1, 0] = self.energy_tracker[i+1, 0] + spring.get_potential()

            for rigid in np.nditer(self.mesh.m, flags=["refs_ok"]):
                rigid = rigid.item()
                self.energy_tracker[i+1, 1] = self.energy_tracker[i+1, 1] + rigid.get_kinetic()
                rigid.react(self.t)
                rigid.forces = np.zeros(3, dtype=float)


            for j, (rigid, axis) in enumerate(zip(self.tracked_objects, self.tracked_axis)):
                self.motion_tracker[i+1, j] = self.tracked_objects[j].pos[axis - 1]

            self.energy_tracker[i + 1, 2] = self.energy_tracker[i + 1, 0] + self.energy_tracker[i + 1, 1]
            self.visual.update()
        print(self.mesh.m)

    def graph_motion(self):
        motion_plot = plt.figure(1)
        plt.plot(self.time_axis, self.motion_tracker[:, 0], self.time_axis, self.motion_tracker[:, 1])
        plt.show()

    def graph_energy(self):
        energy_plot, ax = plt.subplots()
        ax.plot(self.time_axis, self.energy_tracker[:, 0], label="Kinetic Energy")
        ax.plot(self.time_axis, self.energy_tracker[:, 1], label="Potential Energy")
        ax.plot(self.time_axis, self.energy_tracker[:, 2], label="Total Energy")
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Energy (kJ)")
        ax.set_title("Energy of a Spring-Mass System")
        ax.legend()
        energy_plot.show()







TrialMesh = Mesh([1, 3, 2])

TrialMesh.create_anchor([0, 0, 0], [0, 0, 0])
TrialMesh.create_anchor([0, 0, 1], [0, 0, 1])

TrialMesh.create_pointmass([0, 1, 1], [0, 1, 1], 1)
TrialMesh.create_pointmass([0, 1, 0], [0, 1, 0], 1)
TrialMesh.create_pointmass([0, 2, 1], [0, 2, 1], 1)
TrialMesh.create_pointmass([0, 2, 0], [0, 2, 0], 1)

TrialMesh.create_rest_spring([0, 0, 1], [0, 1, 1], 1)
TrialMesh.create_rest_spring([0, 0, 0], [0, 1, 0], 1)
TrialMesh.create_rest_spring([0, 1, 1], [0, 1, 0], 1)

TrialMesh.create_rest_spring([0, 1, 1], [0, 2, 1], 1)
TrialMesh.create_rest_spring([0, 1, 0], [0, 2, 0], 1)
TrialMesh.create_rest_spring([0, 2, 1], [0, 2, 0], 1)

Instance1 = Instance(TrialMesh, 0.01, 25)
Instance1.initialize_tracking([[0, 1, 0], [0, 1, 1]], [3, 3])
Instance1.initialize_displacement([[0, 1, 0], [0, 1, 1]], [[0, 0, -0.2], [0, 0, 0.2]])
Instance1.simulate()
Instance1.graph_energy()

