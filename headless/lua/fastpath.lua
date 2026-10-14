--- Headless fast path: optional patches that make the unmodified game source cheaper to run without a screen.
---
--- Source patches are exact text replacements applied to game modules at load time (like Lovely patches);
--- each must match exactly once, so a game update that changes the patched code fails loudly at boot
--- instead of running unpatched. Every optimization is either a pure reformulation with identical semantics
--- or skips work whose only effect is on rendering; the comment on each states the argument from the game
--- source. Gate: `balatro-headless replay --manifest` must stay at 100% (docs/HEADLESS.md, "Fast path").
---
--- Optimizations are named so they can be toggled one by one (Engine(fastpath=...), CLI --fastpath).
---
--- Rendering state, as used below: a Moveable's visible transform VT and the easing state that drives it
--- (velocity, STATIONARY, juice, pinch, sprite_facing), UI layout (UIBox/UIElement/DynaText transforms and
--- text metrics), particles and sprite animation frames. The game reads VT outside draw/move code in
--- exactly these places (grep `VT` over the source):
---   game.lua:3090 / 3326   shop and round-eval slide-in gates on G.shop / G.round_eval (UIBoxes)
---   card.lua:1787          booster gate on G.pack_cards.VT.y (a CardArea)
---   card.lua:4129,4137     Card:update flip: VT.w <= 0 -> sprite_facing/pinch (both rendering-only)
---   button_callbacks.lua:2632  blind_choice_handler on G.blind_select.VT.y (UI styling only)
---   UI_definitions.lua:309,418 initial T of card popups/buttons (UI layout)
--- Positions (T) never feed game state except through Card/CardArea transforms: card T.x (set by
--- CardArea:align_cards, which adds card.shadow_parrallax.x/30) decides the order of area.cards. Cursor
--- collision never happens headless (G.DRAW_HASH is filled only by draw functions, so
--- Controller:get_cursor_collision returns at its `not G.DRAW_HASH[1]` guard), and the bridge reads no
--- transform at all.

local P = {}

P.NAMES = {"nojit", "moves", "cardmove", "uiupdate", "cardupdate", "remove", "gc"}

-- module name (as passed to require) -> list of {opt, old, new}
P.patches = {
    game = {
        -- moves: the per-frame move pass visits only HEADLESS_FP.kept: the moveables whose class is not in
        -- HEADLESS_FP.skip_move (rendering-only transforms, see P.install), plus UIBoxes so the two
        -- slide-in gate boxes G.shop / G.round_eval keep their place, in G.MOVEABLES order (the list is
        -- maintained by Moveable:init / Moveable:remove, see the engine/moveable patches). The pass itself
        -- never creates or removes moveables (moves only write transforms; CardArea:move's align_cards
        -- only flips, positions and sorts cards), so visiting the kept subsequence in order is the same as
        -- visiting G.MOVEABLES and skipping the rest. A kept object whose major is skipped still gets it
        -- moved on demand (Moveable.move moves `role.major` first), so every Card/CardArea transform,
        -- including G.pack_cards inside the booster UIBox, is computed as before.
        {
            "moves",
            [[
        for k, v in pairs(self.MOVEABLES) do
            if v.FRAME.MOVE < G.FRAMES.MOVE then v:move(move_dt) end
        end]],
            [[
        local _fp_kept, _fp_now, _fp_shop, _fp_reval, _fp_UIBox, _fp_gmt = HEADLESS_FP.kept, G.FRAMES.MOVE, G.shop, G.round_eval, UIBox, getmetatable
        for _fp_i = 1, #_fp_kept do
            local v = _fp_kept[_fp_i]
            if v.FRAME.MOVE < _fp_now and (_fp_gmt(v) ~= _fp_UIBox or v == _fp_shop or v == _fp_reval) then v:move(move_dt) end
        end]],
        },
        -- moves/uiupdate: the update pass calls update only for objects outside HEADLESS_FP.skip_update
        -- and, with uiupdate, for UIElements whose func is not rendering-only. Skipped objects are not given
        -- the `states.collide.is = false` reset: it is already false for every object headless (it is set
        -- true only by Controller:get_cursor_collision for cursor hits and the drag target,
        -- controller.lua:960,977; there is no cursor input).
        -- The pass walks HEADLESS_FP.upd (G.MOVEABLES order minus skip_update classes) instead of all of
        -- G.MOVEABLES. That equals the stock `pairs` walk as long as no moveable is removed during an update
        -- (appends land at the end of both lists). If an update removes moveables, the walk stops after
        -- that call and continues as the stock loop would: `next(G.MOVEABLES, k)` from the stock key k of
        -- the object just updated, reconstructed from the removal log (HEADLESS_FP.resume_key).
        {
            "moves",
            [[
        for k, v in pairs(self.MOVEABLES) do
            v:update(dt*self.SPEEDFACTOR)
            v.states.collide.is = false
        end]],
            [[
        local _fp = HEADLESS_FP
        local _fp_skip_upd, _fp_UIE, _fp_vis, _fp_gmt, _fp_U = _fp.skip_update, _fp.uie_class, _fp.visual_funcs, getmetatable, _fp.upd
        local _fp_i, _fp_resume = 1, nil
        _fp.nremovals = 0
        _fp.in_update_pass = true
        while true do
            local v = _fp_U[_fp_i]
            if v == nil then break end
            if _fp_gmt(v) ~= _fp_UIE or (v.config.func and not _fp_vis[v.config.func]) then
                v:update(dt*self.SPEEDFACTOR)
                v.states.collide.is = false
                if _fp.nremovals > 0 then _fp_resume = _fp.resume_key(self.MOVEABLES, v); break end
            end
            _fp_i = _fp_i + 1
        end
        _fp.in_update_pass = false
        if _fp_resume then
            for k, v in next, self.MOVEABLES, _fp_resume do
                local _mt = _fp_gmt(v)
                if not _fp_skip_upd[_mt] and (_mt ~= _fp_UIE or (v.config.func and not _fp_vis[v.config.func])) then
                    v:update(dt*self.SPEEDFACTOR)
                    v.states.collide.is = false
                end
            end
        end]],
        },
        -- uiupdate: AnimatedSprite:animate only advances the sprite's animation frame (animatedsprite.lua:77).
        {
            "uiupdate",
            [[
        for k, v in pairs(self.ANIMATIONS) do
            v:animate(self.real_dt*self.SPEEDFACTOR)
        end]],
            [[
        if not HEADLESS_FP.skip_animate then for k, v in pairs(self.ANIMATIONS) do
            v:animate(self.real_dt*self.SPEEDFACTOR)
        end end]],
        },
        -- uiupdate: the persistent background-spin event (Game:start_run) eases G.ARGS.spin and
        -- G.TIMERS.BACKGROUND, which only the background shader and the BACKGROUND timer read; its func is
        -- replaced by the no-op HEADLESS_FP.spin_noop (the event stays queued, non-blocking, as before).
        {
            "uiupdate",
            "        func = (function() \n            local _dt = G.ARGS.spin.amount > G.ARGS.spin.eased and G.real_dt*2. or 0.3*G.real_dt",
            "        func = HEADLESS_FP.spin_noop or (function() \n            local _dt = G.ARGS.spin.amount > G.ARGS.spin.eased and G.real_dt*2. or 0.3*G.real_dt",
        },
    },
    card = {
        -- cardmove: a Major card's move without the VT easing (HEADLESS_FP.major_move).
        {
            "cardmove",
            [[
function Card:move(dt)
    Moveable.move(self, dt)]],
            [[
function Card:move(dt)
    if self.role.role_type == 'Major' then HEADLESS_FP.major_move(self, dt) else Moveable.move(self, dt) end]],
        },
        -- cardupdate: Card:update ends with a run of blocks, each guarded by `if self.ability.name == ...`
        -- (Temperance ... Swashbuckler). The run is wrapped in one lookup of the card's name in the set of
        -- names those guards test, extracted from the wrapped source at load (P.post.card), so cards with
        -- none of these names skip ~15 failing comparisons. Nothing in the run changes ability.name.
        {
            "cardupdate",
            [[
        self.sell_cost_label = self.facing == 'back' and '?' or self.sell_cost

        if self.ability.name == 'Temperance' then
            self.ability.money = 0
            for i = 1, #G.jokers.cards do]],
            [[
        self.sell_cost_label = self.facing == 'back' and '?' or self.sell_cost
        if HEADLESS_FP.card_update_names[self.ability.name] then --[==[fp:names]==]
        if self.ability.name == 'Temperance' then
            self.ability.money = 0
            for i = 1, #G.jokers.cards do]],
        },
        {
            "cardupdate",
            [[
            self.ability.mult = sell_cost
        end
    else
        if self.ability.name == 'Temperance' then]],
            [[
            self.ability.mult = sell_cost
        end end --[==[/fp:names]==]
    else
        if self.ability.name == 'Temperance' then]],
        },
    },
    ["engine/moveable"] = {
        -- moves: keep HEADLESS_FP.kept in step with G.MOVEABLES (its only writers are these two functions).
        {
            "moves",
            "    table.insert(G.MOVEABLES, self)\n",
            "    table.insert(G.MOVEABLES, self)\n    HEADLESS_FP.track_moveable(self)\n",
        },
        {
            "moves",
            "function Moveable:remove()\n",
            "function Moveable:remove()\n    HEADLESS_FP.untrack_moveable(self)\n",
        },
    },
}

-- remove: Node:remove and Moveable:remove find the object in instance lists with `pairs` + table.remove.
-- These lists are only appended with table.insert (node.lua:79,85,241, moveable.lua:77,79, text.lua:60,
-- particles.lua:59) and shrunk with table.remove, so they are dense arrays and `pairs` visits 1..n in
-- order; every object is inserted into each list at most once (only by its own init), so the stock
-- first-match index is the only match. HEADLESS_FP.remove_from searches from the end (objects are
-- mostly removed newest-first) and falls back to the stock loop if the list has keys beyond #t.
-- G.STAGE_OBJECTS lists also keep a membership hint (a superset of the list: added at the single
-- insertion site, node.lua:85, dropped when remove_from or remove_all takes the object out), so the
-- common miss -- Game:delete_run's remove_all(G.STAGE_OBJECTS[G.STAGE]) takes each object out of the
-- list before calling its remove() -- costs one lookup instead of a scan of every node of the run.
for _, spec in ipairs({
    {"engine/node", "G.I.POPUP"}, {"engine/node", "G.I.NODE"}, {"engine/node", "G.STAGE_OBJECTS[G.STAGE]"},
    {"engine/moveable", "G.MOVEABLES"}, {"engine/moveable", "G.I.MOVEABLE"},
}) do
    local mod, list = spec[1], spec[2]
    P.patches[mod] = P.patches[mod] or {}
    table.insert(P.patches[mod], {
        "remove",
        "    for k, v in pairs(" .. list .. ") do\n        if v == self then\n            table.remove(" .. list ..
            ", k)\n            break;\n        end\n    end",
        "    HEADLESS_FP.remove_from(" .. list .. ", self)",
    })
end
table.insert(P.patches["engine/node"], {
    "remove",
    "        table.insert(G.STAGE_OBJECTS[G.STAGE], self)\n",
    "        table.insert(G.STAGE_OBJECTS[G.STAGE], self)\n        HEADLESS_FP.note_member(G.STAGE_OBJECTS[G.STAGE], self)\n",
})
P.patches["functions/misc_functions"] = {
    {
        "remove",
        "    local v=t[i]\n    table.remove(t, i)\n",
        "    local v=t[i]\n    table.remove(t, i)\n    HEADLESS_FP.forget_member(t, v)\n",
    },
}

-- Post-processing after a module's patches are applied: module name -> function(src).
P.post = {}
P.card_update_names = {}

function P.post.card(src)
    local a = src:find("--[==[fp:names]==]", 1, true)
    if not a then return end
    local b = assert(src:find("        end end --[==[/fp:names]==]", a, true), "fastpath: cardupdate end marker missing")
    local region = src:sub(a, b - 1)
    -- Every top-level statement of the wrapped run must be a pure name test (or its `end`), otherwise the
    -- wrapper could skip a block that does not depend on the name.
    for line in region:gmatch("[^\n]+") do
        if line:match("^        %S") then
            local norm = line:gsub("%s+$", ""):gsub("self%.ability%.name == (['\"]).-%1", "N")
            assert(norm == "        end" or norm:match("^        if N then$") or norm:match("^        if N or N then$"),
                "fastpath: cardupdate: unexpected top-level statement: " .. line)
        end
    end
    for _, name in region:gmatch("self%.ability%.name == (['\"])(.-)%1") do
        P.card_update_names[name] = true
    end
    assert(next(P.card_update_names), "fastpath: cardupdate: no names found")
end

local function count(s, sub)
    local n, at = 0, 1
    while true do
        local i = s:find(sub, at, true)
        if not i then return n end
        n, at = n + 1, i + #sub
    end
end

--- Apply the enabled patches for module `name` to `src`; errors unless every enabled patch matches once.
function P.apply(name, src, enabled)
    local list = P.patches[name]
    if not list then return src end
    assert(not src:find("\r", 1, true), "fastpath: unexpected CR in " .. name)
    for i, p in ipairs(list) do
        if enabled[p[1]] then
            local n = count(src, p[2])
            assert(n == 1, ("fastpath: patch %d (%s) for %s matched %d times (expected 1)"):format(i, p[1], name, n))
            local at = src:find(p[2], 1, true)
            src = src:sub(1, at - 1) .. p[3] .. src:sub(at + #p[2])
        end
    end
    if P.post[name] then P.post[name](src) end
    return src
end

-- uiupdate: G.FUNCS run from UIElement:update (config.func) whose effects are rendering-only. Each writes
-- only UI element config/children (colour, button, scale, minh, text, alerts, pips), recalculates UI
-- layout, or display state nothing but the UI reads:
--   G.GAME.chips_text, current_hand.{chip,mult,chip_total,handname}_text (read only by these funcs and the
--   HUD DynaTexts), G.GAME.blind.states.visible (draw), G.ARGS.<chip|mult>_flames (flame shader and
--   modulate_sound), G.CONTROLLER:snap_to (cursor focus, consumed only with a gamepad).
-- The bridge computes legality itself (it never reads UI button state). Unlisted funcs still run.
local VISUAL_FUNCS = {
    "HUD_blind_visible", "HUD_blind_debuff", "HUD_blind_debuff_prefix", "HUD_blind_reward",   -- button_callbacks.lua:125-187
    "high_score_alert", "set_button_pip",                                                   -- :372, :408
    "chip_UI_set", "blind_chip_UI_scale", "hand_mult_UI_set", "hand_chip_UI_set",           -- :1891-1935
    "hand_chip_total_UI_set", "flame_handler", "hand_text_UI_set",                         -- :1937-2046
    "can_play", "can_discard",                                                              -- :2048, :2092
    "blind_choice_handler", "hover_tag_proxy",                                              -- :2631, :2718
}

--- Runtime part, called once the game source is loaded (classes exist) and before love.load.
function P.install(enabled)
    local fp = {skip_move = {}, skip_update = {}}

    -- nojit: run LuaJIT 2.0 as a pure interpreter. The game's hot loops are `pairs` loops and closures
    -- (ITERN/FNEW are NYI in 2.0), so traces abort and are retried endlessly; the trace recorder costs more
    -- than it saves. Interpreter and JIT use the same IEEE double arithmetic and libm calls.
    if enabled.nojit then
        jit.off()
        jit.flush()
    end

    if enabled.moves then
        -- Classes whose move only affects rendering state:
        --   Sprite/AnimatedSprite: card faces (Glued to the card), blind chips, tag icons; read only by
        --     draw code and never collide (collide.can = false, card.lua:158,191,217).
        --   Moveable: card shadows (card.lua:39), UI placeholders (flames, jimbo_spot, infotips),
        --     G.ROOM_ATTACH (moved on demand by the UIBoxes attached to it).
        --   UIBox/UIElement/DynaText: UI layout (G.shop / G.round_eval stay in the pass by identity).
        --   Blind: Blind:move = Moveable.move + Blind:align (blind.lua:654,667), positions of its sprites.
        --   Particles: Particles:move ages particles (particles.lua:100).
        for _, cls in ipairs({Sprite, AnimatedSprite, Moveable, UIBox, UIElement, DynaText, Blind, Particles}) do
            fp.skip_move[cls] = true
        end
        -- Exact: these classes resolve `update` to the empty Node.update.
        for _, cls in ipairs({Moveable, Sprite, AnimatedSprite, UIBox, CardArea, Card, Blind, DynaText,
                              UIElement, Particles, Card_Character}) do
            if cls.update == Node.update then fp.skip_update[cls] = true end
        end
        -- The passes' lists, in G.MOVEABLES order: kept (move pass: minus skip_move classes, UIBoxes stay,
        -- see the patch) and upd (update pass: minus skip_update classes). While the update pass runs,
        -- removals from G.MOVEABLES are logged with their index (for resume_key).
        local kept, upd, skip, skip_upd, ui_box, gmt, tremove = {}, {}, fp.skip_move, fp.skip_update, UIBox,
            getmetatable, table.remove
        local rem_obj, rem_idx = {}, {}
        fp.kept, fp.upd, fp.nremovals, fp.in_update_pass = kept, upd, 0, false
        local function drop(list, obj)
            for i = #list, 1, -1 do
                if list[i] == obj then
                    tremove(list, i)
                    return
                end
            end
        end
        -- A UIElement's config.func comes from its UI definition (set before Moveable.init runs in
        -- UIElement:set_values) and is only ever cleared afterwards (button_callbacks.lua:212), so an
        -- element whose update is rendering-only when tracked stays that way (uiupdate).
        fp.track_moveable = function(obj)
            local mt = gmt(obj)
            if not skip[mt] or mt == ui_box then kept[#kept + 1] = obj end
            if not skip_upd[mt] then
                local f = mt == fp.uie_class and obj.config.func
                if f ~= nil and not (f and fp.visual_funcs[f]) then upd[#upd + 1] = obj end
            end
        end
        fp.untrack_moveable = function(obj)
            drop(kept, obj)
            drop(upd, obj)
            if fp.in_update_pass then
                local M = G.MOVEABLES
                for j = 1, #M do
                    if M[j] == obj then
                        local n = fp.nremovals + 1
                        fp.nremovals, rem_obj[n], rem_idx[n] = n, obj, j
                        return
                    end
                end
            end
        end
        -- The key the stock loop would hold for `v` (its G.MOVEABLES index before the logged removals):
        -- a removal at index j shifts every later element down by one, so undo them newest first.
        fp.resume_key = function(M, v)
            local n, idx, last = fp.nremovals, nil, fp.nremovals
            for i = n, 1, -1 do
                if rem_obj[i] == v then idx, last = rem_idx[i], i - 1; break end
            end
            if not idx then
                for j = 1, #M do
                    if M[j] == v then idx = j; break end
                end
                assert(idx, "fastpath: updated moveable vanished from G.MOVEABLES")
            end
            for i = last, 1, -1 do
                if rem_idx[i] <= idx then idx = idx + 1 end
            end
            return idx
        end
    end

    fp.visual_funcs = {}
    if enabled.uiupdate then
        assert(enabled.moves, "fastpath: uiupdate needs moves (it extends the patched update pass)")
        -- DynaText:update (text.lua:64) rebuilds letter tables, text metrics and pop-in animation;
        -- Particles:update (particles.lua:63) spawns particles. Neither writes anything outside the object.
        fp.skip_update[DynaText] = true
        fp.skip_update[Particles] = true
        fp.skip_animate = true
        -- UIElement:update (ui.lua:938): button_delay/button_temp (click handling), the per-element func,
        -- update_text (UIT.T: text from ref_table + layout recalculation) and update_object (UIT.O:
        -- object swap/recalc, refresh_movement, hover popups). All but an unlisted func are UI-only, so an
        -- element's update runs only if it has a func that is not in VISUAL_FUNCS.
        local visual = fp.visual_funcs
        for _, f in ipairs(VISUAL_FUNCS) do
            assert(G.FUNCS[f], "fastpath: G.FUNCS." .. f .. " not found")
            visual[f] = true
        end
        fp.uie_class = UIElement
        -- Game code also calls UIElement:update directly (update_hand_text, common_events.lua:510,532,
        -- for HUD elements whose funcs are listed); same rule.
        local uie_update = UIElement.update
        UIElement.update = function(self, dt)
            local f = self.config.func
            if f ~= nil and not visual[f] then return uie_update(self, dt) end
        end
        fp.spin_noop = function() end
    end

    if enabled.cardmove then
        -- Moveable.move (moveable.lua:278) for a Major card minus move_juice/move_xy/move_r/move_scale/
        -- move_wh, which write only VT, velocity, STATIONARY and juice (rendering state). Kept: the frame
        -- bookkeeping, align_to_major (called unless its own early-return condition holds,
        -- moveable.lua:115-130), calculate_parrallax inlined with the same expression (card
        -- shadow_parrallax feeds card T.x in CardArea:align_cards) and lr_clamp (writes T). STATIONARY is
        -- read only by the moves of Minor children (UI attached to the card: popups, buttons, price tags).
        fp.major_move = function(self, dt)
            local F, now = self.FRAME, G.FRAMES.MOVE
            if F.MOVE >= now then return end
            F.OLD_MAJOR = F.MAJOR
            F.MAJOR = nil
            F.MOVE = now
            if not self.created_on_pause and G.SETTINGS.paused then return end
            local al = self.alignment
            if al.type ~= al.prev_type or al.prev_offset.x ~= al.offset.x or al.prev_offset.y ~= al.offset.y then
                self:align_to_major()
            end
            self.CALCING = nil
            self.STATIONARY = true
            local room = G.ROOM
            if room then
                local T = self.T
                self.shadow_parrallax.x = (T.x + T.w/2 - room.T.w/2)/(room.T.w/2)*1.5
            end
            if self.alignment and self.alignment.lr_clamp then
                self:lr_clamp()
            end
            self.NEW_ALIGNMENT = false
        end
    end

    if enabled.cardupdate then
        fp.card_update_names = P.card_update_names
    end

    if enabled.remove then
        local tremove = table.remove
        local member = {} -- G.STAGE_OBJECTS list -> {obj = true}, a superset of the list's contents
        fp.note_member = function(t, x)
            local s = member[t]
            if not s then s = {}; member[t] = s end
            s[x] = true
        end
        fp.forget_member = function(t, x)
            local s = member[t]
            if s and x ~= nil then s[x] = nil end
        end
        fp.remove_from = function(t, x)
            local s = member[t]
            if s then
                if not s[x] then return end
                s[x] = nil
            end
            local n = #t
            for k = n, 1, -1 do
                if t[k] == x then
                    tremove(t, k)
                    return
                end
            end
            -- Not in 1..n: if t has no other keys the stock loop would not find it either.
            if next(t, n > 0 and n or nil) == nil then return end
            for k, v in pairs(t) do
                if v == x then
                    tremove(t, k)
                    return
                end
            end
        end
    end

    -- gc: garbage-collection policy. nuGC (misc_functions.lua:645, called once per frame by Game:update)
    -- runs incremental GC steps for 0.3 ms of (here virtual) time and then stops the collector. Headless,
    -- a full collection whenever the heap exceeds GC_LIMIT_MB costs less in total than ~3 small steps
    -- every frame. Collection timing has no effect on game state: neither the game nor the bridge uses
    -- weak tables or finalizers.
    if enabled.gc then
        local limit_kb = P.GC_LIMIT_MB * 1024
        local cg = collectgarbage
        nuGC = function()
            if cg("count") > limit_kb then cg("collect") end
            cg("stop")
        end
    end

    -- Moveables that already exist (none in practice: the first are created by love.load) join the lists
    -- once every skip set is final.
    if fp.track_moveable and G and G.MOVEABLES then
        for _, obj in ipairs(G.MOVEABLES) do fp.track_moveable(obj) end
    end
    HEADLESS_FP = fp
end

P.GC_LIMIT_MB = 64

return P
