# This is .NET's Common Language Runtime. It's an execution environment that is able to execute code from several
# different languages.
import clr

import RevitServices

clr.AddReference('RevitServices')  # Dynamo's classes for handling Revit documents

# An internal Dynamo class that keeps track of the document that Dynamo is currently attached to
from RevitServices.Persistence import DocumentManager

# A Dynamo class for opening and closing transactions to change the Revit document's database
from RevitServices.Transactions import TransactionManager

# Loads the Autodesk namespace
import Autodesk

# Loading Revit's API classes
import Autodesk.Revit.DB

# Loading Revit's API UI classes
import Autodesk.Revit.UI

clr.AddReference('RevitAPI')  # Adding reference to Revit's API DLLs
clr.AddReference('RevitAPIUI')  # Adding reference to Revit's UI API DLLs

from typing import Callable, Iterable, Any


def handler(sender: Autodesk.Revit.DB.Document,
            event: Autodesk.Revit.DB.Events.RevitEventArgs) -> None:
    """Handler to be invoked on document save/save as"""

    print(f'info: {handler.__name__}() invoked')

    # todo - print preview command temporarily for testing purposes
    cmd = Autodesk.Revit.UI.RevitCommandId.LookupPostableCommandId(Autodesk.Revit.UI.PostableCommand.PrintPreview)

    try:
        print(f'info: {handler.__name__}() Posting {cmd.Id=} {cmd.Name=}')

        TransactionManager.Instance.EnsureInTransaction(sender)

        # post command
        DocumentManager.Instance.CurrentUIApplication.PostCommand(cmd)

        TransactionManager.Instance.TransactionTaskDone()

    except Autodesk.Revit.Exceptions.ArgumentNullException:
        print(f'error: {handler.__name__}() RevitCommandId for {cmd} could not be determined')

    except Autodesk.Revit.Exceptions.ArgumentException:
        print(f'error: {handler.__name__}() RevitCommandId for {cmd} could not be posted')

    except Autodesk.Revit.Exceptions.InvalidOperationException:
        print(f'error: {handler.__name__}() RevitCommandId for {cmd} could not be posted. This is likely as a '
              f'result of multiple commands being posted (is the same event posting multiple commands?')

    # catch all exception for any unhandled reason
    except Exception as e:
        print(f'error: {handler.__name__}() Unhandled/unexpected exception of type {type(e)}. See below for details')
        print(e)

    else:
        print(f'info: {handler.__name__}() Posted {cmd.Id=} {cmd.Name=}')

    print(f'info: {handler.__name__}() terminated')


def add_handler_to_events(handler_function: Callable,
                          events: Iterable[Autodesk.Revit.DB.Events.RevitEventArgs]) -> None:
    """Add event handlers"""
    for event in events:
        print(f'info: {add_handler_to_events.__name__}() adding {handler_function.__name__} to {event}')
        event += handler_function


def main(args: tuple) -> int:
    """Program Entry Point"""

    events = (DocumentManager.Instance.CurrentDBDocument.DocumentSaved,
              DocumentManager.Instance.CurrentDBDocument.DocumentSavedAs)

    # add the handler to the DocumentSaved and DocumentSavedAs events
    add_handler_to_events(handler, events)

    return 0


OUT = main(tuple(IN))
