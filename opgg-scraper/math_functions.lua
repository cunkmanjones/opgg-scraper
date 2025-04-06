--[[
    Math functions for calculating statistics from raw data.
    Python Lists are converted to Lua Tables prior to being called.
    Lua Tables are then converted back to Python Lists after being returned.

    Functions:
        - Win_rate(win, play)
        - Kda_ratio(kill, death, assist)
        - Average_cs(cs, neutral_cs, play)
        - Average_gold(gold, play)
        - Average_game_length(game_length, play)
        - Cs_per_minute(cs, game_length)
        - Gold_per_minute(gold, game_length)
]]
-- (win / play) * 100 = Winrate
function Win_rate(win, play)
    local result = {}
    for i = 1, #win do
        table.insert(result, (win[i] / play[i]) * 100) -- Calculate Winrate for this row
    end
    return result
end

-- (kill + assist) / death = KDA Ratio
function Kda_ratio(kill, death, assist)
    local result = {}
    for i = 1, #kill do
        -- Handle division by zero (perfect KDA)
        local d = death[i]
        if d == 0 then
            d = 1
        end
        table.insert(result, (kill[i] + assist[i]) / d) -- Calculate KDA ratio for this row
    end
    return result
end

--[[-- kill|death|assist / play = K|D|A Averages
function Kda_averages(stat, play)
    return stat / play
end]]

-- (minion_kill + neutral_minion_kill) / play = Average CS
function Average_cs(cs, neutral_cs, play)
    local result = {}
    for i = 1, #cs do
        table.insert(result, (cs[i] + neutral_cs[i]) / play[i]) -- Calculate Average CS for this row
    end
    return result
end

-- gold_earned / play = Average Gold
function Average_gold(gold, play)
    local result = {}
    for i = 1, #gold do
        table.insert(result, gold[i] / play[i]) -- Calculate Average Gold for this row
    end
    return result
end

-- (game_length_second / 60) / play = Average Game Length
function Average_game_length(game_length, play)
    local result = {}
    for i = 1, #game_length do
        table.insert(result, (game_length[i] / 60) / play[i]) -- Calculate Average Game Length for this row
    end
    return result
end

-- Average CS / Average Game Length = CS Per Minute
function Cs_per_minute(cs, game_length)
    local result = {}
    for i = 1, #cs do
        table.insert(result, cs[i] / game_length[i]) -- Calculate CS Per Minute for this row
    end
    return result
end

-- Average Gold / Average Game Length = Gold Per Minute
function Gold_per_minute(gold, game_length)
    local result = {}
    for i = 1, #gold do
        table.insert(result, gold[i] / game_length[i]) -- Calculate Gold Per Minute for this row
    end
    return result
end
