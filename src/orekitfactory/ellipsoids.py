from org.orekit.frames import Frame
from org.orekit.models.earth import ReferenceEllipsoid

from .frames import get_frame


def get_reference_ellipsoid(
    model: str = "wgs84", frameName: str = "itrf", frame: Frame = None, **kwargs
) -> ReferenceEllipsoid:
    """Create a reference ellipsoid from the string description.

    Args:
        model (str, optional): The model to use. Must be one of [wgs84, iers2010,
        iers2003, iers1996]. Defaults to "wgs84".
        frameName (str, optional): Name of the ellipsoid's body frame. Defaults to
        "itrf".
        frame (Frame, optional): Frame to use as the ellipsoids body frame.
        Overrides the name specified by `frameName`

    Raises:
        ValueError: When an unknown reference ellipsoid model is provided

    Returns:
        ReferenceEllipsoid: The reference ellipsoid instance
    """
    if model is None:
        raise ValueError("reference ellipsoid name cannot be None")

    if frame is None:
        frame = get_frame(frameName, **kwargs)
    elif isinstance(frame, str):
        frame = get_frame(frame, **kwargs)

    lModel = model.lower()
    if lModel == "wgs84" or lModel == "wgs-84":
        return ReferenceEllipsoid.getWgs84(frame)
    elif lModel == "iers2010" or lModel == "iers-2010" or lModel == "2010":
        return ReferenceEllipsoid.getIers2010(frame)
    elif lModel == "iers2003" or lModel == "iers-2003" or lModel == "2003":
        return ReferenceEllipsoid.getIers2003(frame)
    elif (
        lModel == "iers1996"
        or lModel == "iers-1996"
        or lModel == "1996"
        or lModel.lower() == "iers96"
        or lModel.lower() == "iers-96"
        or lModel == "96"
    ):
        return ReferenceEllipsoid.getIers96(frame)
    else:
        raise ValueError(f"Cannot convert unknown reference ellipsoid value {model}")
