
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
from GUI.GuiManager.LLM_Genie import Genie
from GUI.PromptCrafter.LLM_promptCrafter import LlmPromptCrafter
from GUI.PlanSage.LLM_planner import LlmPlanner
from GUI.OntoBuilder.LLM_ontology import LlmOntology
from GUI.OntoMapper.LLM_ontomapper import LlmOntoMapper
from GUI.MermaidOntoFlow.Llm_mermaid import LlmMermaid
from GUI.KG_Generator.RAG import RAG_OntoMapper


class GuiBehavior(QMainWindow):
    """Main GUI behavior and logic."""

    def __init__(self):
        super().__init__(parent=None)
        uic.loadUi('./GUI/GUI.ui', self)

        # Initial GUI Setup
        self.showMaximized()
        self.OUTPUT_tab.setCurrentIndex(0)
        self.LLManswer_textedit.setReadOnly(True)
        self.LLManswer_textedit.setEnabled(False)
        self.csv_textedit.setReadOnly(True)

        # Setup asyncio event loop with Qt
        self.loop = asyncio.get_event_loop()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._run_asyncio_loop)
        self.timer.start(0)

        # Query button callback
        self.query_send_btn.clicked.connect(lambda: self._start_manage_action(self.action_textEdit.toPlainText()))

        # CSV inspector tab callbacks
        self.load_csv_btn.clicked.connect(self.load_csv_data)
        # Description tab callbacks
        self.description_save_btn.clicked.connect(lambda: self.save(self.description_textEdit.toPlainText(), extension="txt"))
        self.description_textEdit.textChanged.connect(lambda: self.on_text_changed(self.plan_builder, self.description_textEdit))
        # Ontology tab callbacks
        self.ontology_save_btn.clicked.connect(lambda: self.save(self.ontology_textedit.toPlainText(), extension="ttl"))
        self.mermaid_btn.clicked.connect(self.create_mermaid)
        self.ontology_textedit.textChanged.connect(
            lambda: self.on_text_changed(self.ontology_builder, self.ontology_textedit)
        )
        # Mapping tab callbacks
        self.mapping_save_btn.clicked.connect(lambda: self.save(self.mapping_textedit.toPlainText(), extension="rml"))
        self.mapping_textedit.textChanged.connect(
            lambda: self.on_text_changed(self.ontology_mapper, self.mapping_textedit)
        )

        # Instantiate supporting classes
        self.metadata_manager = MetadataManager()
        self.metadata_manager.genie_metadata['available_functions']["prompt_crafting"] = self.generate_crafted_prompt
        self.metadata_manager.genie_metadata['available_functions']["data_description"] = self.create_initial_context
        self.metadata_manager.genie_metadata['available_functions']["ontology_building"] = self.generate_ontology
        self.metadata_manager.genie_metadata['available_functions']["ontology_entity_enrichment"] = self.generate_ontology
        self.metadata_manager.genie_metadata['available_functions']["mapping"] = self.create_mapping

        # Instantiate LLM agents
        self.genie = Genie(self.metadata_manager.genie_metadata)
        self.prompt_crafter = LlmPromptCrafter(self.metadata_manager.crafter_metadata)
        self.plan_builder = LlmPlanner(self.metadata_manager.planner_metadata)
        self.ontology_builder = LlmOntology(self.metadata_manager.onto_metadata)
        self.ontology_mapper = LlmOntoMapper(self.metadata_manager.mapper_metadata)
        self.mermaid_generator = LlmMermaid(self.metadata_manager.mermaid_metadata)

        # Instantiate RAG systems
        self.RAG_OntoMapper = RAG_OntoMapper(self.ontology_mapper, self.plan_builder)

        # Data containers
        self.json_data = None

        # Log manager setup
        self.log = log(self.LLManswer_textedit)

    @staticmethod
    def on_text_changed(agent, text_edit):
        """ Update the agents internal "answer" variable with the current text """
        agent.answer = text_edit.toPlainText()

    def _run_asyncio_loop(self):
        """Run the asyncio event loop for a short duration."""
        self.loop.stop()
        self.loop.run_forever()

    def _start_manage_action(self, prompt: str) -> None:
        """Start the asynchronous management of the user's prompt."""
        asyncio.ensure_future(self._manage_action(prompt))

    async def _manage_action(self, prompt: str) -> None:
        """Manage the user's prompt based on the current ontology state."""
        self.log.append_log(message="\n\n------------- GUI MANAGER ----------------", level="manager", end="\n\n")

        async for chunk in self.genie.interaction(prompt=prompt):
            self.log.append_log(chunk, level="manager", end="")
            QCoreApplication.processEvents()

        self.log.append_log(message="", level="manager", end="\n")

    async def generate_crafted_prompt(self, prompt: str) -> None:
        """Helps the user to craft the best prompt."""
        self.log.append_log(message="\n\n------------- GUI MANAGER ----------------", level="manager", end="\n\n")
        content = self.query_prompt_textedit.toPlainText()

        async for chunk in self.prompt_crafter.interaction(prompt=content, json_data=self.json_data):
            self.log.append_log(chunk, level="answer", end="")
            QCoreApplication.processEvents()

        self.log.append_log(message="", level="answer", end="\n")
        self.query_prompt_textedit.setText(self.prompt_crafter.crafted_prompt)

    async def create_initial_context(self, prompt: str) -> None:
        """Create the initial context based on user's prompt."""
        self.description_textEdit.clear()
        self.description_textEdit.setEnabled(False)
        self.OUTPUT_tab.setCurrentIndex(1)
        async for chunk in self.plan_builder.interaction(input_task=prompt, json_data=self.json_data):
            self.description_textEdit.insertPlainText(chunk)
            # Scroll to the bottom to ensure the latest message is visible
            self.description_textEdit.verticalScrollBar().setValue(
                self.description_textEdit.verticalScrollBar().maximum()
            )
            QCoreApplication.processEvents()

        self.description_textEdit.setEnabled(True)

    async def generate_ontology(self, prompt: str) -> None:
        """Generate the ontology based on user's prompt."""
        self.ontology_textedit.clear()
        self.ontology_textedit.setEnabled(False)
        self.OUTPUT_tab.setCurrentIndex(2)
        async for chunk in self.ontology_builder.interact(
                json_data=self.json_data,
                data_description=self.plan_builder.data_description):
            self.ontology_textedit.insertPlainText(chunk)
            # Scroll to the bottom to ensure the latest message is visible
            self.ontology_textedit.verticalScrollBar().setValue(
                self.ontology_textedit.verticalScrollBar().maximum()
            )
            QCoreApplication.processEvents()
        self.ontology_textedit.setEnabled(True)

    async def create_mapping(self, prompt: str) -> None:
        """Create mapping using the rationale and ontology text."""
        self.OUTPUT_tab.setCurrentIndex(4)
        self.mapping_textedit.setEnabled(False)
        for cont in range(self.RAG_OntoMapper.max_iter):
            if self.RAG_OntoMapper.kgen.error_feedback != "DONE":
                self.mapping_textedit.clear()
                async for chunk in self.ontology_mapper.interact(
                        rationale=self.plan_builder.data_description,
                        error=self.RAG_OntoMapper.kgen.error_feedback):
                    self.mapping_textedit.insertPlainText(chunk)
                    # Scroll to the bottom to ensure the latest message is visible
                    self.mapping_textedit.verticalScrollBar().setValue(
                        self.mapping_textedit.verticalScrollBar().maximum()
                    )
                    QCoreApplication.processEvents()
                self.log.append_log(message="I will generate the knowledge graph.",level="warning")
                self.RAG_OntoMapper.generateKG()
                self.log.append_log(
                    message="Knowledge Graph Generation Status: " + self.RAG_OntoMapper.kgen.error_feedback,
                    level="warning"
                )
            else:
                break
        self.mapping_textedit.setEnabled(True)

    def create_mermaid(self) -> None:
        """Generate a mermaid diagram from the ontology text."""
        try:
            self.OUTPUT_tab.setCurrentIndex(3)
            self.mermaid_generator.interact(self.ontology_textedit.toPlainText())
            graph = self.mermaid_generator.get_diagram()
            self.mermaid_widget.plot(graph)
        except Exception as e:
            self.log.append_log(f"An error occurred while generating the mermaid diagram: {e}", level="error")
            self.OUTPUT_tab.setCurrentIndex(4)

    def move_cursor_to_end(self, textEdit):
        """Move the text cursor to the end of LLManswer_textedit."""
        cursor = textEdit.textCursor()
        cursor.movePosition(QTextCursor.End)
        textEdit.setTextCursor(cursor)

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
        return fileName + '.' + file_filter

    def save(self, text: str, extension: str) -> None:
        """Open a file dialog to save the given text with the specified extension."""
        filter_str = f"Text Files (*.{extension})"
        fileName = self.save_file_dialog(title="Save File", file_filter=filter_str)
        if not fileName:  # User cancelled the file dialog
            return
        try:
            with open(fileName, 'w', encoding='utf-8') as file:
                file.write(text)
        except OSError:
            self.log.append_log(f"Creation of the file {fileName} failed", level="error")
        else:
            self.log.append_log(f"Successfully created the file {fileName}")

    def load_csv_data(self) -> None:
        """Open a file dialog to load a CSV file and display its data."""
        fileName = self.open_file_dialog("Load CSV File", "CSV Files (*.csv)")
        if not fileName:  # User cancelled the file dialog
            return
        else:
            try:
                # Log the loading process
                self.log.append_log(f"loading the csv dataset: {fileName}")

                # Set paths and configurations for the metadata manager
                self.metadata_manager.parse_datasetPath(fileName)
                self.metadata_manager.create_config4morph()

                # Update the dataset paths for various components
                dataset_base_path = self.metadata_manager.dataset_base_path()
                self.plan_builder.dataset_path = dataset_base_path
                self.ontology_builder.dataset_path = dataset_base_path
                self.ontology_mapper.dataset_path = self.metadata_manager.dataset_full_path()
                print("que paz tenemos en mapper: ", self.ontology_mapper.dataset_path)
                self.RAG_OntoMapper.build_kgen(
                    self.metadata_manager.base_path,
                    self.metadata_manager.dataset_folder,
                    self.metadata_manager.dataset_file
                )
                # Convert the CSV data to JSON and display in GUI
                dataframe = csv_data_preprocessing(self.metadata_manager.dataset_full_path())
                self.json_data = dataframe2prettyjson(dataframe)
                self.csv_textedit.setText(self.json_data)

                # Update the output tab and log the success
                self.log.append_log(f"{fileName} loaded!")
                self.OUTPUT_tab.setCurrentIndex(0)
            except ValueError as e:
                self.log.append_log(f"An error occurred while loading csv data: {e}", level="error")
                self.OUTPUT_tab.setCurrentIndex(4)
