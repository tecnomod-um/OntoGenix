from PyQt5.QtWidgets import QMainWindow, QFileDialog, QDialog, QVBoxLayout, QTreeView, QApplication, QPlainTextEdit
from PyQt5.QtCore import QTimer, QCoreApplication, Qt, QRegularExpression, pyqtSignal
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QTextCursor, QColor, QTextCharFormat, QFont, \
    QSyntaxHighlighter
from PyQt5 import QtWidgets, QtCore, uic

# Standard and third-party libraries
from collections import OrderedDict
import asyncio
import sys
import re
import markdown
from enum import Enum

# Internal modules imports
from GUI.metadata import MetadataManager
from GUI.log import log
from GUI.tools.tools import csv2dataset, dataframe2prettyjson, csv_data_preprocessing, load_string_from_file
from GUI.GuiManager.LLM_Genie import Genie
from GUI.PromptCrafter.LLM_promptCrafter import LlmPromptCrafter
from GUI.PlanSage.LLM_planner import LlmPlanner
from GUI.OntoBuilder.LLM_ontology import LlmOntology
from GUI.OntoMapper.LLM_ontomapper import LlmOntoMapper
from GUI.MermaidOntoFlow.Llm_mermaid import LlmMermaid
from GUI.KG_Generator.RAG import RAG_OntoMapper


class GuiBehavior(QMainWindow):
    """
    Main GUI behavior and logic class for the application.

    This class manages the overall behavior of the application's GUI. It handles UI events,
    initializes and manages connections with other components like log manager and various
    LLM agents, and sets up the asyncio event loop for asynchronous operations.
    """

    def __init__(self):
        super().__init__(parent=None)
        uic.loadUi('./GUI/GUI.ui', self)  # Load the UI design from the specified file

        # Initial GUI Setup
        self.showMaximized()  # Start with maximized window
        self.OUTPUT_tab.setCurrentIndex(0)  # Set the default tab
        self.LLManswer_textedit.setReadOnly(True)  # Set the text edit as read-only
        self.LLManswer_textedit.setEnabled(False)  # Disable the text edit widget
        self.csv_textedit.setReadOnly(True)  # Set the CSV text edit as read-only

        # Setup asyncio event loop with Qt
        self.loop = asyncio.get_event_loop()  # Get the asyncio event loop
        self.timer = QTimer(self)  # Create a QTimer
        self.timer.timeout.connect(self._run_asyncio_loop)  # Connect timer to the asyncio loop runner
        self.timer.start(0)  # Start the timer

        # Connect UI elements to their respective functions
        self.query_send_btn.clicked.connect(lambda: self._start_manage_action(self.action_textEdit.toPlainText()))
        self.load_csv_btn.clicked.connect(self.load_csv_data)
        self.description_save_btn.clicked.connect(
            lambda: self.save(self.description_textEdit.toPlainText(), extension="txt"))
        self.description_textEdit.textChanged.connect(
            lambda: self.on_text_changed(self.plan_builder, self.description_textEdit))
        self.ontology_save_btn.clicked.connect(lambda: self.save(self.ontology_textedit.toPlainText(), extension="ttl"))
        self.mermaid_btn.clicked.connect(self.create_mermaid)
        self.ontology_textedit.textChanged.connect(
            lambda: self.on_text_changed(self.ontology_builder, self.ontology_textedit))
        self.mapping_save_btn.clicked.connect(lambda: self.save(self.mapping_textedit.toPlainText(), extension="rml"))
        self.mapping_textedit.textChanged.connect(
            lambda: self.on_text_changed(self.ontology_mapper, self.mapping_textedit))

        # Instantiate supporting classes and configure their interactions
        self.metadata_manager = MetadataManager()
        self.metadata_manager.genie_metadata['available_functions'] = {
            "prompt_crafting": self.generate_crafted_prompt,
            "data_description": self.create_initial_context,
            "ontology_building": self.generate_ontology,
            "ontology_entity_enrichment": self.generate_ontology,
            "mapping": self.create_mapping
        }

        # Instantiate LLM agents
        self.genie = Genie(self.metadata_manager.genie_metadata)
        self.prompt_crafter = LlmPromptCrafter(self.metadata_manager.crafter_metadata)
        self.plan_builder = LlmPlanner(self.metadata_manager.planner_metadata)
        self.ontology_builder = LlmOntology(self.metadata_manager.onto_metadata)
        self.ontology_mapper = LlmOntoMapper(self.metadata_manager.mapper_metadata)
        self.mermaid_generator = LlmMermaid(self.metadata_manager.mermaid_metadata)

        # Instantiate RAG systems
        self.RAG_OntoMapper = RAG_OntoMapper(self.ontology_mapper, self.plan_builder)

        # Initialize data containers
        self.json_data = None

        # Log manager setup
        self.log = log(self.LLManswer_textedit)
        self._start_manage_action("Introduce yourself and explain your role to the future users.")

    @staticmethod
    def on_text_changed(agent, text_edit: QtWidgets.QPlainTextEdit):
        """
        Static method to update an agent's internal "answer" variable with the current text.

        This method is intended to be connected to the textChanged signal of a QTextEdit,
        allowing the agent's state to be updated in real-time as the text changes.

        Args:
            agent: The agent whose 'answer' attribute should be updated.
            text_edit (QPlainTextEdit): The text edit widget containing the updated text.
        """
        agent.answer = text_edit.toPlainText()

    def _run_asyncio_loop(self):
        """
        Run the asyncio event loop for a short duration.

        This method is connected to a QTimer and is repeatedly called to keep the
        asyncio event loop running alongside the Qt event loop.
        """
        self.loop.stop()
        self.loop.run_forever()

    def _start_manage_action(self, prompt: str) -> None:
        """
        Start the asynchronous management of the user's prompt.

        This method ensures that the handling of the user's prompt is done asynchronously,
        allowing the GUI to remain responsive.

        Args:
            prompt (str): The user's input prompt to be processed.
        """
        asyncio.ensure_future(self._manage_action(prompt))

    async def _manage_action(self, prompt: str) -> None:
        """
        Asynchronously manage the user's prompt based on the current ontology state.

        This coroutine interacts with the Genie agent to process the user's prompt and
        logs the responses in the GUI's log area.

        Args:
            prompt (str): The user's input prompt to be processed.
        """
        # Disable the text edit while processing the prompt
        self.LLManswer_textedit.setEnabled(False)

        # Log the start of a new GUI manager process
        self.log.append_log(message="\n\n------------- GUI MANAGER ----------------", level="manager", end="\n\n")

        # Process the prompt in chunks, allowing for asynchronous operation
        async for chunk in self.genie.interaction(prompt=prompt):
            self.log.append_log(chunk, level="manager", end="")
            QCoreApplication.processEvents()  # Process any pending GUI events

        # Log the end of the process and re-enable the text edit
        self.log.append_log(message="", level="manager", end="\n")
        self.LLManswer_textedit.setEnabled(True)

    async def generate_crafted_prompt(self, prompt: str) -> None:
        """
        Asynchronously helps the user to craft a better prompt.

        This coroutine interacts with the prompt_crafter agent to refine the user's prompt.
        The process involves sending the current content of the query_prompt_textedit to the agent
        and updating the GUI with the agent's responses.

        Args:
            prompt (str): The initial user prompt to be refined.
        """
        # Log the start of the prompt crafting process
        self.log.append_log(message="\n\n------------- GUI MANAGER ----------------", level="manager", end="\n\n")

        content = 'Query: ' + prompt + ': \n ' + self.query_prompt_textedit.toPlainText()

        # Process the content to craft a better prompt
        async for chunk in self.prompt_crafter.interaction(prompt=content, json_data=self.json_data):
            self.log.append_log(chunk, level="answer", end="")
            QCoreApplication.processEvents()  # Process any pending GUI events

        # Update the GUI with the crafted prompt and log the end of the process
        self.log.append_log(message="", level="answer", end="\n")
        self.query_prompt_textedit.setText(self.prompt_crafter.crafted_prompt)

    async def create_initial_context(self, prompt: str) -> None:
        """
        Asynchronously create the initial context based on the user's prompt.

        This coroutine interacts with the plan_builder agent to generate an initial context.
        It combines the user's prompt with additional content and updates the GUI with the response.

        Args:
            prompt (str): The user's initial prompt to create context from.
        """
        # Clear the description text edit and disable it during processing
        self.description_textEdit.clear()
        self.description_textEdit.setEnabled(False)
        self.OUTPUT_tab.setCurrentIndex(1)  # Switch to the appropriate tab in the GUI

        content = prompt + ' ' + self.query_prompt_textedit.toPlainText()

        # Process the input to create initial context
        async for chunk in self.plan_builder.interaction(input_task=content, json_data=self.json_data):
            self.description_textEdit.insertPlainText(chunk)
            # Scroll to the bottom to ensure the latest message is visible
            self.description_textEdit.verticalScrollBar().setValue(
                self.description_textEdit.verticalScrollBar().maximum()
            )
            QCoreApplication.processEvents()  # Process any pending GUI events

        # Re-enable the description text edit after processing
        self.description_textEdit.setEnabled(True)

    async def generate_ontology(self, prompt: str) -> None:
        """
        Asynchronously generate the ontology based on the user's prompt.

        This coroutine interacts with the ontology_builder agent to generate an ontology
        using the provided data description from the plan_builder. The process involves
        updating the ontology_textedit widget with the generated ontology.

        Args:
            prompt (str): The user's prompt to guide the ontology generation.
        """
        # Clear the ontology text edit and disable it during processing
        self.ontology_textedit.clear()
        self.ontology_textedit.setEnabled(False)
        self.OUTPUT_tab.setCurrentIndex(2)  # Switch to the appropriate tab in the GUI

        # Generate the ontology using the ontology_builder agent
        async for chunk in self.ontology_builder.interact(
                json_data=self.json_data,
                data_description=self.plan_builder.data_description):
            self.ontology_textedit.insertPlainText(chunk)
            # Scroll to the bottom to ensure the latest message is visible
            self.ontology_textedit.verticalScrollBar().setValue(
                self.ontology_textedit.verticalScrollBar().maximum()
            )
            QCoreApplication.processEvents()  # Process any pending GUI events

        # Re-enable the ontology text edit after processing
        self.ontology_textedit.setEnabled(True)


    async def create_mapping(self, prompt: str) -> None:
        """
        Asynchronously create mapping using the rationale and ontology text.

        This coroutine uses the ontology_mapper to create mappings for knowledge graph generation.
        It iterates through a series of steps, updating the mapping_textedit widget with the
        generated mappings and monitoring the progress of the RAG_OntoMapper's knowledge graph
        generation process.

        Args:
            prompt (str): The user's prompt to guide the mapping creation process.
        """
        self.OUTPUT_tab.setCurrentIndex(4)  # Switch to the mapping tab in the GUI
        self.mapping_textedit.setEnabled(False)  # Disable the text edit during processing

        for cont in range(self.RAG_OntoMapper.max_iter):
            # Check if the knowledge graph generation is not done
            if self.RAG_OntoMapper.kgen.error_feedback != "DONE":
                self.mapping_textedit.clear()
                # Generate mapping using ontology_mapper
                async for chunk in self.ontology_mapper.interact(
                        rationale=self.plan_builder.data_description,
                        error=self.RAG_OntoMapper.kgen.error_feedback):
                    self.mapping_textedit.insertPlainText(chunk)
                    # Scroll to the bottom to ensure the latest message is visible
                    self.mapping_textedit.verticalScrollBar().setValue(
                        self.mapping_textedit.verticalScrollBar().maximum()
                    )
                    QCoreApplication.processEvents()  # Process any pending GUI events

                # Log the initiation of knowledge graph generation
                self.log.append_log(message="I will generate the knowledge graph.", level="warning")
                self.RAG_OntoMapper.generateKG()  # Start knowledge graph generation

                # Log the status of knowledge graph generation
                self.log.append_log(
                    message="Knowledge Graph Generation Status: " + self.RAG_OntoMapper.kgen.error_feedback,
                    level="warning"
                )
            else:
                break  # Exit the loop if knowledge graph generation is complete

        self.mapping_textedit.setEnabled(True)  # Re-enable the text edit after processing

    def create_mermaid(self) -> None:
        """
        Generate a mermaid diagram from the ontology text.

        This method interacts with the mermaid_generator to create a visual diagram (mermaid diagram)
        based on the text present in the ontology_textedit widget. It then displays this diagram
        in the mermaid_widget. If an error occurs, it logs the error message.
        """
        try:
            self.OUTPUT_tab.setCurrentIndex(3)  # Switch to the mermaid diagram tab
            self.mermaid_generator.interact(self.ontology_textedit.toPlainText())  # Generate diagram
            graph = self.mermaid_generator.get_diagram()  # Retrieve the generated diagram
            self.mermaid_widget.plot(graph)  # Plot the diagram in the mermaid_widget
        except Exception as e:
            # Log any exceptions that occur during diagram generation
            self.log.append_log(f"An error occurred while generating the mermaid diagram: {e}", level="error")
            self.OUTPUT_tab.setCurrentIndex(4)  # Switch to the error tab

    @staticmethod
    def move_cursor_to_end(self, textEdit: QPlainTextEdit):
        """
        Move the text cursor to the end of the given text edit widget.

        Args:
            textEdit (QPlainTextEdit): The text edit widget whose cursor should be moved.
        """
        cursor = textEdit.textCursor()  # Get the current text cursor
        cursor.movePosition(QTextCursor.End)  # Move the cursor to the end
        textEdit.setTextCursor(cursor)  # Set the cursor in the text edit

    def open_file_dialog(self, title: str, file_filter: str) -> str:
        """
        Open a file dialog and return the selected file's path.

        Args:
            title (str): The title of the file dialog window.
            file_filter (str): The filter for file types.

        Returns:
            str: The path of the selected file.
        """
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self, title, "", file_filter, options=options)
        return fileName

    def save_file_dialog(self, title: str, file_filter: str) -> str:
        """
        Open a save file dialog and return the selected file's path.

        Args:
            title (str): The title of the save file dialog window.
            file_filter (str): The filter for file types.

        Returns:
            str: The path of the file to be saved.
        """
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(self, title, "", file_filter, options=options)
        return fileName + '.' + file_filter

    def save(self, text: str, extension: str) -> None:
        """
        Open a file dialog to save the given text with the specified extension.

        This method displays a file save dialog with a filter for the specified extension.
        If the user selects a file, the method writes the provided text to this file.
        It logs the outcome of the file creation process, whether successful or not.

        Args:
            text (str): The text content to be saved.
            extension (str): The file extension for the save file dialog filter.
        """
        filter_str = f"Text Files (*.{extension})"  # Define the file type filter string
        fileName = self.save_file_dialog(title="Save File", file_filter=filter_str)  # Open the save file dialog

        if not fileName:  # Check if the user cancelled the file dialog
            return  # Exit the function if there's no file name (dialog cancelled)

        try:
            with open(fileName, 'w', encoding='utf-8') as file:  # Open the file for writing
                file.write(text)  # Write the text to the file
        except OSError:
            # Log an error message if file creation fails
            self.log.append_log(f"Creation of the file {fileName} failed", level="error")
        else:
            # Log a success message if the file is created successfully
            self.log.append_log(f"Successfully created the file {fileName}")


    def load_csv_data(self) -> None:
        """
        Open a file dialog to load a CSV file and display its data.

        This method provides a file dialog for the user to select a CSV file. Once a file is selected,
        it updates various components with the new dataset's path, processes the CSV file, and displays
        the data in the GUI. It logs the progress and any errors that might occur during the loading process.
        """
        fileName = self.open_file_dialog("Load CSV File", "CSV Files (*.csv)")  # Open a file dialog to select a CSV file

        if not fileName:  # Check if the user cancelled the file dialog
            return  # Exit the function if no file was selected

        try:
            self.log.append_log(f"loading the csv dataset: {fileName}")  # Log the initiation of the CSV loading process

            # Set paths and configurations for the metadata manager
            self.metadata_manager.parse_datasetPath(fileName)
            self.metadata_manager.create_config4morph()

            # Update the dataset paths for various components
            dataset_base_path = self.metadata_manager.dataset_base_path()
            self.plan_builder.dataset_path = dataset_base_path
            self.ontology_builder.dataset_path = dataset_base_path
            self.ontology_mapper.dataset_path = self.metadata_manager.dataset_full_path()
            self.RAG_OntoMapper.build_kgen(
                self.metadata_manager.base_path,
                self.metadata_manager.dataset_folder,
                self.metadata_manager.dataset_file
            )

            # Convert the CSV data to JSON and display it in the GUI
            dataframe = csv_data_preprocessing(self.metadata_manager.dataset_full_path())
            self.json_data = dataframe2prettyjson(dataframe)
            self.csv_textedit.setText(self.json_data)

            # Update the output tab and log the successful loading of the file
            self.log.append_log(f"{fileName} loaded!")
            self.OUTPUT_tab.setCurrentIndex(0)

        except ValueError as e:
            # Log any errors that occur during the loading process
            self.log.append_log(f"An error occurred while loading csv data: {e}", level="error")
            self.OUTPUT_tab.setCurrentIndex(4)  # Switch to the error tab
