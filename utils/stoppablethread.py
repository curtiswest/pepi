"""
Stoppablethread.py: Threads that can be called upon to stop (as long as they obey the stop command).
"""
from threading import Thread, Event

__author__ = 'Curtis West'
__credits__ = '@philippe-f on StackOverflow for first StoppableThread implementation'
__version__ = '0.1'
__maintainer__ = 'Curtis West'
__email__ = "curtis@curtiswest.net"
__status__ = 'Development'


class StoppableThread(Thread):
    """
    A thread that has a stop() event that the function running can access to decide to stop when appropriate.
    """
    def __init__(self, target=None, name=None, args=()):
        """
        Initialises a StoppableThread.
        Args:
            target: the function to call when the thread starts running. This function should take two arguments:
                (args, stopped_func). The stopped_func can be called from inside the passed function and internally
                queries the thread's `stop` event to determine whether the function should cleanup and terminate.
            args: the argument tuple passed during target invocation.
            name: the thread name
        """
        self.target = target
        self.args = args
        super(StoppableThread, self).__init__(name=name)
        self._stop_event = Event()

    def stop(self):
        """
            Signals a Stop event for this thread that a running function can query.
        Returns:
            None
        """
        self._stop_event.set()

    def is_stopped(self):
        """
            Returns the Stop event's set status.
        Returns:
            bool: whether this thread has received a Stop event
        """
        return self._stop_event.is_set()

    def run(self):
        """
        Calls the target function in the form:
            `target(self.is_stopped, args)`
        so that the target can call the is_stopped function from inside itself (as the function does not know which
        thread it is executing in). The function should respect the is_stopped call and stop as soon as it is possible.
        Returns:
            None
        """
        self.target(self.is_stopped, *self.args)

class StoppableLoopingThread(StoppableThread):
    """
    A Stoppable thread that handles the looping and stopping internally.
    """
    def run(self):
        """
        Calls the target function in a while(not self.is_stopped()) loop, such that the target function is invoked
        repeatedly until the Stop event occurs. As such, the target function should not block internally to ensure
        the Stop event is responded to.
        Returns:
            None
        """
        while not self.is_stopped():
            self.target(*self.args)
