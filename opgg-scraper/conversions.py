import os

from lupa import LuaRuntime
import pandas as pd


# Call Lua math functions
def call_lua_math_function(funcName, *args):
    lua = LuaRuntime()

    # Load Lua script
    lua_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'math_functions.lua')
    with open(lua_file_path, 'r') as f:
        lua_code = f.read()
    lua.execute(lua_code)

    # Convert each argument to Lua-compatible string
    lua_args = []
    for arg in args:
        if isinstance(arg, list):
            # Convert Python list to Lua table syntax
            lua_args.append("{" + ", ".join(map(str, arg)) + "}")
        else:
            # Pass non-list arguments as-is
            lua_args.append(str(arg))
    
    # Construct Lua function call
    lua_call = f"{funcName}({', '.join(lua_args)})"
    return lua.eval(lua_call)

# Function to convert Lua table to Python list
def _lua_table_to_list(luaTable) -> list:
    return [luaTable[i] for i in range(1, len(luaTable) + 1)]

# Round Dataframe Values
def round_dataframe(data):
    numericColumns = data.select_dtypes(include=['float64', 'int64']).columns
    data[numericColumns] = data[numericColumns].round(3)
    return data

# Turn Python list of Dictionaries into Single Dictionary
def dict_from_list(list) -> dict:
    newList = {}
    for dictionary in list:
        for key, value in dictionary.items():
            newList.setdefault(key, []).append(value)
    return newList

# Merge Function Created Columns with Existing Dataframe
def merge_function_columns(funcDict, data, champData):
    for key, value in funcDict.items():
        result = value()
        data.insert(len(data.columns), key, _lua_table_to_list(result))
    # Align Champion Names ('name') with IDs ('id')
    alignedNames = pd.merge(data, champData, on = 'id', how = 'left')
    return alignedNames
