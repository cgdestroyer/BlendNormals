import maya.OpenMaya as om


def copyNormals(sourceObject=None, targetObject=None, threshold=.01):
    """
    :param sourceObject: The polygon object to have the normals copied from
    :param targetObject: The polygon object to have its vertex normals set
    :param threshold: The minimum world space distance that considers vertices "on top" of each other
    :return: None
    """

    # do nothing if we haven't been given a source or target object
    if not sourceObject or not targetObject:
        return

    # get the dag paths to each obj
    sel = om.MSelectionList()
    sel.add(sourceObject)
    sel.add(targetObject)
    dagA = om.MDagPath()
    dagB = om.MDagPath()
    sel.getDagPath(0, dagA)
    sel.getDagPath(1, dagB)

    # create a vertex iterator for our first mesh
    iterA = om.MItMeshVertex(dagA)
    # Create arrays to store the indexes and positions of the boundary vertices on our source object
    boundaryVertsA = om.MIntArray()
    boundaryVertLocsA = om.MPointArray()

    while not iterA.isDone():
        # If the vertex is a boundary vertex (i.e. on the edge of a "hole") then store its information
        if iterA.onBoundary():
            # append that vertex's index
            boundaryVertsA.append(iterA.index())
            # append that vertex's position
            boundaryVertLocsA.append(iterA.position(om.MSpace.kWorld))

        iterA.next()

    # do the same for our target object
    iterB = om.MItMeshVertex(dagB)
    boundaryVertsB = om.MIntArray()
    boundaryVertLocsB = om.MPointArray()

    while not iterB.isDone():
        if iterB.onBoundary():
            boundaryVertsB.append(iterB.index())
            boundaryVertLocsB.append(iterB.position(om.MSpace.kWorld))

        iterB.next()

    # compare the two lists, seeing which vertices are "on top" of each other
    vertPairs = {}

    for i in range(boundaryVertLocsA.length()):
        # make a vector out of our boundary vertex position
        vectorA = om.MVector(boundaryVertLocsA[i].x, boundaryVertLocsA[i].y, boundaryVertLocsA[i].z)
        # iterate through each vertex of our target object
        for j in range(boundaryVertLocsB.length()):
            vectorB = om.MVector(boundaryVertLocsB[j].x, boundaryVertLocsB[j].y, boundaryVertLocsB[j].z)
            # if the length (distance) of the difference between these two vectors is less than the threshold:
            if om.MVector(vectorA - vectorB).length() <= threshold:
                # declare that vertex pairing
                vertPairs[boundaryVertsA[i]] = boundaryVertsB[j]
                # don't waste time comparing to the other vertices
                break

    # now set the vertex normals for each pairing
    fnMeshA = om.MFnMesh(dagA)
    fnMeshB = om.MFnMesh(dagB)

    for vert in vertPairs:
        # vector object to store the vertex normal
        vertNormal = om.MVector()
        # get the vertex normal at the source object's vert index
        fnMeshA.getVertexNormal(vert, vertNormal, om.MSpace.kWorld)
        # set the vertex normal at that source vert's pair
        fnMeshB.setVertexNormal(vertNormal, vertPairs[vert], om.MSpace.kWorld)

    # TODO: Not a seamless transition on high resolution meshes but still much better than before.
