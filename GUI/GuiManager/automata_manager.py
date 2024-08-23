class State:
    def __init__(self, name: str):
        """
        Initialize a State object.

        Parameters:
        name (str): The name of the state.
        """
        self.name = name

class Transition:
    def __init__(self, from_state: State, to_state: State, action: str, requires_confirmation: bool):
        """
        Initialize a Transition object.

        Parameters:
        from_state (State): The state the transition starts from.
        to_state (State): The state the transition goes to.
        action (str): The action associated with the transition.
        requires_confirmation (bool): Whether the transition requires confirmation.
        """
        self.from_state = from_state
        self.to_state = to_state
        self.action = action
        self.requires_confirmation = requires_confirmation

    def is_valid(self, reached_states: list[State]) -> bool:
        """
        Check if a transition is valid based on reached states.

        Parameters:
        reached_states (list[State]): List of states that have been reached.

        Returns:
        bool: True if the transition is valid, False otherwise.
        """
        if self.from_state.name == "PROMPT_CRAFT" and self.to_state.name == "ONTOLOGY_ENTITY":
            # Check if ONTOLOGY has been reached previously
            return "ONTOLOGY" in [state.name for state in reached_states]
        return True

class Automaton:
    def __init__(self):
        self.states = {}
        self.transitions = []
        self._reached_states = set()

        # Set the automaton initial states
        self.current_state = None
        self.action = None

    @property
    def reached_states(self) -> list[State]:
        """
        Get the list of reached states.

        Returns:
        list[State]: List of reached states.
        """
        return list(self._reached_states)

    def add_state(self, name: str) -> State:
        """
        Add a state to the automaton.

        Parameters:
        name (str): The name of the state.

        Returns:
        State: The added state.
        """
        state = State(name)
        self.states[name] = state
        return state

    def add_transition(self, from_state: State, to_state: State, action: str, requires_confirmation: bool):
        """
        Add a transition to the automaton.

        Parameters:
        from_state (State): The state the transition starts from.
        to_state (State): The state the transition goes to.
        action (str): The action associated with the transition.
        requires_confirmation (bool): Whether the transition requires confirmation.
        """
        transition = Transition(from_state, to_state, action, requires_confirmation)
        self.transitions.append(transition)

    def can_transition(self, from_state: State, to_state: State) -> bool:
        """
        Check if a transition is possible from one state to another.

        Parameters:
        from_state (State): The current state.
        to_state (State): The target state.

        Returns:
        bool: True if the transition is possible, False otherwise.
        """
        for transition in self.transitions:
            if (
                transition.from_state.name == from_state.name
                and transition.to_state.name == to_state.name
            ):
                if not transition.is_valid(self.reached_states):
                    return False  # Transition is not valid based on conditions
                return True
        return False

    def perform_transition(self, to_state: State) -> bool:
        """
        Perform a transition to a new state.

        Parameters:
        to_state (State): The target state.

        Returns:
        bool: True if the transition was performed, False otherwise.
        """
        if self.can_transition(self.current_state, to_state):
            self._reached_states.add(to_state)
            self.current_state = to_state
            return True
        else:
            return False

    def possible_next_states(self) -> list[str]:
        """
        Get the possible next states from the current state.

        Returns:
        list[str]: List of possible next state names.
        """
        possible_states = []
        for transition in self.transitions:
            if transition.from_state.name == self.current_state.name:
                possible_states.append(transition.to_state.name)
        return possible_states

class Automata_Manager:

    def __init__(self):
        # Create the automaton
        self.droid = Automaton()

        # Define states
        PROMPT_CRAFT = self.droid.add_state("PROMPT_CRAFT")
        HIGH_LEVEL_STRUCTURE = self.droid.add_state("HIGH_LEVEL_STRUCTURE")
        ONTOLOGY = self.droid.add_state("ONTOLOGY")
        ONTOLOGY_ENTITY = self.droid.add_state("ONTOLOGY_ENTITY")
        MAPPING = self.droid.add_state("MAPPING")
        None_STATE = self.droid.add_state("None")

        # Set initial states
        self.droid.current_state = None_STATE

        # Define transitions
        self.droid.add_transition(None_STATE, PROMPT_CRAFT, "prompt_crafting", False)
        self.droid.add_transition(None_STATE, HIGH_LEVEL_STRUCTURE, "data_description", False)

        self.droid.add_transition(PROMPT_CRAFT, PROMPT_CRAFT, "prompt_crafting", True)
        self.droid.add_transition(PROMPT_CRAFT, HIGH_LEVEL_STRUCTURE, "data_description", True)
        self.droid.add_transition(PROMPT_CRAFT, ONTOLOGY_ENTITY, "ontology_building", True)

        self.droid.add_transition(HIGH_LEVEL_STRUCTURE, ONTOLOGY, "ontology_building", False)
        self.droid.add_transition(HIGH_LEVEL_STRUCTURE, MAPPING, "mapping", False)
        self.droid.add_transition(HIGH_LEVEL_STRUCTURE, PROMPT_CRAFT, "prompt_crafting", False)

        self.droid.add_transition(ONTOLOGY, PROMPT_CRAFT, "prompt_crafting", False)
        self.droid.add_transition(ONTOLOGY, HIGH_LEVEL_STRUCTURE, "data_description", False)
        self.droid.add_transition(ONTOLOGY, ONTOLOGY_ENTITY, "ontology_entity_enrichment", False)
        self.droid.add_transition(ONTOLOGY, MAPPING, "mapping", False)

        self.droid.add_transition(ONTOLOGY_ENTITY, ONTOLOGY_ENTITY, "ontology_entity_enrichment", False)
        self.droid.add_transition(ONTOLOGY_ENTITY, PROMPT_CRAFT, "prompt_crafting", False)
        self.droid.add_transition(ONTOLOGY_ENTITY, HIGH_LEVEL_STRUCTURE, "data_description", False)
        self.droid.add_transition(ONTOLOGY_ENTITY, MAPPING, "mapping", False)

        self.droid.add_transition(MAPPING, PROMPT_CRAFT, "prompt_crafting", False)
        self.droid.add_transition(MAPPING, HIGH_LEVEL_STRUCTURE, "data_description", False)
        self.droid.add_transition(MAPPING, ONTOLOGY_ENTITY, "ontology_entity_enrichment", False)
