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
    -- Find the header/body separator
    local header_end = data:find("\r\n\r\n")
    if not header_end then
        -- No complete headers yet
        return nil
    end

    local header_part = data:sub(1, header_end - 1)
    local body = data:sub(header_end + 4)  -- Skip \r\n\r\n

    -- Parse header lines
    local lines = {}
    for line in header_part:gmatch("[^\r\n]+") do
        lines[#lines + 1] = line
    end

    if #lines < 1 then return nil end

    local method, path, version = lines[1]:match("^(%w+)%s+([^%s]+)%s+HTTP/([%d%.]+)")
    if not method then return nil end

    local headers = {}
    for i = 2, #lines do
        local line = lines[i]
        local key, value = line:match("^([^:]+):%s*(.*)$")
        if key then
            headers[key:lower()] = value
        end
    end

    -- If body is empty string, set to nil for consistency
    if body == "" then body = nil end

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

-- Extract a card from a shop area (jokers, vouchers, boosters)
local function extract_shop_card(card, index)
    if not card then return nil end

    local card_type = "unknown"
    if card.ability and card.ability.set then
        card_type = card.ability.set
    elseif card.config and card.config.center and card.config.center.set then
        card_type = card.config.center.set
    end

    local key = nil
    if card.config and card.config.center then
        key = card.config.center.key or card.config.center_key
    end

    return {
        index = index,
        name = safe_get(card, "ability", "name") or safe_get(card, "label") or "Unknown",
        key = key,
        cost = card.cost or 0,
        type = card_type,
        edition = card.edition and (
            card.edition.foil and "foil" or
            card.edition.holo and "holo" or
            card.edition.polychrome and "polychrome" or
            card.edition.negative and "negative" or nil
        ) or nil,
        sell_cost = card.sell_cost or 0,
        ability = card.ability,
    }
end

-- Extract cards from a CardArea (shop areas, pack cards, etc.)
local function extract_cards_from_area(area, extractor)
    local result = {}
    if area and area.cards then
        for i, card in ipairs(area.cards) do
            local data = extractor(card, i)
            if data then
                result[#result + 1] = data
            end
        end
    end
    return result
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

    if G.GAME then
        -- Pack opening states (check before SHOP since packs open from shop)
        if G.STATE == G.STATES.TAROT_PACK or
           G.STATE == G.STATES.PLANET_PACK or
           G.STATE == G.STATES.SPECTRAL_PACK or
           G.STATE == G.STATES.STANDARD_PACK or
           G.STATE == G.STATES.BUFFOON_PACK or
           G.STATE == 999 then -- SMODS_BOOSTER_OPENED
            return "PACK_OPENING"
        end

        if G.STATE == G.STATES.SHOP then
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

        if G.STATE == G.STATES.GAME_OVER then
            return "GAME_OVER"
        end

        if G.STATE == G.STATES.ROUND_EVAL or G.STATE == G.STATES.NEW_ROUND then
            return "ROUND_EVAL"
        end

        if G.STATE == G.STATES.NEW_ROUND then
            return "NEW_ROUND"
        end

        if G.STATE == G.STATES.PLAY_TAROT then
            return "PLAY_TAROT"
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
            local card_type = nil
            if card.ability and card.ability.set then
                card_type = card.ability.set
            elseif card.config and card.config.center and card.config.center.set then
                card_type = card.config.center.set
            end

            local can_use = false
            if card.can_use_consumeable then
                local ok_check, use_result = pcall(function() return card:can_use_consumeable(card) end)
                if ok_check then can_use = use_result end
            end

            state.consumables[#state.consumables + 1] = {
                index = i,
                name = safe_get(card, "ability", "name") or safe_get(card, "label"),
                key = card.config and card.config.center and card.config.center.key,
                type = card_type,
                can_use = can_use,
                ability = card.ability,
            }
        end
    end

    -- Shop state (three separate card areas)
    if state.phase == "SHOP" then
        state.shop = {
            jokers = extract_cards_from_area(G.shop_jokers, extract_shop_card),
            vouchers = extract_cards_from_area(G.shop_vouchers, extract_shop_card),
            boosters = extract_cards_from_area(G.shop_booster, extract_shop_card),
            reroll_cost = game.current_round and game.current_round.reroll_cost or 5,
        }
    end

    -- Pack opening state
    if state.phase == "PACK_OPENING" and G.pack_cards and G.pack_cards.cards then
        state.pack = {
            cards = {},
            choices_remaining = game.pack_choices or 1,
        }
        for i, card in ipairs(G.pack_cards.cards) do
            local pack_card = {
                index = i,
                name = safe_get(card, "ability", "name") or safe_get(card, "label"),
                key = card.config and card.config.center and card.config.center.key,
                type = card.ability and card.ability.set or (card.config and card.config.center and card.config.center.set) or "unknown",
                facing = card.facing or "back",
            }
            -- For playing cards (standard packs), include suit/rank/enhancements
            if pack_card.type == "Default" or pack_card.type == "Enhanced" then
                pack_card.suit = safe_get(card, "base", "suit")
                pack_card.rank = safe_get(card, "base", "value") or safe_get(card, "base", "nominal")
                if card.edition then
                    if card.edition.foil then pack_card.edition = "foil"
                    elseif card.edition.holo then pack_card.edition = "holo"
                    elseif card.edition.polychrome then pack_card.edition = "polychrome"
                    end
                end
                if card.ability and card.ability.name then
                    pack_card.enhancement = card.ability.name
                end
                if card.seal then pack_card.seal = card.seal end
            end
            state.pack.cards[#state.pack.cards + 1] = pack_card
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

        -- Use consumable (tarots/planets/spectrals)
        if G.consumeables and G.consumeables.cards then
            for i, card in ipairs(G.consumeables.cards) do
                local can_use = false
                if card.can_use_consumeable then
                    local ok_check, use_result = pcall(function() return card:can_use_consumeable(card) end)
                    if ok_check then can_use = use_result end
                end
                if can_use then
                    legal.actions[#legal.actions + 1] = {
                        type = "USE_CONSUMABLE",
                        description = "Use " .. (safe_get(card, "ability", "name") or "consumable"),
                        params = {
                            index = i,
                        }
                    }
                end
            end
        end

    elseif phase == "SHOP" then
        -- Shop actions
        local money = game.dollars or 0
        local reroll_cost = game.current_round and game.current_round.reroll_cost or 5

        -- Buy from joker/consumable area
        if G.shop_jokers and G.shop_jokers.cards then
            for i, card in ipairs(G.shop_jokers.cards) do
                local cost = card.cost or 0
                if cost <= money then
                    legal.actions[#legal.actions + 1] = {
                        type = "SHOP_BUY",
                        description = "Buy " .. (safe_get(card, "ability", "name") or "item") .. " from shop",
                        params = {
                            slot = i,
                            cost = cost,
                        }
                    }
                end
            end
        end

        -- Buy voucher
        if G.shop_vouchers and G.shop_vouchers.cards then
            for i, card in ipairs(G.shop_vouchers.cards) do
                local cost = card.cost or 0
                if cost <= money then
                    legal.actions[#legal.actions + 1] = {
                        type = "SHOP_BUY_VOUCHER",
                        description = "Buy voucher: " .. (safe_get(card, "ability", "name") or "voucher"),
                        params = {
                            slot = i,
                            cost = cost,
                        }
                    }
                end
            end
        end

        -- Buy booster pack
        if G.shop_booster and G.shop_booster.cards then
            for i, card in ipairs(G.shop_booster.cards) do
                local cost = card.cost or 0
                if cost <= money then
                    legal.actions[#legal.actions + 1] = {
                        type = "SHOP_BUY_BOOSTER",
                        description = "Buy booster: " .. (safe_get(card, "ability", "name") or "pack"),
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
                    description = "Sell joker: " .. (safe_get(joker, "ability", "name") or "joker"),
                    params = {
                        joker_index = i,
                        sell_value = joker.sell_cost or 0,
                    }
                }
            end
        end

        -- Use consumable (tarots/planets/spectrals from consumable slots)
        if G.consumeables and G.consumeables.cards then
            for i, card in ipairs(G.consumeables.cards) do
                local can_use = false
                if card.can_use_consumeable then
                    local ok_check, use_result = pcall(function() return card:can_use_consumeable(card) end)
                    if ok_check then can_use = use_result end
                end
                if can_use then
                    legal.actions[#legal.actions + 1] = {
                        type = "USE_CONSUMABLE",
                        description = "Use " .. (safe_get(card, "ability", "name") or "consumable"),
                        params = {
                            index = i,
                        }
                    }
                end
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
        local choices_remaining = game.pack_choices or 1
        if G.pack_cards and G.pack_cards.cards and choices_remaining > 0 then
            for i, card in ipairs(G.pack_cards.cards) do
                legal.actions[#legal.actions + 1] = {
                    type = "SELECT_PACK_CARD",
                    description = "Select " .. (safe_get(card, "ability", "name") or safe_get(card, "label") or "card") .. " from pack",
                    params = {
                        index = i,
                    }
                }
            end
        end

        -- Skip pack
        legal.actions[#legal.actions + 1] = {
            type = "SKIP_PACK",
            description = "Skip remaining pack choices",
            params = {}
        }

    elseif phase == "ROUND_EVAL" then
        -- After winning a round the player must cash out to proceed to shop
        legal.actions[#legal.actions + 1] = {
            type = "CASH_OUT",
            description = "Cash out and proceed to shop",
            params = {}
        }

    elseif phase == "MENU" then
        -- Can start a new run from the menu
        legal.actions[#legal.actions + 1] = {
            type = "START_RUN",
            description = "Start a new run with default settings (stake 1, Red Deck)",
            params = {
                stake = 1,
            }
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

    if action_type == "SELECT_CARDS" then
        -- Select/highlight cards in hand without playing or discarding.
        local indices = params.card_indices or {}

        if not G.hand or not G.hand.cards then
            return {ok = false, error = "No hand available"}
        end

        -- Deselect all cards first
        for _, card in ipairs(G.hand.cards) do
            if card.highlighted then
                card:click()
            end
        end

        -- Select the specified cards
        local selected = {}
        for _, idx in ipairs(indices) do
            if G.hand.cards[idx] then
                if not G.hand.cards[idx].highlighted then
                    G.hand.cards[idx]:click()
                end
                selected[#selected + 1] = idx
            end
        end

        result.ok = true
        result.message = "Cards selected"
        result.cards_highlighted = selected

    elseif action_type == "PLAY_HAND" then
        -- Select cards and play them as a poker hand.
        local indices = params.card_indices or {}
        if #indices == 0 or #indices > 5 then
            return {ok = false, error = "Must select 1-5 cards"}
        end

        if not G.hand or not G.hand.cards then
            return {ok = false, error = "No hand available"}
        end

        -- Deselect all currently highlighted cards
        for _, card in ipairs(G.hand.cards) do
            if card.highlighted then
                card:click()
            end
        end

        -- Highlight the selected cards
        for _, idx in ipairs(indices) do
            if G.hand.cards[idx] and not G.hand.cards[idx].highlighted then
                G.hand.cards[idx]:click()
            end
        end

        -- Validate selection happened
        if #G.hand.highlighted == 0 then
            return {ok = false, error = "No cards were highlighted after selection"}
        end

        -- Play the hand
        if G.FUNCS.play_cards_from_highlighted then
            local ok, err = pcall(G.FUNCS.play_cards_from_highlighted, nil)
            if ok then
                result.ok = true
                result.message = "Hand played"
            else
                log_error("play_cards_from_highlighted failed: " .. tostring(err))
                result.error = "play_cards_from_highlighted failed: " .. tostring(err)
            end
        else
            result.error = "play_cards_from_highlighted function not available"
        end

    elseif action_type == "DISCARD" then
        -- Select cards and discard them.
        local indices = params.card_indices or {}
        if #indices == 0 then
            return {ok = false, error = "Must select at least 1 card"}
        end

        if not G.hand or not G.hand.cards then
            return {ok = false, error = "No hand available"}
        end

        -- Deselect all currently highlighted cards
        for _, card in ipairs(G.hand.cards) do
            if card.highlighted then
                card:click()
            end
        end

        -- Highlight the discard cards
        for _, idx in ipairs(indices) do
            if G.hand.cards[idx] and not G.hand.cards[idx].highlighted then
                G.hand.cards[idx]:click()
            end
        end

        -- Validate selection happened
        if #G.hand.highlighted == 0 then
            return {ok = false, error = "No cards were highlighted after selection"}
        end

        -- Discard the hand
        if G.FUNCS.discard_cards_from_highlighted then
            local ok, err = pcall(G.FUNCS.discard_cards_from_highlighted, nil)
            if ok then
                result.ok = true
                result.message = "Cards discarded"
            else
                log_error("discard_cards_from_highlighted failed: " .. tostring(err))
                result.error = "discard_cards_from_highlighted failed: " .. tostring(err)
            end
        else
            result.error = "discard_cards_from_highlighted function not available"
        end

    elseif action_type == "SHOP_BUY" then
        local slot = params.slot
        if G.shop_jokers and G.shop_jokers.cards and G.shop_jokers.cards[slot] then
            local card = G.shop_jokers.cards[slot]
            if card.cost and card.cost <= (G.GAME.dollars or 0) then
                if G.FUNCS and G.FUNCS.buy_from_shop then
                    -- Debug: log what we're passing
                    local is_card = card and card.is and card:is(Card)
                    local has_space = is_card and G.FUNCS.check_for_buy_space and G.FUNCS.check_for_buy_space(card)
                    log_info("SHOP_BUY slot=" .. slot .. " is_Card=" .. tostring(is_card) .. " has_space=" .. tostring(has_space) .. " jokers=" .. tostring(G.jokers and #G.jokers.cards) .. "/" .. tostring(G.jokers and G.jokers.config.card_limit))
                    local fake_e = {config = {ref_table = card}}
                    local ok, buy_result = pcall(G.FUNCS.buy_from_shop, fake_e)
                    if ok and buy_result ~= false then
                        result.ok = true
                        result.message = "Bought from shop slot " .. slot
                    elseif ok and buy_result == false then
                        result.error = "buy_from_shop returned false: no space or card not purchasable"
                    else
                        log_error("buy_from_shop failed: " .. tostring(buy_result))
                        result.error = "buy_from_shop failed: " .. tostring(buy_result)
                    end
                else
                    result.error = "buy_from_shop function not available"
                end
            else
                result.error = "Not enough money"
            end
        else
            result.error = "Invalid shop joker slot"
        end

    elseif action_type == "SHOP_BUY_VOUCHER" then
        -- Vouchers use use_card (which calls card:redeem()), not buy_from_shop
        local slot = params.slot
        if G.shop_vouchers and G.shop_vouchers.cards and G.shop_vouchers.cards[slot] then
            local card = G.shop_vouchers.cards[slot]
            if card.cost and card.cost <= (G.GAME.dollars or 0) then
                if G.FUNCS and G.FUNCS.use_card then
                    local fake_e = {config = {ref_table = card}}
                    local ok, err = pcall(G.FUNCS.use_card, fake_e)
                    if ok then
                        result.ok = true
                        result.message = "Redeemed voucher from slot " .. slot
                    else
                        log_error("use_card (voucher) failed: " .. tostring(err))
                        result.error = "use_card (voucher) failed: " .. tostring(err)
                    end
                else
                    result.error = "use_card function not available"
                end
            else
                result.error = "Not enough money"
            end
        else
            result.error = "Invalid voucher slot"
        end

    elseif action_type == "SHOP_BUY_BOOSTER" then
        -- Boosters use use_card (which calls card:open()), not buy_from_shop
        local slot = params.slot
        if G.shop_booster and G.shop_booster.cards and G.shop_booster.cards[slot] then
            local card = G.shop_booster.cards[slot]
            if card.cost and card.cost <= (G.GAME.dollars or 0) then
                if G.FUNCS and G.FUNCS.use_card then
                    local fake_e = {config = {ref_table = card}}
                    local ok, err = pcall(G.FUNCS.use_card, fake_e)
                    if ok then
                        result.ok = true
                        result.message = "Opened booster from slot " .. slot
                    else
                        log_error("use_card (booster) failed: " .. tostring(err))
                        result.error = "use_card (booster) failed: " .. tostring(err)
                    end
                else
                    result.error = "use_card function not available"
                end
            else
                result.error = "Not enough money"
            end
        else
            result.error = "Invalid booster slot"
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

    elseif action_type == "SELECT_PACK_CARD" then
        local idx = params.index
        if G.pack_cards and G.pack_cards.cards and G.pack_cards.cards[idx] then
            local card = G.pack_cards.cards[idx]
            -- Highlight the card, then trigger use
            if not card.highlighted then
                card:click()
            end
            if G.FUNCS and G.FUNCS.use_card then
                local fake_e = {config = {ref_table = card}}
                local ok, err = pcall(G.FUNCS.use_card, fake_e, false, true)
                if ok then
                    result.ok = true
                    result.message = "Selected pack card " .. idx
                else
                    log_error("use_card (pack) failed: " .. tostring(err))
                    result.error = "use_card (pack) failed: " .. tostring(err)
                end
            elseif card.click then
                card:click()
                result.ok = true
                result.message = "Clicked pack card " .. idx
            else
                result.error = "Cannot select pack card"
            end
        else
            result.error = "Invalid pack card index"
        end

    -- Keep legacy alias for backward compat
    elseif action_type == "SELECT_PACK_ITEM" then
        local idx = params.choice_index or params.index
        if G.pack_cards and G.pack_cards.cards and G.pack_cards.cards[idx] then
            local card = G.pack_cards.cards[idx]
            if not card.highlighted then
                card:click()
            end
            if G.FUNCS and G.FUNCS.use_card then
                local fake_e = {config = {ref_table = card}}
                local ok, err = pcall(G.FUNCS.use_card, fake_e, false, true)
                if ok then
                    result.ok = true
                    result.message = "Selected pack item " .. idx
                else
                    log_error("use_card (pack legacy) failed: " .. tostring(err))
                    result.error = "use_card (pack legacy) failed: " .. tostring(err)
                end
            elseif card.click then
                card:click()
                result.ok = true
            else
                result.error = "Cannot select pack card"
            end
        else
            result.error = "Invalid pack index"
        end

    elseif action_type == "SKIP_PACK" then
        if G.FUNCS and G.FUNCS.skip_booster then
            local fake_e = {config = {ref_table = G.pack_cards}}
            local ok, err = pcall(G.FUNCS.skip_booster, fake_e)
            if ok then
                result.ok = true
                result.message = "Pack skipped"
            else
                log_error("skip_booster failed: " .. tostring(err))
                result.error = "skip_booster failed: " .. tostring(err)
            end
        else
            result.error = "skip_booster function not available"
        end

    elseif action_type == "USE_CONSUMABLE" then
        local idx = params.index
        if G.consumeables and G.consumeables.cards and G.consumeables.cards[idx] then
            local card = G.consumeables.cards[idx]
            -- Check if the consumable can be used
            local can_use = false
            if card.can_use_consumeable then
                local ok_check, use_result = pcall(function() return card:can_use_consumeable(card) end)
                if ok_check then can_use = use_result end
            end
            if not can_use then
                result.error = "Consumable cannot be used right now (may need target cards selected)"
                return result
            end
            -- Use the consumable
            if G.FUNCS and G.FUNCS.use_card then
                local fake_e = {config = {ref_table = card}}
                local ok, err = pcall(G.FUNCS.use_card, fake_e)
                if ok then
                    result.ok = true
                    result.message = "Used consumable " .. (safe_get(card, "ability", "name") or tostring(idx))
                else
                    log_error("use_card (consumable) failed: " .. tostring(err))
                    result.error = "use_card (consumable) failed: " .. tostring(err)
                end
            else
                result.error = "use_card function not available"
            end
        else
            result.error = "Invalid consumable index"
        end

    elseif action_type == "START_RUN" then
        -- Start a new run from the menu
        if G.FUNCS and G.FUNCS.start_run then
            local stake = params.stake or 1
            local ok, err = pcall(function()
                G.FUNCS.start_run(nil, {stake = stake})
            end)
            if ok then
                result.ok = true
                result.message = "New run started with stake " .. tostring(stake)
            else
                log_error("start_run failed: " .. tostring(err))
                result.error = "start_run failed: " .. tostring(err)
            end
        else
            result.error = "start_run function not available"
        end

    elseif action_type == "SELECT_BLIND" then
        -- Select a blind to play (small, big, or boss).
        -- Use fake_e with G.P_BLINDS ref_table directly — avoids get_UIE_by_ID which
        -- fails for Boss blind (different UIBox structure). select_blind(e) reads:
        --   e.config.ref_table  → the blind config object
        --   e.UIBox:get_UIE_by_ID('tag_container') → optional tag (we return nil = no tag)
        if G.FUNCS and G.FUNCS.select_blind then
            local blind_on_deck = G.GAME and G.GAME.blind_on_deck  -- 'Small', 'Big', or 'Boss'
            if not blind_on_deck then
                -- BLIND_SELECT state is initializing; blind_on_deck isn't set yet. Retry.
                return {ok = false, error = "blind_on_deck not set yet, retry"}
            end
            local blind_choices = G.GAME and G.GAME.round_resets and G.GAME.round_resets.blind_choices
            local blind_key = blind_choices and blind_choices[blind_on_deck]
            local blind_cfg = blind_key and G.P_BLINDS and G.P_BLINDS[blind_key]
            if blind_cfg then
                local fake_e = {
                    config = {ref_table = blind_cfg},
                    UIBox = {get_UIE_by_ID = function() return nil end}
                }
                local ok, err = pcall(G.FUNCS.select_blind, fake_e)
                if ok then
                    result.ok = true
                    result.message = "Selected " .. tostring(blind_on_deck) .. " blind"
                else
                    log_error("select_blind failed: " .. tostring(err))
                    result.error = "select_blind failed: " .. tostring(err)
                end
            else
                result.error = "Could not resolve blind config for " .. tostring(blind_on_deck)
                    .. " (blind_key=" .. tostring(blind_key) .. ")"
            end
        else
            result.error = "select_blind function not available"
        end

    elseif action_type == "SKIP_BLIND" then
        -- Skip the current blind
        if G.FUNCS and G.FUNCS.skip_blind then
            local ok, err = pcall(function()
                G.FUNCS.skip_blind({config = {}})
            end)
            if ok then
                result.ok = true
                result.message = "Blind skipped"
            else
                log_error("skip_blind failed: " .. tostring(err))
                result.error = "skip_blind failed: " .. tostring(err)
            end
        else
            result.error = "skip_blind function not available"
        end

    elseif action_type == "CASH_OUT" then
        -- Guard: wait until it is safe to call cash_out.
        -- cash_out adds [delay(0.3), remove_round_eval] to the queue. If evaluate_round's
        -- row events are still pending, they'll be queued AFTER remove_round_eval and crash.
        -- Safe condition: no incomplete blocking events in the queue.
        --   - animation-wait event (blocking, fires evaluate_round): if still pending → not safe
        --   - row events from evaluate_round (blocking): if still pending → not safe
        --   - persistent non-blocking event from game.lua: always present, never blocks → safe
        -- Note: 'before' events with complete=true are just timing out → safe to proceed.
        if not G.round_eval then
            return {ok = false, error = "Round eval UI not ready yet, retry shortly"}
        end
        if G.E_MANAGER then
            local has_pending_blocking = false
            for _, ev in ipairs(G.E_MANAGER.queues.base) do
                if ev.blocking and not ev.complete then
                    has_pending_blocking = true
                    break
                end
            end
            if has_pending_blocking then
                return {ok = false, error = "Round eval blocking events still pending, retry shortly"}
            end
        end
        -- Cash out after winning a round to proceed to the shop
        if G.FUNCS and G.FUNCS.cash_out then
            local ok, err = pcall(function()
                G.FUNCS.cash_out({config = {}})
            end)
            if ok then
                result.ok = true
                result.message = "Cashed out"
            else
                log_error("cash_out failed: " .. tostring(err))
                result.error = "cash_out failed: " .. tostring(err)
            end
        else
            result.error = "cash_out function not available"
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

function handlers.GET_debug(req)
    -- Debug endpoint to list available G.FUNCS and game info
    local result = {
        g_funcs = {},
        state = nil,
        buttons = {},
    }

    -- List all G.FUNCS that might be relevant
    if G and G.FUNCS then
        for k, v in pairs(G.FUNCS) do
            if type(v) == "function" then
                result.g_funcs[#result.g_funcs + 1] = k
            end
        end
        table.sort(result.g_funcs)
    end

    -- Get current state info
    if G then
        result.state = G.STATE
        result.states = {}
        if G.STATES then
            for k, v in pairs(G.STATES) do
                result.states[k] = v
            end
        end
    end

    -- List buttons if available
    if G and G.buttons and G.buttons.cards then
        for i, btn in ipairs(G.buttons.cards) do
            if btn.config and btn.config.button then
                result.buttons[#result.buttons + 1] = {
                    index = i,
                    button = btn.config.button,
                    label = btn.config.label,
                }
            end
        end
    end

    return result
end

--------------------------------------------------------------------------------
-- Main Server Loop
--------------------------------------------------------------------------------

local pending_clients = {}

local function handle_request(client)
    -- Non-blocking read: all our requests are small and fit in a single TCP segment.
    -- settimeout(0) avoids blocking the game loop for up to 1 second.
    client:settimeout(0)

    local chunk, err, partial = client:receive(65536)
    local data = chunk or partial or ""

    if #data == 0 then
        return false
    end

    request_count = request_count + 1

    local req = parse_http_request(data)
    if not req then
        send_json(client, 400, {error = "Invalid HTTP request"})
        return true
    end

    -- Body is already included in the initial read for all our small payloads.
    -- No retry loop needed.

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

--------------------------------------------------------------------------------
-- Save Data Migration
-- Steamodded expects wins_by_key/losses_by_key in deck_usage and joker_usage,
-- but vanilla Balatro save data only has wins/losses (indexed by number).
-- Steamodded's convert_save_data() should handle this, but it may not run
-- before the run-setup UI accesses deck_usage.wins_by_key, causing a crash.
-- We ensure the fields exist as a safety net.
--------------------------------------------------------------------------------

local save_migration_done = false

local function ensure_save_data_migrated()
    if save_migration_done then return end
    if not G or not G.PROFILES or not G.SETTINGS or not G.SETTINGS.profile then return end
    local profile = G.PROFILES[G.SETTINGS.profile]
    if not profile then return end

    -- Migrate deck_usage
    if profile.deck_usage then
        for k, v in pairs(profile.deck_usage) do
            if not v.wins_by_key then v.wins_by_key = {} end
            if not v.losses_by_key then v.losses_by_key = {} end
        end
    end

    -- Migrate joker_usage
    if profile.joker_usage then
        for k, v in pairs(profile.joker_usage) do
            if not v.wins_by_key then v.wins_by_key = {} end
            if not v.losses_by_key then v.losses_by_key = {} end
        end
    end

    -- Call Steamodded's full migration if available (populates from wins/losses)
    if convert_save_data then
        local ok, err = pcall(convert_save_data)
        if not ok then
            log_error("convert_save_data failed: " .. tostring(err))
        end
    end

    save_migration_done = true
    log_info("Save data migration check completed")
end

local _wipe_off_patched = false

function RLBridge.update(dt)
    ensure_save_data_migrated()

    -- Completely replace wipe_off with a safe version.
    -- The original events access G.screenwipe by global name. If START_RUN is called
    -- twice, wipe_off fires twice: the first call's 1.1s event nils G.screenwipe, then
    -- the second call's events crash trying to access nil. Fix: capture the screenwipe
    -- object in a local variable at call time (sw/swcard) and use it directly in all
    -- event callbacks. The global G.screenwipe is only nil'd if it still points to sw.
    if not _wipe_off_patched and G and G.FUNCS and G.FUNCS.wipe_off then
        G.FUNCS.wipe_off = function()
            if not G.screenwipe then return end
            local sw = G.screenwipe      -- captured reference; used in place of G.screenwipe
            local swcard = G.screenwipecard
            G.E_MANAGER:add_event(Event({
                no_delete = true,
                func = function()
                    if sw.REMOVED then return true end
                    delay(0.3)
                    sw.children.particles.max = 0
                    G.E_MANAGER:add_event(Event({
                        trigger = 'ease', no_delete = true, blockable = false,
                        blocking = false, timer = 'REAL',
                        ref_table = sw.colours.black, ref_value = 4,
                        ease_to = 0, delay = 0.3, func = (function(t) return t end)
                    }))
                    G.E_MANAGER:add_event(Event({
                        trigger = 'ease', no_delete = true, blockable = false,
                        blocking = false, timer = 'REAL',
                        ref_table = sw.colours.white, ref_value = 4,
                        ease_to = 0, delay = 0.3, func = (function(t) return t end)
                    }))
                    return true
                end
            }))
            G.E_MANAGER:add_event(Event({
                trigger = 'after', delay = 0.55, no_delete = true,
                blocking = false, timer = 'REAL',
                func = function()
                    if sw.REMOVED then return true end
                    if swcard then swcard:start_dissolve({G.C.BLACK, G.C.ORANGE, G.C.GOLD, G.C.RED}) end
                    local text_el = sw:get_UIE_by_ID('text')
                    if text_el then
                        for k, v in ipairs(text_el.children) do
                            v.children[1].config.object:pop_out(4)
                        end
                    end
                    return true
                end
            }))
            G.E_MANAGER:add_event(Event({
                trigger = 'after', delay = 1.1, no_delete = true,
                blocking = false, timer = 'REAL',
                func = function()
                    if sw.REMOVED then return true end
                    sw.children.particles:remove()
                    sw:remove()
                    sw.children.particles = nil
                    -- Only nil the global if it still points to our screenwipe object.
                    -- If another START_RUN ran, G.screenwipe already points to a newer one.
                    if G.screenwipe == sw then G.screenwipe = nil end
                    if G.screenwipecard == swcard then G.screenwipecard = nil end
                    return true
                end
            }))
            G.E_MANAGER:add_event(Event({
                trigger = 'after', delay = 1.2, no_delete = true,
                blocking = true, timer = 'REAL',
                func = function() return true end
            }))
        end
        _wipe_off_patched = true
    end

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
