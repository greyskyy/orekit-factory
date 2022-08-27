from org.orekit.data import DataContext
from org.orekit.frames import Frame, Predefined

from .conventions import to_iers_conventions


def get_predefined(s: str) -> Predefined:
    if s is None:
        raise ValueError("Cannot determine Predefined frame from None.")

    try:
        return Predefined.valueOf(s)
    except BaseException:
        for p in Predefined.values():
            if p.getName().lower() == s.lower():
                return p

        raise ValueError(f"unknown frame type: {s}")


def get_frame(
    s: str,
    context: DataContext = None,
    iersConventions: str = None,
    simpleEop: bool = False,
    **kwargs,
) -> Frame:
    """Construct an orekit Frame from the provided string.

    Args:
        s (str): Frame name
        context (DataContext, optional): Data context from which frames will be loaded.
        Defaults to None.
        iersConventions (str, optional): IERSConventions to use when loading an ITRF.
        Defaults to None.
        simpleEop (bool, optional): When True, tidal effects will be ignored when
        converting to an ITRF. Defaults to False.

    Raises:
        ValueError: When the string is None or describes an unknown frame

    Returns:
        Frame: The orekit frame instance
    """
    if s is None:
        raise ValueError("frame name must be specified")

    if context is None:
        context = DataContext.getDefault()

    if s.lower() == "j2000" or s.lower() == "eme2000":
        return context.getFrames().getEME2000()
    elif s.lower() == "gcrf" or s.lower() == "eci":
        return context.getFrames().getGCRF()
    elif s.lower() == "itrf" or s.lower() == "ecef" or s.lower() == "ecf":
        iers = to_iers_conventions(iersConventions, "iers_2010")
        return context.getFrames().getITRF(iers, simpleEop)
    else:
        predefined = get_predefined(s)  # this will raise if undefined
        return context.getFrames().getFrame(predefined)
