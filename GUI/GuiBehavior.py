from PyQt5.QtWidgets import QMainWindow, QFileDialog
from PyQt5.QtCore import QTimer, QCoreApplication
from PyQt5 import QtWidgets, QtCore, uic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QTextCursor
from PyQt5.QtWidgets import QMainWindow, QDialog, QVBoxLayout, QTreeView
from PyQt5.QtGui import QColor
from PyQt5.QtCore import pyqtSignal
from collections import OrderedDict
import asyncio

from GUI.metadata import MetadataManager
from GUI.log import log
from tools.tools import csv2dataset
from tools.tools import dataframe2prettyjson
from PlanSage.LLM_planner import LlmPlanner
from OntoBuilder.LLM_ontology import LlmOntology
from OntoMapper.LLM_ontomapper import LlmOntoMapper
from MermaidOntoFlow.Llm_mermaid import LlmMermaid
from enum import Enum


class State(Enum):
    DATA_DESCRIPTION = "DATA_DESCRIPTION"
    INIT_CONTEXT = "INIT_CONTEXT"
    ONTOLOGY_OBJECT_PROPERTIES = "ONTOLOGY_OBJECT_PROPERTIES"
    ONTOLOGY_DATA_PROPERTIES = "ONTOLOGY_DATA_PROPERTIES"
    ONTOLOGY_CLASSES = "ONTOLOGY_CLASSES"
    ONTOLOGY_PROPERTIES = "ONTOLOGY_PROPERTIES"
    MAPPING = "MAPPING"
    MERMAID = "MERMAID"


class GuiBehavior(QMainWindow):

    def __init__(self):
        QMainWindow.__init__(self, parent=None)
        uic.loadUi('./GUI/GUI.ui', self)
        # ------ show ----------
        self.showMaximized()
        self.OUTPUT_tab.setCurrentIndex(0)
        self.entity_lineEdit.setReadOnly(True)
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
        # self.regenerate_btn.clicked.connect(self._start_manage_regenerate)
        self.chat_edit_btn.clicked.connect(self.chat_edit)
        self.chat_save_btn.clicked.connect(self.chat_save)
        self.ontology_save_btn.clicked.connect(lambda: self.save(self.ontology_textedit.toPlainText(), extension="owl"))
        self.mapping_save_btn.clicked.connect(lambda: self.save(self.mapping_textedit.toPlainText(), extension="rml"))
        self.LLMANSWER_scrollbar = self.LLManswer_textedit.verticalScrollBar()
        self.state_cbox.currentIndexChanged.connect(self._handle_state)

        # -- instantiate classes --
        self.metadata_manager = MetadataManager()
        self.plan_builder = LlmPlanner(self.metadata_manager.planner_metadata)
        self.ontology_builder = LlmOntology(self.metadata_manager.onto_metadata)
        self.ontology_mapper = LlmOntoMapper(self.metadata_manager.mapper_metadata)
        self.mermaid_generator = LlmMermaid(self.metadata_manager.mermaid_metadata)
        self.state = State.DATA_DESCRIPTION

        # -- data containers --
        self.csv_data = None
        self.json_data = None

        # -- log manager
        self.log = log(self.logger)

    def chat_edit(self):
        current_state = self.LLManswer_textedit.isReadOnly()
        self.LLManswer_textedit.setReadOnly(not current_state)

    def chat_save(self):
        answer_text = self.LLManswer_textedit.toPlainText()

        if self.state == ChatState.INIT_CONTEXT:
            self.plan_builder.answer = answer_text
        elif self.state == ChatState.MAPPING:
            self.ontology_mapper.answer = answer_text
        elif self.state in {ChatState.ONTOLOGY_OBJECT_PROPERTIES,
                            ChatState.ONTOLOGY_DATA_PROPERTIES,
                            ChatState.ONTOLOGY_CLASSES,
                            ChatState.ONTOLOGY_PROPERTIES}:
            self.ontology_builder.answer = answer_text
        else:
            raise log.myprint_error(f"Unexpected state: {self.state}")

    def set_state(self, new_state_str: str):
        try:
            # Try to convert the string to a State enum member
            new_state = State[new_state_str]
        except KeyError:
            # The string does not correspond to a valid State enum member
            raise ValueError(f"Invalid state: {new_state_str}")
        # Update the state
        self.state = new_state

    def _handle_state(self):
        next_state = State[self.state_cbox.currentText()]

        if next_state in [State.ONTOLOGY_DATA_PROPERTIES, State.ONTOLOGY_CLASSES, State.ONTOLOGY_PROPERTIES]:
            self.entity_lineEdit.setReadOnly(False)
        else:
            self.entity_lineEdit.setReadOnly(True)
            self.entity_lineEdit.clear()

        self.state = next_state

    def moveCursorToEnd(self):
        cursor = self.LLManswer_textedit.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.LLManswer_textedit.setTextCursor(cursor)


    def _run_asyncio_loop(self):
        """Run the asyncio event loop for a short duration."""
        self.loop.stop()
        self.loop.run_forever()

    # def _start_manage_regenerate(self):
    #     asyncio.ensure_future(self.regenerate_answer())
    #
    # async def regenerate_answer(self):
    #     self.LLManswer_textedit.clear()
    #     if self.state == State.INIT_CONTEXT:
    #         async for data_chunk in self.plan_builder.regenerate():
    #             self.LLManswer_textedit.insertPlainText(data_chunk)
    #             self.LLMANSWER_scrollbar.setValue(self.LLMANSWER_scrollbar.maximum())
    #             QCoreApplication.processEvents()
    #
    #     elif self.state == State.BASE_ONTOLOGY:
    #         async for data_chunk in self.ontology_builder.regenerate():
    #             self.LLManswer_textedit.insertPlainText(data_chunk)
    #             self.LLMANSWER_scrollbar.setValue(self.LLMANSWER_scrollbar.maximum())
    #             QCoreApplication.processEvents()
    #
    #     elif self.state == State.ONTOLOGY_ENTITY:
    #         async for data_chunk in self.ontology_builder.regenerate():
    #             self.LLManswer_textedit.insertPlainText(data_chunk)
    #             self.LLMANSWER_scrollbar.setValue(self.LLMANSWER_scrollbar.maximum())
    #             QCoreApplication.processEvents()
    #
    #     elif self.state == State.MAPPING:
    #         async for data_chunk in self.ontology_mapper.regenerate():
    #             self.LLManswer_textedit.insertPlainText(data_chunk)
    #             self.LLMANSWER_scrollbar.setValue(self.LLMANSWER_scrollbar.maximum())
    #             QCoreApplication.processEvents()

    def _start_manage_prompt(self, prompt):
        """Start the asynchronous _manage_prompt method."""
        asyncio.ensure_future(self._manage_prompt(prompt))

    async def _manage_prompt(self, prompt):
        self.LLManswer_textedit.setEnabled(False)
        self.moveCursorToEnd()

        if self.state == State.DATA_DESCRIPTION:
            await self.create_data_description(prompt)
        elif self.state == State.INIT_CONTEXT:
            await self.create_initial_context(prompt)
        elif self.state == State.ONTOLOGY_OBJECT_PROPERTIES:
            await self.create_object_properties_ontology()
        elif self.state == State.ONTOLOGY_DATA_PROPERTIES:
            await self.create_data_properties_ontology()
        elif self.state == State.ONTOLOGY_CLASSES:
            await self.improve_entity(mode="classes")
        elif self.state == State.ONTOLOGY_PROPERTIES:
            await self.improve_entity(mode="properties")
        elif self.state == State.MAPPING:
            await self.create_mapping()
        elif self.state == State.MERMAID:
            await self.create_mermaid()

        self.LLManswer_textedit.insertPlainText('\n')
        self.LLManswer_textedit.insertPlainText('***************************************************************************')
        self.LLManswer_textedit.insertPlainText('\n')
        self.LLManswer_textedit.setEnabled(True)

    async def create_data_description(self, prompt: str):
        async for data_chunk in self.plan_builder.interaction(
                input_task=prompt,
                json_data=self.json_data):

            self.LLManswer_textedit.insertPlainText(data_chunk)
            self.LLMANSWER_scrollbar.setValue(self.LLMANSWER_scrollbar.maximum())
            QCoreApplication.processEvents()

    async def create_initial_context(self, prompt: str):
        async for data_chunk in self.plan_builder.interaction(
                input_task=prompt,
                data_description=self.plan_builder.data_description):

            self.LLManswer_textedit.insertPlainText(data_chunk)
            self.LLMANSWER_scrollbar.setValue(self.LLMANSWER_scrollbar.maximum())
            QCoreApplication.processEvents()

    async def create_object_properties_ontology(self):
        async for data_chunk in self.ontology_builder.interact(
                data_description=self.plan_builder.data_description,
                rationale=self.plan_builder.rationale):
            self.LLManswer_textedit.insertPlainText(data_chunk)
            self.LLMANSWER_scrollbar.setValue(self.LLMANSWER_scrollbar.maximum())
            QCoreApplication.processEvents()

    async def create_data_properties_ontology(self):
        async for data_chunk in self.ontology_builder.interact(
                data_description=self.plan_builder.data_description,
                rationale=self.plan_builder.rationale,
                class_entity=self.entity_lineEdit.text()):
            self.LLManswer_textedit.insertPlainText(data_chunk)
            self.LLMANSWER_scrollbar.setValue(self.LLMANSWER_scrollbar.maximum())
            QCoreApplication.processEvents()

    async def improve_entity(self, mode: str):
        async for data_chunk in self.ontology_builder.interact(
                rationale=self.ontology_builder.answer,
                next_entity=self.entity_lineEdit.text(),
                mode=mode):
            self.LLManswer_textedit.insertPlainText(data_chunk)
            self.LLMANSWER_scrollbar.setValue(self.LLMANSWER_scrollbar.maximum())
            QCoreApplication.processEvents()
        self.OUTPUT_tab.setCurrentIndex(1)
        QCoreApplication.processEvents()

    async def create_mapping(self):
        rationale = self.plan_builder.rationale + '\n' + self.ontology_textedit.toPlainText()
        async for data_chunk in self.ontology_mapper.interact(rationale=rationale):
            self.LLManswer_textedit.insertPlainText(data_chunk)
            self.LLMANSWER_scrollbar.setValue(self.LLMANSWER_scrollbar.maximum())
            QCoreApplication.processEvents()

    def create_mermaid(self):
        try:
            self.mermaid_generator.interact(self.ontology_textedit.toPlainText())
            graph = self.mermaid_generator.get_diagram()
            self.mermaid_widget.plot(graph)
            self.OUTPUT_tab.setCurrentIndex(2)
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
            self.plan_builder.dataset_path = self.metadata_manager.dataset_base_path()
            self.ontology_builder.dataset_path = self.metadata_manager.dataset_base_path()
            self.ontology_mapper.dataset_path = self.metadata_manager.dataset_base_path()
            # get, chunk and format the dataset
            self.csv_data = csv2dataset(
                self.metadata_manager.dataset_full_path(),
                max_tokens=int(self.chunksize_lineEdit.text())
            )
            self.json_data = dataframe2prettyjson(self.csv_data)

            # show in gui
            self.csv_textedit.setText(self.json_data)
            # logging
            self.log.myprint(f"{fileName} loaded!")
            self.OUTPUT_tab.setCurrentIndex(0)
        except ValueError as e:
            self.log.myprint_error(f"An error occurred while loading csv data: {e}")
            self.OUTPUT_tab.setCurrentIndex(4)
