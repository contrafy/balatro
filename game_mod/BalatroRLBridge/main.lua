--- BalatroRLBridge - HTTP API for Reinforcement Learning
--- Exposes game state, legal actions, and action execution via localhost HTTP

local socket = require("socket")

local RLBridge = {}

-- Configuration
local CONFIG = {
    host = "127.0.0.1",
    port = 7777,
    max_request_size = 65536,
    schema_version = "1.0.0",
}

-- Server state
local server = nil
local start_time = nil
local request_count = 0
local error_count = 0
local last_error = nil

-- Logging utility
local function log(level, msg)
    local timestamp = os.date("%Y-%m-%d %H:%M:%S")
    print(string.format("[BalatroRLBridge][%s][%s] %s", timestamp, level, msg))
end

local function log_info(msg) log("INFO", msg) end
local function log_error(msg)
    log("ERROR", msg)
    error_count = error_count + 1
    last_error = msg
end
local function log_debug(msg) log("DEBUG", msg) end

--------------------------------------------------------------------------------
-- JSON Encoding (minimal implementation for Lua tables)
--------------------------------------------------------------------------------

local function json_encode_value(val, depth)
    depth = depth or 0
    if depth > 50 then return '"[max depth]"' end

    local t = type(val)
    if t == "nil" then
        return "null"
    elseif t == "boolean" then
        return val and "true" or "false"
    elseif t == "number" then
        if val ~= val then return "null" end -- NaN
        if val == math.huge or val == -math.huge then return "null" end
        return tostring(val)
    elseif t == "string" then
        -- Escape special characters
        local escaped = val:gsub('\\', '\\\\')
                           :gsub('"', '\\"')
                           :gsub('\n', '\\n')
                           :gsub('\r', '\\r')
                           :gsub('\t', '\\t')
        return '"' .. escaped .. '"'
    elseif t == "table" then
        -- Check if array or object
        local is_array = true
        local max_idx = 0
        for k, v in pairs(val) do
            if type(k) ~= "number" or k < 1 or math.floor(k) ~= k then
                is_array = false
                break
            end
            if k > max_idx then max_idx = k end
        end
        -- Check for sparse arrays
        if is_array and max_idx > 0 then
            for i = 1, max_idx do
                if val[i] == nil then
                    is_array = false
                    break
                end
            end
        end

        local parts = {}
        if is_array and max_idx > 0 then
            for i = 1, max_idx do
                parts[#parts + 1] = json_encode_value(val[i], depth + 1)
            end
            return "[" .. table.concat(parts, ",") .. "]"
        else
            for k, v in pairs(val) do
                local key = type(k) == "string" and k or tostring(k)
                parts[#parts + 1] = json_encode_value(key, depth + 1) .. ":" .. json_encode_value(v, depth + 1)
            end
            return "{" .. table.concat(parts, ",") .. "}"
        end
    elseif t == "function" or t == "userdata" or t == "thread" then
        return '"[' .. t .. ']"'
    else
        return '"[unknown]"'
    end
end

local function json_encode(val)
    local ok, result = pcall(json_encode_value, val, 0)
    if ok then
        return result
    else
        return '{"error":"json encoding failed: ' .. tostring(result) .. '"}'
    end
end

--------------------------------------------------------------------------------
-- JSON Decoding (minimal implementation)
--------------------------------------------------------------------------------

local function json_decode(str)
    if not str or str == "" then return nil end

    local pos = 1
    local function skip_whitespace()
        while pos <= #str and str:sub(pos, pos):match("[ \t\n\r]") do
            pos = pos + 1
        end
    end

    local function parse_value()
        skip_whitespace()
        local c = str:sub(pos, pos)

        if c == '"' then
            -- String
            pos = pos + 1
            local start = pos
            local result = ""
            while pos <= #str do
                local ch = str:sub(pos, pos)
                if ch == '"' then
                    pos = pos + 1
                    return result
                elseif ch == '\\' then
                    pos = pos + 1
                    local esc = str:sub(pos, pos)
                    if esc == 'n' then result = result .. '\n'
                    elseif esc == 'r' then result = result .. '\r'
                    elseif esc == 't' then result = result .. '\t'
                    elseif esc == '"' then result = result .. '"'
                    elseif esc == '\\' then result = result .. '\\'
                    else result = result .. esc
                    end
                    pos = pos + 1
                else
                    result = result .. ch
                    pos = pos + 1
                end
            end
            error("Unterminated string")
        elseif c == '{' then
            -- Object
            pos = pos + 1
            local obj = {}
            skip_whitespace()
            if str:sub(pos, pos) == '}' then
                pos = pos + 1
                return obj
            end
            while true do
                skip_whitespace()
                local key = parse_value()
                skip_whitespace()
                if str:sub(pos, pos) ~= ':' then error("Expected ':'") end
                pos = pos + 1
                local val = parse_value()
                obj[key] = val
                skip_whitespace()
                local sep = str:sub(pos, pos)
                if sep == '}' then
                    pos = pos + 1
                    return obj
                elseif sep == ',' then
                    pos = pos + 1
                else
                    error("Expected ',' or '}'")
                end
            end
        elseif c == '[' then
            -- Array
            pos = pos + 1
            local arr = {}
            skip_whitespace()
            if str:sub(pos, pos) == ']' then
                pos = pos + 1
                return arr
            end
            while true do
                arr[#arr + 1] = parse_value()
                skip_whitespace()
                local sep = str:sub(pos, pos)
                if sep == ']' then
                    pos = pos + 1
                    return arr
                elseif sep == ',' then
                    pos = pos + 1
                else
                    error("Expected ',' or ']'")
                end
            end
        elseif str:sub(pos, pos + 3) == "true" then
            pos = pos + 4
            return true
        elseif str:sub(pos, pos + 4) == "false" then
            pos = pos + 5
            return false
        elseif str:sub(pos, pos + 3) == "null" then
            pos = pos + 4
            return nil
        elseif c:match("[%d%-]") then
            -- Number
            local start = pos
            if str:sub(pos, pos) == '-' then pos = pos + 1 end
            while pos <= #str and str:sub(pos, pos):match("[%d%.eE%+%-]") do
                pos = pos + 1
            end
            return tonumber(str:sub(start, pos - 1))
        else
            error("Unexpected character: " .. c)
        end
    end

    local ok, result = pcall(parse_value)
    if ok then
        return result
    else
        return nil
    end
end

--------------------------------------------------------------------------------
-- HTTP Server
--------------------------------------------------------------------------------

local function parse_http_request(data)
    local lines = {}
    for line in data:gmatch("[^\r\n]+") do
        lines[#lines + 1] = line
    end

    if #lines < 1 then return nil end

    local method, path, version = lines[1]:match("^(%w+)%s+([^%s]+)%s+HTTP/([%d%.]+)")
    if not method then return nil end

    local headers = {}
    local body_start = nil
    for i = 2, #lines do
        local line = lines[i]
        if line == "" then
            body_start = i + 1
            break
        end
        local key, value = line:match("^([^:]+):%s*(.*)$")
        if key then
            headers[key:lower()] = value
        end
    end

    local body = nil
    if body_start then
        -- Find body after headers (after \r\n\r\n)
        local _, body_pos = data:find("\r\n\r\n")
        if body_pos then
            body = data:sub(body_pos + 1)
        end
    end

    return {
        method = method,
        path = path,
        version = version,
        headers = headers,
        body = body
    }
end

local function send_response(client, status_code, status_text, body, content_type)
    content_type = content_type or "application/json"
    local response = string.format(
        "HTTP/1.1 %d %s\r\n" ..
        "Content-Type: %s\r\n" ..
        "Content-Length: %d\r\n" ..
        "Connection: close\r\n" ..
        "Access-Control-Allow-Origin: *\r\n" ..
        "Access-Control-Allow-Methods: GET, POST, OPTIONS\r\n" ..
        "Access-Control-Allow-Headers: Content-Type\r\n" ..
        "\r\n%s",
        status_code, status_text,
        content_type,
        #body,
        body
    )
    client:send(response)
end

local function send_json(client, status_code, data)
    local status_text = status_code == 200 and "OK" or
                        status_code == 400 and "Bad Request" or
                        status_code == 404 and "Not Found" or
                        status_code == 500 and "Internal Server Error" or
                        "Unknown"
    send_response(client, status_code, status_text, json_encode(data), "application/json")
end

--------------------------------------------------------------------------------
-- Game State Extraction
--------------------------------------------------------------------------------

-- Helper to safely get nested table values
local function safe_get(tbl, ...)
    local current = tbl
    for _, key in ipairs({...}) do
        if type(current) ~= "table" then return nil end
        current = current[key]
    end
    return current
end

-- Extract card data from a card object
local function extract_card(card)
    if not card then return nil end

    local data = {
        id = card.sort_id or card.unique_val or tostring(card),
        -- Base card properties
        rank = safe_get(card, "base", "value") or safe_get(card, "base", "nominal"),
        suit = safe_get(card, "base", "suit"),
        -- Display name
        name = safe_get(card, "base", "name") or safe_get(card, "label"),
        -- Enhancements
        edition = nil,
        enhancement = nil,
        seal = nil,
        -- Status
        debuffed = card.debuff or false,
        facing = card.facing or "front",
        highlighted = card.highlighted or false,
        -- Position in hand (for selection)
        area_index = nil,
    }

    -- Extract edition
    if card.edition then
        if card.edition.foil then data.edition = "foil"
        elseif card.edition.holo then data.edition = "holo"
        elseif card.edition.polychrome then data.edition = "polychrome"
        elseif card.edition.negative then data.edition = "negative"
        end
    end

    -- Extract enhancement
    if card.ability then
        local ability_name = card.ability.name
        if ability_name then
            data.enhancement = ability_name
        end
    end

    -- Extract seal
    if card.seal then
        data.seal = card.seal
    end

    -- Position in parent area
    if card.area and card.area.cards then
        for i, c in ipairs(card.area.cards) do
            if c == card then
                data.area_index = i
                break
            end
        end
    end

    return data
end

-- Extract joker data
local function extract_joker(joker)
    if not joker then return nil end

    return {
        id = joker.sort_id or tostring(joker),
        name = safe_get(joker, "ability", "name") or safe_get(joker, "label"),
        key = joker.config and joker.config.center and joker.config.center.key,
        rarity = safe_get(joker, "config", "center", "rarity"),
        sell_cost = joker.sell_cost or 0,
        -- Ability-specific data
        ability = joker.ability,
        edition = joker.edition,
        area_index = nil,
    }
end

-- Determine current game phase
local function get_game_phase()
    if not G then return "UNKNOWN" end

    -- Check various game states
    if G.STATE == G.STATES.MENU then return "MENU" end
    if G.STATE == G.STATES.SPLASH then return "SPLASH" end

    -- Check for specific UI states
    if G.GAME then
        if G.GAME.shop and G.shop and G.shop.cards and #G.shop.cards > 0 then
            return "SHOP"
        end

        if G.STATE == G.STATES.SELECTING_HAND then
            return "SELECTING_HAND"
        end

        if G.STATE == G.STATES.HAND_PLAYED then
            return "HAND_PLAYED"
        end

        if G.STATE == G.STATES.DRAW_TO_HAND then
            return "DRAW_TO_HAND"
        end

        if G.STATE == G.STATES.BLIND_SELECT then
            return "BLIND_SELECT"
        end

        if G.pack_cards and #G.pack_cards > 0 then
            return "PACK_OPENING"
        end

        -- Check for booster pack selection
        if G.STATE == G.STATES.PLANET_PACK or
           G.STATE == G.STATES.TAROT_PACK or
           G.STATE == G.STATES.SPECTRAL_PACK or
           G.STATE == G.STATES.STANDARD_PACK or
           G.STATE == G.STATES.BUFFOON_PACK then
            return "PACK_OPENING"
        end
    end

    -- Fallback: try to determine from state number
    if G.STATE then
        return "STATE_" .. tostring(G.STATE)
    end

    return "UNKNOWN"
end

-- Build complete game state
local function build_game_state()
    local state = {
        schema_version = CONFIG.schema_version,
        timestamp_ms = math.floor(socket.gettime() * 1000),
        phase = get_game_phase(),
    }

    -- Check if game is running
    if not G or not G.GAME then
        state.error = "Game not active"
        return state
    end

    local game = G.GAME

    -- Run metadata
    state.run_id = game.pseudorandom and game.pseudorandom.seed or "unknown"
    state.round = game.round or 0
    state.ante = game.round_resets and game.round_resets.ante or 0

    -- Resources
    state.money = game.dollars or 0
    state.hands_remaining = game.current_round and game.current_round.hands_left or 0
    state.discards_remaining = game.current_round and game.current_round.discards_left or 0

    -- Current blind info
    if game.blind then
        state.blind = {
            name = game.blind.name,
            chips_needed = game.blind.chips,
            chips_scored = game.chips or 0,
            boss = game.blind.boss or false,
            debuff_text = game.blind.debuff_text,
        }
    end

    -- Hand cards
    state.hand = {}
    if G.hand and G.hand.cards then
        for i, card in ipairs(G.hand.cards) do
            local card_data = extract_card(card)
            if card_data then
                card_data.hand_index = i
                state.hand[#state.hand + 1] = card_data
            end
        end
    end

    -- Jokers
    state.jokers = {}
    if G.jokers and G.jokers.cards then
        for i, joker in ipairs(G.jokers.cards) do
            local joker_data = extract_joker(joker)
            if joker_data then
                joker_data.joker_index = i
                state.jokers[#state.jokers + 1] = joker_data
            end
        end
    end

    -- Consumables
    state.consumables = {}
    if G.consumeables and G.consumeables.cards then
        for i, card in ipairs(G.consumeables.cards) do
            state.consumables[#state.consumables + 1] = {
                index = i,
                name = safe_get(card, "ability", "name") or safe_get(card, "label"),
                key = card.config and card.config.center and card.config.center.key,
            }
        end
    end

    -- Shop state
    if state.phase == "SHOP" and G.shop then
        state.shop = {
            items = {},
            reroll_cost = game.current_round and game.current_round.reroll_cost or 5,
        }
        if G.shop.cards then
            for i, card in ipairs(G.shop.cards) do
                state.shop.items[#state.shop.items + 1] = {
                    slot = i,
                    name = safe_get(card, "ability", "name") or safe_get(card, "label"),
                    cost = card.cost or 0,
                    type = card.ability and card.ability.set or "unknown",
                }
            end
        end
    end

    -- Pack opening state
    if state.phase == "PACK_OPENING" and G.pack_cards then
        state.pack = {
            cards = {}
        }
        for i, card in ipairs(G.pack_cards) do
            state.pack.cards[#state.pack.cards + 1] = {
                index = i,
                name = safe_get(card, "ability", "name") or safe_get(card, "label"),
            }
        end
    end

    -- Deck counts
    state.deck_counts = {
        deck_size = G.deck and G.deck.cards and #G.deck.cards or 0,
        discard_size = G.discard and G.discard.cards and #G.discard.cards or 0,
    }

    -- Played hand info
    if game.current_round then
        state.hands_played = game.current_round.hands_played or 0
    end

    -- Hand levels (poker hand upgrades)
    if game.hands then
        state.hand_levels = {}
        for hand_type, hand_info in pairs(game.hands) do
            if hand_info.level then
                state.hand_levels[hand_type] = {
                    level = hand_info.level,
                    mult = hand_info.mult,
                    chips = hand_info.chips,
                }
            end
        end
    end

    return state
end

--------------------------------------------------------------------------------
-- Legal Actions
--------------------------------------------------------------------------------

local function get_legal_actions()
    local legal = {
        schema_version = CONFIG.schema_version,
        phase = get_game_phase(),
        actions = {}
    }

    if not G or not G.GAME then
        legal.error = "Game not active"
        return legal
    end

    local phase = legal.phase
    local game = G.GAME

    if phase == "SELECTING_HAND" then
        -- Can play or discard cards
        local hand_indices = {}
        if G.hand and G.hand.cards then
            for i = 1, #G.hand.cards do
                hand_indices[#hand_indices + 1] = i
            end
        end

        local hands_left = game.current_round and game.current_round.hands_left or 0
        local discards_left = game.current_round and game.current_round.discards_left or 0

        if hands_left > 0 and #hand_indices > 0 then
            legal.actions[#legal.actions + 1] = {
                type = "PLAY_HAND",
                description = "Play selected cards as a poker hand",
                params = {
                    card_indices = {
                        available = hand_indices,
                        min_select = 1,
                        max_select = 5,
                    }
                }
            }
        end

        if discards_left > 0 and #hand_indices > 0 then
            legal.actions[#legal.actions + 1] = {
                type = "DISCARD",
                description = "Discard selected cards",
                params = {
                    card_indices = {
                        available = hand_indices,
                        min_select = 1,
                        max_select = 5,
                    }
                }
            }
        end

        -- Sort hand options
        legal.actions[#legal.actions + 1] = {
            type = "SORT_HAND",
            description = "Sort hand by rank or suit",
            params = {
                mode = {"rank", "suit"}
            }
        }

    elseif phase == "SHOP" then
        -- Shop actions
        local money = game.dollars or 0
        local reroll_cost = game.current_round and game.current_round.reroll_cost or 5

        -- Buy items
        if G.shop and G.shop.cards then
            for i, card in ipairs(G.shop.cards) do
                local cost = card.cost or 0
                if cost <= money then
                    legal.actions[#legal.actions + 1] = {
                        type = "SHOP_BUY",
                        description = "Buy item from shop",
                        params = {
                            slot = i,
                            cost = cost,
                        }
                    }
                end
            end
        end

        -- Reroll
        if reroll_cost <= money then
            legal.actions[#legal.actions + 1] = {
                type = "SHOP_REROLL",
                description = "Reroll shop items",
                params = {
                    cost = reroll_cost,
                }
            }
        end

        -- Sell jokers
        if G.jokers and G.jokers.cards then
            for i, joker in ipairs(G.jokers.cards) do
                legal.actions[#legal.actions + 1] = {
                    type = "SHOP_SELL_JOKER",
                    description = "Sell a joker",
                    params = {
                        joker_index = i,
                        sell_value = joker.sell_cost or 0,
                    }
                }
            end
        end

        -- End shop / next round
        legal.actions[#legal.actions + 1] = {
            type = "SHOP_END",
            description = "Leave shop and continue to next round",
            params = {}
        }

    elseif phase == "BLIND_SELECT" then
        -- Blind selection actions
        legal.actions[#legal.actions + 1] = {
            type = "SELECT_BLIND",
            description = "Select a blind to play",
            params = {
                options = {"small", "big", "boss"}
            }
        }

        -- Skip blind (if tag allows)
        legal.actions[#legal.actions + 1] = {
            type = "SKIP_BLIND",
            description = "Skip the current blind (uses tag)",
            params = {}
        }

    elseif phase == "PACK_OPENING" then
        -- Pack card selection
        if G.pack_cards then
            for i = 1, #G.pack_cards do
                legal.actions[#legal.actions + 1] = {
                    type = "SELECT_PACK_ITEM",
                    description = "Select card from pack",
                    params = {
                        choice_index = i,
                    }
                }
            end
        end

        -- Skip pack
        legal.actions[#legal.actions + 1] = {
            type = "SKIP_PACK",
            description = "Skip pack selection",
            params = {}
        }
    end

    return legal
end

--------------------------------------------------------------------------------
-- Action Execution
--------------------------------------------------------------------------------

local function execute_action(action_data)
    if not action_data or not action_data.type then
        return {ok = false, error = "Invalid action: missing type"}
    end

    local action_type = action_data.type
    local params = action_data.params or {}

    if not G or not G.GAME then
        return {ok = false, error = "Game not active"}
    end

    local result = {ok = false}

    if action_type == "PLAY_HAND" then
        -- Select and play cards
        local indices = params.card_indices or {}
        if #indices == 0 or #indices > 5 then
            return {ok = false, error = "Must select 1-5 cards"}
        end

        -- Highlight the selected cards
        if G.hand and G.hand.cards then
            -- First unhighlight all
            for _, card in ipairs(G.hand.cards) do
                card.highlighted = false
            end
            -- Highlight selected
            for _, idx in ipairs(indices) do
                if G.hand.cards[idx] then
                    G.hand.cards[idx].highlighted = true
                end
            end
        end

        -- Trigger play action
        if G.FUNCS and G.FUNCS.play_cards_from_highlighted then
            G.FUNCS.play_cards_from_highlighted()
            result.ok = true
        elseif G.play_button and G.play_button.config and G.play_button.config.button then
            -- Try clicking play button programmatically
            G.FUNCS[G.play_button.config.button](G.play_button)
            result.ok = true
        else
            result.error = "Cannot find play function"
        end

    elseif action_type == "DISCARD" then
        -- Select and discard cards
        local indices = params.card_indices or {}
        if #indices == 0 then
            return {ok = false, error = "Must select at least 1 card"}
        end

        -- Highlight the selected cards
        if G.hand and G.hand.cards then
            for _, card in ipairs(G.hand.cards) do
                card.highlighted = false
            end
            for _, idx in ipairs(indices) do
                if G.hand.cards[idx] then
                    G.hand.cards[idx].highlighted = true
                end
            end
        end

        -- Trigger discard action
        if G.FUNCS and G.FUNCS.discard_cards_from_highlighted then
            G.FUNCS.discard_cards_from_highlighted()
            result.ok = true
        else
            result.error = "Cannot find discard function"
        end

    elseif action_type == "SHOP_BUY" then
        local slot = params.slot
        if G.shop and G.shop.cards and G.shop.cards[slot] then
            local card = G.shop.cards[slot]
            if card.cost and card.cost <= (G.GAME.dollars or 0) then
                -- Try to buy the card
                if G.FUNCS and G.FUNCS.buy_from_shop then
                    G.FUNCS.buy_from_shop(card)
                    result.ok = true
                elseif card.click then
                    card:click()
                    result.ok = true
                else
                    result.error = "Cannot find buy function"
                end
            else
                result.error = "Not enough money"
            end
        else
            result.error = "Invalid shop slot"
        end

    elseif action_type == "SHOP_REROLL" then
        if G.FUNCS and G.FUNCS.reroll_shop then
            G.FUNCS.reroll_shop()
            result.ok = true
        else
            result.error = "Cannot find reroll function"
        end

    elseif action_type == "SHOP_SELL_JOKER" then
        local joker_idx = params.joker_index
        if G.jokers and G.jokers.cards and G.jokers.cards[joker_idx] then
            local joker = G.jokers.cards[joker_idx]
            if joker.sell_card then
                joker:sell_card()
                result.ok = true
            elseif G.FUNCS and G.FUNCS.sell_card then
                G.FUNCS.sell_card(joker)
                result.ok = true
            else
                result.error = "Cannot find sell function"
            end
        else
            result.error = "Invalid joker index"
        end

    elseif action_type == "SHOP_END" then
        if G.FUNCS and G.FUNCS.toggle_shop then
            G.FUNCS.toggle_shop()
            result.ok = true
        elseif G.shop and G.shop.toggle then
            G.shop:toggle()
            result.ok = true
        else
            result.error = "Cannot find shop exit function"
        end

    elseif action_type == "SORT_HAND" then
        local mode = params.mode or "rank"
        if G.FUNCS and G.FUNCS.sort_hand_suit and G.FUNCS.sort_hand_value then
            if mode == "suit" then
                G.FUNCS.sort_hand_suit()
            else
                G.FUNCS.sort_hand_value()
            end
            result.ok = true
        else
            result.error = "Cannot find sort function"
        end

    elseif action_type == "SELECT_PACK_ITEM" then
        local idx = params.choice_index
        if G.pack_cards and G.pack_cards[idx] then
            local card = G.pack_cards[idx]
            if card.click then
                card:click()
                result.ok = true
            else
                result.error = "Cannot click pack card"
            end
        else
            result.error = "Invalid pack index"
        end

    elseif action_type == "SKIP_PACK" then
        if G.FUNCS and G.FUNCS.skip_booster then
            G.FUNCS.skip_booster()
            result.ok = true
        else
            result.error = "Cannot find skip function"
        end

    else
        result.error = "Unknown action type: " .. tostring(action_type)
    end

    -- Attach new state after action
    if result.ok then
        -- Small delay might be needed for state to update
        result.state = build_game_state()
        result.legal = get_legal_actions()
    end

    return result
end

--------------------------------------------------------------------------------
-- HTTP Request Handlers
--------------------------------------------------------------------------------

local handlers = {}

function handlers.GET_health(req)
    local uptime = start_time and math.floor((socket.gettime() - start_time) * 1000) or 0
    return {
        status = "ok",
        version = CONFIG.schema_version,
        uptime_ms = uptime,
        request_count = request_count,
        error_count = error_count,
        last_error = last_error,
    }
end

function handlers.GET_state(req)
    return build_game_state()
end

function handlers.GET_legal(req)
    return get_legal_actions()
end

function handlers.POST_action(req)
    local action_data = req.body and json_decode(req.body)
    if not action_data then
        return {ok = false, error = "Invalid JSON body"}
    end
    return execute_action(action_data)
end

function handlers.POST_reset(req)
    -- Reset is tricky - may need to restart run
    -- For now, provide instructions
    return {
        ok = false,
        error = "Reset not fully implemented - please restart run manually",
        hint = "Press Escape > Abandon Run > Start New Run"
    }
end

function handlers.POST_config(req)
    local config_data = req.body and json_decode(req.body)
    if config_data then
        if config_data.port then
            -- Would need to restart server - just acknowledge for now
            log_info("Port change requested to " .. config_data.port .. " (requires restart)")
        end
    end
    return {
        current_config = CONFIG
    }
end

function handlers.OPTIONS_any(req)
    -- CORS preflight
    return {}
end

--------------------------------------------------------------------------------
-- Main Server Loop
--------------------------------------------------------------------------------

local pending_clients = {}

local function handle_request(client)
    -- Set timeout for read
    client:settimeout(0.001)

    local data, err, partial = client:receive(CONFIG.max_request_size)
    data = data or partial

    if not data or #data == 0 then
        return false
    end

    request_count = request_count + 1

    local req = parse_http_request(data)
    if not req then
        send_json(client, 400, {error = "Invalid HTTP request"})
        return true
    end

    local path = req.path:match("^([^?]+)") or req.path
    path = path:gsub("^/+", "")  -- Remove leading slashes

    -- Route to handler
    local handler_name = req.method .. "_" .. path
    local handler = handlers[handler_name]

    -- Try OPTIONS handler for CORS
    if not handler and req.method == "OPTIONS" then
        handler = handlers.OPTIONS_any
    end

    if handler then
        local ok, result = pcall(handler, req)
        if ok then
            send_json(client, 200, result)
        else
            log_error("Handler error: " .. tostring(result))
            send_json(client, 500, {error = "Internal server error", details = tostring(result)})
        end
    else
        send_json(client, 404, {error = "Not found", path = path, method = req.method})
    end

    return true
end

local function server_tick()
    if not server then return end

    -- Accept new connections (non-blocking)
    local client, err = server:accept()
    if client then
        client:settimeout(0)
        pending_clients[#pending_clients + 1] = {
            socket = client,
            time = socket.gettime()
        }
    end

    -- Process pending clients
    local i = 1
    while i <= #pending_clients do
        local pc = pending_clients[i]
        local done = false
        local timeout = (socket.gettime() - pc.time) > 5  -- 5 second timeout

        if timeout then
            pc.socket:close()
            done = true
        else
            local ok, result = pcall(handle_request, pc.socket)
            if not ok then
                log_error("Request handling error: " .. tostring(result))
                done = true
            elseif result then
                pc.socket:close()
                done = true
            end
        end

        if done then
            table.remove(pending_clients, i)
        else
            i = i + 1
        end
    end
end

--------------------------------------------------------------------------------
-- Initialization
--------------------------------------------------------------------------------

function RLBridge.init()
    log_info("Initializing RL Bridge...")

    -- Create TCP server
    server = socket.tcp()
    if not server then
        log_error("Failed to create TCP socket")
        return false
    end

    server:setoption("reuseaddr", true)

    local ok, err = server:bind(CONFIG.host, CONFIG.port)
    if not ok then
        log_error("Failed to bind to " .. CONFIG.host .. ":" .. CONFIG.port .. " - " .. tostring(err))
        server:close()
        server = nil
        return false
    end

    ok, err = server:listen(5)
    if not ok then
        log_error("Failed to listen: " .. tostring(err))
        server:close()
        server = nil
        return false
    end

    server:settimeout(0)  -- Non-blocking
    start_time = socket.gettime()

    log_info("HTTP server started on http://" .. CONFIG.host .. ":" .. CONFIG.port)
    log_info("Endpoints: /health, /state, /legal, /action, /reset, /config")

    return true
end

function RLBridge.update(dt)
    server_tick()
end

function RLBridge.shutdown()
    if server then
        server:close()
        server = nil
        log_info("HTTP server stopped")
    end
end

--------------------------------------------------------------------------------
-- Steamodded Integration
--------------------------------------------------------------------------------

-- Register with Steamodded
SMODS.current_mod.config_tab = function()
    return {n = G.UIT.ROOT, config = {colour = G.C.BLACK, padding = 0.1}, nodes = {
        {n = G.UIT.T, config = {text = "RL Bridge running on port " .. CONFIG.port, colour = G.C.WHITE, scale = 0.4}}
    }}
end

-- Hook into game update loop
local original_update = love.update
love.update = function(dt)
    if original_update then original_update(dt) end
    RLBridge.update(dt)
end

-- Initialize on load
RLBridge.init()

return RLBridge
