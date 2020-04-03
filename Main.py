import numpy as np
from matplotlib import pyplot as plt
from vis2 import MeshVisual


class Rigid:
    def __init__(self, position):
        self.pos = np.asarray(position, dtype=float)
        self.initial_pos = self.pos
        self.forces = np.zeros(3, dtype=float)
        self.connections = []

    def attach(self, spring):
        self.connections.append(spring)


class PointMass(Rigid):
    def __init__(self, position, mass):
        super().__init__(position)
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
        self.force_d = dict()
        self.visual = MeshVisual(mesh, 1)

    def initialize_tracking(self, tracked_object_locs, tracked_axis):
        self.energy_tracker = np.zeros([int(self.extent / self.t), 3])
        for spring in self.mesh.spring_list:
            self.energy_tracker[0, 0] = self.energy_tracker[0, 0] + spring.get_potential()
        for rigid in np.nditer(self.mesh.m, flags=["refs_ok"]):
            rigid = rigid.item()
            if rigid is not None:
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

    def initialize_static_load(self, loaded_objects_locs, forces):
        for loc, force in zip(loaded_objects_locs, forces):
            self.force_d[self.mesh.m[tuple(loc)]] = force

    def simulate(self):
        for i, tick in enumerate(np.arange(self.t, self.extent, self.t)):
            for rigid, force in self.force_d.items():
                rigid.forces = rigid.forces + force

            for spring in self.mesh.spring_list:
                force_applicator = spring.find_forces()
                spring.rigids[1].forces = spring.rigids[1].forces + force_applicator
                spring.rigids[0].forces = spring.rigids[0].forces + -1 * force_applicator
                self.energy_tracker[i+1, 0] = self.energy_tracker[i+1, 0] + spring.get_potential()

            for rigid in np.nditer(self.mesh.m, flags=["refs_ok"]):
                rigid = rigid.item()
                if rigid is not None:
                    self.energy_tracker[i+1, 1] = self.energy_tracker[i+1, 1] + rigid.get_kinetic()
                    rigid.react(self.t)
                    rigid.forces = np.zeros(3, dtype=float)

            for j, (rigid, axis) in enumerate(zip(self.tracked_objects, self.tracked_axis)):
                self.motion_tracker[i+1, j] = self.tracked_objects[j].pos[axis - 1]

            self.energy_tracker[i + 1, 2] = self.energy_tracker[i + 1, 0] + self.energy_tracker[i + 1, 1]
            self.visual.update()

    def graph_motion(self):
        self.sin_set = np.sin(self.time_axis)
        motion_plot = plt.figure()
        ax = motion_plot.add_subplot()
        for j, rigid in enumerate(self.tracked_objects):
            ax.plot(self.time_axis, self.motion_tracker[:, j], label=f"Rigid at {rigid.initial_pos}")
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Position (m)")
        ax.set_title("Displacements in a Hookean System")
        ax.legend()
        motion_plot.show()

    def graph_energy(self):
        energy_plot = plt.figure()
        ax = energy_plot.add_subplot()
        ax.plot(self.time_axis, self.energy_tracker[:, 0], label="Kinetic Energy")
        ax.plot(self.time_axis, self.energy_tracker[:, 1], label="Potential Energy")
        ax.plot(self.time_axis, self.energy_tracker[:, 2], label="Total Energy")
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Energy (kJ)")
        ax.set_title("Energy of a Hookean System")
        ax.legend()
        energy_plot.show()

    def simple_fourier(self):
        frequency_plot = plt.figure()
        ax = frequency_plot.add_subplot()
        for j, rigid in enumerate(self.tracked_objects):
            fourier = np.fft.fft(self.motion_tracker[:, j] - np.mean(self.motion_tracker[:, j]))
            fourier = np.fft.fftshift(fourier)
            freq = np.fft.fftfreq(self.time_axis.shape[-1], d=self.t)
            freq = np.fft.fftshift(freq)
            ax.plot(freq, np.absolute(fourier))
        frequency_plot.show()

    def deviation_from_ideal(self, analytical):
        ideal = analytical(self.time_axis)
        error = [ideal[t] - self.motion_tracker[t, 0] for t, comp in enumerate(self.time_axis)]
        error_plot = plt.figure()
        ax = error_plot.add_subplot()
        ax.plot(self.time_axis, error)
        error_plot.show()





TrialMesh = Mesh([1, 1, 2])

TrialMesh.create_anchor([0, 0, 0], [0, 0, 0])
TrialMesh.create_pointmass([0, 0, 1], [0, 0, 1], 1)

TrialMesh.create_rest_spring([0, 0, 0], [0, 0, 1], 1)

Instance1 = Instance(TrialMesh, 0.001, 20)
Instance1.initialize_displacement([[0, 0, 1]], [[0, 0, 0.1]])
Instance1.initialize_tracking([[0, 0, 1]], [3])
Instance1.simulate()
Instance1.graph_motion()
Instance1.graph_energy()
Instance1.simple_fourier()
#Instance1.deviation_from_ideal(lambda t: (0.1 * np.sin(t + 0.5 * np.pi)) + 1)



#np.savetxt('1DOFTime.csv', self.time_axis[0::10], delimiter=',', fmt='%1.5f')
#np.savetxt('1DOFDisp.csv', self.motion_tracker[0::10], delimiter=',', fmt='%1.5f')
#np.savetxt(f'freq.csv', freq, delimiter=',', fmt='%1.10f')
#np.savetxt(f'fourier.csv', np.absolute(fourier), delimiter=',', fmt='%1.10f')



