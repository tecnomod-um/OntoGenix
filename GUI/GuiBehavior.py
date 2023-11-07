# Qt imports
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QDialog, QVBoxLayout, QTreeView, QApplication, QPlainTextEdit
from PyQt5.QtCore import QTimer, QCoreApplication, Qt, QRegularExpression, pyqtSignal
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QTextCursor, QColor, QTextCharFormat, QFont, QSyntaxHighlighter
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
from GUI.PlanSage.LLM_planner import LlmPlanner
from GUI.OntoBuilder.LLM_ontology import LlmOntology
from GUI.OntoMapper.LLM_ontomapper import LlmOntoMapper
from GUI.MermaidOntoFlow.Llm_mermaid import LlmMermaid
from GUI.KG_Generator.RAG import RAG_OntoMapper


class OntologyState(Enum):
    """Enum class to represent different states of ontology."""

    DESCRIPTION = "DATA_DESCRIPTION"
    ONTOLOGY_OBJECT_PROPERTIES = "ONTOLOGY_OBJECT_PROPERTIES"
    ONTOLOGY_DATA_PROPERTIES = "ONTOLOGY_DATA_PROPERTIES"
    ONTOLOGY_ENTITY = "ONTOLOGY_ENTITY"
    MAPPING = "MAPPING"


class GuiBehavior(QMainWindow):
    """Main GUI behavior and logic."""

    def __init__(self):
        super().__init__(parent=None)
        uic.loadUi('./GUI/GUI.ui', self)

        # Initial GUI Setup
        self.showMaximized()
        self.OUTPUT_tab.setCurrentIndex(0)
        self.LLManswer_textedit.setReadOnly(True)
        self.csv_textedit.setReadOnly(True)
        guidelines = load_string_from_file("./GUI/Help_Guidelines/guidelines.md")
        html = markdown.markdown(guidelines)
        self.help_textEdit.setHtml(html)

        # Setup asyncio event loop with Qt
        self.loop = asyncio.get_event_loop()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._run_asyncio_loop)
        self.timer.start(0)

        # Button callbacks
        self.load_csv_btn.clicked.connect(self.load_csv_data)
        self.query_send_btn.clicked.connect(lambda: self._start_manage_prompt(self.query_prompt_textedit.toPlainText()))
        self.chat_edit_btn.clicked.connect(self.chat_edit)
        self.chat_save_btn.clicked.connect(self.chat_save)
        self.ontology_save_btn.clicked.connect(lambda: self.save(self.ontology_textedit.toPlainText(), extension="owl"))
        self.mapping_save_btn.clicked.connect(lambda: self.save(self.mapping_textedit.toPlainText(), extension="rml"))
        self.mermaid_btn.clicked.connect(self.create_mermaid)
        self.state_cbox.currentTextChanged.connect(self._handle_state)

        self.LLMANSWER_scrollbar = self.LLManswer_textedit.verticalScrollBar()

        # Instantiate supporting classes
        self.metadata_manager = MetadataManager()
        # Instantiate LLM agents
        self.plan_builder = LlmPlanner(self.metadata_manager.planner_metadata)
        self.ontology_builder = LlmOntology(self.metadata_manager.onto_metadata)
        self.ontology_mapper = LlmOntoMapper(self.metadata_manager.mapper_metadata)
        self.mermaid_generator = LlmMermaid(self.metadata_manager.mermaid_metadata)
        # Instantiate RAG systems
        self.RAG_ontomapper = RAG_OntoMapper(self.ontology_mapper, self.plan_builder)

        self.state = OntologyState.DESCRIPTION
        self._handle_state()

        # Data container
        self.json_data = None

        # Log manager setup
        self.log = log(self.logger)

    def chat_edit(self):
        """Toggle the read-only state of LLManswer_textedit."""
        current_state = self.LLManswer_textedit.isReadOnly()
        self.LLManswer_textedit.setReadOnly(not current_state)

    def chat_save(self):
        """Save the chat contents based on the current state."""
        answer_text = self.LLManswer_textedit.toPlainText()

        if self.state == OntologyState.DESCRIPTION:
            self.plan_builder.data_description = answer_text

        # elif self.state == OntologyState.INIT_CONTEXT:
        #     self.plan_builder.rationale = answer_text

        elif self.state == OntologyState.MAPPING:
            self.ontology_mapper.answer = answer_text

        elif self.state in {OntologyState.ONTOLOGY_OBJECT_PROPERTIES,
                            OntologyState.ONTOLOGY_DATA_PROPERTIES,
                            OntologyState.ONTOLOGY_ENTITY}:
            self.ontology_builder.answer = answer_text

        else:
            # Unexpected state error
            raise log.myprint_error(f"Unexpected state: {self.state}")

    def _handle_state(self):
        """Set the current state based on the state combobox and load the help guidelines."""
        self.state = OntologyState[self.state_cbox.currentText()]


    def move_cursor_to_end(self):
        """Move the text cursor to the end of LLManswer_textedit."""
        cursor = self.LLManswer_textedit.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.LLManswer_textedit.setTextCursor(cursor)

    def _run_asyncio_loop(self):
        """Run the asyncio event loop for a short duration."""
        self.loop.stop()
        self.loop.run_forever()

    def _start_manage_prompt(self, prompt: str) -> None:
        """Start the asynchronous management of the user's prompt."""
        asyncio.ensure_future(self._manage_prompt(prompt))

    async def _manage_prompt(self, prompt: str) -> None:
        """Manage the user's prompt based on the current ontology state."""
        # Determine action based on current state
        print('#####################################')
        print(self.state)
        if self.state in [OntologyState.DESCRIPTION]:
            await self.create_initial_context(prompt)
        elif self.state in [OntologyState.ONTOLOGY_OBJECT_PROPERTIES,
                            OntologyState.ONTOLOGY_DATA_PROPERTIES,
                            OntologyState.ONTOLOGY_ENTITY]:
            await self.generate_ontology(prompt)
        elif self.state == OntologyState.MAPPING:
            await self.create_mapping()

    async def _process_interaction(self, interaction_gen, *args, **kwargs):
        """Process the asynchronous interaction, updating the LLManswer_textedit."""
        self.CHATs_tab.setCurrentIndex(1)
        self.LLManswer_textedit.setEnabled(False)
        self.move_cursor_to_end()
        self.LLManswer_textedit.clear()

        # Extract the expected attribute for the answer from kwargs
        llm_agent = kwargs.pop("agent")
        async for _ in interaction_gen(*args, **kwargs):
            self.LLManswer_textedit.setPlainText(llm_agent.answer)
            self.LLMANSWER_scrollbar.setValue(self.LLMANSWER_scrollbar.maximum())
            QCoreApplication.processEvents()

        # Append extra newline and re-enable text edit
        self.LLManswer_textedit.insertPlainText("\n\n")
        self.LLManswer_textedit.setEnabled(True)

    async def create_initial_context(self, prompt: str) -> None:
        """Create the initial context based on user's prompt."""
        await self._process_interaction(
            self.plan_builder.interaction,
            input_task=prompt,
            json_data=self.json_data,
            state=self.state,
            agent=self.plan_builder
        )

    async def generate_ontology(self, prompt: str) -> None:
        """Generate the ontology based on user's prompt."""
        await self._process_interaction(
            self.ontology_builder.interact,
            data_description=self.plan_builder.data_description,
            entity=prompt,
            state=self.state,
            agent=self.ontology_builder
        )

    async def create_mapping(self) -> None:
        """Create mapping using the rationale and ontology text."""
        for cont in range(self.RAG_ontomapper.max_iter):
            if self.RAG_ontomapper.kgen.error_feedback != "DONE":
                await self._process_interaction(
                    self.ontology_mapper.interact,
                    rationale=self.plan_builder.data_description,
                    error=self.RAG_ontomapper.kgen.error_feedback,
                    agent=self.ontology_mapper
                )

                self.RAG_ontomapper.generateKG()
            else:
                break

    def create_mermaid(self) -> None:
        """Generate a mermaid diagram from the ontology text."""
        try:
            self.mermaid_generator.interact(self.ontology_textedit.toPlainText())
            graph = self.mermaid_generator.get_diagram()
            self.mermaid_widget.plot(graph)
            self.OUTPUT_tab.setCurrentIndex(3)
        except Exception as e:
            self.log.myprint_error(f"An error occurred while generating the mermaid diagram: {e}")
            self.OUTPUT_tab.setCurrentIndex(4)

    def open_file_dialog(self, title: str, file_filter: str) -> str:
        """Open a file dialog and return the selected file's path."""
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog

        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self, title, "", file_filter, options=options)
        return fileName

    def save_file_dialog(self, title: str, file_filter: str) -> str:
        """Open a save file dialog and return the selected file's path."""
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(self, title, "", file_filter, options=options)
        return fileName

    def save(self, text: str, extension: str) -> None:
        """Open a file dialog to save the given text with the specified extension."""
        filter_str = f"Text Files (*.{extension})"
        fileName = self.save_file_dialog("Save File", filter_str)
        if not fileName:  # User cancelled the file dialog
            return
        try:
            with open(fileName, 'w', encoding='utf-8') as file:
                file.write(text)
        except OSError:
            self.log.myprint_error(f"Creation of the file {fileName} failed")
        else:
            self.log.myprint_out(f"Successfully created the file {fileName}")

    def load_csv_data(self) -> None:
        """Open a file dialog to load a CSV file and display its data."""
        fileName = self.open_file_dialog("Load CSV File", "CSV Files (*.csv)")
        if not fileName:  # User cancelled the file dialog
            return
        else:
            try:
                # Log the loading process
                self.log.myprint_in(f"loading the csv dataset: {fileName}")

                # Set paths and configurations for the metadata manager
                self.metadata_manager.parse_datasetPath(fileName)
                self.metadata_manager.create_config4morph()

                # Update the dataset paths for various components
                dataset_base_path = self.metadata_manager.dataset_base_path()
                self.plan_builder.dataset_path = dataset_base_path
                self.ontology_builder.dataset_path = dataset_base_path
                self.ontology_mapper.dataset_path = self.metadata_manager.dataset_full_path()
                print("que paz tenemos en mapper: ", self.ontology_mapper.dataset_path)
                self.RAG_ontomapper.build_kgen(
                    self.metadata_manager.base_path,
                    self.metadata_manager.dataset_folder,
                    self.metadata_manager.dataset_file
                )
                # Convert the CSV data to JSON and display in GUI
                dataframe = csv_data_preprocessing(self.metadata_manager.dataset_full_path())
                self.json_data = dataframe2prettyjson(dataframe)
                self.csv_textedit.setText(self.json_data)

                # Update the output tab and log the success
                self.log.myprint(f"{fileName} loaded!")
                self.OUTPUT_tab.setCurrentIndex(0)
            except ValueError as e:
                self.log.myprint_error(f"An error occurred while loading csv data: {e}")
                self.OUTPUT_tab.setCurrentIndex(4)
