# Orekit-factory

A collection of utilities to bootstrap an orekit-based python application.

## Installation

```sh
$ pip install orekit-factory
```

## Usage

The utilities provided by the `orekitfactory` module can be broken out into the categories below.  See the python docs for complete details.

### Application initialization

The `orekitfactory.init_orekit()` method reduces the boilerplate for starting python-based orekit applications. It performs the following steps, then returns a handle to the orekit VM:

1. Downloads the default orekit data zip to a data directory. Note the option to re-download the file, if it exists, or simply use the cached version.
2. Setup the data context using that default data zip.

A basic example:

```python
import orekit
import orekitfactory

vm = orekit.initVM()
orekitfactory.init_orekit()
```

### Enumeration utilties

`orekitfactory.to_iers_conventions()` - Convert a string to the `IERSConventions` orekit enumeration.

```python
import orekitfactory

iers_conventions = orekitfactory.to_iers_conventions("iers_2010")
```

### Date utilities

Multiple date utilities improve application's abilities to use AbsoluteDate.

`orekitfactory.to_absolute_date()` - Converts an ISO-8601 string or a `datetime` instance into an `AbsoluteDate` instance based on UTC. The data context and time scale can be provided via optional parameters. This method is a no-op if an `AbsoluteDate` instance is provided.

`orekitfactory.DateInterval` - This class provides an interval of `AbsoluteDate` and provides the standard interval operations like *duration*, *comparison*, *overlap*, and *intersection*.

`orekitfactory.DateIntervalList` - A list of non-overlapping `DateInterval` instances. Provides set operations like *union*, *intersection*, and *subtraction*.

`orekitfactory.DateIntervalListBuilder` - A utility class useful when incrementally building up a `DateIntervalList`.

```python
import orekitfactory

date1 = orekitfactory.to_absolute_date("2022-08-28T13:15:00Z")
date2 = orekitfactory.to_absolute_date("2022-08-28T13:16:00Z")
date3 = orekitfactory.to_absolute_date("2022-08-28T13:17:00Z")
date4 = orekitfactory.to_absolute_date("2022-08-28T13:18:00Z")

ivl1 = orekitfactory.DateInterval(date1, date3)
ivl2 = orekitfactory.DateInterval(date2, date4)
ivl3 = orekitfactory.DateInterval(date1, date2)

dlist = orekitfactory.DateInteralList(intervals=[ivl1, ivl2, ivl3])

assert 2 == len(dlist)
print(dlist)

dlist2 = orekitfactory.DateIntervalList(interval=DateInterval(date1, date5)).subtract(dlist)

print(dlist2)
```

### Frames and reference ellipsoids

`orekitfactory.get_reference_ellipsoid()` - A utility function for loading `ReferenceEllipsoid` instances from summary strings.

`orekitfactory.get_frame()` - A utility function for loading `Frame` instances based on shortened summary names, or predefined builtins.

```python
import orekitfactory

itrf = orekitfactory.get_frame("itrf")
wgs84 = orekitfactory.get_reference_ellipsoid("wgs84", frame=itrf)

# an alternate calls
wgs84 = orekitfactory.get_reference_ellipsoid("wgs84", frame="itrf")
wgs84 = orekitfactory.get_reference_ellipsoid("wgs84", frameName="itrf")
```

### Orbit definitions and propagators

`orekitfactory.check_tle()` - Checks the two lines of a TLE for valid format.

`orekitfactory.to_tle()` - Constructs an orekit `TLE` instance using the provided UTC time scale, or loading one from the default data context.

`orekitfactory.to_orbit()` - Constructs a `KeplerianOrbit` instance from the provided parameters.

`orekitfactory.to_propgator()` - Construct a propagator (`SGP4` or `SDP4` as appropriate for a TLE, or a `NumericalPropagator` for keplerian orbits) from the provided orbit.

```python
import orekitfactory

assert orekitfactory.check_tle(
    "1 49260U 21088A   22166.94778099  .00000339  00000+0  85254-4 0  9992",
    "2 49260  98.2276 237.1831 0001142  78.2478 281.8849 14.57099002 38060"
)

tle = orekitfactory.to_tle(
    "1 49260U 21088A   22166.94778099  .00000339  00000+0  85254-4 0  9992",
    "2 49260  98.2276 237.1831 0001142  78.2478 281.8849 14.57099002 38060"
)

orbit = orekitfactory.to_orbit(
    a="7080 km",
    e=0.0008685,
    i=85,
    omega=u.Quantity("261.9642 deg"),
    w="257.7333 deg",
    epoch="2022-06-16T17:54:00Z",
    v=1.2,
)

sgp4 = to_propagator(tle)
prop = to_propagator(orbit)
```

### Vectors and Rotations

`orekitfactory.to_vector()` - Simplifies the creation of `Vector3D` instances, avoiding the `InvalidArgument` errors caused by passing `int` instead of `float` to the `Vector3D` constructor.

`orekitfactory.to_rotation()` - Creates a `Rotation` using the provided axis defintions.

```python
import orekitfactory

new_x = orekitfactory.to_vector(1, 2, 3).normalize()
new_y = new_x.crossProduct(Vector3D.PLUS_K)

tx = orekitfactory.to_rotation(x=new_x, y=new_y)
```
