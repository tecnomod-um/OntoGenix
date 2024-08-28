"""
    File that contains the different types of Exception raised during the Automaton processing.
"""

class InvalidTransitionException(Exception):
    """
        Raised when a transition in the automata is invalid.

        transition: Text with the invalid transition
    """
    def __init__(self, transition: str = ""):
        super().__init__()
        self.message = "Invalid automata transition: \"" + transition + "\""

class MissedPreviousStepException(Exception):
    """
        Raised when a try to execute a step without executing the previous one

        transition: Text with the invalid transition
    """
    def __init__(self, step: str = "", tab: int = 0):
        super().__init__()
        self.message = "Missed Previous Step: \"" + step + "\""
        self.tab = tab