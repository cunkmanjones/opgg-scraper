import json
import os
import sys
import warnings

import pandas as pd
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, 
    QLabel, QComboBox, QTableWidget, QTableWidgetItem, QTabWidget, 
    QPushButton, QFileDialog, QStackedLayout, QSizePolicy, QCompleter
)
from PySide6.QtGui import QGuiApplication, QIcon
import qdarktheme

from constants import GAMETYPES_PLAYER, GAMETYPES_CHAMPION, RANKS, REGIONS 
from generic_champion import get_champion_stats, get_league_api, get_opgg_patches
from player_champion import get_summoner_stats
from player_season import get_seasons_list
from player_summoner import get_summoner_id
from pyside6_champion import setup_stats_columns


# Suppress Deprecation Warning 
warnings.filterwarnings("ignore", category=DeprecationWarning, message="sipPyTypeDict.*")

# Fetch LoL Champion Names/IDs
lolChampions = get_league_api()
lolChampionsDataFrame = pd.DataFrame(list(lolChampions.items()), columns=['name', 'id'])

# Main Application Class
class MainApp(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.initUI()

    # Setup UI
    def initUI(self) -> None:
        mainLayout = QVBoxLayout()

        self.tabs = QTabWidget(self)

        mainLayout.addWidget(self.tabs)
        self.setLayout(mainLayout)

        self.initialize_tabs()

        self.setWindowTitle("OP.GG Scraper - League of Legends")
        self.resize(1300, 600)
        self.center()
    
    # Center Main Window on Screen
    def center(self) -> None:
        screenGeometry = QGuiApplication.primaryScreen().geometry()
        windowGeometry = self.frameGeometry()

        centerPoint = screenGeometry.center()
        windowGeometry.moveCenter(centerPoint)
        self.move(windowGeometry.topLeft())
    
    # Initialize Tabs
    def initialize_tabs(self) -> None:
        # Storage
        self.tab1Stats, self.tab2Stats1, self.tab2Stats2  = None, None, None

        self.tab1, self.tab2, self.tab3 = QWidget(), QWidget(), QWidget()
        self.tabs.addTab(self.tab1, "Season Data")
        self.tabs.addTab(self.tab2, "Compare Players")
        self.tabs.addTab(self.tab3, "Champion Data")

        self.setup_tab1()
        self.setup_tab2()
        self.setup_tab3()

    # Setup First Tab
    def setup_tab1(self) -> None:
        self.layoutVerticalTab1, self.widgetsTab1 = self.create_player_widgets(self.tab1, export=True, orientation=True)
        self.connect_widget_signals(self.widgetsTab1, 'tab1', export=True, orientation=True)
    
    # Setup Second Tab
    def setup_tab2(self) -> None:
        layoutHorizontal = QHBoxLayout(self.tab2)
        layoutHorizontal.setContentsMargins(0, 0, 0, 0)
        layoutHorizontal.setSpacing(0)

        containerLeft = QWidget(self.tab2)
        self.layoutVerticalTab2Left, self.widgetsTab2Left = self.create_player_widgets(containerLeft)
        layoutHorizontal.addWidget(containerLeft)

        containerRight = QWidget(self.tab2)
        self.layoutVerticalTab2Right, self.widgetsTab2Right = self.create_player_widgets(containerRight)
        layoutHorizontal.addWidget(containerRight)

        self.connect_widget_signals(self.widgetsTab2Left, 'tab2_player1')
        self.connect_widget_signals(self.widgetsTab2Right, 'tab2_player2')

    # Setup Third Tab
    def setup_tab3(self) -> None:
        layoutVertical = QVBoxLayout(self.tab3)
        layoutVertical.setContentsMargins(0, 0, 0, 0)
        layoutVertical.setSpacing(0)
        container = QWidget(self.tab3)
        layoutHorizontal = QHBoxLayout(container)

        championDict = lolChampions # championDict = get_league_api()
        championNamesList = list(championDict.keys())
        completer = QCompleter(championNamesList)
        completer.setCaseSensitivity(Qt.CaseInsensitive)

        self.lineSearchBar = QLineEdit(self)
        self.lineSearchBar.setPlaceholderText("Enter Champion Name")
        self.lineSearchBar.setCompleter(completer)

        self.championStats = []
        self.lineSearchBar.returnPressed.connect(
            lambda: (
                self.championStats.clear(),
                self.championStats.append(
                    get_champion_stats(
                        X, 
                        championDict, 
                        self.comboboxVersion.currentText(),
                        self.comboboxRegion.currentText(),
                        self.comboboxGametype.currentText(),
                        self.comboboxRank.currentData()
                    )
                )
                if ( X := next(( x for x in championNamesList if x.lower() == self.lineSearchBar.text().lower() ), None) )
                else layoutStacked.setCurrentIndex(0),
                setup_stats_columns(layoutStacked, self.championStats, championDict)
            )
        )
        
        self.comboboxRegion = QComboBox()
        self.comboboxRegion.addItems(['Global'] + REGIONS)
        self.comboboxRegion.setFixedWidth(80)
        
        self.comboboxGametype = QComboBox()
        self.comboboxGametype.addItems(GAMETYPES_CHAMPION)

        self.comboboxRank = QComboBox()
        for key, value in RANKS.items():
            self.comboboxRank.addItem(key, value)
        self.comboboxRank.setFixedWidth(120)
        
        self.labelVersion = QLabel('OP.GG Version:')
        self.comboboxVersion = QComboBox()
        self.comboboxVersion.addItems(get_opgg_patches())
        self.comboboxVersion.setFixedWidth(80)

        self.buttonExport = QPushButton('Export JSON', self)
        self.buttonExport.clicked.connect(
            lambda: (
                self.export_json(self.championStats[0])
                if len(self.championStats) > 0
                else print("No Champion Data")
            )
        )

        # Order
        layoutHorizontal.addWidget(self.comboboxRegion)
        layoutHorizontal.addWidget(self.comboboxGametype)
        layoutHorizontal.addWidget(self.comboboxRank)
        layoutHorizontal.addWidget(self.lineSearchBar)
        layoutHorizontal.addWidget(self.labelVersion)
        layoutHorizontal.addWidget(self.comboboxVersion)
        layoutHorizontal.addWidget(self.buttonExport)

        self.containerLabelEmpty = QWidget()
        self.layoutLabelEmpty = QVBoxLayout(self.containerLabelEmpty)
        self.labelEmpty = QLabel('Currently not displaying any data.')
        self.labelEmpty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.labelEmpty.setStyleSheet("margin-top: -11px;") # Thanks Layouts :(
        self.layoutLabelEmpty.addWidget(self.labelEmpty)
        
        containerStacked = QWidget(self.tab3)
        layoutStacked = QStackedLayout(containerStacked)
        layoutStacked.addWidget(self.containerLabelEmpty)
        layoutStacked.setCurrentIndex(0)

        layoutVertical.addWidget(container)
        layoutVertical.addWidget(containerStacked)

    # Create Player Widgets
    def create_player_widgets(self, parent, export=False, orientation=False) -> tuple[QVBoxLayout, dict]:
        widgets = {}
        layoutVertical = QVBoxLayout(parent)
        layoutHorizontal = QHBoxLayout() # First Row

        # Main Dropdown Menu
        widgets['dropdown_region'] = QComboBox(parent)
        widgets['dropdown_region'].addItems(REGIONS)
        widgets['dropdown_region'].setFixedWidth(80)
        layoutHorizontal.addWidget(widgets['dropdown_region'])

        # Text Input Bar
        widgets['text_input'] = QLineEdit(parent)
        widgets['text_input'].setPlaceholderText("Enter SummonerName#Tagline")
        layoutHorizontal.addWidget(widgets['text_input'])

        # Search Button
        widgets['search_button'] = QPushButton("Search", parent)
        widgets['search_button'].setEnabled(False)
        layoutHorizontal.addWidget(widgets['search_button'])

        # Export Button (optional)
        if export:
            widgets['export_button'] = QPushButton("Export CSV", parent)
            widgets['export_button'].setEnabled(False)
            layoutHorizontal.addWidget(widgets['export_button'])

        layoutVertical.addLayout(layoutHorizontal)
        layoutHorizontalDropdowns = QHBoxLayout() # Second Row

        # Orientation Button (optional)
        if orientation:
            widgets['orientation_button'] = QPushButton("Orientation", parent)
            widgets['orientation_button'].setFixedWidth(80)
            widgets['orientation_button'].setEnabled(False)
            widgets['orientation_button'].hide()
            layoutHorizontalDropdowns.addWidget(widgets['orientation_button'])
            widgets['orientation_current'] = 'columns'

        # Seasons Dropdown
        widgets['dropdown_seasons'] = QComboBox(parent)
        widgets['dropdown_seasons'].setEnabled(False)
        widgets['dropdown_seasons'].hide()
        layoutHorizontalDropdowns.addWidget(widgets['dropdown_seasons'])
        
        # GameType Dropdown
        widgets['dropdown_gametype'] = QComboBox(parent)
        widgets['dropdown_gametype'].addItems(GAMETYPES_PLAYER)
        widgets['dropdown_gametype'].setEnabled(False)
        widgets['dropdown_gametype'].hide()
        layoutHorizontalDropdowns.addWidget(widgets['dropdown_gametype'])

        # Add the new dropdowns layout to the tab1 layout
        layoutVertical.addLayout(layoutHorizontalDropdowns)

        # DataFrame Viewer
        widgets['table'] = QTableWidget(parent)
        widgets['table'].setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding) # Make table stretch vertically

        # Empty Dataframe Label
        widgets['label_emptytable'] = QLabel('Currently not displaying any data.')
        widgets['label_emptytable'].setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Stacked Layout Container for Dataframe Viewer and Empty Dataframe Label
        widgets['stacked_container'] = QWidget(parent) # REMOVES SMALL WINDOW WOOOOOO
        widgets['stacked_layout'] = QStackedLayout(widgets['stacked_container'])
        widgets['stacked_layout'].addWidget(widgets['table'])
        widgets['stacked_layout'].addWidget(widgets['label_emptytable'])
        widgets['stacked_layout'].setCurrentIndex(1)
        layoutVertical.addWidget(widgets['stacked_container'])

        # Technically not needed, but for consistency
        widgets['dataframe'] = pd.DataFrame()

        return layoutVertical, widgets

    # Connect singals to specific Widgets
    def connect_widget_signals(self, widgets, dataStorage, export=False, orientation=False) -> None:
        widgets['dropdown_region'].currentIndexChanged.connect(lambda: self.check_inputs(widgets))
        widgets['text_input'].textChanged.connect(lambda: self.check_inputs(widgets))
        widgets['text_input'].returnPressed.connect(lambda: self.on_search_clicked(widgets, dataStorage))
        widgets['search_button'].clicked.connect(lambda: self.on_search_clicked(widgets, dataStorage))
        widgets['dropdown_seasons'].currentIndexChanged.connect(lambda: self.on_dropdown_select(widgets, dataStorage))
        widgets['dropdown_gametype'].currentIndexChanged.connect(lambda: self.on_dropdown_select(widgets, dataStorage))

        if export:
            widgets['export_button'].clicked.connect(lambda: self.export_csv(widgets))
        if orientation:
            widgets['orientation_button'].clicked.connect(lambda: self.change_orientation(widgets))

    # Check if values used
    def check_inputs(self, widgets) -> None:
        dropdownValue = widgets['dropdown_region'].currentText() != ""
        textValue = widgets['text_input'].text() != ""
        widgets['search_button'].setEnabled(dropdownValue and textValue)

    # Update Table with DataFrame
    def update_table(self, dataframe, table) -> None:
        table.setRowCount(dataframe.shape[0])
        table.setColumnCount(dataframe.shape[1])
        table.setHorizontalHeaderLabels(dataframe.columns)

        for i in range(dataframe.shape[0]):
            for j in range(dataframe.shape[1]):
                item = QTableWidgetItem(str(dataframe.iat[i, j]))
                table.setItem(i, j, item)

    # Alternative Search Function for Dropdowns
    def on_dropdown_select(self, widgets, dataStorage) -> None:
        # Ugly for now
        if dataStorage == 'tab1':
            playerData = self.tab1Stats
        elif dataStorage == 'tab2_player1':
            playerData = self.tab2Stats1
        elif dataStorage == 'tab2_player2':
            playerData = self.tab2Stats2
        else:
            playerData = None
            return playerData

        if playerData is not None:
            #print(f"Season ID: {widgets['dropdown_seasons'].currentData()} | Gametype: {widgets['dropdown_gametype'].currentText()}")
            self.summoner_stats_dataframe(
                widgets['text_input'].text(),
                widgets['dropdown_seasons'].currentData(),
                widgets['dropdown_gametype'].currentText(),
                playerData,
                widgets
            )

    # Update Variables on Search Button Click
    def on_search_clicked(self, widgets, dataStorage) -> None:
        userText, region = widgets['text_input'].text(), widgets['dropdown_region'].currentText()
        #print(f"Text: {userText} | Region: {region}")
        validData = get_summoner_id(userText, region)

        if not validData:
            widgets['dropdown_seasons'].setEnabled(False)
            widgets['dropdown_seasons'].hide()
            widgets['dropdown_seasons'].blockSignals(True)
            widgets['dropdown_seasons'].clear()
            widgets['dropdown_seasons'].blockSignals(False)
            
            widgets['dropdown_gametype'].setEnabled(False)
            widgets['dropdown_gametype'].hide()
            widgets['dropdown_gametype'].blockSignals(True)
            widgets['dropdown_gametype'].setCurrentIndex(0)
            widgets['dropdown_gametype'].blockSignals(False)

            if 'export_button' in widgets:
                widgets['export_button'].setEnabled(False)

            if 'orientation_button' in widgets:
                widgets['orientation_button'].setEnabled(False)
                widgets['orientation_button'].hide()
            
            if not widgets['dataframe'].empty:
                widgets['dataframe'] = pd.DataFrame()
                widgets['stacked_layout'].setCurrentIndex(1)
                self.update_table(widgets['dataframe'], widgets['table'])
            
            #print("Invalid inputs. Please check the Summoner Name and/or Region.")
            return

        # Ugly for now
        if dataStorage == 'tab1':
            self.tab1Stats = validData
        elif dataStorage == 'tab2_player1':
            self.tab2Stats1 = validData
        elif dataStorage == 'tab2_player2':
            self.tab2Stats2 = validData

        if widgets['dropdown_seasons'].count() == 0:
            widgets['dropdown_seasons'].blockSignals(True)

            seasonsList = get_seasons_list() # seasonsList = get_seasons_list(validData)
            
            for index, row in seasonsList.iterrows():
                displayText = f"Season: {str(row['display_value'])}"
                if str(row['split']) != "nan":
                    displayText += f" (Split: { str(row['split'])[:-2] })"
                widgets['dropdown_seasons'].addItem(displayText, row['id'])
            widgets['dropdown_seasons'].blockSignals(False)

        dropdownSeasonsValue = widgets['dropdown_seasons'].itemData(0)
        widgets['dropdown_seasons'].blockSignals(True)
        widgets['dropdown_seasons'].setCurrentIndex(0)
        widgets['dropdown_seasons'].blockSignals(False)
        dropdownGametypeValue = widgets['dropdown_gametype'].itemText(0)
        widgets['dropdown_gametype'].blockSignals(True)
        widgets['dropdown_gametype'].setCurrentIndex(0)
        widgets['dropdown_gametype'].blockSignals(False)

        #print(f"Starting Season ID: {dropdownSeasonsValue} | Starting Gametype: {dropdownGametypeValue}")

        if 'export_button' in widgets:
            widgets['orientation_button'].setEnabled(True)
            widgets['orientation_button'].show()

        widgets['dropdown_seasons'].setEnabled(True)
        widgets['dropdown_seasons'].show()
        widgets['dropdown_gametype'].setEnabled(True)
        widgets['dropdown_gametype'].show()

        self.summoner_stats_dataframe(
            userText, 
            dropdownSeasonsValue, 
            dropdownGametypeValue, 
            validData, 
            widgets
        )

    # Fetch Summoner Stats
    def summoner_stats_dataframe(self, name, season, gametype, data, widgets):
        try:
            summonerDataFrame = get_summoner_stats(widgets['dropdown_region'].currentText(), season, gametype, data, lolChampionsDataFrame)

            # If Headers don't Exist, Update Table
            if 'vertical_headers' and 'horizontal_headers' not in widgets:
                widgets['dataframe'] = summonerDataFrame
                self.update_table(widgets['dataframe'], widgets['table'])

            # If Headers Exist, Update Table Orientation and Headers
            if 'vertical_headers' and 'horizontal_headers' in widgets:
                if widgets['orientation_current'] == 'columns':
                    widgets['dataframe'] = summonerDataFrame # Default Orientation is Columns
                
                if widgets['orientation_current'] == 'rows':
                    widgets['dataframe'] = summonerDataFrame.transpose()
                
                self.update_table(widgets['dataframe'], widgets['table'])

                widgets['vertical_headers'] = [str(row) for row in widgets['dataframe'].index.tolist()]
                widgets['horizontal_headers'] = [str(col) for col in widgets['dataframe'].columns.tolist()]

                widgets['table'].setVerticalHeaderLabels( widgets['vertical_headers'] )
                widgets['table'].setHorizontalHeaderLabels( widgets['horizontal_headers'] )

            # Change Stacked Layout Index
            if widgets['dataframe'].empty:
                widgets['stacked_layout'].setCurrentIndex(1)
                return
            widgets['stacked_layout'].setCurrentIndex(0)

            # Display Export Button if its in Widgets
            if 'export_button' in widgets:
                widgets['export_button'].setEnabled(True)     
        except Exception as e:
            print(f"Error fetching data: {e}")

            if 'export_button' in widgets:
                widgets['export_button'].setEnabled(False)
            return

    # Export Dataframe as CSV
    def export_csv(self, widgets) -> None:
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getSaveFileName(
            self, 
            "Save as CSV File", 
            "", 
            "CSV Files (*.csv);;All Files (*)", 
            options = options
        )
        if fileName:
            widgets['dataframe'].to_csv(fileName, index=False)
            #print(f"DataFrame exported to {fileName}")
            return

    # Export Dataframe as JSON
    def export_json(self, data_dict) -> None:
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getSaveFileName(
            self, 
            "Save JSON File", 
            "", 
            "JSON Files (*.json);;All Files (*)", 
            options = options
        )
        if fileName:
            try:
                with open(fileName, 'w', encoding='utf-8') as f:
                    json.dump(
                        data_dict, 
                        f, 
                        indent = 4, 
                        ensure_ascii = False
                    )
                #print(f"Dictionary exported to {fileName}")
                return
            except Exception as e:
                #print(f"Export failed: {str(e)}")
                return

    # Change DataFrame Orientation
    def change_orientation(self, widgets) -> None:
        if widgets['orientation_current'] == 'columns':
            widgets['orientation_current'] = 'rows'
        elif widgets['orientation_current'] == 'rows':
            widgets['orientation_current'] = 'columns'

        widgets['dataframe'] = widgets['dataframe'].transpose()
        self.update_table(widgets['dataframe'], widgets['table'])

        widgets['vertical_headers'] = [str(row) for row in widgets['dataframe'].index.tolist()]
        widgets['horizontal_headers'] = [str(col) for col in widgets['dataframe'].columns.tolist()]

        widgets['table'].setVerticalHeaderLabels( widgets['vertical_headers'] )
        widgets['table'].setHorizontalHeaderLabels( widgets['horizontal_headers'] )

# Main
if __name__ == "__main__":
    app = QApplication(sys.argv)

    app.setWindowIcon(QIcon(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'favicon.ico')))

    qdarktheme.setup_theme()
    
    window = MainApp()
    window.show()
    
    sys.exit(app.exec())
