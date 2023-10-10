from PyQt5.QtWidgets import QMainWindow, QFileDialog
from PyQt5.QtCore import QTimer, QCoreApplication
from PyQt5 import QtWidgets, QtCore, uic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem
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

class GuiBehavior(QMainWindow):

    planner_interaction_signal = pyqtSignal()
    ontobuilder_interaction_signal = pyqtSignal()
    ontomapper_interaction_signal = pyqtSignal()

    def __init__(self):
        QMainWindow.__init__(self, parent=None)
        uic.loadUi('./GUI/GUI.ui', self)
        # ------ show ----------
        self.showMaximized()
        self.OUTPUT_tab.setCurrentIndex(0)
        # ---------- Setup asyncio event loop with Qt ----------
        self.loop = asyncio.get_event_loop()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._run_asyncio_loop)
        self.timer.start(0)

        # -- buttons callbacks --
        self.load_csv_btn.clicked.connect(self._load_csv_data)
        self.query_send_btn.clicked.connect(
            lambda: self._start_manage_prompt(self.query_prompt_textedit.toPlainText())
        )
        self.LLMANSWER_scrollbar = self.LLManswer_textedit.verticalScrollBar()

        # -- instantiate classes --
        self.metadata_manager = MetadataManager()
        self.plan_builder = LlmPlanner(self.metadata_manager.planner_metadata)
        self.ontology_builder = LlmOntology(self.metadata_manager.onto_metadata)
        self.ontology_mapper = LlmOntoMapper(self.metadata_manager.mapper_metadata)
        self.mermaid_generator = LlmMermaid(self.metadata_manager.mermaid_metadata)

        # -- data containers --
        self.csv_data = None
        self.json_data = None

        # -- log manager
        self.log = log(self.logger)

        # -- pyqtsignals
        self.planner_interaction_signal.connect(self._trigger_create_ontology)
        self.ontobuilder_interaction_signal.connect(self._trigger_create_mapping)
        self.ontomapper_interaction_signal.connect(self.create_mermaid)

    def on_interaction_finished(self):
        # This function will be called when the asynchronous interaction is finished
        print("Interaction finished!")

    def _run_asyncio_loop(self):
        """Run the asyncio event loop for a short duration."""
        self.loop.stop()
        self.loop.run_forever()

    def _start_manage_prompt(self, prompt):
        """Start the asynchronous _manage_prompt method."""
        asyncio.ensure_future(self._manage_prompt(prompt))

    def _trigger_create_ontology(self):
        asyncio.ensure_future(self.create_ontology())

    def _trigger_create_mapping(self):
        asyncio.ensure_future(self.create_mapping())

    async def _manage_prompt(self, prompt):
        self.LLManswer_textedit.insertPlainText("-------------------- CONTEXT GENERATION --------------------\n")

        # generate context
        async for data_chunk in self.plan_builder.interaction(input_task=prompt, json_data=self.json_data):
            self.LLManswer_textedit.insertPlainText(data_chunk)
            self.LLMANSWER_scrollbar.setValue(self.LLMANSWER_scrollbar.maximum())
            QCoreApplication.processEvents()

        self.planner_interaction_signal.emit()

    async def create_ontology(self):
        self.LLManswer_textedit.insertPlainText("\n-------------------- RDF/XML OWL --------------------\n")
        # generate context
        async for data_chunk in self.ontology_builder.interact(
                json_data=self.json_data,
                rationale=self.plan_builder.answer):
            self.LLManswer_textedit.insertPlainText(data_chunk)
            self.LLMANSWER_scrollbar.setValue(self.LLMANSWER_scrollbar.maximum())
            QCoreApplication.processEvents()

        try:
            print(self.ontology_builder.answer)
            self.ontology_textedit.setText(self.ontology_builder.get_xml_codeblock())
        except:
            self.ontology_textedit.setText("Could not obtain the RDF/XML codeblock from source.")
        finally:
            self.OUTPUT_tab.setCurrentIndex(1)
            QCoreApplication.processEvents()

        self.ontobuilder_interaction_signal.emit()

    async def create_mapping(self):
        self.LLManswer_textedit.insertPlainText("\n-------------------- RML MAPPING --------------------\n")
        # generate context
        async for data_chunk in self.ontology_mapper.interact(rationale=self.ontology_builder.answer):
            self.LLManswer_textedit.insertPlainText(data_chunk)
            self.LLMANSWER_scrollbar.setValue(self.LLMANSWER_scrollbar.maximum())
            QCoreApplication.processEvents()

        try:
            print(self.ontology_mapper.answer)
            self.rml_textedit.setText(self.ontology_mapper.get_rml_codeblock())
        except:
            self.rml_textedit.setText("Could not obtain the RML codeblock from source.")
        finally:
            self.OUTPUT_tab.setCurrentIndex(3)
            QCoreApplication.processEvents()

        self.ontomapper_interaction_signal.emit()

    def create_mermaid(self):
        try:
            print(self.ontology_builder.get_xml_codeblock())
            self.mermaid_generator.interact(self.ontology_builder.get_xml_codeblock())
            print(self.mermaid_generator.answer)
            graph = self.mermaid_generator.get_diagram()
            self.mermaid_widget.plot(graph)
            self.OUTPUT_tab.setCurrentIndex(2)
        except Exception as e:
            self.log.myprint_error(f"An error occurred while generating the mermaid diagram: {e}")
            self.OUTPUT_tab.setCurrentIndex(4)

    def _load_csv_data(self, btn):
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
