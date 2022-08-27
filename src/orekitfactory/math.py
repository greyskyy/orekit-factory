from typing import Sequence
from org.hipparchus.geometry.euclidean.threed import Rotation, Vector3D


def to_vector(
    x: float | list[float] | tuple[float] | None, y: float = 0.0, z: float = 0.0
) -> Vector3D:
    """Create a Vector3D instance from the values.

    Args:
        x (float | list[float] | tuple[float] | None): If a scalar, the x value.
        Otherwise the [x, y, z] vector.
        y (float, optional): If `x` is a scalar, the y value. Defaults to 0.0.
        z (float, optional): If `x` is a scalar, the z value. Defaults to 0.

    Returns:
        Vector3D: The vector instance.
    """

    if isinstance(x, Sequence) or x is None:
        a: list[float] = x
        if a is None or len(a) == 0:
            return Vector3D.ZERO
        elif len(a) == 1:
            return Vector3D(float(a[0]), 0.0, 0.0)
        elif len(a) == 2:
            return Vector3D(float(a[0]), float(a[1]), 0.0)
        else:
            return Vector3D(float(a[0]), float(a[1]), float(a[2]))
    else:
        return Vector3D(float(x), float(y), float(z))


def to_rotation(x: Vector3D = None, y: Vector3D = None, z: Vector3D = None) -> Rotation:
    """Create a rotation using the defined axis.

    Rotation is created from the source to the destination as defined by the provided
    axis. If none are provided, the Identity rotation is returned.

    Args:
        x (Vector3D, optional): The destination X unit vector, defined in the source
        frame. Defaults to None.
        y (Vector3D, optional): The destination Y unit vector, defined in the source
        frame. Defaults to None.
        z (Vector3D, optional): The destination Z unit vector, defined in the source
        frame. Defaults to None.

    Returns:
        Rotation: The rotation transforming the source frame to the destination.

    Raises:
        If the norm of any provided axis is zero, or if 2 provided vectors are colinear.
    """
    if Vector3D.ZERO.equals(x):
        x = None
    if Vector3D.ZERO.equals(y):
        y = None
    if Vector3D.ZERO.equals(z):
        z = None

    # if x is specified
    if x is not None:
        # x and y are specifed
        if y is not None:
            return Rotation(x, y, Vector3D.PLUS_I, Vector3D.PLUS_J)
        # if x and z are specfied
        elif z is not None:
            return Rotation(x, z, Vector3D.PLUS_I, Vector3D.PLUS_K)
        # if only x is specified
        else:
            return Rotation(x, Vector3D.PLUS_I)
    # x is not specified, by y is
    elif y is not None:
        # if y and z are specifed
        if z is not None:
            return Rotation(y, z, Vector3D.PLUS_J, Vector3D.PLUS_K)
        # only y is specified
        else:
            return Rotation(y, Vector3D.PLUS_J)
    # if only z is specified
    elif z is not None:
        return Rotation(z, Vector3D.PLUS_K)
    # none are specified
    else:
        return Rotation.IDENTITY
