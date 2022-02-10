# HookesMesh
Simulates hookean mechanics for a multidimensional mesh, and visualizes it using MeshVisualizer from tkrasnoperov.

## Creating a Mesh
All mesh and simulation parameters are controlled through the addition and modification of code at the bottom of main.py
[] indicates a list that should be 3D, even if the simulation will logically only operate in less
#### Physical Parameters
Mesh([list containing sizes in up to 3 dimensions) 
Mesh.create_anchor([position in mesh array "logically"], [actual position])
Mesh.create_pointmass([position in mesh array "logically"], [actual position])
Mesh.create_rest_spring([one mesh array "logical" position], [other mesh array "logical" position], k-value for spring)
#### Simulation Parameters
Instance(Mesh object, simulation tick duration in seconds, total simulation time in seconds)
Instance.intialize_displacement([one mesh array "logical" position], [displacement])
Instance.intialize_static_load([one mesh array "logical" position], [force])
Instance.intialize_tracking([one mesh array "logical" position], [axis to track (1 to 3)])
Instance.simulate()
#### Analysis Tools
Instance.graph_motion()
Instance.graph_energy()
Instance.simple_fourier()
Instance.deviation_from_ideal(lambda function representing x(t) analytical solution)
