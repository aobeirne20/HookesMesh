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

Instance1 = Instance(TrialMesh, 0.01, 300)
Instance1.simple_initiate([[0, 1, 0]], [[0, 0, -0.1]], [[0, 1, 0], [0, 1, 1]], [3, 3])




TrialMesh = Mesh([1, 1, 2])

TrialMesh.create_anchor([0, 0, 0], [0, 0, 0])
TrialMesh.create_pointmass([0, 0, 1], [0, 0, 1], 1)

TrialMesh.create_spring([0, 0, 0], [0, 0, 1], 1, 1)

Instance1 = Instance(TrialMesh, 0.001, 10)
Instance1.simple_initiate([[0, 0, 1]], [[0, 0, 0.2]], [[0, 0, 1]], [3])



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

Instance1 = Instance(TrialMesh, 0.01, 10)
Instance1.initialize_tracking([[0, 1, 0], [0, 1, 1]], [3, 3])
Instance1.initialize_displacement([[0, 1, 0], [0, 1, 1]], [[0, 0, -0.2], [0, 0, 0.2]])
Instance1.simulate()