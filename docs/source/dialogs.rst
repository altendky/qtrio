.. _dialogs:

Dialogs
=======

Usage Pattern
-------------

Creation Functions
------------------

.. autofunction:: qtrio.dialogs.create_integer_dialog
.. autofunction:: qtrio.dialogs.create_text_input_dialog
.. autofunction:: qtrio.dialogs.create_file_open_dialog
.. autofunction:: qtrio.dialogs.create_file_save_dialog
.. autofunction:: qtrio.dialogs.create_message_box
.. autofunction:: qtrio.dialogs.create_progress_dialog


Classes
-------

.. autoclass:: qtrio.dialogs.IntegerDialog
   :members:

.. autoclass:: qtrio.dialogs.TextInputDialog
   :members:

.. autoclass:: qtrio.dialogs.FileDialog
   :members:

.. autoclass:: qtrio.dialogs.MessageBox
   :members:

.. autoclass:: qtrio.dialogs.ProgressDialog
   :members:


Protocols
---------

.. autoclass:: qtrio.dialogs.BasicDialogProtocol
   :members:

.. autoclass:: qtrio.dialogs.DialogProtocol
   :members:


Protocol Checkers
*****************

These callables can be used if you want to verify that your own classes properly
implement the associated protocols.  They are simple pass through decorators at runtime
but when checking type hints they will result in a failure if the class does not
implement the protocol.

.. autodata:: qtrio.dialogs.check_basic_dialog_protocol
.. autodata:: qtrio.dialogs.check_dialog_protocol
