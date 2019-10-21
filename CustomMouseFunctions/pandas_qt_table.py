# some experiments in creating a PyQt table from a pandas DataFrame
# Background info:
# 
# https://stackoverflow.com/questions/31475965/fastest-way-to-populate-qtableview-from-pandas-data-frame/31557937
# https://stackoverflow.com/questions/41192293/make-qtableview-editable-when-model-is-pandas-dataframe
# https://www.youtube.com/watch?v=hJEQEECZSH0
# https://stackoverflow.com/questions/39914926/pyqt-load-sql-in-qabstracttablemodel-qtableview-using-pandas-dataframe-edi/39971773#39971773
import sys
import pandas as pd
from qtpy.QtWidgets import QApplication, QTableView
from qtpy.QtCore import QAbstractTableModel, Qt

df = pd.DataFrame({'a': ['Mary', 'Jim', 'John'],
                   'b': [100, 200, 300],
                   'c': ['a', 'b', 'c']})

class pandasModel(QAbstractTableModel):

    def __init__(self, data):
        QAbstractTableModel.__init__(self)
        self._data = data

    def rowCount(self, parent=None):
        return self._data.shape[0]

    def columnCount(self, parnet=None):
        return self._data.shape[1]

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole:
                return str(self._data.iloc[index.row(), index.column()])
        return None

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._data.columns[col]
        return None
    
    def setData_disabled(self, index, value, role):
        if not index.isValid():
            return False
        if role != Qt.EditRole:
            return False
        row = index.row()
        if row < 0 or row >= len(self._data.values):
            return False
        column = index.column()
        if column < 0 or column >= self._data.columns.size:
            return False
        self._data.values[row][column] = value
        self.dataChanged.emit(index, index)
        return True

    def setData(self, index, value, role=Qt.EditRole):
        if index.isValid():
            print(f"row {index.row()}, col {index.column()}")
            print("data set with keyboard : " , str(value))
            # in contrast to a couple if stackoverflow posts, the following
            # line did the trick. The nested indexing used in the stackoverflow posts
            # may not modify the original item but returns a copy of the cell
            # With the following modification I can now edit and the changes
            # are reflected in the data table
            self._data.iloc[index.row(),index.column()] = value
            print(self._data)
            print("data committed : " , self._data.values[index.row()][index.column()])
            self.dataChanged.emit(index, index)
            return True
        return None

    def updateData(self, new_dataframe):
        # quick hack, not sure whether the dataChanged signal I am emitting
        # is consistent with expectations
        self._data=new_dataframe
        self.dataChanged.emit(0,0)
        for i in range(len(new_dataframe)):
            self.dataChanged.emit(i,i)

    def flags(self, index):
        flags = super(self.__class__,self).flags(index)
        flags |= Qt.ItemIsSelectable
        flags |= Qt.ItemIsEnabled

        return flags

if __name__ == '__main__':
    app = QApplication(sys.argv)
    model = pandasModel(df)
    view = QTableView()
    view.setModel(model)
    view.resize(800, 600)
    view.show()
    sys.exit(app.exec_())