"""Pytest global fixtures."""
import orekit
import orekit.pyhelpers
import pytest


@pytest.fixture(autouse=True, scope="session")
def vm():
    """Fixture for the orekit VM initialization."""
    vm = orekit.initVM()

    import java.io
    import org.orekit.data

    # just crawl the entire directory for data files. It'll
    # find data in src/tests/data/*.
    ctx = org.orekit.data.LazyLoadedDataContext()
    ctx.getDataProvidersManager().addProvider(
        org.orekit.data.DirectoryCrawler(java.io.File("."))
    )

    org.orekit.data.DataContext.setDefault(ctx)

    return vm
