from PyQt5.QtWidgets import QMainWindow, QFileDialog
from PyQt5 import QtWidgets, QtCore, uic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QMainWindow, QDialog, QVBoxLayout, QTreeView
from PyQt5.QtGui import QColor
from collections import OrderedDict

#from OntoGenix_v_1_1.tools import csv2dataset, dataframe2prettyjson, extract_text, preprocess_yaml, text2dict
#from OntoGenix_v_1_1.PlanSage.LLM_planner import LlmPlanner
#from OntoGenix_v_1_1.OntoBuilder.LLM_ontology import LlmOntology
#from OntoGenix_v_1_1.MermaidOntoFlow.Llm_mermaid import LlmMermaid
#from GUI.popup_dialog import PopupDialog
#from GUI.log import log
#from GUI.plan_manager import PlanManager


class GuiBehavior(QMainWindow):

    # planner_metadata = {'first_instructions': './OntoGenix_v_1_1/PlanSage/first_instructions.prompt',
    #                     'instructions': './OntoGenix_v_1_1/PlanSage/instructions.prompt',
    #                     'role': 'You are a powerful ontology engineer that generates OWL ontologies in turtle format.'
    #                     }

    # onto_metadata = {'instructions': './OntoGenix_v_1_1/OntoBuilder/instructions.prompt',
    #                  'examples': './OntoGenix_v_1_1/OntoBuilder/examples.prompt',
    #                  'autocompletion': './OntoGenix_v_1_1/OntoBuilder/auto_completion.prompt',
    #                  'role': 'You are a powerful ontology engineer that generates OWL ontologies in turtle format.'
    #                  }

    # mermaid_metadata = {'instructions': './OntoGenix_v_1_1/MermaidOntoFlow/instructions.prompt',
    #                     'examples': './OntoGenix_v_1_1/MermaidOntoFlow/examples.prompt',
    #                     'role': 'You are a powerful ontology engineer that translates OWL ontologies in turtle format '
    #                             'to mermaid diagrams.'
    #                     }

    def __init__(self):
        QMainWindow.__init__(self, parent=None)
        uic.loadUi('GUI.ui', self)

    #     # ------ show ----------     
        self.showMaximized()

    #     # -- buttons callbacks --
    #     self.query_send_btn.clicked.connect(lambda: self._manage_prompt(self.query_prompt_textedit.toPlainText(),
    #                                                                     self.query_instruction_textedit.toPlainText()))

    #     # -- instantiate classes --
    #     self.plan_builder = LlmPlanner(self.planner_metadata)
    #     self.ontology_builder = LlmOntology(self.onto_metadata)
    #     self.mermaid_generator = LlmMermaid(self.mermaid_metadata)

    #     # -- general plan treeview
    #     self.general_plan_model = QStandardItemModel()
    #     self.general_root_item = self.general_plan_model.invisibleRootItem()
    #     self.plantree_treeview.setModel(self.general_plan_model)

    #     # -- buttons
    #     self.load_csv_btn.clicked.connect(self.load_csv_data)
    #     self.add_btn.clicked.connect(self.add_item)
    #     self.remove_btn.clicked.connect(self.remove_item)
    #     self.up_btn.clicked.connect(lambda: self.move_item(1))
    #     self.down_btn.clicked.connect(lambda: self.move_item(-1))

    #     # -- data containers
    #     self.csv_data = None
    #     self.plan_manager = PlanManager()

    #     # -- other classes instances
    #     self.dialog = PopupDialog()

    #     # -- log manager
    #     self.log = log(self.logger)


    # def _manage_prompt(self, task_description=None, instruction=None):

    #     if self.query_radiobutton.isChecked():
    #         # get selected indexes
    #         self.plan_manager.plan_dict = self._get_selected_items_as_dict(self.plantree_treeview)
    #         self.plan_manager.instruction = instruction

    #         planner_response = self.plan_builder.interaction(
    #             self.plan_manager.plan_dict,
    #             self.plan_manager.instruction,
    #             self.plan_manager.short_term_memory,
    #             self.plan_manager.long_term_memory
    #         )

    #     else:
    #         self.log.myprint_in("PlanSage: asking for a response.")
    #         planner_response = self.plan_builder.first_interaction(
    #             task_description,
    #             self.csv_data
    #         )

    #         self.plan_manager.short_term_memory = extract_text(
    #             text=planner_response,
    #             start_marker="Updated Memory:",
    #             end_marker="Output Tasks:"
    #         ).strip()
    #         self.plan_manager.long_term_memory = ""
    #         self.log.myprint_out("PlanSage: response generated.")

    #     try:
    #         plan_text = extract_text(planner_response, "START", "END").strip()
    #         instructions = extract_text(planner_response, "Output Instructions:", "Finish Statement: FINISH").strip()
    #         self.plan_manager.instructions = preprocess_yaml(instructions, parse="Instruction")
    #         self.plan_manager.text2dict(plan_text)

    #         self._manage_general_plan_treeview(self.plan_manager.plan_dict)
    #         self.instructions_textEdit.setText(self.plan_manager.instructions)
    #         self.instructions_textEdit.repaint()

    #         self.log.myprint_in("OntoBuilder: asking for a response.")
    #         owl_response = self.ontology_builder.interact(
    #             self.plan_manager.plan_dict2text(),
    #             self.csv_data
    #         )
    #         self.log.myprint_out("OntoBuilder: response generated.")

    #         print(f"############ owl_response:\n {owl_response}")
    #         owl_code_str = extract_text(owl_response, "Output Tasks:", "Finish Statement: FINISH").strip()
    #         self.ontology_textedit.setText(owl_code_str)
    #         self.tabWidget.setCurrentIndex(1)
    #         self.ontology_textedit.repaint()

    #         self.log.myprint_in("MermaidOntoFlow: asking for a response.")
    #         diagram_response = self.mermaid_generator.interact(owl_code_str)
    #         self.log.myprint_out("MermaidOntoFlow: response generated.")

    #         print(f"############ diagram_response\n: {diagram_response}")
    #         diagram_response_str = extract_text(diagram_response, "Output Tasks:", "Finish Statement: FINISH").strip()
    #         print(f"############ diagram_response_str\n: {diagram_response_str}")
    #         self.mermaid_widget.plot(diagram_response_str)
    #         self.tabWidget.setCurrentIndex(2)

    #     except ValueError as e:
    #         self.tabWidget.setCurrentIndex(4)
    #         self.log.myprint_error(f"An error occurred while processing the plan: {e}")

    # def _get_selected_items_as_dict(self, tree_view):
    #     selected_indexes = tree_view.selectionModel().selectedIndexes()
    #     result = {}
    #     for index in selected_indexes:
    #         item = tree_view.model().itemFromIndex(index)
    #         item_text = item.text()
    #         item_dict = {item_text: {}}
    #         for i in range(item.rowCount()):
    #             child_item = item.child(i)
    #             item_dict[item_text][child_item.text()] = {}
    #         result.update(item_dict)

    #     return str(result)

    # def _manage_general_plan_treeview(self, data_dict):
    #     self.general_plan_model.removeRows(0, self.general_plan_model.rowCount())
    #     self.general_plan_model.setHorizontalHeaderLabels(['Key', 'Value'])
    #     self._create_items(self.general_root_item, data_dict)
    #     self.plantree_treeview.expandAll()
    #     self.plantree_treeview.repaint()

    # def _create_items(self, parent, elements):
    #     for key, value in elements.items():
    #         if not isinstance(value, dict):
    #             item1 = QStandardItem(key)
    #             item1.setText(str(key))
    #             item2 = QStandardItem(value)
    #             item2.setText(str(value))
    #             item2.setFlags(item2.flags() | Qt.ItemIsEditable)
    #             parent.appendRow([item1, item2])
    #         else:
    #             item = QStandardItem(key)
    #             item.setText(str(key))
    #             parent.appendRow(item)
    #             self._create_items(item, value)  # Do not pass position for children

    # def insert_in_position(self, odict, new_dict):
    #     new_odict = OrderedDict()
    #     position = int(list(new_dict.keys())[0].split('_')[1])
    #     i = 1
    #     for key, value in odict.items():
    #         if i == position:
    #             new_odict[f'task_{i}'] = new_dict[f'task_{position}']
    #             i += 1
    #         new_odict[f'task_{i}'] = value
    #         i += 1
    #     if position >= i:
    #         new_odict[f'task_{position}'] = new_dict[f'task_{position}']
    #     return new_odict

    # def add_item(self):
    #     self.dialog.exec_()
    #     # After the dialog is closed, get the content of the tree
    #     tree_content = self.dialog.get_tree_content()
    #     if self.plan_dict is not None:
    #         self.plan_dict = self.insert_in_position(self.plan_dict, tree_content)
    #     else:
    #         self.plan_dict = tree_content
    #     self._manage_general_plan_treeview(self.plan_dict)

    # def remove_item(self):
    #     current_item = self.plantree_treeview.currentIndex()
    #     item_data = self.plantree_treeview.model().data(current_item)

    #     if item_data and 'task' in item_data:
    #         self.general_plan_model.removeRow(current_item.row(), current_item.parent())
    #         del self.plan_dict[item_data]

    # def move_item(self, direction):
    #     def move_in_dict(d, index, direction):
    #         # Convert the OrderedDict to a list of tuples
    #         items = list(d.items())

    #         # Check if the index is within the valid range
    #         if 0 <= index + direction < len(items):
    #             # Swap the item at the given index with the next or previous item
    #             items[index + direction], items[index] = items[index], items[index + direction]

    #         # Convert the list back to an OrderedDict
    #         return OrderedDict(items)

    #     current_item_index = self.plantree_treeview.currentIndex()
    #     if current_item_index.isValid():
    #         key_column_index = self.plantree_treeview.model().index(current_item_index.row(), 0,
    #                                                                 current_item_index.parent())
    #         item_data = self.plantree_treeview.model().data(key_column_index)
    #         if item_data is not None:
    #             print(item_data)
    #             if 'task' in item_data:
    #                 row_number = current_item_index.row()
    #                 print(row_number)
    #                 self.plan_dict = move_in_dict(self.plan_dict, row_number, direction)
    #                 print(self.plan_dict)
    #                 self._manage_general_plan_treeview(self.plan_dict)
    #             else:
    #                 print("Selected item has no text.")
    #     else:
    #         print("No item is currently selected.")

    # def load_csv_data(self, btn):
    #     options = QtWidgets.QFileDialog.Options()
    #     options |= QtWidgets.QFileDialog.DontUseNativeDialog
    #     fileType = "CSV Files (*.csv)"
    #     fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "",
    #                                                         fileType, options=options)

    #     try:
    #         self.log.myprint_in(f"loading the csv dataset: {fileName}")
    #         self.csv_data = csv2dataset(fileName)
    #         json = dataframe2prettyjson(self.csv_data)
    #         self.csv_textedit.setText(json)
    #         self.log.myprint(f"{fileName} loaded!")
    #         self.tabWidget.setCurrentIndex(0)
    #     except ValueError as e:
    #         self.log.myprint_error(f"An error occurred while loading csv data: {e}")
    #         self.tabWidget.setCurrentIndex(4)


