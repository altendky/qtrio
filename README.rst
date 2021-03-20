
QTrio - a library bringing Qt GUIs together with ``async`` and ``await`` via Trio
*********************************************************************************


Resources
=========

+---------------------------------------------------------------------+---------------------------------------------------------------------+---------------------------------------------------------------------+
| `Documentation                                                      | `Read the Docs                                                      | `documentation                                                      |
| <https://qtrio.readthedocs.io>`_                                    | <https://qtrio.readthedocs.io>`_                                    | <https://qtrio.readthedocs.io>`_                                    |
+---------------------------------------------------------------------+---------------------------------------------------------------------+---------------------------------------------------------------------+
| `Chat                                                               | `Gitter                                                             | `chat                                                               |
| <https://gitter.im/python-trio/general>`_                           | <https://gitter.im/python-trio/general>`_                           | <https://gitter.im/python-trio/general>`_                           |
+---------------------------------------------------------------------+---------------------------------------------------------------------+---------------------------------------------------------------------+
| `Forum                                                              | `Discourse                                                          | `forum                                                              |
| <https://trio.discourse.group>`_                                    | <https://trio.discourse.group>`_                                    | <https://trio.discourse.group>`_                                    |
+---------------------------------------------------------------------+---------------------------------------------------------------------+---------------------------------------------------------------------+
| `Issues                                                             | `GitHub                                                             | `issues                                                             |
| <https://github.com/altendky/qtrio/issues>`_                        | <https://github.com/altendky/qtrio/issues>`_                        | <https://github.com/altendky/qtrio/issues>`_                        |
+---------------------------------------------------------------------+---------------------------------------------------------------------+---------------------------------------------------------------------+
| `Repository                                                         | `GitHub                                                             | `repository                                                         |
| <https://github.com/altendky/qtrio>`_                               | <https://github.com/altendky/qtrio>`_                               | <https://github.com/altendky/qtrio>`_                               |
+---------------------------------------------------------------------+---------------------------------------------------------------------+---------------------------------------------------------------------+
| `Tests                                                              | `GitHub Actions                                                     | `tests                                                              |
| <https://github.com/altendky/qtrio/actions?query=branch%3Amaster>`_ | <https://github.com/altendky/qtrio/actions?query=branch%3Amaster>`_ | <https://github.com/altendky/qtrio/actions?query=branch%3Amaster>`_ |
+---------------------------------------------------------------------+---------------------------------------------------------------------+---------------------------------------------------------------------+
| `Coverage                                                           | `Codecov                                                            | `coverage                                                           |
| <https://codecov.io/gh/altendky/qtrio>`_                            | <https://codecov.io/gh/altendky/qtrio>`_                            | <https://codecov.io/gh/altendky/qtrio>`_                            |
+---------------------------------------------------------------------+---------------------------------------------------------------------+---------------------------------------------------------------------+
| `Distribution                                                       | `PyPI                                                               | `distribution                                                       |
| <https://pypi.org/project/qtrio>`_                                  | <https://pypi.org/project/qtrio>`_                                  | <https://pypi.org/project/qtrio>`_`distribution                     |
+---------------------------------------------------------------------+---------------------------------------------------------------------+---------------------------------------------------------------------+


Introduction
============

Note:
   This library is in early development.  It works.  It has tests.  It
   has documentation.  Expect breaking changes as we explore a clean
   API.  By paying this price you get the privilege to provide
   feedback via `GitHub issues
   <https://github.com/altendky/qtrio/issues>`_ to help shape our
   future.  ``:]``

The QTrio project’s goal is to bring the friendly concurrency of Trio
using Python’s ``async`` and ``await`` syntax together with the GUI
features of Qt to enable more correct code and a more pleasant
developer experience.  QTrio is `permissively licensed
<https://github.com/altendky/qtrio/blob/master/LICENSE>`_ to avoid
introducing restrictions beyond those of the underlying Python Qt
library you choose.  Both PySide2 and PyQt5 are supported.

By enabling use of ``async`` and ``await`` it is possible in some
cases to write related code more concisely and clearly than you would
get with the signal and slot mechanisms of Qt concurrency.  In this
set of small examples we will allow the user to input their name then
use that input to generate an output message.  The user will be able
to cancel the input to terminate the program early.  In the first
example we will do it in the form of a classic “hello” console
program.  Well, classic plus a bit of boilerplate to allow explicit
testing without using special external tooling.  Then second, the form
of a general Qt program implementing this same activity.  And finally,
the QTrio way.

.. code:: python3

   import sys
   import typing


   def main(
       input_file: typing.TextIO = sys.stdin, output_file: typing.TextIO = sys.stdout
   ) -> None:
       try:
           output_file.write("What is your name? ")
           output_file.flush()
           name = input_file.readline()[:-1]
           output_file.write(f"Hi {name}, welcome to the team!\n")
       except KeyboardInterrupt:
           pass


   if __name__ == "__main__":  # pragma: no cover
       main()

Nice and concise, including the cancellation via ``ctrl+c``.  This is
because we can stay in one scope thus using both local variables and a
``try``/``except`` block.  This kind of explodes when you shift into a
classic Qt GUI setup.

.. code:: python3

   import typing

   from qtpy import QtCore
   from qtpy import QtWidgets


   def create_input() -> QtWidgets.QInputDialog:
       dialog = QtWidgets.QInputDialog()
       dialog.setWindowTitle("Hello")
       dialog.setLabelText("Enter your name:")

       return dialog


   def create_output() -> QtWidgets.QMessageBox:
       return QtWidgets.QMessageBox(
           QtWidgets.QMessageBox.Icon.Question,
           "Hello",
           "",
           QtWidgets.QMessageBox.Ok,
       )


   class Main:
       def __init__(
           self,
           input_dialog: typing.Optional[QtWidgets.QInputDialog] = None,
           output_dialog: typing.Optional[QtWidgets.QMessageBox] = None,
       ):
           if input_dialog is None:  # pragma: no cover
               input_dialog = create_input()

           if output_dialog is None:  # pragma: no cover
               output_dialog = create_output()

           self.input_dialog = input_dialog
           self.output_dialog = output_dialog

       def setup(self) -> None:
           self.input_dialog.accepted.connect(self.input_accepted)
           self.input_dialog.rejected.connect(self.input_rejected)

           self.input_dialog.show()

       def input_accepted(self) -> None:
           name = self.input_dialog.textValue()

           self.output_dialog.setText(f"Hi {name}, welcome to the team!")

           self.output_dialog.finished.connect(self.output_finished)
           self.output_dialog.show()

       def input_rejected(self) -> None:
           QtCore.QCoreApplication.instance().quit()

       def output_finished(self) -> None:
           QtCore.QCoreApplication.instance().quit()


   def main() -> None:  # pragma: no cover
       application = QtWidgets.QApplication([])
       application.setQuitOnLastWindowClosed(False)
       main_object = Main()
       main_object.setup()
       application.exec_()


   if __name__ == "__main__":  # pragma: no cover
       main()

The third example, below, shows how using ``async`` and ``await``
allows us to return to the more concise and clear description of the
sequenced activity. Most of the code is just setup for testability
with only the last four lines really containing the activity.

.. code:: python3

   import contextlib
   import typing

   from qtpy import QtWidgets

   import qtrio
   import qtrio.dialogs


   def create_input() -> qtrio.dialogs.TextInputDialog:
       return qtrio.dialogs.create_text_input_dialog(
           title="Hello",
           label="Enter your name:",
       )


   def create_output() -> qtrio.dialogs.MessageBox:
       return qtrio.dialogs.create_message_box(
           title="Hello",
           text="",
           icon=QtWidgets.QMessageBox.Icon.Question,
           buttons=QtWidgets.QMessageBox.Ok,
       )


   async def main(
       input_dialog: typing.Optional[qtrio.dialogs.TextInputDialog] = None,
       output_dialog: typing.Optional[qtrio.dialogs.MessageBox] = None,
   ) -> None:
       if input_dialog is None:  # pragma: no cover
           input_dialog = create_input()

       if output_dialog is None:  # pragma: no cover
           output_dialog = create_output()

       with contextlib.suppress(qtrio.UserCancelledError):
           name = await input_dialog.wait()

           output_dialog.text = f"Hi {name}, welcome to the team!"

           await output_dialog.wait()


   if __name__ == "__main__":  # pragma: no cover
       qtrio.run(main)
