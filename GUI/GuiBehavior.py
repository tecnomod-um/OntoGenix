from PyQt5.QtWidgets import QMainWindow, QFileDialog, QDialog, QVBoxLayout, QTreeView
from PyQt5.QtCore import QTimer, QCoreApplication
from PyQt5 import QtWidgets, QtCore, uic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QTextCursor
from PyQt5.QtGui import QColor
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QApplication, QPlainTextEdit
from PyQt5.QtGui import QColor, QTextCharFormat, QFont, QSyntaxHighlighter
from PyQt5.QtCore import Qt, QRegularExpression
from collections import OrderedDict
import asyncio
import sys
import re
import markdown

from GUI.metadata import MetadataManager
from GUI.log import log
from tools.tools import csv2dataset, dataframe2prettyjson, csv_statistical_description, load_string_from_file
from PlanSage.LLM_planner import LlmPlanner
from OntoBuilder.LLM_ontology import LlmOntology
from OntoMapper.LLM_ontomapper import LlmOntoMapper
from MermaidOntoFlow.Llm_mermaid import LlmMermaid
from enum import Enum


class OntologyState(Enum):
    DESCRIPTION = "DATA_DESCRIPTION"
    INIT_CONTEXT = "INITIAL_CONTEXT"
    ONTOLOGY_OBJECT_PROPERTIES = "ONTOLOGY_OBJECT_PROPERTIES"
    ONTOLOGY_DATA_PROPERTIES = "ONTOLOGY_DATA_PROPERTIES"
    ONTOLOGY_ENTITY = "ONTOLOGY_ENTITY"
    MAPPING = "MAPPING"


class GuiBehavior(QMainWindow):

    def __init__(self):
        QMainWindow.__init__(self, parent=None)
        uic.loadUi('./GUI/GUI.ui', self)
        # ------ show ----------
        self.showMaximized()
        self.OUTPUT_tab.setCurrentIndex(0)
        self.LLManswer_textedit.setReadOnly(True)
        self.csv_textedit.setReadOnly(True)
        # ---------- Setup asyncio event loop with Qt ----------
        self.loop = asyncio.get_event_loop()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._run_asyncio_loop)
        self.timer.start(0)

        # -- callbacks --
        self.load_csv_btn.clicked.connect(self.load_csv_data)
        self.query_send_btn.clicked.connect(
            lambda: self._start_manage_prompt(
                self.query_prompt_textedit.toPlainText()
            )
        )
        self.chat_edit_btn.clicked.connect(self.chat_edit)
        self.chat_save_btn.clicked.connect(self.chat_save)
        self.ontology_save_btn.clicked.connect(lambda: self.save(self.ontology_textedit.toPlainText(), extension="owl"))
        self.mapping_save_btn.clicked.connect(lambda: self.save(self.mapping_textedit.toPlainText(), extension="rml"))
        self.mermaid_btn.clicked.connect(self.create_mermaid)
        self.LLMANSWER_scrollbar = self.LLManswer_textedit.verticalScrollBar()
        self.state_cbox.currentIndexChanged.connect(self._handle_state)

        # -- instantiate classes --
        self.metadata_manager = MetadataManager()
        self.plan_builder = LlmPlanner(self.metadata_manager.planner_metadata)
        self.ontology_builder = LlmOntology(self.metadata_manager.onto_metadata)
        self.ontology_mapper = LlmOntoMapper(self.metadata_manager.mapper_metadata)
        self.mermaid_generator = LlmMermaid(self.metadata_manager.mermaid_metadata)
        self.state = OntologyState.DESCRIPTION
        self._handle_state()

        # -- data containers --
        self.json_data = None

        # -- log manager
        self.log = log(self.logger)

    def chat_edit(self):
        current_state = self.LLManswer_textedit.isReadOnly()
        self.LLManswer_textedit.setReadOnly(not current_state)

    def chat_save(self):
        answer_text = self.LLManswer_textedit.toPlainText()

        if self.state == ChatState.DESCRIPTIOM:
            self.plan_builder.data_description = answer_text

        elif self.state == ChatState.INIT_CONTEXT:
            self.ontology_mapper.rationale = answer_text

        elif self.state == ChatState.MAPPING:
            self.ontology_mapper.answer = answer_text

        elif self.state in {ChatState.ONTOLOGY_OBJECT_PROPERTIES,
                            ChatState.ONTOLOGY_DATA_PROPERTIES,
                            ChatState.ONTOLOGY_ENTITY}:
            self.ontology_builder.answer = answer_text
        else:
            raise log.myprint_error(f"Unexpected state: {self.state}")

    def _handle_state(self):
        self.state = OntologyState[self.state_cbox.currentText()]
        guidelines = load_string_from_file("./Help_Guidelines/guidelines.md")
        html = markdown.markdown(guidelines)
        self.help_textEdit.setHtml(html)

    def move_cursor_to_end(self):
        cursor = self.LLManswer_textedit.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.LLManswer_textedit.setTextCursor(cursor)

    def _run_asyncio_loop(self):
        """Run the asyncio event loop for a short duration."""
        self.loop.stop()
        self.loop.run_forever()

    def _start_manage_prompt(self, prompt):
        """Start the asynchronous _manage_prompt method."""
        asyncio.ensure_future(self._manage_prompt(prompt))

    async def _manage_prompt(self, prompt):
        self.CHATs_tab.setCurrentIndex(1)
        self.LLManswer_textedit.setEnabled(False)
        self.move_cursor_to_end()
        self.LLManswer_textedit.clear()

        if self.state in [OntologyState.DESCRIPTION, OntologyState.INIT_CONTEXT]:
            await self.create_initial_context(prompt)

        elif self.state in [OntologyState.ONTOLOGY_OBJECT_PROPERTIES,
                            OntologyState.ONTOLOGY_DATA_PROPERTIES,
                            OntologyState.ONTOLOGY_ENTITY]:
            await self.generate_ontology(prompt)

        elif self.state == OntologyState.MAPPING:
            await self.create_mapping()

        self.LLManswer_textedit.insertPlainText("\n\n")
        self.LLManswer_textedit.setEnabled(True)

    async def create_initial_context(self, prompt: str):
        async for _ in self.plan_builder.interaction(
                input_task=prompt,
                json_data=self.json_data,
                data_description=self.plan_builder.data_description,
                state=self.state):
            self.LLManswer_textedit.setPlainText(self.plan_builder.answer)
            self.LLMANSWER_scrollbar.setValue(self.LLMANSWER_scrollbar.maximum())
            QCoreApplication.processEvents()

    async def generate_ontology(self, prompt: str):
        async for _ in self.ontology_builder.interact(
                data_description=self.plan_builder.data_description,
                rationale=self.plan_builder.rationale,
                entity=prompt,
                state=self.state):
            self.LLManswer_textedit.setPlainText(self.ontology_builder.answer)
            self.LLMANSWER_scrollbar.setValue(self.LLMANSWER_scrollbar.maximum())
            QCoreApplication.processEvents()

    async def create_mapping(self):
        rationale = self.plan_builder.rationale + '\n' + self.ontology_textedit.toPlainText()
        async for _ in self.ontology_mapper.interact(rationale=rationale):
            self.LLManswer_textedit.setPlainText(self.ontology_mapper.answer)
            self.LLMANSWER_scrollbar.setValue(self.LLMANSWER_scrollbar.maximum())
            QCoreApplication.processEvents()

    def create_mermaid(self):
        try:
            self.mermaid_generator.interact(self.ontology_textedit.toPlainText())
            graph = self.mermaid_generator.get_diagram()
            self.mermaid_widget.plot(graph)
            self.OUTPUT_tab.setCurrentIndex(3)
        except Exception as e:
            self.log.myprint_error(f"An error occurred while generating the mermaid diagram: {e}")
            self.OUTPUT_tab.setCurrentIndex(4)

    def save(self, text: str, extension: str):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog

        # Create the filter string based on the mode parameter
        filter_str = f"Text Files (*.{extension})"

        fileName, filetype = QFileDialog.getSaveFileName(self,
                                                         "QFileDialog.getSaveFileName()", "",
                                                         filter_str,
                                                         options=options)
        try:
            # Open the file with write permissions ('w')
            with open(fileName, 'w', encoding='utf-8') as file:
                # Write the text to the file
                file.write(text)
        except OSError:
            self.log.myprint_error("Creation of the file %s failed" % fileName)
        else:
            self.log.myprint_out("Successfully created the file %s " % fileName)

    def load_csv_data(self, btn):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()",
                                                            "", "CSV Files (*.csv)", options=options)
        try:
            # set path
            self.log.myprint_in(f"loading the csv dataset: {fileName}")
            self.metadata_manager.parse_datasetPath(fileName)
            self.metadata_manager.create_config4morph()
            # set path into LLMs
            self.plan_builder.dataset_path = self.metadata_manager.dataset_base_path()
            self.ontology_builder.dataset_path = self.metadata_manager.dataset_base_path()
            self.ontology_mapper.dataset_path = self.metadata_manager.dataset_base_path()
            dataframe = csv_statistical_description(self.metadata_manager.dataset_full_path())
            self.json_data = dataframe2prettyjson(dataframe)

            # show in gui
            self.csv_textedit.setText(self.json_data)
            # logging
            self.log.myprint(f"{fileName} loaded!")
            self.OUTPUT_tab.setCurrentIndex(0)
        except ValueError as e:
            self.log.myprint_error(f"An error occurred while loading csv data: {e}")
            self.OUTPUT_tab.setCurrentIndex(4)
