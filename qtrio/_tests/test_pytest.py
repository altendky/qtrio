import pytest
import trio

import qtrio


@pytest.mark.xfail(reason="this is supposed to fail", strict=True)
@qtrio.host
async def test_times_out(request):
    await trio.sleep(10)


# TODO: test that the timeout case doesn't leave trio active...  like
#       it was doing five minutes ago.
