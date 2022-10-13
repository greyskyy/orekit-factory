"""Unit tests for math.py."""


def test_to_vector():
    from org.hipparchus.geometry.euclidean.threed import Vector3D

    from orekitfactory.factory import to_vector

    # test none return zero-vector
    assert Vector3D.ZERO.equals(to_vector(None))

    # test specifying each parameter positionally
    assert Vector3D(1.0, 0.0, 0.0).equals(to_vector(1.0))
    assert Vector3D(1.0, 2.0, 0.0).equals(to_vector(1, 2))
    assert Vector3D(1.0, 2.0, 3.0).equals(to_vector(1, 2, 3))

    # test specifying parameters as a list
    assert Vector3D(1.0, 0.0, 0.0).equals(to_vector([1.0]))
    assert Vector3D(1.0, 2.0, 0.0).equals(to_vector([1, 2]))
    assert Vector3D(1.0, 2.0, 3.0).equals(to_vector([1, 2, 3]))

    # test specifying parameters as a tuple
    assert Vector3D(1.0, 0.0, 0.0).equals(to_vector((1.0)))
    assert Vector3D(1.0, 2.0, 0.0).equals(to_vector((1, 2)))
    assert Vector3D(1.0, 2.0, 3.0).equals(to_vector((1, 2, 3)))


def test_to_rotation():
    from org.hipparchus.geometry.euclidean.threed import Rotation, Vector3D

    from orekitfactory.factory import to_rotation

    # verify None and Zero result in identity rotation
    assert Rotation.IDENTITY.equals(to_rotation())
    assert Rotation.IDENTITY.equals(
        to_rotation(x=Vector3D.ZERO, y=Vector3D.ZERO, z=Vector3D.ZERO)
    )

    # verify single axis rotation
    v1 = Vector3D(1.0, 2.0, 3.0).normalize()
    assert_rotations_equal(Rotation(v1, Vector3D.PLUS_I), to_rotation(x=v1))
    assert_rotations_equal(Rotation(v1, Vector3D.PLUS_J), to_rotation(y=v1))
    assert_rotations_equal(Rotation(v1, Vector3D.PLUS_K), to_rotation(z=v1))

    # verify 2-axis rotation
    v2 = v1.crossProduct(Vector3D.PLUS_K)
    assert_rotations_equal(
        Rotation(v1, v2, Vector3D.PLUS_I, Vector3D.PLUS_J), to_rotation(x=v1, y=v2)
    )
    assert_rotations_equal(
        Rotation(v1, v2, Vector3D.PLUS_I, Vector3D.PLUS_K), to_rotation(x=v1, z=v2)
    )
    assert_rotations_equal(
        Rotation(v1, v2, Vector3D.PLUS_J, Vector3D.PLUS_K), to_rotation(y=v1, z=v2)
    )

    # verify 3-axis rotation -- z axis is ignored
    assert_rotations_equal(
        Rotation(v1, v2, Vector3D.PLUS_I, Vector3D.PLUS_J),
        to_rotation(x=v1, y=v2, z=v1.crossProduct(v2)),
    )


def assert_rotations_equal(r1, r2):
    assert r1.getQ0() == r2.getQ0()
    assert r1.getQ1() == r2.getQ1()
    assert r1.getQ2() == r2.getQ2()
    assert r1.getQ3() == r2.getQ3()
