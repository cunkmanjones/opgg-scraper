import math
import json
import requests
import pandas as pd
from bs4 import BeautifulSoup

# Round Up Data
# (kill + assist) / death = KDA Ratio
def kda_ratio(kill, death, assist):
    # if perfect KDA
    if (death == 0).any().any():
        return kill + assist
    return (kill + assist) / death

# kill|death|assist / play = K|D|A Averages
def kda_averages(stat, play):
    return stat / play

# (minion_kill + neutral_minion_kill) / play = Average CS
def average_cs(minions, jg_monsters, play):
    return (minions + jg_monsters) / play

# gold_earned / play = Average Gold
def average_gold(gold, play):
    return gold / play

# (game_length_second / 60) / play = Average Game Length
def average_game_length(game_length, play):
    return (game_length / 60) / play

# Average CS / Average Game Length = CS Per Minute
def cs_per_minute(cs, game_length):
    return cs / game_length

# Average Gold / Average Game Length = Gold Per Minute
def gold_per_minute(gold, game_length):
    return gold / game_length

# Get Summoner Stats
def get_summoner_stats(player_name):
    #player_name = 'Budwolf-NA1'
    #url = 'https://www.op.gg/summoners/na/Budwolf-NA1/champions'
    url = f'https://www.op.gg/summoners/na/{player_name}/champions'
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/114.0'}
    soup = BeautifulSoup(requests.get(url, headers=headers).content, 'html.parser')

    # Get Data Keys
    data = soup.select_one('#__NEXT_DATA__').text
    data = json.loads(data)
    #print(data['props']['pageProps']['data'].keys())

    # Get Champion Stats
    champion_stats = data['props']['pageProps']['data']['most_champions']['champion_stats']
    #print(champion_stats)

    # Champion-Stats Data Frame
    cs_selected_columns = ['id', 'play', 'win', 'lose', 'kill', 'death', 'assist']
    cs_df = pd.DataFrame(champion_stats)
    #print(cs_df[selected_columns])

    cs_df_container = cs_df[cs_selected_columns]
    #cs_df_container.insert(len(cs_df_container.columns), 'cs', (cs_df['minion_kill'] + cs_df['neutral_minion_kill']) / cs_df['play'] )
    cs_df_container.insert( len(cs_df_container.columns), 'cs', average_cs(cs_df['minion_kill'], cs_df['neutral_minion_kill'], cs_df['play']) )
    cs_df_container.insert( len(cs_df_container.columns), 'kda', kda_ratio(cs_df['kill'], cs_df['death'], cs_df['assist']) )
    cs_df_container.insert( len(cs_df_container.columns), 'gold', average_gold(cs_df['gold_earned'], cs_df['play']) )
    cs_df_container.insert( len(cs_df_container.columns), 'game_length', average_game_length(cs_df['game_length_second'], cs_df['play']) )
    cs_df_container.insert( len(cs_df_container.columns), 'csm', cs_per_minute(cs_df_container['cs'], cs_df_container['game_length']) )
    cs_df_container.insert( len(cs_df_container.columns), 'gpm', gold_per_minute(cs_df_container['gold'], cs_df_container['game_length']) )
    #cs_df_container.insert(len(cs_df_container.columns), 'name', '' )
    print(cs_df_container)

    # Champion-Data Data Frame
    champion_data = data['props']['pageProps']['data']['champions']
    #cd_selected_columns = ['id', 'name']
    cd_df_container = pd.DataFrame(champion_data)[['id', 'name']]
    #print(cd_df_container)

    # Data Frame Merge
    merged_container = cs_df_container.merge(cd_df_container, on='id', how='left')
    #print("Budwolf#NA1 Stats:")
    #print(merged_container[['name', 'play', 'win', 'lose', 'kill', 'death', 'assist', 'cs']])
    print(f"{player_name} Stats:")
    print(merged_container[['name', 'play', 'win', 'lose', 'kda', 'kill', 'death', 'assist', 'cs', 'csm', 'gold', 'gpm', 'game_length']])

# Get Summoner Name
def get_summoner_name():
    summoner_name = input("Enter Summoner Name: ")
    get_summoner_stats(summoner_name)

# Main
if __name__ == '__main__':
    get_summoner_name()
