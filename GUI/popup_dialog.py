from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTreeView
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt
from collections import OrderedDict


class PopupDialog(QDialog):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        # Create a tree view and set the model
        self.tree_view = QTreeView()
        self.model = QStandardItemModel()
        self.root_item = self.model.invisibleRootItem()
        self.tree_view.setModel(self.model)

        layout.addWidget(self.tree_view)
        self.setLayout(layout)

        default = OrderedDict({'task_0': {'step_name': "", 'step_description': ""}})
        self._manage_general_plan_treeview(default)

    def _manage_general_plan_treeview(self, data_dict):
        # Clear the model
        self.model.removeRows(0, self.model.rowCount())
        self.model.setHorizontalHeaderLabels(['Key', 'Value'])
        self._create_items(self.root_item, data_dict)
        self.tree_view.expandAll()
        self.tree_view.repaint()

    def _create_items(self, parent, elements):

        for key, value in elements.items():

            if not isinstance(value, dict):
                item1 = QStandardItem(key)
                item2 = QStandardItem()
                item2.setFlags(item2.flags() | Qt.ItemIsEditable)
                parent.appendRow([item1, item2])
            else:
                item = QStandardItem(key)
                parent.appendRow(item)
                self._create_items(item, value)

    def get_tree_content(self):
        return self.get_item_content(self.root_item)

    def get_item_content(self, item):
        item_dict = {}

        for row in range(item.rowCount()):
            key_item = item.child(row, 0)
            value_item = item.child(row, 1)

            if key_item.rowCount() > 0:
                item_dict[key_item.text()] = self.get_item_content(key_item)
            else:
                item_dict[key_item.text()] = value_item.text() if value_item else ""

        return item_dict
