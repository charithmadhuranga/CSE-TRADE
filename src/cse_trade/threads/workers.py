from PySide6.QtCore import QRunnable, Slot, QObject, Signal
import traceback
import sys

class WorkerSignals(QObject):
    """
    Defines the signals available from a running worker thread.
    """
    finished = Signal()
    error = Signal(tuple)
    result = Signal(object)
    progress = Signal(int)

class Worker(QRunnable):
    """
    Worker thread for running API calls.
    """
    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()
        
        # Explicitly avoid auto-delete if we want to manage it, 
        # but auto-delete is usually fine if signals are connected correctly.
        # The crash often happens if the WorkerSignals QObject is destroyed 
        # while the threadpool is still cleaning up.
        self.setAutoDelete(True)

    @Slot()
    def run(self):
        try:
            # Perform the task
            result = self.fn(*self.args, **self.kwargs)
        except Exception:
            # Traceback and error signal
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            # Result signal
            self.signals.result.emit(result)
        finally:
            # Finished signal
            self.signals.finished.emit()
