Core
====

Running
-------

.. autofunction:: qtrio.run
.. autoclass:: qtrio.Runner
.. autoclass:: qtrio.Outcomes

Emissions
---------

The basics of handling Qt GUIs is to respond to the widgets' signals being emitted.
:func:`qtrio.enter_emissions_channel` is the primary tool for handling this.  It allows
for connection of signals prior to showing a window and subsequent iteration of the
emissions.  See the :doc:`emissions example <examples/emissions>` for an example usage.

.. autofunction:: qtrio.enter_emissions_channel
.. autoclass:: qtrio.Emission
.. autoclass:: qtrio.Emissions

If you need a more Qt-like callback mechanism :func:`qtrio.open_emissions_nursery`
offers that.  Instead of tossing the callbacks behind the couch where they can leave
their errors on the floor they will be run inside a nursery.

.. autofunction:: qtrio.open_emissions_nursery
.. autoclass:: qtrio.EmissionsNursery

Helpers
-------

.. autoclass:: qtrio.Signal

Reentry Events
--------------

Generally you should not need to use these functions.  If you want to have control over
when the Qt event type is registered, what value it gets, or handle any exceptions
raised then you may like to call these directly.

.. autofunction:: qtrio.register_event_type
.. autofunction:: qtrio.register_requested_event_type
.. autofunction:: qtrio.registered_event_type
