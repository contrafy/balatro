--- BalatroRLBridge: HTTP bridge + trajectory recorder for the Balatro RL harness.
---
--- Loaded by Lovely only (lovely.toml registers this file as the module `balatro_rl_bridge` and calls
--- `.update(dt)` once per frame from love.update). No Steamodded; game logic is vanilla.
--- The API, the /legal domain format, the settled predicate and the trajectory file format are
--- specified in docs/DATA_CONTRACT.md. Keep that file in sync with this one.

local socket = require("socket")

local RLBridge = {}

local BRIDGE_VERSION = "2.0.0"

local function env_or_nil(name)
    local v = os.getenv(name)
    if v == nil or v == "" then return nil end
    return v
end

local CONFIG = {
    host = "127.0.0.1",
    -- BALATRO_RL_PORT lets several game instances run side by side, each with its own bridge
    port = tonumber(os.getenv("BALATRO_RL_PORT") or "") or 7777,
    schema_version = "2.0.0",
    format_version = 1,
    data_dir = env_or_nil("BALATRO_RL_DATA_DIR"),
    git_sha = env_or_nil("BALATRO_RL_GIT_SHA"),
    -- Enables POST /debug/eval (test setup only). Any use taints the open trajectory.
    debug_eval = env_or_nil("BALATRO_RL_DEBUG") == "1",
}

-- Server state
local server = nil
local start_time = nil
local request_count = 0
local error_count = 0
local last_error = nil
local unlock_done = false

local function log(level, msg)
    print(string.format("[BalatroRLBridge][%s][%s] %s", os.date("%Y-%m-%d %H:%M:%S"), level, msg))
end
local function log_info(msg) log("INFO", msg) end
local function log_error(msg)
    log("ERROR", msg)
    error_count = error_count + 1
    last_error = msg
end

-- LOVE's socket.gettime() is not epoch-based here; anchor it to os.time() once for epoch milliseconds.
local EPOCH_BASE_MS, CLOCK_BASE = os.time() * 1000, socket.gettime()
local function now_ms() return math.floor(EPOCH_BASE_MS + (socket.gettime() - CLOCK_BASE) * 1000) end

--------------------------------------------------------------------------------
-- JSON
--------------------------------------------------------------------------------

-- Tables tagged with ARRAY_MT always encode as JSON arrays (so empty lists are [] not {}).
local ARRAY_MT = {}
local function arr(t) return setmetatable(t or {}, ARRAY_MT) end

local JSON_ESC = {['"'] = '\\"', ['\\'] = '\\\\', ['\n'] = '\\n', ['\r'] = '\\r', ['\t'] = '\\t'}
local function json_escape_char(c)
    return JSON_ESC[c] or string.format("\\u%04x", c:byte())
end

local function json_encode_value(val, depth)
    if depth > 40 then return '"[max depth]"' end
    local t = type(val)
    if t == "nil" then
        return "null"
    elseif t == "boolean" then
        return val and "true" or "false"
    elseif t == "number" then
        if val ~= val or val == math.huge or val == -math.huge then return "null" end
        -- %.0f, not %d: this LuaJIT's %d truncates to 32 bits (epoch ms would wrap)
        if val == math.floor(val) and math.abs(val) < 1e15 then return string.format("%.0f", val) end
        return string.format("%.14g", val)
    elseif t == "string" then
        return '"' .. val:gsub('[%c"\\]', json_escape_char) .. '"'
    elseif t == "table" then
        local parts = {}
        if getmetatable(val) == ARRAY_MT then
            for i = 1, #val do parts[i] = json_encode_value(val[i], depth + 1) end
            return "[" .. table.concat(parts, ",") .. "]"
        end
        local n, is_array = 0, true
        for k in pairs(val) do
            if type(k) ~= "number" or k < 1 or k ~= math.floor(k) then is_array = false; break end
            n = n + 1
        end
        if is_array and n > 0 then
            for i = 1, n do
                if val[i] == nil then is_array = false; break end
            end
        end
        if is_array and n > 0 then
            for i = 1, n do parts[i] = json_encode_value(val[i], depth + 1) end
            return "[" .. table.concat(parts, ",") .. "]"
        end
        -- Objects: keys sorted so files are byte-stable and diffable
        local keys = {}
        for k in pairs(val) do
            local kt = type(k)
            if kt == "string" or kt == "number" then keys[#keys + 1] = tostring(k) end
        end
        table.sort(keys)
        for i, ks in ipairs(keys) do
            local v = val[ks]
            if v == nil then v = val[tonumber(ks)] end
            parts[i] = json_encode_value(ks, depth + 1) .. ":" .. json_encode_value(v, depth + 1)
        end
        return "{" .. table.concat(parts, ",") .. "}"
    end
    return "null"
end

local function json_encode(val)
    local ok, result = pcall(json_encode_value, val, 0)
    if ok then return result end
    return '{"error":"json encoding failed"}'
end

local function utf8_char(cp)
    if cp < 0x80 then return string.char(cp) end
    if cp < 0x800 then return string.char(0xC0 + math.floor(cp / 0x40), 0x80 + cp % 0x40) end
    return string.char(0xE0 + math.floor(cp / 0x1000), 0x80 + math.floor(cp / 0x40) % 0x40, 0x80 + cp % 0x40)
end

local function json_decode(str)
    if not str or str == "" then return nil end
    local pos = 1
    local function ws()
        pos = str:find("[^ \t\n\r]", pos) or (#str + 1)
    end
    local parse_value
    local function parse_string()
        pos = pos + 1
        local buf = {}
        while pos <= #str do
            local c = str:sub(pos, pos)
            if c == '"' then
                pos = pos + 1
                return table.concat(buf)
            elseif c == "\\" then
                local e = str:sub(pos + 1, pos + 1)
                if e == "n" then buf[#buf + 1] = "\n"
                elseif e == "r" then buf[#buf + 1] = "\r"
                elseif e == "t" then buf[#buf + 1] = "\t"
                elseif e == "b" then buf[#buf + 1] = "\b"
                elseif e == "f" then buf[#buf + 1] = "\f"
                elseif e == "u" then
                    local hex = str:sub(pos + 2, pos + 5)
                    buf[#buf + 1] = utf8_char(tonumber(hex, 16) or 63)
                    pos = pos + 4
                else buf[#buf + 1] = e end
                pos = pos + 2
            else
                local s, e2 = str:find('^[^"\\]+', pos)
                buf[#buf + 1] = str:sub(s, e2)
                pos = e2 + 1
            end
        end
        error("Unterminated string")
    end
    parse_value = function()
        ws()
        local c = str:sub(pos, pos)
        if c == '"' then
            return parse_string()
        elseif c == "{" then
            pos = pos + 1
            local obj = {}
            ws()
            if str:sub(pos, pos) == "}" then pos = pos + 1; return obj end
            while true do
                ws()
                if str:sub(pos, pos) ~= '"' then error("Expected key") end
                local key = parse_string()
                ws()
                if str:sub(pos, pos) ~= ":" then error("Expected ':'") end
                pos = pos + 1
                obj[key] = parse_value()
                ws()
                local sep = str:sub(pos, pos)
                pos = pos + 1
                if sep == "}" then return obj end
                if sep ~= "," then error("Expected ',' or '}'") end
            end
        elseif c == "[" then
            pos = pos + 1
            local a = {}
            ws()
            if str:sub(pos, pos) == "]" then pos = pos + 1; return a end
            while true do
                a[#a + 1] = parse_value()
                ws()
                local sep = str:sub(pos, pos)
                pos = pos + 1
                if sep == "]" then return a end
                if sep ~= "," then error("Expected ',' or ']'") end
            end
        elseif str:sub(pos, pos + 3) == "true" then
            pos = pos + 4; return true
        elseif str:sub(pos, pos + 4) == "false" then
            pos = pos + 5; return false
        elseif str:sub(pos, pos + 3) == "null" then
            pos = pos + 4; return nil
        else
            local s, e = str:find("^-?%d+%.?%d*[eE]?[+-]?%d*", pos)
            if not s then error("Unexpected character: " .. c) end
            pos = e + 1
            return tonumber(str:sub(s, e))
        end
    end
    local ok, result = pcall(parse_value)
    if ok then return result end
    return nil
end

--------------------------------------------------------------------------------
-- HTTP
--------------------------------------------------------------------------------

local function parse_http_request(data)
    local header_end = data:find("\r\n\r\n", 1, true)
    if not header_end then return nil end
    local header_part = data:sub(1, header_end - 1)
    local body = data:sub(header_end + 4)
    local lines = {}
    for line in header_part:gmatch("[^\r\n]+") do lines[#lines + 1] = line end
    if #lines < 1 then return nil end
    local method, path, version = lines[1]:match("^(%w+)%s+([^%s]+)%s+HTTP/([%d%.]+)")
    if not method then return nil end
    local headers = {}
    for i = 2, #lines do
        local key, value = lines[i]:match("^([^:]+):%s*(.*)$")
        if key then headers[key:lower()] = value end
    end
    if body == "" then body = nil end
    return {method = method, path = path, version = version, headers = headers, body = body}
end

local function send_response(client, status_code, status_text, body, content_type)
    local response = string.format(
        "HTTP/1.1 %d %s\r\n" ..
        "Content-Type: %s\r\n" ..
        "Content-Length: %d\r\n" ..
        "Connection: close\r\n" ..
        "Access-Control-Allow-Origin: *\r\n" ..
        "Access-Control-Allow-Methods: GET, POST, OPTIONS\r\n" ..
        "Access-Control-Allow-Headers: Content-Type\r\n" ..
        "\r\n%s",
        status_code, status_text, content_type or "application/json", #body, body)
    -- Large bodies may not fit the socket buffer in one non-blocking send; finish them with a short
    -- blocking timeout (bounded so a stalled client cannot freeze the game).
    client:settimeout(1)
    local sent, attempts = 0, 0
    while sent < #response and attempts < 5 do
        attempts = attempts + 1
        local last, err, partial = client:send(response, sent + 1)
        if last then
            sent = last
        elseif partial and partial > sent then
            sent = partial
        elseif err ~= "timeout" then
            break
        end
    end
end

local function send_json(client, status_code, data)
    local status_text = status_code == 200 and "OK" or status_code == 400 and "Bad Request" or
        status_code == 404 and "Not Found" or status_code == 500 and "Internal Server Error" or "Unknown"
    send_response(client, status_code, status_text, json_encode(data), "application/json")
end

--------------------------------------------------------------------------------
-- Generic helpers
--------------------------------------------------------------------------------

-- Plain-data copy of a game table: numbers/strings/booleans and nested plain tables only.
-- Objects (tables with a metatable, e.g. Card) and functions are dropped.
local function plain(v, depth)
    depth = depth or 0
    local t = type(v)
    if t == "number" or t == "string" or t == "boolean" then return v end
    if t ~= "table" or depth > 6 or getmetatable(v) ~= nil then return nil end
    local out = {}
    for k, x in pairs(v) do
        local kt = type(k)
        if kt == "string" or kt == "number" then
            local px = plain(x, depth + 1)
            if px ~= nil then out[k] = px end
        end
    end
    return out
end

local function center_key(card)
    return card and card.config and card.config.center and card.config.center.key
end

local function edition_of(card)
    local e = card and card.edition
    if not e then return nil end
    if e.type then return e.type end
    if e.foil then return "foil" end
    if e.holo then return "holo" end
    if e.polychrome then return "polychrome" end
    if e.negative then return "negative" end
    return nil
end

local function bool(v) return v and true or false end

local function range_list(n)
    local out = arr()
    for i = 1, n do out[i] = i end
    return out
end

local function area_cards(area)
    return (area and area.cards) or {}
end

--------------------------------------------------------------------------------
-- Phase and settled predicate
--------------------------------------------------------------------------------

local function is_pack_state(st)
    local S = G.STATES
    return st == S.TAROT_PACK or st == S.PLANET_PACK or st == S.SPECTRAL_PACK or
        st == S.STANDARD_PACK or st == S.BUFFOON_PACK
end

local function pack_kind()
    local S, st = G.STATES, G.STATE
    if st == S.TAROT_PACK then return "Arcana" end
    if st == S.PLANET_PACK then return "Celestial" end
    if st == S.SPECTRAL_PACK then return "Spectral" end
    if st == S.STANDARD_PACK then return "Standard" end
    if st == S.BUFFOON_PACK then return "Buffoon" end
    return nil
end

local function get_phase()
    if not G or not G.STATES or not G.STAGES then return "UNKNOWN" end
    local S, st = G.STATES, G.STATE
    if G.STAGE ~= G.STAGES.RUN then
        if st == S.MENU then return "MENU" end
        if st == S.SPLASH then return "SPLASH" end
        return "STATE_" .. tostring(st)
    end
    if st == S.GAME_OVER then return "GAME_OVER" end
    if G.GAME and G.GAME.won and G.OVERLAY_MENU and st == S.ROUND_EVAL then return "WIN" end
    if is_pack_state(st) then return "PACK_OPENING" end
    if st == S.SHOP then return "SHOP" end
    if st == S.SELECTING_HAND then return "SELECTING_HAND" end
    if st == S.HAND_PLAYED then return "HAND_PLAYED" end
    if st == S.DRAW_TO_HAND then return "DRAW_TO_HAND" end
    if st == S.BLIND_SELECT then return "BLIND_SELECT" end
    if st == S.ROUND_EVAL then return "ROUND_EVAL" end
    if st == S.NEW_ROUND then return "NEW_ROUND" end
    if st == S.PLAY_TAROT then return "PLAY_TAROT" end
    if st == S.MENU then return "MENU" end
    return "STATE_" .. tostring(st)
end

local IN_RUN_DECISION = {BLIND_SELECT = true, SELECTING_HAND = true, SHOP = true, PACK_OPENING = true, ROUND_EVAL = true}

local function controller_lock()
    if G.screenwipe then return "screenwipe" end
    local locks = G.CONTROLLER and G.CONTROLLER.locks
    if locks then
        for k, v in pairs(locks) do
            if v then return tostring(k) end
        end
    end
    return nil
end

local function blocking_events_pending()
    local q = G.E_MANAGER and G.E_MANAGER.queues and G.E_MANAGER.queues.base
    if not q then return false end
    for _, ev in ipairs(q) do
        if ev.blocking and not ev.complete then return true end
    end
    return false
end

-- Returns settled(bool), reason(string|nil). See DATA_CONTRACT.md "Settled".
local function settle_status(phase)
    if not G or not G.STATES then return false, "game_not_ready" end
    if G.screenwipe then return false, "screenwipe" end
    if phase == "MENU" then
        if not unlock_done then return false, "unlocking_profile" end
        if not G.MAIN_MENU_UI then return false, "menu_loading" end
        return true, nil
    elseif phase == "GAME_OVER" then
        if not G.STATE_COMPLETE or not G.OVERLAY_MENU then return false, "game_over_loading" end
        return true, nil
    elseif phase == "WIN" then
        return true, nil
    elseif not IN_RUN_DECISION[phase] then
        return false, "phase:" .. phase
    end
    if not G.STATE_COMPLETE then return false, "state_incomplete" end
    if G.OVERLAY_MENU then return false, "overlay" end
    if G.SETTINGS and G.SETTINGS.paused then return false, "paused" end
    local lk = controller_lock()
    if lk then return false, "lock:" .. lk end
    if G.GAME.STOP_USE and G.GAME.STOP_USE > 0 then return false, "stop_use" end
    if G.play and G.play.cards and #G.play.cards > 0 then return false, "cards_in_play" end
    if G.TAROT_INTERRUPT then return false, "tarot_interrupt" end
    if blocking_events_pending() then return false, "events_pending" end
    if phase == "BLIND_SELECT" then
        if not (G.blind_select and G.blind_select_opts and G.GAME.blind_on_deck) then return false, "blind_select_ui" end
    elseif phase == "SELECTING_HAND" then
        if not (G.buttons and G.hand and G.hand.cards and #G.hand.cards > 0) then return false, "hand_ui" end
        if G.GAME.blind and G.GAME.blind.block_play then return false, "boss_alert" end
    elseif phase == "SHOP" then
        if not (G.shop and G.shop_jokers and G.shop_vouchers and G.shop_booster) then return false, "shop_ui" end
    elseif phase == "ROUND_EVAL" then
        -- The Cash Out button is its own UIBox created by evaluate_round's last (blocking) event, so
        -- "G.round_eval exists and no blocking events pending" means it is up.
        if not G.round_eval then return false, "round_eval_ui" end
    elseif phase == "PACK_OPENING" then
        if not (G.booster_pack and G.pack_cards and G.pack_cards.cards and #G.pack_cards.cards > 0) then
            return false, "pack_ui"
        end
        for _, c in ipairs(G.pack_cards.cards) do
            if c.facing ~= "front" or c.flipping then return false, "pack_flipping" end
        end
        local st = G.STATE
        if (st == G.STATES.TAROT_PACK or st == G.STATES.SPECTRAL_PACK) and
            not (G.hand and (G.hand.cards[1] or G.hand.config.card_limit <= 0)) then
            return false, "pack_hand_draw"
        end
    end
    return true, nil
end

--------------------------------------------------------------------------------
-- Observation (policy-visible) and hidden state
--------------------------------------------------------------------------------

local function playing_card_fields(card, t)
    t.id = card.sort_id
    t.rank = card.base and card.base.value
    t.suit = card.base and card.base.suit
    local ck = center_key(card)
    if ck and ck ~= "c_base" then t.enhancement = ck end
    t.edition = edition_of(card)
    t.seal = card.seal
    t.perma_bonus = (card.ability and card.ability.perma_bonus) or 0
    return t
end

local function hand_card_obs(card, i)
    local t = {
        index = i,
        facing = card.facing == "back" and "back" or "front",
        highlighted = bool(card.highlighted),
        forced = bool(card.ability and card.ability.forced_selection),
    }
    if t.facing == "back" then return t end
    playing_card_fields(card, t)
    t.debuff = bool(card.debuff)
    return t
end

local function joker_sticker_fields(card, t)
    local ab = card.ability or {}
    t.eternal = bool(ab.eternal)
    t.perishable = bool(ab.perishable)
    t.perish_tally = ab.perishable and ab.perish_tally or nil
    t.rental = bool(ab.rental)
    t.pinned = bool(card.pinned)
end

local function joker_obs(card, i)
    if card.facing == "back" then return {index = i, facing = "back"} end
    local ab = card.ability or {}
    local t = {
        index = i,
        facing = "front",
        id = card.sort_id,
        key = center_key(card),
        name = ab.name,
        rarity = card.config and card.config.center and card.config.center.rarity,
        edition = edition_of(card),
        sell_cost = card.sell_cost or 0,
        debuff = bool(card.debuff),
        ability = plain(ab),
    }
    joker_sticker_fields(card, t)
    return t
end

local function consumable_obs(card, i)
    if card.facing == "back" then return {index = i, facing = "back"} end
    local ab = card.ability or {}
    return {
        index = i,
        facing = "front",
        id = card.sort_id,
        key = center_key(card),
        name = ab.name,
        set = ab.set,
        edition = edition_of(card),
        sell_cost = card.sell_cost or 0,
        debuff = bool(card.debuff),
        ability = plain(ab),
    }
end

-- Shop items and pack cards. with_cost: shop areas show the buy price.
local function item_obs(card, i, with_cost)
    local t = {index = i}
    if with_cost then t.cost = card.cost or 0 end
    if card.facing == "back" then
        t.facing = "back"
        return t
    end
    local ab = card.ability or {}
    t.facing = "front"
    t.id = card.sort_id
    t.key = center_key(card)
    t.name = ab.name
    t.set = ab.set
    t.edition = edition_of(card)
    if ab.set == "Default" or ab.set == "Enhanced" then
        playing_card_fields(card, t)
        t.name = nil
    elseif ab.set == "Joker" then
        t.rarity = card.config and card.config.center and card.config.center.rarity
        t.sell_cost = card.sell_cost or 0
        t.ability = plain(ab)
        joker_sticker_fields(card, t)
    elseif ab.set == "Booster" then
        local center = card.config and card.config.center or {}
        t.kind = center.kind
        t.size = ab.extra
        t.choose = center.config and center.config.choose or 1
    elseif ab.consumeable then
        t.ability = plain(ab)
    end
    return t
end

local function identity_of(card)
    local t = {id = card.sort_id, key = center_key(card), set = card.ability and card.ability.set,
        name = card.ability and card.ability.name, edition = edition_of(card), seal = card.seal}
    if card.base and card.base.value and (t.set == "Default" or t.set == "Enhanced") then
        t.rank = card.base.value
        t.suit = card.base.suit
        t.name = nil
    end
    return t
end

local function blind_obs()
    local b = G.GAME and G.GAME.blind
    if not b or not b.config or not b.config.blind or not b.config.blind.key or (b.name or "") == "" then return nil end
    local t = {
        key = b.config.blind.key,
        name = b.name,
        boss = bool(b.boss),
        chips_needed = b.chips,
        chips_scored = G.GAME.chips or 0,
        dollars = b.dollars,
        disabled = bool(b.disabled),
    }
    if t.boss then
        local ok, txt = pcall(b.get_loc_debuff_text, b)
        if ok and type(txt) == "string" and txt ~= "" then t.effect_text = txt end
        if b.name == "The Eye" and type(b.hands) == "table" then
            local used = arr()
            for hand, v in pairs(b.hands) do
                if v then used[#used + 1] = hand end
            end
            table.sort(used)
            t.hands_used = used
        end
        if b.name == "The Mouth" and b.only_hand then t.only_hand = b.only_hand end
        if b.name == "The Ox" then
            t.target_hand = G.GAME.current_round and G.GAME.current_round.most_played_poker_hand
        end
    end
    return t
end

local function blind_select_obs()
    local game = G.GAME
    local rr = game.round_resets
    if not (rr and rr.blind_choices) then return nil end
    local sel = {on_deck = game.blind_on_deck, boss_rerolled = bool(rr.boss_rerolled), choices = {}}
    for k, key in pairs(rr.blind_choices) do
        local b = G.P_BLINDS and G.P_BLINDS[key]
        local tagkey = rr.blind_tags and rr.blind_tags[k]
        local tag = tagkey and G.P_TAGS and G.P_TAGS[tagkey]
        local choice = {
            key = key,
            name = b and b.name,
            boss = b and b.boss and true or false,
            chips = b and math.floor(get_blind_amount(rr.ante) * b.mult * (game.starting_params.ante_scaling or 1)),
            dollars = b and b.dollars,
            state = rr.blind_states and rr.blind_states[k],
        }
        if k ~= "Boss" then
            choice.tag_key = tagkey
            choice.tag = tag and tag.name or tagkey
            -- The offered Tag object (with per-instance ability, e.g. orbital_hand) lives in the blind option UI
            local ui = G.blind_select_opts and G.blind_select_opts[string.lower(k)]
            local tc = ui and ui.get_UIE_by_ID and ui:get_UIE_by_ID("tag_container")
            local tobj = tc and tc.config and tc.config.ref_table
            if choice.tag_key == "tag_orbital" and tobj and tobj.ability and tobj.ability.orbital_hand then
                choice.orbital_hand = tobj.ability.orbital_hand
            end
        end
        sel.choices[k] = choice
    end
    return sel
end

local function run_counters_obs()
    local g = G.GAME
    local cr = g.current_round or {}
    local rr = g.round_resets or {}
    return {
        skips = g.skips or 0,
        hands_played_total = g.hands_played or 0,
        round_hands_played = cr.hands_played or 0,
        discards_used = cr.discards_used or 0,
        unused_discards = g.unused_discards or 0,
        consumeable_usage_total = plain(g.consumeable_usage_total) or {},
        last_tarot_planet = g.last_tarot_planet,
        starting_deck_size = g.starting_deck_size,
        bankrupt_at = g.bankrupt_at or 0,
        free_rerolls = cr.free_rerolls or 0,
        reroll_cost = cr.reroll_cost,
        boss_rerolled = bool(rr.boss_rerolled),
        round_dollars = cr.dollars,
        previous_round_dollars = g.previous_round and g.previous_round.dollars,
        jokers_purchased = cr.jokers_purchased or 0,
        inflation = g.inflation or 0,
        discount_percent = g.discount_percent or 0,
        probabilities_normal = g.probabilities and g.probabilities.normal,
        most_played_poker_hand = cr.most_played_poker_hand,
        idol_card = cr.idol_card and {rank = cr.idol_card.rank, suit = cr.idol_card.suit},
        mail_card = cr.mail_card and {rank = cr.mail_card.rank},
        ancient_card = cr.ancient_card and {suit = cr.ancient_card.suit},
        castle_card = cr.castle_card and {suit = cr.castle_card.suit},
        joker_buffer = g.joker_buffer,
        ecto_minus = g.ecto_minus,
    }
end

-- Mirrors View Deck: every playing card (sorted by stable id) with its public identity.
-- `remaining` = shown in the "Remaining" view (in the draw pile, or face-down in hand: vanilla counts
-- wheel_flipped cards as remaining so the view does not reveal them).
local function deck_obs()
    local cards = arr()
    local by_suit, by_rank, face = {}, {}, 0
    local remaining_n = 0
    for _, c in ipairs(G.playing_cards or {}) do
        local t = playing_card_fields(c, {})
        local remaining = (c.area and c.area == G.deck) or bool(c.ability and c.ability.wheel_flipped)
        t.remaining = bool(remaining)
        cards[#cards + 1] = t
        if remaining then
            remaining_n = remaining_n + 1
            local s, r = c.base and c.base.suit, c.base and c.base.value
            if s then by_suit[s] = (by_suit[s] or 0) + 1 end
            if r then by_rank[r] = (by_rank[r] or 0) + 1 end
            if r == "Jack" or r == "Queen" or r == "King" then face = face + 1 end
        end
    end
    table.sort(cards, function(a, b) return (a.id or 0) < (b.id or 0) end)
    return {
        total = #(G.playing_cards or {}),
        draw_pile = #area_cards(G.deck),
        discard_pile = #area_cards(G.discard),
        remaining = remaining_n,
        remaining_by_suit = by_suit,
        remaining_by_rank = by_rank,
        remaining_face_cards = face,
        cards = cards,
    }
end

local function build_obs(phase)
    local obs = {schema_version = CONFIG.schema_version, phase = phase}
    if not G or not G.GAME or G.STAGE ~= G.STAGES.RUN then return obs end
    local game = G.GAME
    local cr = game.current_round or {}
    local rr = game.round_resets or {}

    local back = game.selected_back
    obs.deck_key = back and back.effect and back.effect.center and back.effect.center.key or nil
    obs.deck_name = back and back.name or nil
    obs.deck_config = back and back.effect and plain(back.effect.config) or {}
    obs.stake = game.stake
    obs.won = bool(game.won)
    obs.win_ante = game.win_ante
    obs.round = game.round or 0
    obs.ante = rr.ante or 0
    obs.money = game.dollars or 0
    -- Score of the current round (still visible during ROUND_EVAL; reset at cash out)
    obs.chips = game.chips or 0
    obs.hands_remaining = cr.hands_left or 0
    obs.discards_remaining = cr.discards_left or 0
    obs.hands_per_round = rr.hands
    obs.discards_per_round = rr.discards
    obs.hand_size = G.hand and G.hand.config and G.hand.config.card_limit or nil
    obs.highlight_limit = G.hand and G.hand.config and G.hand.config.highlighted_limit or nil
    obs.joker_slots = G.jokers and G.jokers.config and G.jokers.config.card_limit or nil
    obs.consumable_slots = G.consumeables and G.consumeables.config and G.consumeables.config.card_limit or nil
    obs.interest_amount = game.interest_amount
    obs.interest_cap = game.interest_cap
    obs.no_interest = bool(game.modifiers and game.modifiers.no_interest)
    obs.modifiers = plain(game.modifiers) or {}
    obs.starting_params = plain(game.starting_params) or {}
    obs.shop_rates = {
        joker = game.joker_rate,
        tarot = game.tarot_rate,
        planet = game.planet_rate,
        spectral = game.spectral_rate,
        playing_card = game.playing_card_rate,
        edition = game.edition_rate,
    }
    obs.used_vouchers = arr()
    for k, v in pairs(game.used_vouchers or {}) do
        if v then obs.used_vouchers[#obs.used_vouchers + 1] = k end
    end
    table.sort(obs.used_vouchers)

    obs.tags = arr()
    for i, t in ipairs(game.tags or {}) do
        obs.tags[i] = {
            key = t.key,
            name = t.name or (G.P_TAGS and G.P_TAGS[t.key] and G.P_TAGS[t.key].name) or t.key,
            orbital_hand = t.ability and t.ability.orbital_hand or nil,
        }
    end

    obs.run = run_counters_obs()
    obs.blind = blind_obs()
    -- The ante's blinds (incl. upcoming Boss) are visible in vanilla at any time (Run Info / blind HUD)
    do
        local ok, sel = pcall(blind_select_obs)
        if ok then obs.blind_select = sel end
    end

    obs.hand = arr()
    for i, c in ipairs(area_cards(G.hand)) do obs.hand[i] = hand_card_obs(c, i) end
    obs.jokers = arr()
    for i, c in ipairs(area_cards(G.jokers)) do obs.jokers[i] = joker_obs(c, i) end
    obs.consumables = arr()
    for i, c in ipairs(area_cards(G.consumeables)) do obs.consumables[i] = consumable_obs(c, i) end

    if phase == "SHOP" then
        local shop = {jokers = arr(), vouchers = arr(), boosters = arr(), reroll_cost = cr.reroll_cost}
        for i, c in ipairs(area_cards(G.shop_jokers)) do shop.jokers[i] = item_obs(c, i, true) end
        for i, c in ipairs(area_cards(G.shop_vouchers)) do shop.vouchers[i] = item_obs(c, i, true) end
        for i, c in ipairs(area_cards(G.shop_booster)) do shop.boosters[i] = item_obs(c, i, true) end
        obs.shop = shop
    end

    if phase == "PACK_OPENING" then
        local pack = {kind = pack_kind(), size = game.pack_size, choices_remaining = game.pack_choices or 1, cards = arr()}
        for i, c in ipairs(area_cards(G.pack_cards)) do pack.cards[i] = item_obs(c, i, false) end
        obs.pack = pack
    end

    obs.deck = deck_obs()

    obs.hand_levels = {}
    for hand_type, h in pairs(game.hands or {}) do
        if type(h) == "table" and h.level then
            obs.hand_levels[hand_type] = {
                level = h.level, chips = h.chips, mult = h.mult,
                played = h.played, played_this_round = h.played_this_round, visible = bool(h.visible),
            }
        end
    end
    return obs
end

local function build_hidden()
    local hidden = {face_down = arr(), draw_order = arr()}
    if not G or not G.GAME or G.STAGE ~= G.STAGES.RUN then return hidden end
    hidden.seed = G.GAME.pseudorandom and G.GAME.pseudorandom.seed
    -- G.deck draws from the end of its card list: next-drawn first
    local deck = area_cards(G.deck)
    for i = #deck, 1, -1 do hidden.draw_order[#hidden.draw_order + 1] = deck[i].sort_id end
    local function scan(area, name)
        for i, c in ipairs(area_cards(area)) do
            if c.facing == "back" then
                local t = identity_of(c)
                t.area = name
                t.index = i
                hidden.face_down[#hidden.face_down + 1] = t
            end
        end
    end
    scan(G.hand, "hand")
    scan(G.jokers, "jokers")
    scan(G.consumeables, "consumables")
    scan(G.pack_cards, "pack")
    scan(G.shop_jokers, "shop_jokers")
    return hidden
end

--------------------------------------------------------------------------------
-- Legality (mirrors the vanilla can_* checks; see DATA_CONTRACT.md "/legal")
--------------------------------------------------------------------------------

local function d_one_of(list) return {one_of = arr(list)} end
local function d_subset(of, min, max, must)
    local s = {of = arr(of), min = min, max = max}
    if must and #must > 0 then s.must_include = arr(must) end
    return {subset = s}
end

local function money_available()
    return (G.GAME.dollars or 0) - (G.GAME.bankrupt_at or 0)
end

-- G.FUNCS.can_buy / can_open: disabled iff cost > dollars - bankrupt_at and cost > 0
local function affordable(cost)
    cost = cost or 0
    return cost <= 0 or cost <= money_available()
end

-- G.FUNCS.check_for_buy_space without the alert side effect
local function has_buy_space(card)
    local ab = card.ability or {}
    local set = ab.set
    if set == "Voucher" or set == "Enhanced" or set == "Default" then return true end
    local neg = (card.edition and card.edition.negative) and 1 or 0
    if set == "Joker" and #G.jokers.cards < G.jokers.config.card_limit + neg then return true end
    if ab.consumeable and #G.consumeables.cards < G.consumeables.config.card_limit + neg then return true end
    return false
end

-- G.FUNCS.can_select_card (pack picks)
local function can_select_pack_card(card)
    local ab = card.ability or {}
    return ab.set ~= "Joker" or bool(card.edition and card.edition.negative) or #G.jokers.cards < G.jokers.config.card_limit
end

local function hand_target_state()
    local S, st = G.STATES, G.STATE
    return st == S.SELECTING_HAND or st == S.TAROT_PACK or st == S.SPECTRAL_PACK or st == S.PLANET_PACK
end

local function forced_indices()
    local out = {}
    for i, c in ipairs(area_cards(G.hand)) do
        if c.ability and c.ability.forced_selection then out[#out + 1] = i end
    end
    return out
end

local function hand_highlight_limit()
    return (G.hand and G.hand.config and G.hand.config.highlighted_limit) or 5
end

-- Use domain of a consumable (held, in shop, or in a pack) at this decision point.
-- Returns nil if unusable; {} if usable without targets; {targets = <subset domain>} if it needs targets.
-- Mirrors Card:can_use_consumeable(): targeted cards (max_highlighted, Aura) need hand cards highlighted;
-- vanilla only checks the count (and Aura's no-edition rule), which the subset domain encodes exactly.
local function use_domain(card)
    local ab = card.ability or {}
    local cons = ab.consumeable
    if not cons then return nil end
    local hand = area_cards(G.hand)
    local forced = forced_indices()
    if cons.max_highlighted then
        if not hand_target_state() then return nil end
        local mn = cons.min_highlighted or 1
        local mx = cons.mod_num or math.min(5, cons.max_highlighted)
        mx = math.min(mx, hand_highlight_limit())
        if #hand < mn or mx < mn or #forced > mx then return nil end
        return {targets = d_subset(range_list(#hand), mn, mx, forced)}
    end
    if ab.name == "Aura" then
        local of = {}
        for i, c in ipairs(hand) do
            if not c.edition then of[#of + 1] = i end
        end
        if #of == 0 or #forced > 1 then return nil end
        if #forced == 1 and hand[forced[1]].edition then return nil end
        return {targets = d_subset(of, 1, 1, forced)}
    end
    local ok, usable = pcall(card.can_use_consumeable, card)
    if ok and usable then return {} end
    return nil
end

local function add_entry(list, atype, params, info)
    list[#list + 1] = {type = atype, params = params or {}, info = info}
end

local function card_info(card, extra)
    local t = {}
    if card.facing == "back" then
        t.facing = "back"
    else
        t.key = center_key(card)
        t.name = card.ability and card.ability.name
    end
    for k, v in pairs(extra or {}) do t[k] = v end
    return t
end

-- Sell / use / reorder: allowed in every in-run decision phase (V:card.lua can_sell_card, can_use_consumeable).
local function management_entries(list, phase)
    for i, c in ipairs(area_cards(G.jokers)) do
        local ok, can = pcall(c.can_sell_card, c)
        if ok and can then
            add_entry(list, "SELL_JOKER", {index = d_one_of({i})},
                card_info(c, c.facing ~= "back" and {sell_value = c.sell_cost or 0} or nil))
        end
    end
    for i, c in ipairs(area_cards(G.consumeables)) do
        local ok, can = pcall(c.can_sell_card, c)
        if ok and can then
            add_entry(list, "SELL_CONSUMABLE", {index = d_one_of({i})}, card_info(c, {sell_value = c.sell_cost or 0}))
        end
    end
    for i, c in ipairs(area_cards(G.consumeables)) do
        local dom = use_domain(c)
        if dom then
            local params = {index = d_one_of({i})}
            if dom.targets then params.targets = dom.targets end
            add_entry(list, "USE_CONSUMABLE", params, card_info(c))
        end
    end
    local hand_n = #area_cards(G.hand)
    if hand_n >= 2 and (phase == "SELECTING_HAND" or phase == "PACK_OPENING") then
        add_entry(list, "REORDER", {area = d_one_of({"hand"}), order = {permutation = hand_n}})
    end
    local jn = #area_cards(G.jokers)
    if jn >= 2 then add_entry(list, "REORDER", {area = d_one_of({"jokers"}), order = {permutation = jn}}) end
    local cn = #area_cards(G.consumeables)
    if cn >= 2 then add_entry(list, "REORDER", {area = d_one_of({"consumables"}), order = {permutation = cn}}) end
end

local function deck_keys()
    local keys = {}
    for k, v in pairs(G.P_CENTERS or {}) do
        if type(v) == "table" and v.set == "Back" and not v.omit then keys[#keys + 1] = k end
    end
    table.sort(keys)
    return keys
end

local function start_run_entry(list)
    add_entry(list, "START_RUN", {
        deck = d_one_of(deck_keys()),
        stake = d_one_of({1, 2, 3, 4, 5, 6, 7, 8}),
        seed = {seed = true, optional = true},
    })
end

local function build_legal_actions(phase)
    local list = {}
    local game = G.GAME
    if phase == "MENU" or phase == "GAME_OVER" or phase == "WIN" then
        start_run_entry(list)
        return list
    end
    if not IN_RUN_DECISION[phase] then return list end

    if phase == "BLIND_SELECT" then
        local on_deck = game.blind_on_deck
        add_entry(list, "SELECT_BLIND", {}, {blind = on_deck})
        if on_deck == "Small" or on_deck == "Big" then
            add_entry(list, "SKIP_BLIND", {}, {blind = on_deck})
        end
        local uv = game.used_vouchers or {}
        if money_available() - 10 >= 0 and (uv["v_retcon"] or (uv["v_directors_cut"] and not game.round_resets.boss_rerolled)) then
            add_entry(list, "REROLL_BOSS", {}, {cost = 10})
        end
    elseif phase == "SELECTING_HAND" then
        local n = #area_cards(G.hand)
        local forced = forced_indices()
        local limit = hand_highlight_limit()
        local all = range_list(n)
        local play_max = math.min(5, limit, n)
        if n > 0 and #forced <= play_max then
            add_entry(list, "PLAY_HAND", {card_indices = d_subset(all, 1, play_max, forced)})
        end
        local discard_max = math.min(limit, n)
        if (game.current_round.discards_left or 0) > 0 and n > 0 and #forced <= discard_max then
            add_entry(list, "DISCARD", {card_indices = d_subset(all, 1, discard_max, forced)})
        end
        add_entry(list, "SORT_HAND", {mode = d_one_of({"rank", "suit"})})
    elseif phase == "SHOP" then
        for i, c in ipairs(area_cards(G.shop_jokers)) do
            if affordable(c.cost) and has_buy_space(c) then
                add_entry(list, "SHOP_BUY", {slot = d_one_of({i})}, card_info(c, {cost = c.cost}))
            end
            if c.ability and c.ability.consumeable and affordable(c.cost) then
                local dom = use_domain(c)
                if dom then
                    local params = {slot = d_one_of({i})}
                    if dom.targets then params.targets = dom.targets end
                    add_entry(list, "SHOP_BUY_AND_USE", params, card_info(c, {cost = c.cost}))
                end
            end
        end
        for i, c in ipairs(area_cards(G.shop_vouchers)) do
            if (c.cost or 0) <= money_available() then
                add_entry(list, "SHOP_BUY_VOUCHER", {slot = d_one_of({i})}, card_info(c, {cost = c.cost}))
            end
        end
        for i, c in ipairs(area_cards(G.shop_booster)) do
            if affordable(c.cost) then
                add_entry(list, "SHOP_BUY_BOOSTER", {slot = d_one_of({i})}, card_info(c, {cost = c.cost}))
            end
        end
        local rc = game.current_round.reroll_cost or 0
        if money_available() - rc >= 0 or rc == 0 then
            add_entry(list, "SHOP_REROLL", {}, {cost = rc})
        end
        add_entry(list, "SHOP_END", {})
    elseif phase == "ROUND_EVAL" then
        add_entry(list, "CASH_OUT", {}, {dollars = game.current_round.dollars})
    elseif phase == "PACK_OPENING" then
        if (game.pack_choices or 0) > 0 then
            for i, c in ipairs(area_cards(G.pack_cards)) do
                local ab = c.ability or {}
                if ab.consumeable then
                    local dom = use_domain(c)
                    if dom then
                        local params = {index = d_one_of({i})}
                        if dom.targets then params.targets = dom.targets end
                        add_entry(list, "SELECT_PACK_CARD", params, card_info(c))
                    end
                elseif can_select_pack_card(c) then
                    add_entry(list, "SELECT_PACK_CARD", {index = d_one_of({i})}, card_info(c))
                end
            end
        end
        local st = G.STATE
        if G.pack_cards.cards[1] and (st == G.STATES.PLANET_PACK or st == G.STATES.STANDARD_PACK or
            st == G.STATES.BUFFOON_PACK or (G.hand and (G.hand.cards[1] or G.hand.config.card_limit <= 0))) then
            add_entry(list, "SKIP_PACK", {})
        end
    end
    management_entries(list, phase)
    return list
end

local function build_legal(phase, settled, reason)
    local legal = {schema_version = CONFIG.schema_version, phase = phase, settled = settled, actions = arr()}
    if not settled then
        legal.settle_reason = reason
        return legal
    end
    for i, e in ipairs(build_legal_actions(phase)) do legal.actions[i] = e end
    return legal
end

--------------------------------------------------------------------------------
-- Validation against /legal
--------------------------------------------------------------------------------

local function is_int(v) return type(v) == "number" and v == math.floor(v) end

local function domain_match(d, v)
    if d.one_of then
        for _, x in ipairs(d.one_of) do
            if x == v then return true end
        end
        return false, "not one of the legal values"
    elseif d.subset then
        local s = d.subset
        if type(v) ~= "table" then return false, "expected a list" end
        local allowed, seen = {}, {}
        for _, x in ipairs(s.of) do allowed[x] = true end
        local n = 0
        for k in pairs(v) do
            if not is_int(k) then return false, "expected a list" end
        end
        for _, x in ipairs(v) do
            if not is_int(x) or not allowed[x] then return false, "index " .. tostring(x) .. " not allowed" end
            if seen[x] then return false, "duplicate index " .. tostring(x) end
            seen[x] = true
            n = n + 1
        end
        if n < s.min or n > s.max then
            return false, string.format("needs %d..%d entries, got %d", s.min, s.max, n)
        end
        for _, x in ipairs(s.must_include or {}) do
            if not seen[x] then return false, "must include forced card " .. tostring(x) end
        end
        return true
    elseif d.permutation then
        if type(v) ~= "table" or #v ~= d.permutation then
            return false, "order must list all " .. tostring(d.permutation) .. " positions"
        end
        local seen = {}
        for _, x in ipairs(v) do
            if not is_int(x) or x < 1 or x > d.permutation or seen[x] then
                return false, "order is not a permutation of 1.." .. tostring(d.permutation)
            end
            seen[x] = true
        end
        return true
    elseif d.seed then
        if type(v) ~= "string" or not v:match("^[0-9A-Z]+$") or #v > 8 then
            return false, "seed must be 1-8 chars of 0-9A-Z"
        end
        return true
    end
    return false, "unknown domain"
end

local function is_empty(v) return v == nil or (type(v) == "table" and next(v) == nil) end

local function check_param(name, d, v)
    if is_empty(v) then
        if not d.optional then return false, "missing param '" .. name .. "'" end
        return true
    end
    local ok, why = domain_match(d, v)
    if not ok then return false, "param '" .. name .. "': " .. why end
    return true
end

local function match_entry(e, params)
    -- Selector params (one_of: index/slot/area/mode...) first, so a wrong index is reported as such
    -- rather than as a problem with another entry's targets.
    for pass = 1, 2 do
        for name, d in pairs(e.params) do
            if (pass == 1) == (d.one_of ~= nil) then
                local ok, why = check_param(name, d, params[name])
                if not ok then return false, why end
            end
        end
    end
    for name, v in pairs(params) do
        if e.params[name] == nil and not is_empty(v) then
            return false, "unexpected param '" .. tostring(name) .. "'"
        end
    end
    return true
end

local function validate(atype, params, actions)
    local errs, any = {}, false
    for _, e in ipairs(actions) do
        if e.type == atype then
            any = true
            local ok, why = match_entry(e, params)
            if ok then return true end
            errs[#errs + 1] = why
        end
    end
    if not any then return false, atype .. " is not legal now" end
    -- Report the most specific error: an entry whose selector matched beats "index not legal"
    for _, m in ipairs(errs) do
        if not m:find("not one of the legal values", 1, true) then return false, m end
    end
    return false, errs[1] or "params do not match any legal entry"
end

--------------------------------------------------------------------------------
-- Canonicalization and refs
--------------------------------------------------------------------------------

local SEED_ALPHABET = "123456789ABCDEFGHIJKLMNPQRSTUVWXYZ"
local function generate_seed()
    local x = math.floor((socket.gettime() * 1000003) % 2147483647) + CONFIG.port + request_count
    local out = {}
    for i = 1, 8 do
        x = (x * 16807) % 2147483647
        local k = (x % #SEED_ALPHABET) + 1
        out[i] = SEED_ALPHABET:sub(k, k)
    end
    return table.concat(out)
end

local function canonicalize(atype, params)
    if atype ~= "START_RUN" then return params end
    local out = {}
    for k, v in pairs(params) do out[k] = v end
    local deck = params.deck or "b_red"
    if type(deck) == "string" and not (G.P_CENTERS[deck] and G.P_CENTERS[deck].set == "Back") then
        for k, v in pairs(G.P_CENTERS) do
            if type(v) == "table" and v.set == "Back" and type(v.name) == "string" and v.name:lower() == deck:lower() then
                deck = k
                break
            end
        end
    end
    out.deck = deck
    out.stake = params.stake or 1
    if params.seed == nil or params.seed == "" then
        out.seed = generate_seed()
    else
        out.seed = tostring(params.seed):upper()
    end
    return out
end

local SHOP_AREA = {
    SHOP_BUY = function() return G.shop_jokers end,
    SHOP_BUY_AND_USE = function() return G.shop_jokers end,
    SHOP_BUY_VOUCHER = function() return G.shop_vouchers end,
    SHOP_BUY_BOOSTER = function() return G.shop_booster end,
}
local INDEX_AREA = {
    SELL_JOKER = function() return G.jokers end,
    SELL_CONSUMABLE = function() return G.consumeables end,
    USE_CONSUMABLE = function() return G.consumeables end,
    SELECT_PACK_CARD = function() return G.pack_cards end,
}
local REORDER_AREA = {
    hand = function() return G.hand end,
    jokers = function() return G.jokers end,
    consumables = function() return G.consumeables end,
}

local function ids_of(area, indices)
    local out = arr()
    for i, idx in ipairs(indices or {}) do
        local c = area_cards(area)[idx]
        out[i] = c and c.sort_id or -1
    end
    return out
end

local function build_refs(atype, p)
    local r = {}
    if p.card_indices then r.card_indices = ids_of(G.hand, p.card_indices) end
    if not is_empty(p.targets) then r.targets = ids_of(G.hand, p.targets) end
    if p.index and INDEX_AREA[atype] then
        local c = area_cards(INDEX_AREA[atype]())[p.index]
        r.index = c and c.sort_id
    end
    if p.slot and SHOP_AREA[atype] then
        local c = area_cards(SHOP_AREA[atype]())[p.slot]
        r.slot = c and c.sort_id
    end
    if p.order and p.area and REORDER_AREA[p.area] then r.order = ids_of(REORDER_AREA[p.area](), p.order) end
    return r
end

--------------------------------------------------------------------------------
-- Execution (vanilla G.FUNCS paths, called the way their UI buttons call them)
--------------------------------------------------------------------------------

local function fake_e(card, id)
    return {config = {ref_table = card, id = id}}
end

-- Highlight exactly `indices` in hand (forced Cerulean Bell card stays highlighted; validation
-- already required it). Returns false if the resulting highlight set differs from the request.
local function set_hand_highlight(indices)
    G.hand:unhighlight_all()
    for _, i in ipairs(indices) do
        local c = G.hand.cards[i]
        if c and not c.highlighted then G.hand:add_to_highlighted(c, true) end
    end
    local want = {}
    for _, i in ipairs(indices) do want[G.hand.cards[i]] = true end
    if #G.hand.highlighted ~= #indices then return false end
    for _, c in ipairs(G.hand.highlighted) do
        if not want[c] then return false end
    end
    return true
end

local function reorder_area(area, order)
    local reordered = {}
    for i, idx in ipairs(order) do reordered[i] = area.cards[idx] end
    area.cards = reordered
    area:set_ranks()
    area:align_cards()
end

local run_token = 0       -- incremented per START_RUN; set live once G:start_run has run
local live_token = 0

local function start_run(p)
    local center = G.P_CENTERS[p.deck]
    -- Vanilla Game:start_run takes the deck from G.GAME.viewed_back (the run-setup deck picker).
    G.GAME.viewed_back = Back(center)
    run_token = run_token + 1
    local token = run_token
    -- Same steps as G.FUNCS.start_run(nil, args), plus G.sort_id = 0 so entity ids (sort_id) are
    -- per-run and identical between an original run and its replay.
    G.SETTINGS.paused = true
    G.E_MANAGER:clear_queue()
    G.FUNCS.wipe_on()
    G.E_MANAGER:add_event(Event({
        no_delete = true,
        func = function()
            G:delete_run()
            return true
        end
    }))
    G.E_MANAGER:add_event(Event({
        trigger = "immediate",
        no_delete = true,
        func = function()
            G.sort_id = 0
            G:start_run({stake = p.stake, seed = p.seed})
            live_token = token
            return true
        end
    }))
    G.FUNCS.wipe_off()
end

local EXEC = {}

EXEC.SELECT_BLIND = function()
    local on_deck = G.GAME.blind_on_deck
    local key = G.GAME.round_resets.blind_choices[on_deck]
    G.FUNCS.select_blind({config = {ref_table = G.P_BLINDS[key]}, UIBox = {get_UIE_by_ID = function() return nil end}})
end

EXEC.SKIP_BLIND = function()
    -- skip_blind reads the offered Tag from the blind option's UIBox ('tag_container')
    local uibox = G.blind_select_opts[string.lower(G.GAME.blind_on_deck)]
    G.FUNCS.skip_blind({UIBox = uibox, config = {}})
end

EXEC.REROLL_BOSS = function()
    G.FUNCS.reroll_boss({config = {}})
end

EXEC.PLAY_HAND = function(p)
    if not set_hand_highlight(p.card_indices) then
        G.hand:unhighlight_all()
        return "highlight mismatch"
    end
    G.FUNCS.play_cards_from_highlighted(nil)
end

EXEC.DISCARD = function(p)
    if not set_hand_highlight(p.card_indices) then
        G.hand:unhighlight_all()
        return "highlight mismatch"
    end
    G.FUNCS.discard_cards_from_highlighted(nil)
end

EXEC.SORT_HAND = function(p)
    if p.mode == "suit" then G.FUNCS.sort_hand_suit() else G.FUNCS.sort_hand_value() end
end

EXEC.REORDER = function(p)
    reorder_area(REORDER_AREA[p.area](), p.order)
end

local function use_with_targets(card, targets, run)
    local targeted = not is_empty(targets)
    if targeted then
        if not set_hand_highlight(targets) then
            G.hand:unhighlight_all()
            return "highlight mismatch"
        end
    end
    if card.ability.consumeable then
        local ok, usable = pcall(card.can_use_consumeable, card)
        if not (ok and usable) then
            if targeted then G.hand:unhighlight_all() end
            return "can_use_consumeable() is false"
        end
    end
    run()
end

EXEC.USE_CONSUMABLE = function(p)
    local card = G.consumeables.cards[p.index]
    return use_with_targets(card, p.targets, function() G.FUNCS.use_card(fake_e(card)) end)
end

EXEC.SELECT_PACK_CARD = function(p)
    local card = G.pack_cards.cards[p.index]
    return use_with_targets(card, p.targets, function() G.FUNCS.use_card(fake_e(card)) end)
end

EXEC.SELL_JOKER = function(p)
    G.FUNCS.sell_card(fake_e(G.jokers.cards[p.index]))
end

EXEC.SELL_CONSUMABLE = function(p)
    G.FUNCS.sell_card(fake_e(G.consumeables.cards[p.index]))
end

EXEC.SHOP_BUY = function(p)
    if G.FUNCS.buy_from_shop(fake_e(G.shop_jokers.cards[p.slot])) == false then return "buy_from_shop refused" end
end

EXEC.SHOP_BUY_AND_USE = function(p)
    local card = G.shop_jokers.cards[p.slot]
    return use_with_targets(card, p.targets, function() G.FUNCS.buy_from_shop(fake_e(card, "buy_and_use")) end)
end

EXEC.SHOP_BUY_VOUCHER = function(p)
    G.FUNCS.use_card(fake_e(G.shop_vouchers.cards[p.slot]))
end

EXEC.SHOP_BUY_BOOSTER = function(p)
    G.FUNCS.use_card(fake_e(G.shop_booster.cards[p.slot]))
end

EXEC.SHOP_REROLL = function()
    G.FUNCS.reroll_shop()
end

EXEC.SHOP_END = function()
    G.FUNCS.toggle_shop()
end

EXEC.SKIP_PACK = function()
    G.FUNCS.skip_booster(fake_e(G.pack_cards))
end

EXEC.CASH_OUT = function()
    G.FUNCS.cash_out({config = {}})
end

EXEC.START_RUN = function(p)
    start_run(p)
end

--------------------------------------------------------------------------------
-- Recorder (docs/DATA_CONTRACT.md "Files")
--------------------------------------------------------------------------------

local REC = {
    ok = true,            -- false once the current trajectory hit a recorder error
    error = nil,          -- last recorder error message
    error_count = 0,
    traj = nil,           -- open trajectory: {file, path, steps, header, token}
    last_path = nil,      -- path of the open or most recently closed trajectory
    bridge_hash = nil,
    bridge_hash_error = nil,
}

local function rec_fail(msg)
    REC.ok = false
    REC.error = msg
    REC.error_count = REC.error_count + 1
    log_error("recorder: " .. msg)
end

local mkdir_impl = nil
do
    local ok, ffi = pcall(require, "ffi")
    if ok and ffi then
        if ffi.os == "Windows" then
            pcall(ffi.cdef, "int CreateDirectoryA(const char* lpPathName, void* lpSecurityAttributes);")
            mkdir_impl = function(p) return ffi.C.CreateDirectoryA((p:gsub("/", "\\")), nil) ~= 0 end
        else
            pcall(ffi.cdef, "int mkdir(const char* path, unsigned int mode);")
            mkdir_impl = function(p) return ffi.C.mkdir(p, 493) == 0 end
        end
    end
end

local function mkdir_p(path)
    if not mkdir_impl then return end
    path = path:gsub("\\", "/")
    local i = 1
    while true do
        local j = path:find("/", i + 1, true)
        local prefix = j and path:sub(1, j - 1) or path
        if prefix ~= "" and not prefix:match("^%a:$") then pcall(mkdir_impl, prefix) end
        if not j then break end
        i = j
    end
end

local function bridge_dir()
    local d = env_or_nil("BALATRO_RL_BRIDGE_DIR")
    if d then return d end
    local ok, lovely = pcall(require, "lovely")
    if ok and type(lovely) == "table" and lovely.mod_dir then return lovely.mod_dir .. "/BalatroRLBridge" end
    return nil
end

local function lovely_version()
    local ok, lovely = pcall(require, "lovely")
    if ok and type(lovely) == "table" then return lovely.version end
    return nil
end

-- sha256 (hex) of main.lua bytes followed by lovely.toml bytes, as deployed.
local function compute_bridge_hash()
    local dir = bridge_dir()
    if not dir then return nil, "bridge dir unknown" end
    local parts = {}
    for _, name in ipairs({"main.lua", "lovely.toml"}) do
        local f = io.open(dir .. "/" .. name, "rb")
        if not f then return nil, "cannot read " .. dir .. "/" .. name end
        parts[#parts + 1] = f:read("*a")
        f:close()
    end
    local raw = love.data.hash("sha256", table.concat(parts))
    return love.data.encode("string", "hex", raw)
end

local function unlock_counts()
    local locked, undiscovered = 0, 0
    for _, pool in ipairs({G.P_CENTERS or {}, G.P_BLINDS or {}, G.P_TAGS or {}, G.P_SEALS or {}}) do
        for _, v in pairs(pool) do
            if type(v) == "table" and not v.demo and not v.wip then
                if v.unlocked == false then locked = locked + 1 end
                if v.discovered == false then undiscovered = undiscovered + 1 end
            end
        end
    end
    return {locked = locked, undiscovered = undiscovered}
end

local function rec_write(obj)
    local traj = REC.traj
    if not traj or not traj.file then return end
    local ok, err = pcall(function()
        assert(traj.file:write(json_encode(obj), "\n"))
        traj.file:flush()
    end)
    if not ok then rec_fail("write failed for " .. traj.path .. ": " .. tostring(err)) end
end

local function rec_open(params, meta)
    REC.ok = true
    if not CONFIG.data_dir then
        rec_fail("BALATRO_RL_DATA_DIR not set: this run is not recorded")
        return
    end
    local started = now_ms()
    local dir = CONFIG.data_dir:gsub("\\", "/") .. "/trajectories/" .. os.date("%Y-%m-%d")
    mkdir_p(dir)
    local path = string.format("%s/%s_%d_%.0f.jsonl", dir, params.seed, CONFIG.port, started)
    local f, err = io.open(path, "wb")
    if not f then
        rec_fail("cannot open " .. path .. ": " .. tostring(err))
        return
    end
    REC.traj = {file = f, path = path, steps = 0, token = run_token}
    REC.last_path = path
    rec_write({
        t = "header",
        format_version = CONFIG.format_version,
        schema_version = CONFIG.schema_version,
        bridge_version = BRIDGE_VERSION,
        bridge_hash = REC.bridge_hash,
        git_sha = CONFIG.git_sha,
        game_version = G.VERSION,
        lovely_version = lovely_version(),
        seed = params.seed,
        deck_key = params.deck,
        stake = params.stake,
        start_params = params,
        start_meta = meta,
        unlocks = unlock_counts(),
        port = CONFIG.port,
        started_at_ms = started,
    })
end

local function compress_file(path)
    local f = assert(io.open(path, "rb"))
    local data = f:read("*a")
    f:close()
    local gz = love.data.compress("string", "gzip", data, 6)
    local tmp = path .. ".gz.tmp"
    local g = assert(io.open(tmp, "wb"))
    assert(g:write(gz))
    g:close()
    os.remove(path .. ".gz")
    assert(os.rename(tmp, path .. ".gz"))
    os.remove(path)
    return path .. ".gz"
end

local function rec_close(outcome)
    local traj = REC.traj
    if not traj then return end
    local ok_obs, final_obs = pcall(build_obs, get_phase())
    rec_write({
        t = "end",
        outcome = outcome,
        ante = G.GAME and G.GAME.round_resets and G.GAME.round_resets.ante,
        round = G.GAME and G.GAME.round,
        steps = traj.steps,
        tainted = traj.tainted or nil,
        final_obs = ok_obs and final_obs or nil,
        ts_ms = now_ms(),
    })
    pcall(traj.file.close, traj.file)
    REC.traj = nil
    local ok, res = pcall(compress_file, traj.path)
    if ok then
        REC.last_path = res
    else
        rec_fail("gzip failed, left uncompressed: " .. tostring(res))
    end
    log_info("trajectory closed (" .. outcome .. ", " .. traj.steps .. " steps): " .. tostring(REC.last_path))
end

-- Close the open trajectory when the run it belongs to ends.
local function rec_watch()
    local traj = REC.traj
    if not traj or traj.token ~= live_token or not G or G.STAGE ~= G.STAGES.RUN then return end
    if G.STATE == G.STATES.GAME_OVER then
        rec_close("loss")
    elseif G.GAME and G.GAME.won then
        rec_close("win")
    end
end

--------------------------------------------------------------------------------
-- /action
--------------------------------------------------------------------------------

local function reject(atype, params, meta, phase, err, retry)
    local traj = REC.traj
    if traj then
        rec_write({
            t = "reject", i = traj.steps, ts_ms = now_ms(), phase = phase,
            action = {type = atype, params = params}, meta = meta, error = err, retry = retry or nil,
        })
    end
    return {ok = false, error = err, retry = retry or nil}
end

local function handle_action(body)
    local action = json_decode(body or "")
    if type(action) ~= "table" or type(action.type) ~= "string" then
        return {ok = false, error = "Invalid action: body must be JSON {type, params?, meta?}"}
    end
    local atype = action.type
    local params = type(action.params) == "table" and action.params or {}
    local meta = type(action.meta) == "table" and action.meta or {}
    local phase = get_phase()

    -- Close a finished run before anything else (START_RUN from GAME_OVER/WIN).
    rec_watch()

    local settled, reason = settle_status(phase)
    if not settled then
        return reject(atype, params, meta, phase, "not settled (" .. tostring(reason) .. "), retry", true)
    end
    if not EXEC[atype] then
        return reject(atype, params, meta, phase, "unknown action type " .. atype)
    end

    local cparams = canonicalize(atype, params)

    if atype == "START_RUN" then
        -- Listed in /legal at MENU / GAME_OVER / WIN. Mid-run it is accepted as an admin restart that
        -- abandons the open trajectory; it is never a step line (its params + meta go in the header).
        local entries = {}
        start_run_entry(entries)
        local ok, why = validate(atype, cparams, entries)
        if not ok then return reject(atype, cparams, meta, phase, why) end
        if REC.traj then rec_close("abandoned") end
        local ok_run, err = pcall(EXEC.START_RUN, cparams)
        if not ok_run then
            log_error("START_RUN failed: " .. tostring(err))
            return {ok = false, error = "start_run failed: " .. tostring(err)}
        end
        rec_open(cparams, meta)
        return {ok = true, params = cparams, trajectory_path = REC.traj and REC.traj.path or nil,
            recorder_ok = REC.ok, recorder_error = (not REC.ok) and REC.error or nil}
    end

    local legal = build_legal(phase, true, nil)
    local ok, why = validate(atype, cparams, legal.actions)
    if not ok then return reject(atype, cparams, meta, phase, why) end

    -- Snapshot the decision point before executing
    local obs, hidden, refs
    if REC.traj then
        obs = build_obs(phase)
        hidden = build_hidden()
        refs = build_refs(atype, cparams)
    end

    local ok_exec, exec_res = pcall(EXEC[atype], cparams)
    local result
    if not ok_exec then
        log_error(atype .. " failed: " .. tostring(exec_res))
        result = {ok = false, error = "execution error: " .. tostring(exec_res)}
    elseif type(exec_res) == "string" then
        -- Refused by the game's own check after validation: nothing was executed
        return reject(atype, cparams, meta, phase, exec_res)
    else
        result = {ok = true}
    end

    local step = nil
    if REC.traj then
        step = REC.traj.steps
        rec_write({
            t = "step", i = step, ts_ms = now_ms(),
            obs = obs, hidden = hidden, legal = legal,
            action = {type = atype, params = cparams}, refs = refs, meta = meta, result = result,
        })
        REC.traj.steps = REC.traj.steps + 1
    end
    result.step = step
    return result
end

--------------------------------------------------------------------------------
-- /preview (read-only)
--------------------------------------------------------------------------------

local function handle_preview(body)
    local req = json_decode(body or "")
    local idx = type(req) == "table" and req.card_indices
    if type(idx) ~= "table" or #idx == 0 then return {ok = false, error = "body must be {card_indices:[...]}"} end
    if not (G and G.GAME and G.STAGE == G.STAGES.RUN and G.hand and G.hand.cards and #G.hand.cards > 0) then
        return {ok = false, error = "no hand to preview"}
    end
    if #idx > 5 then return {ok = false, error = "at most 5 cards"} end
    local cards, seen = {}, {}
    for _, i in ipairs(idx) do
        if not is_int(i) or not G.hand.cards[i] or seen[i] then
            return {ok = false, error = "invalid or duplicate hand index " .. tostring(i)}
        end
        seen[i] = true
        cards[#cards + 1] = G.hand.cards[i]
    end
    for _, c in ipairs(cards) do
        if c.facing == "back" then return {ok = true, hand = nil, hidden = true} end
    end
    local blind = G.GAME.blind
    local saved_triggered, saved_throw = blind and blind.triggered, G.boss_throw_hand
    local ok, text, _, poker_hands, scoring, disp = pcall(G.FUNCS.get_poker_hand_info, cards)
    if not ok then return {ok = false, error = "get_poker_hand_info failed: " .. tostring(text)} end
    if text == "NULL" then return {ok = true, hand = nil} end
    local debuffed = false
    if blind and G.GAME.facing_blind and blind.debuff_hand then
        local ok_d, d = pcall(blind.debuff_hand, blind, cards, poker_hands, text, true)
        debuffed = ok_d and bool(d)
    end
    if blind then blind.triggered = saved_triggered end
    G.boss_throw_hand = saved_throw
    -- Same scoring set as G.FUNCS.evaluate_play: Splash scores everything, Stone cards always score
    local scoring_set = {}
    for _, c in ipairs(scoring or {}) do scoring_set[c] = true end
    local splash = next(find_joker("Splash")) ~= nil
    for _, c in ipairs(cards) do
        if splash or (c.ability and c.ability.effect == "Stone Card") then scoring_set[c] = true end
    end
    local positions = arr()
    for i, c in ipairs(G.hand.cards) do
        if scoring_set[c] then positions[#positions + 1] = i end
    end
    local h = G.GAME.hands[text] or {}
    return {ok = true, hand = text, display = disp, scoring = positions, level = h.level, chips = h.chips,
        mult = h.mult, blind_debuffed = debuffed}
end

--------------------------------------------------------------------------------
-- HTTP handlers
--------------------------------------------------------------------------------

local handlers = {}

local function envelope(t, phase)
    local settled, reason = settle_status(phase)
    t.settled = settled
    t.settle_reason = reason
    t.timestamp_ms = now_ms()
    t.step = REC.traj and REC.traj.steps or nil
    t.trajectory = REC.last_path
    return t
end

function handlers.GET_health()
    return {
        status = "ok",
        version = CONFIG.schema_version,
        bridge_version = BRIDGE_VERSION,
        bridge_hash = REC.bridge_hash,
        bridge_hash_error = REC.bridge_hash_error,
        game_version = G and G.VERSION,
        lovely_version = lovely_version(),
        git_sha = CONFIG.git_sha,
        port = CONFIG.port,
        uptime_ms = start_time and math.floor((socket.gettime() - start_time) * 1000) or 0,
        request_count = request_count,
        error_count = error_count,
        last_error = last_error,
        unlocked = unlock_done,
        data_dir = CONFIG.data_dir,
        recorder_ok = REC.ok and CONFIG.data_dir ~= nil,
        recorder_error = REC.error,
        recorder_error_count = REC.error_count,
        trajectory_open = REC.traj ~= nil,
        trajectory_path = REC.last_path,
        trajectory_steps = REC.traj and REC.traj.steps or nil,
    }
end

function handlers.GET_state()
    local phase = get_phase()
    return envelope(build_obs(phase), phase)
end

function handlers.GET_legal()
    local phase = get_phase()
    local settled, reason = settle_status(phase)
    return build_legal(phase, settled, reason)
end

function handlers.POST_action(req)
    return handle_action(req.body)
end

function handlers.POST_preview(req)
    return handle_preview(req.body)
end

function handlers.OPTIONS_any()
    return {}
end

-- Test-only state surgery (e.g. make a joker eternal to exercise a rejection). Disabled unless the
-- instance was launched with BALATRO_RL_DEBUG=1. Never an action: it writes a `debug` line and marks the
-- open trajectory tainted (its end line carries tainted:true), so tooling must quarantine it.
handlers["POST_debug/eval"] = function(req)
    if not CONFIG.debug_eval then return {ok = false, error = "debug eval disabled (set BALATRO_RL_DEBUG=1)"} end
    local body = json_decode(req.body or "")
    local code = type(body) == "table" and body.lua
    if type(code) ~= "string" then return {ok = false, error = "body must be {lua: <chunk>}"} end
    local fn, err = loadstring(code, "=debug_eval")
    if not fn then return {ok = false, error = tostring(err)} end
    local ok, res = pcall(fn)
    if REC.traj then
        REC.traj.tainted = true
        rec_write({t = "debug", i = REC.traj.steps, ts_ms = now_ms(), lua = code, ok = ok})
    end
    if not ok then return {ok = false, error = tostring(res)} end
    return {ok = true, result = plain(res)}
end

-- Read-only debugging aid (not part of the data contract)
function handlers.GET_debug()
    local result = {g_funcs = arr(), locks = {}, events = {}}
    if G and G.FUNCS then
        for k, v in pairs(G.FUNCS) do
            if type(v) == "function" then result.g_funcs[#result.g_funcs + 1] = k end
        end
        table.sort(result.g_funcs)
    end
    if G then
        result.state = G.STATE
        result.stage = G.STAGE
        result.state_complete = G.STATE_COMPLETE
        result.stop_use = G.GAME and G.GAME.STOP_USE
        result.paused = G.SETTINGS and G.SETTINGS.paused
        result.overlay = G.OVERLAY_MENU ~= nil
        for k, v in pairs(G.CONTROLLER and G.CONTROLLER.locks or {}) do result.locks[tostring(k)] = tostring(v) end
        local q = G.E_MANAGER and G.E_MANAGER.queues and G.E_MANAGER.queues.base or {}
        result.events = {total = #q, blocking_pending = 0}
        for _, ev in ipairs(q) do
            if ev.blocking and not ev.complete then result.events.blocking_pending = result.events.blocking_pending + 1 end
        end
    end
    return result
end

--------------------------------------------------------------------------------
-- Server loop
--------------------------------------------------------------------------------

local pending_clients = {}

local function handle_request(client, pc)
    -- Non-blocking read; data is buffered on the pending-client record until headers and Content-Length
    -- bytes have arrived: urllib3 2.x sends the body in a separate send(), which on Windows often lands a
    -- frame later, and closing a socket with an unread body makes Windows reset the connection.
    client:settimeout(0)
    local chunk, err, partial = client:receive(65536)
    pc.buf = (pc.buf or "") .. (chunk or partial or "")
    local data = pc.buf
    if #data == 0 or not data:find("\r\n\r\n", 1, true) then return false end

    local req = parse_http_request(data)
    if not req then
        request_count = request_count + 1
        send_json(client, 400, {error = "Invalid HTTP request"})
        return true
    end
    if #(req.body or "") < (tonumber(req.headers["content-length"]) or 0) then return false end

    request_count = request_count + 1
    local path = (req.path:match("^([^?]+)") or req.path):gsub("^/+", "")
    local handler = handlers[req.method .. "_" .. path]
    if not handler and req.method == "OPTIONS" then handler = handlers.OPTIONS_any end
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
    local client = server:accept()
    if client then
        client:settimeout(0)
        pending_clients[#pending_clients + 1] = {socket = client, time = socket.gettime()}
    end
    local i = 1
    while i <= #pending_clients do
        local pc = pending_clients[i]
        local done = false
        if (socket.gettime() - pc.time) > 5 then
            pc.socket:close()
            done = true
        else
            local ok, result = pcall(handle_request, pc.socket, pc)
            if not ok then
                log_error("Request handling error: " .. tostring(result))
                pc.socket:close()
                done = true
            elseif result then
                pc.socket:close()
                done = true
            end
        end
        if done then table.remove(pending_clients, i) else i = i + 1 end
    end
end

--------------------------------------------------------------------------------
-- Profile setup (boot only; never an action)
--------------------------------------------------------------------------------

-- Unlock and discover every item (mirrors G.FUNCS.unlock_all) and mark the tutorial done, so every
-- harness profile has the full pools. Runs once per boot, before the menu reports settled.
local function unlock_everything()
    local prof = G.PROFILES and G.SETTINGS and G.PROFILES[G.SETTINGS.profile]
    if not (prof and G.P_CENTERS and G.P_BLINDS and G.P_TAGS) then return false end
    prof.all_unlocked = true
    if G.P_LOCKED then EMPTY(G.P_LOCKED) end
    for _, pool in ipairs({G.P_CENTERS, G.P_BLINDS, G.P_TAGS, G.P_SEALS or {}}) do
        for _, v in pairs(pool) do
            if type(v) == "table" and not v.demo and not v.wip then
                v.alerted = true
                v.discovered = true
                v.unlocked = true
            end
        end
    end
    pcall(set_profile_progress)
    pcall(set_discover_tallies)
    pcall(function() G:save_progress() end)
    if not G.SETTINGS.tutorial_complete then
        G.SETTINGS.tutorial_complete = true
        G.SETTINGS.tutorial_progress = nil
        pcall(function() G:save_settings() end)
    end
    if G.FILE_HANDLER then G.FILE_HANDLER.force = true end
    unlock_done = true
    log_info("Unlocked and discovered all items for profile " .. tostring(G.SETTINGS.profile))
    return true
end

--------------------------------------------------------------------------------
-- Init / per-frame update
--------------------------------------------------------------------------------

function RLBridge.init()
    log_info("Initializing RL Bridge " .. BRIDGE_VERSION .. " (Lovely-only)")
    local hash, herr = compute_bridge_hash()
    REC.bridge_hash = hash
    REC.bridge_hash_error = herr
    if not hash then log_error("bridge_hash unavailable: " .. tostring(herr)) end
    if not CONFIG.data_dir then
        rec_fail("BALATRO_RL_DATA_DIR not set: runs will not be recorded")
    end

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
    server:settimeout(0)
    start_time = socket.gettime()
    log_info("HTTP server started on http://" .. CONFIG.host .. ":" .. CONFIG.port)
    return true
end

function RLBridge.update(dt)
    if not unlock_done and G and G.STAGE and G.STAGE ~= G.STAGES.SPLASH then pcall(unlock_everything) end
    local ok, err = pcall(rec_watch)
    if not ok then rec_fail("watch failed: " .. tostring(err)) end
    server_tick()
end

RLBridge.init()

return RLBridge
