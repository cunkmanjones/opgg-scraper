# Round Up Data
# (win / play) * 100 = Win Rate
def win_rate(win, play):
    return (win / play) * 100

# (kill + assist) / death = KDA Ratio
def kda_ratio(kill, death, assist):
    # Incase of Perfect KDA
    for i in range(0, len(death)):
        if death[i] == 0:
            death[i] = 1
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
