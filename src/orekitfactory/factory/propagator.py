import functools
import orekit
import astropy.units as units

from org.hipparchus.ode.nonstiff import DormandPrince853Integrator
from org.orekit.attitudes import AttitudeProvider, InertialProvider
from org.orekit.bodies import CelestialBody
from org.orekit.data import DataContext
from org.orekit.forces import ForceModel
from org.orekit.forces.drag import DragForce, IsotropicDrag
from org.orekit.forces.gravity import (
    HolmesFeatherstoneAttractionModel,
    ThirdBodyAttraction,
)
from org.orekit.forces.gravity.potential import GravityFieldFactory
from org.orekit.forces.radiation import (
    IsotropicRadiationClassicalConvention,
    SolarRadiationPressure,
)
from org.orekit.models.earth import ReferenceEllipsoid
from org.orekit.models.earth.atmosphere import HarrisPriester
from org.orekit.orbits import Orbit, OrbitType
from org.orekit.propagation import Propagator, SpacecraftState
from org.orekit.propagation.analytical.tle import TLE, TLEPropagator
from org.orekit.propagation.numerical import NumericalPropagator

from .ellipsoids import get_reference_ellipsoid
from ..utils import validate_quantity


@functools.singledispatch
def to_propagator(
    orbit: Orbit | TLE,
    attitudeProvider: AttitudeProvider = None,
    mass: units.Quantity[units.kg] | float = 100.0 * units.kg,
    centralBody: ReferenceEllipsoid = None,
    context: DataContext = None,
    minStep: float = 0.001,
    maxStep: float = 1000.0,
    positionTolerance: units.Quantity[units.m] | float = 10.0 * units.m,
    considerGravity: bool = True,
    gravityFieldDegree: int = 2,
    gravityFieldOrder: int = 2,
    considerSolarPressure: bool = True,
    sun: CelestialBody = None,
    solarPressureCrossSection: units.Quantity[units.m**2]
    | float = 1.0 * units.m**2,
    solarCa: float = 0.2,
    solarCs: float = 0.8,
    considerAtmosphere: bool = True,
    atmosphereCrossSection: units.Quantity[units.m**2] | float = 1.0 * units.m**2,
    atmosphereDragCoeff: float = 2.2,
    bodies: list = ["sun", "moon", "jupiter"],
    orbitType: OrbitType = None,
    **kwargs
) -> Propagator:
    """Build a propagator instance for the provided orbit definition

    Args:
        orbit (TLE|Orbit): The orbit definition.
        attitudeProvider (AttitudeProvider, optional): The attitude provider to use
        when propagating. Defaults to None.
        mass (float, optional): mass of the spacecraft in kg. Defaults to 100..
        centralBody (ReferenceEllipsoid, optional): Central body, the WGS-84 ellipsoid
        will be used if unspecified. Defaults to None.
        context (DataContext, optional): Data context to use when building the
        propagator. If None, the default will be used. Defaults to None.
        minStep (float, optional): Minimum time step to take during propagation, in
        seconds. Ignored for TLE orbits. Defaults to 0.001.
        maxStep (float, optional): Maxmimum time step to take during propagation, in
        seconds. Ignored for TLE orbits. Defaults to 1000.
        positionTolerance (float, optional): Positional tolerance during propagation,
        in meters. Ignored for TLE orbits. Defaults to 10.
        considerGravity (bool, optional): Indication whether to consider a gravity
        model during propagation. Ignored for TLE orbits. Defaults to True.
        gravityFieldDegree (int, optional): Degree of the gravity field (use 10 for
        high fidelity, 2 for low). Ignored for TLE orbits. Defaults to 2.
        gravityFieldOrder (int, optional): Order of the gravity field (use 10 for high
        fidelity and 2 for low). Ignored for TLE orbits. Defaults to 2.
        considerSolarPressure (bool, optional): Indication whether to consider solar
        pressure during propagation. Ignored for TLE orbits. Defaults to True.
        sun (CelestialBody, optional): Sun location, default will be loaded if not
        provided.  Ignored for TLE orbits.  Defaults to None.
        solarPressureCrossSection (float, optional): Cross section facing the solar
        pressure vector, in square meters. Ignored for TLE orbits. Defaults to 1.
        solarCa (float, optional): solar absorption coefficient. Ignored for TLE orbits.
        Defaults to 0.2.
        solarCs (float, optional): solar reflection coefficient. Ignored for TLE orbits.
        Defaults to 0.8.
        considerAtmosphere (bool, optional): Indication whether to include atmospheric
        drag. Ignored for TLE orbits. Defaults to True.
        atmosphereCrossSection (float, optional): Cross section facing the drag force,
        in square meters. Ignored for TLE orbits. Defaults to 1..
        atmosphereDragCoeff (float, optional): drag coefficient. Ignored for TLE orbits.
        Defaults to 4.
        bodies (list, optional): List of celestial bodies whose gravitational effects
        will be considered. Ignored for TLE orbits. Defaults to
        ['sun','moon','jupiter'].

    Raises:
        ValueError: When an invalid orbit definition was provided.

    Returns:
        Propagator: The orbit propagator. Either SGP4 or SDP4 (for TLEs), or a
        numerical propagator for a keplerian, equanotial, or circular orbit.
    """
    if not orbit:
        return None

    raise ValueError(
        "Cannot construct a propagator for unknown orbit type: " + str(type(orbit))
    )


@to_propagator.register
def to_sgp4_sdp4(
    tle: TLE,
    attitudeProvider: AttitudeProvider = None,
    mass: units.Quantity[units.kg] | float = 100.0 * units.kg,
    context: DataContext = None,
    **kwargs
) -> Propagator:
    """Construct a propagator from a TLE.

    Args:
        tle (TLE): The two line element
        attitudeProvider (AttitudeProvider, optional): The attitude provider to use
        when propagating. Defaults to None.
        mass (u.Quantity[u.kg]|float, optional): mass of the spacecraft in kg. Defaults
        to 100 kg.
        context (DataContext, optional): Data context to use when building the
        propagator. If None, the default will be used. Defaults to None.

    Returns:
        Propagator: The SGP4 (or SDP4, as appropriate) propagator for the TLE.
    """
    if context is None:
        context = DataContext.getDefault()

    mass = validate_quantity(mass, units.kg)

    teme = context.getFrames().getTEME()
    if attitudeProvider is None:
        attitudeProvider = InertialProvider.of(teme)

    return TLEPropagator.selectExtrapolator(
        tle, attitudeProvider, float(mass.to_value(units.kg)), teme
    )


@to_propagator.register
def to_numerical_propagator(
    orbit: Orbit,
    attitudeProvider: AttitudeProvider = None,
    mass: units.Quantity[units.kg] | float = 100.0 * units.kg,
    centralBody: ReferenceEllipsoid = None,
    context: DataContext = None,
    minStep: float = 0.001,
    maxStep: float = 1000.0,
    positionTolerance: units.Quantity[units.m] | float = 10.0 * units.m,
    considerGravity: bool = True,
    gravityFieldDegree: int = 2,
    gravityFieldOrder: int = 2,
    considerSolarPressure: bool = True,
    sun: CelestialBody = None,
    solarPressureCrossSection: units.Quantity[units.m**2]
    | float = 1.0 * units.m**2,
    solarCa: float = 0.2,
    solarCs: float = 0.8,
    considerAtmosphere: bool = True,
    atmosphereCrossSection: units.Quantity[units.m**2] | float = 1.0 * units.m**2,
    atmosphereDragCoeff: float = 2.2,
    bodies: list = ["sun", "moon", "jupiter"],
    orbitType: OrbitType = None,
    **kwargs
) -> Propagator:
    """
    Generate a propagator from an Orbit definition.

    Note that this method currently uses a HarrisPriester atmospheric model, which
    takes into account the diurnal density bulge , but doesn't need space weather.

    Args:
        orbit (Orbit): The orbit for which a numerical propagtor will be built
        attitudeProvider (AttitudeProvider, optional): The attitude provider to use
        when propagating. Defaults to None.
        mass (float, optional): mass of the spacecraft in kg. Defaults to 100.
        centralBody (ReferenceEllipsoid, optional): Central body, the WGS-84 ellipsoid
        will be used if unspecified. Defaults to None.
        context (DataContext, optional): Data context to use when building the
        propagator. If None, the default will be used. Defaults to None.
        minStep (float, optional): Minimum time step to take during propagation, in
        seconds. Defaults to 0.001.
        maxStep (float, optional): Maxmimum time step to take during propagation, in
        seconds. Defaults to 1000..
        positionTolerance (float, optional): Positional tolerance during propagation,
        in meters. Defaults to 10..
        considerGravity (bool, optional): Indication whether to consider a gravity
        model during propagation. Defaults to True.
        gravityFieldDegree (int, optional): Degree of the gravity field (use 10 for
        high fidelity, 2 for low). Defaults to 2.
        gravityFieldOrder (int, optional): Order of the gravity field (use 10 for high
        fidelity and 2 for low). Defaults to 2.
        considerSolarPressure (bool, optional): Indication whether to consider solar
        pressure during propagation. Defaults to True.
        sun (CelestialBody, optional): Sun location, default will be loaded if not
        provided. Defaults to None.
        solarPressureCrossSection (float, optional): Cross section facing the solar
        pressure vector, in square meters. Defaults to 1..
        solarCa (float, optional): solar absorption coefficient. Defaults to 0.2.
        solarCs (float, optional): solar reflection coefficient. Defaults to 0.8.
        considerAtmosphere (bool, optional): Indication whether to include atmospheric
        drag. Defaults to True.
        atmosphereCrossSection (float, optional): Cross section facing the drag force,
        in square meters. Defaults to 1..
        atmosphereDragCoeff (float, optional): drag coefficient. Defaults to 4..
        bodies (list, optional): List of celestial bodies whose gravitational effects
        will be considered. Defaults to ['sun','moon','jupiter'].
        orbitType (OrbitType, optional): Override the orbit type, for use in
        propagation. Defaults to `orbit.getType()`.

    Returns:
        Propagator: the propagator
    """

    # create default values for None parameters
    if context is None:
        context = DataContext.getDefault()

    if centralBody is None:
        centralBody = get_reference_ellipsoid(
            "wgs84", frameName="itrf", simpleEop=False, iersConventions="iers2010"
        )

    # validate quantity parameters
    mass: units.Quantity = validate_quantity(mass, units.kg)
    solarPressureCrossSection: units.Quantity = validate_quantity(
        solarPressureCrossSection, units.m**2
    )
    atmosphereCrossSection: units.Quantity = validate_quantity(
        atmosphereCrossSection, units.m**2
    )
    positionTolerance = validate_quantity(positionTolerance, units.m)

    # load sun if needed
    if (considerSolarPressure or considerAtmosphere) and sun is None:
        sun = context.getCelestialBodies().getSun()

    # build the propagator
    propagator = _build_propagator(positionTolerance, orbit, minStep, maxStep)
    propagator.setOrbitType(orbitType or orbit.getType())

    # add gravity force model, if necessary
    if considerGravity:
        propagator.addForceModel(
            _build_gravity(gravityFieldDegree, gravityFieldOrder, centralBody)
        )

    # add solar pressure force model, if necessary
    if considerSolarPressure:
        propagator.addForceModel(
            _build_solar_pressure(
                sun, solarPressureCrossSection, solarCa, solarCs, centralBody
            )
        )

    # add atmospheric model, if necessary
    if considerAtmosphere:
        propagator.addForceModel(
            _build_drag_force(
                sun, centralBody, atmosphereCrossSection, atmosphereDragCoeff
            )
        )

    # add 3rd body force models if any bodies are specified
    if bodies is not None:
        for bodyName in bodies:
            body = context.getCelestialBodies().getBody(bodyName)
            if body is not None:
                propagator.addForceModel(ThirdBodyAttraction(body))

    # initialize propagator with an initial state at the orbit epoch
    initialState = SpacecraftState(orbit, float(mass.to_value(units.kg)))
    propagator.setInitialState(initialState)

    # add the attitude provider, creating a default one if none was provided
    propagator.setAttitudeProvider(
        attitudeProvider or InertialProvider.of(initialState.getFrame())
    )

    return propagator


def _build_propagator(
    positionTolerance: units.Quantity[units.m],
    orbit: Orbit,
    minStep: float,
    maxStep: float,
) -> Propagator:
    tolerances = NumericalPropagator.tolerances(
        float(positionTolerance.to_value(units.m)), orbit, orbit.getType()
    )
    integrator = DormandPrince853Integrator(
        float(minStep),
        float(maxStep),
        orekit.JArray("double").cast_(tolerances[0]),
        orekit.JArray("double").cast_(tolerances[1]),
    )

    return NumericalPropagator(integrator)


def _build_gravity(
    gravityFieldDegree: int, gravityFieldOrder: int, centralBody: ReferenceEllipsoid
) -> ForceModel:
    gravityProvider = GravityFieldFactory.getNormalizedProvider(
        gravityFieldDegree, gravityFieldOrder
    )
    return HolmesFeatherstoneAttractionModel(
        centralBody.getBodyFrame(), gravityProvider
    )


def _build_solar_pressure(
    sun: CelestialBody,
    solarPressureCrossSection: units.Quantity,
    solarCa: float,
    solarCs: float,
    centralBody: ReferenceEllipsoid,
) -> ForceModel:
    convention = IsotropicRadiationClassicalConvention(
        float(solarPressureCrossSection.to_value(units.m**2)),
        float(solarCa),
        float(solarCs),
    )
    return SolarRadiationPressure(sun, centralBody.getEquatorialRadius(), convention)


def _build_drag_force(
    sun: CelestialBody,
    centralBody: ReferenceEllipsoid,
    atmosphereCrossSection: units.Quantity,
    atmosphereDragCoeff: float,
) -> ForceModel:
    atmosphere = HarrisPriester(sun, centralBody)
    drag = IsotropicDrag(
        float(atmosphereCrossSection.to_value(units.m**2)), float(atmosphereDragCoeff)
    )
    dragForce = DragForce(atmosphere, drag)
    return dragForce
