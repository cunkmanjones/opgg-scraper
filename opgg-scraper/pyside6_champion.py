from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QStackedLayout

from constants import FIELD_DISPLAYNAMES


# Create Champion Data Columns
def setup_stats_columns(stackedLayout: QStackedLayout, championStats: list, championDict: dict) -> None:
    # Return if Champion Stats are Invalid
    if not championStats or not isinstance(championStats[0], dict):
        return
    statsData = championStats[0]
    
    # Remove Previous Champion Stats if Any
    if stackedLayout.count() > 1:
        stackedLayout.takeAt(1).widget().deleteLater()

    _setup_column_container(stackedLayout, statsData, championDict)

# Create Column Container
def _setup_column_container(stackedLayout: QStackedLayout, statsData: dict, championDict: dict) -> None:
    container = QWidget()
    columnsLayout = QHBoxLayout(container)
    columnsLayout.setAlignment(Qt.AlignHCenter | Qt.AlignTop)

    # Create average stats column
    if 'average_stats' in statsData:
        avgStats = _get_column_stats(statsData, False)
        avgColumn = _create_columns(
            "Overall Statistics", 
            avgStats, 
            False,
            championDict
        )
        columnsLayout.addWidget(avgColumn)

    # Create position-specific columns
    for position in statsData.get('positions', []):
        positionName = position.get('name', 'UNKNOWN')
        positionStats = _get_column_stats(position, True)
        
        positionColumn = _create_columns(
            f"{positionName} Statistics", 
            positionStats, 
            True,
            championDict
        )
        columnsLayout.addWidget(positionColumn)

    stackedLayout.addWidget(container)
    stackedLayout.setCurrentIndex(1)

# Create Stats Dictionaries
def _get_column_stats(statsData: dict, isPosition: bool) -> dict:
    if isPosition:
        return {
            **statsData.get('stats', {}),
            'roles': statsData.get('roles', []),
            'counters': statsData.get('counters', [])
        }
    
    return {
        'id': statsData.get('id'),
        **{k: v for k, v in statsData['average_stats'].items() 
           if k not in ['tier_data', 'tier', 'rank']}
    }

# Create Specific Columns
def _create_columns(title: str, stats: dict, isPosition: bool, championDict: dict) -> QWidget:
    column = QWidget()
    column.setStyleSheet("background-color: #2d2d2d; ")
    
    if isPosition:
        _setup_position_column(column, title, stats, championDict)
    else:
        _setup_average_column(column, title, stats)
    
    return column

# Create 'Average Stats' QVBoxLayout
def _setup_average_column(column: QWidget, title: str, stats: dict) -> None:
    layout = QVBoxLayout(column)
    layout.setAlignment(Qt.AlignTop)
    
    titleLabel = QLabel(title)
    titleLabel.setStyleSheet("font-weight: bold; font-size: 16px; margin-top: 9px;")
    layout.addWidget(titleLabel)
    
    for key, value in stats.items():
        if value is None:
            continue
            
        displayName = FIELD_DISPLAYNAMES.get(key, key.replace('_', ' ').title())
        formattedString = _format_stats(key, value)
        
        statLabel = QLabel(f"{displayName}: {formattedString}")
        statLabel.setStyleSheet("font-size: 13px; margin-left: 2px;")
        layout.addWidget(statLabel)
    
    layout.addStretch()

# Create 'Champion Data' QHBoxLayout
def _setup_position_column(column: QWidget, title: str, stats: dict, championDict: dict) -> None:
    mainLayout = QHBoxLayout(column)
    
    # Left side = Main stats | Right side = Class and Counters
    leftWidget = _create_position_main_stats(title, stats)
    rightWidget = _create_position_secondary_stats(stats, championDict)
    
    mainLayout.addWidget(leftWidget)
    mainLayout.addWidget(rightWidget)

# Create Leftside QWidget
def _create_position_main_stats(title: str, stats: dict) -> QWidget:
    leftWidget = QWidget()
    leftLayout = QVBoxLayout(leftWidget)
    leftLayout.setAlignment(Qt.AlignTop)
    
    titleLabel = QLabel(title)
    titleLabel.setStyleSheet("font-weight: bold; font-size: 16px;")
    leftLayout.addWidget(titleLabel)
    
    for key, value in stats.items():
        if value is None or key in ['counters', 'roles', 'tier_data']:
            continue
            
        displayName = FIELD_DISPLAYNAMES.get(key, key.replace('_', ' ').title())
        formattedString = _format_stats(key, value)
        
        statLabel = QLabel(f"{displayName}: {formattedString}")
        statLabel.setStyleSheet("font-size: 13px; margin-left: 2px;")
        leftLayout.addWidget(statLabel)
    
    leftLayout.addStretch()
    return leftWidget

# Create Rightside QWidget
def _create_position_secondary_stats(stats: dict, championDict: dict) -> QWidget:
    rightWidget = QWidget()
    rightLayout = QVBoxLayout(rightWidget)
    rightLayout.setAlignment(Qt.AlignTop)
    
    # Add role breakdown if exists
    if 'roles' in stats and stats['roles']:
        rolesWidget = _create_role_stats(stats['roles'])
        rightLayout.addWidget(rolesWidget)
    
    # Add counters if exists
    if 'counters' in stats and stats['counters']:
        countersWidget = _create_counter_stats(stats['counters'], championDict)
        rightLayout.addWidget(countersWidget)
    
    rightLayout.addStretch()
    return rightWidget

# Create Class Roles QWidget
def _create_role_stats(roles: list) -> QWidget:
    rolesWidget = QWidget()
    rolesLayout = QVBoxLayout(rolesWidget)
    rolesLayout.setContentsMargins(0, 0, 0, 0)
    
    rolesTitle = QLabel("Role Breakdown")
    rolesTitle.setStyleSheet("font-weight: bold; font-size: 16px;")
    rolesLayout.addWidget(rolesTitle)
    
    for role in roles:
        roleName = role.get('name', 'Unknown')
        roleStats = role.get('stats', {})
        
        roleLabel = QLabel(f"{roleName}:")
        roleLabel.setStyleSheet("font-weight: bold; margin-left: 2px;")
        rolesLayout.addWidget(roleLabel)
        
        for key, value in roleStats.items():
            if key in ['play', 'win']:
                continue
                
            displayName = FIELD_DISPLAYNAMES.get(key, key.replace('_', ' ').title())
            formattedString = _format_stats(key, value)
            rolesLayout.addWidget(QLabel(f"  {displayName}: {formattedString}"))
    
    return rolesWidget

# Create Counters QWidget
def _create_counter_stats(counters: list, championDict: dict) -> QWidget:
    countersWidget = QWidget()
    countersLayout = QVBoxLayout(countersWidget)
    countersLayout.setContentsMargins(0, 0, 0, 0)
    
    countersTitle = QLabel("Counters via Rank")
    countersTitle.setStyleSheet("font-weight: bold; font-size: 16px;")
    countersLayout.addWidget(countersTitle)
    
    # Sort by Total Games played against Counter
    countersTop = sorted(counters, key=lambda x: x.get('play', 0), reverse=True)[:5]
    
    for counter in countersTop:
        championId = counter.get('champion_id')
        play = counter.get('play', 0)
        win = counter.get('win', 0)
        winrate = win / play if play > 0 else 0
        
        counterLabel = QLabel(
            f"{_get_champion_name(championId, championDict)}: "
            f"{winrate*100:.1f}% ({win}-{play-win})"
        )
        counterLabel.setStyleSheet("font-size: 12px; margin-left: 2px;")
        countersLayout.addWidget(counterLabel)
    
    return countersWidget

# Stats Formatting
def _format_stats(key: str, value) -> str:
    if key == 'win_rate' and isinstance(value, float):
        return f"{value * 100:.1f}%"
    
    if key.endswith('_rate') and isinstance(value, float):
        return f"{value * 100:.2f}%"
    
    if key == 'kda' and isinstance(value, float):
        return f"{value:.2f}:1"
    
    # Exception
    return str(value)

# Return Champion Name from ID
def _get_champion_name(championId, championDict: dict) -> str:
    championId = int(championId)
    for key, value in championDict.items():
        if value == championId:
            # Expected
            return f"{key}"
    # Exception
    return f"Champion ID {championId}"
