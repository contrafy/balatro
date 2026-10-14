--- Headless Balatro runtime: boots the unmodified game source with the RL bridge under plain LuaJIT.
---
--- The host (python/balatro_env/headless/engine.py, via lupa) calls:
---   H.boot(cfg, host)            stub LOVE, load conf.lua + main.lua (with the bridge's Lovely patch), love.load()
---   H.frames(n)                  run n frames of love.update(dt) with the fixed virtual dt
---   H.settle(max_frames)         run frames until the bridge's own settled predicate holds
---   H.request(method, path, body) one HTTP request through the bridge's server loop (fake socket)
--- Everything the policy sees (obs, /legal, validation, execution, recording) is the bridge's own code.

local H = {}

local cfg, love, socket, bridge
local settle_status, get_phase
local frame_count = 0

-- Same edit as game_mod/BalatroRLBridge/lovely.toml: after `G:update(dt)` in love.update, call the bridge.
local LOVELY_PAYLOAD = "require('balatro_rl_bridge').update(dt)"

local function read_file(path)
    local f = assert(io.open(path, "rb"))
    local s = f:read("*a")
    f:close()
    return s
end

local function patch_main(src)
    local out, n = {}, 0
    for line in (src .. "\n"):gmatch("([^\n]*)\n") do
        out[#out + 1] = line
        local indent, body = line:match("^(%s*)(.-)%s*$")
        if body == "G:update(dt)" then
            out[#out + 1] = indent .. LOVELY_PAYLOAD
            n = n + 1
        end
    end
    assert(n == 1, "lovely pattern 'G:update(dt)' matched " .. n .. " lines in main.lua (expected 1)")
    return table.concat(out, "\n")
end

-- Breadth-first search through function upvalues for a local named `name` (bridge internals).
local function find_upvalue(roots, name)
    local seen, queue = {}, {}
    for _, f in ipairs(roots) do queue[#queue + 1] = f end
    local head = 1
    while head <= #queue do
        local f = queue[head]
        head = head + 1
        if not seen[f] then
            seen[f] = true
            local i = 1
            while true do
                local n, v = debug.getupvalue(f, i)
                if not n then break end
                if n == name and type(v) == "function" then return v end
                if type(v) == "function" then
                    queue[#queue + 1] = v
                elseif type(v) == "table" and n == "handlers" then
                    for _, hv in pairs(v) do
                        if type(hv) == "function" then queue[#queue + 1] = hv end
                    end
                end
                i = i + 1
            end
        end
    end
    error("bridge local function '" .. name .. "' not found")
end

local function steam_stub()
    local ok2 = function() return true, true end
    local st = {
        init = function() return true end,
        shutdown = function() end,
        userStats = {
            getAchievement = ok2,
            setAchievement = function() return true end,
            getStatInt = function() return true, 0 end,
            setStatInt = function() return true end,
            storeStats = function() return true end,
            requestCurrentStats = function() return true end,
        },
        user = {getSteamID = function() return 0 end},
        friends = {setRichPresence = function() return true end},
    }
    return st
end

-- Identifies this loader in place of Lovely (trajectory header `lovely_version`).
H.LOADER_VERSION = "headless-1.0.0"

-- Trajectory files the bridge opens for writing get `"host":"headless"` in their header line. The bridge
-- writes objects with sorted keys and every header key before "host" is a scalar, so the first top-level
-- `,"lovely_version":` (or `,"port":` when absent) is where the key belongs.
local function stamp_header(line)
    if line:sub(1, 1) ~= "{" or not line:find('"t":"header"', 1, true) then return line end
    local at = line:find(',"lovely_version":', 1, true) or line:find(',"port":', 1, true)
    if not at then return line end
    return line:sub(1, at - 1) .. ',"host":"headless"' .. line:sub(at)
end

local open_files = {} -- trajectory files currently open for writing (closed by H.close)

local function wrap_io_open(data_dir)
    local real_open = io.open
    local prefix = data_dir:gsub("\\", "/") .. "/trajectories/"
    local File = {}
    File.__index = File
    function File:write(s, ...)
        if not self.stamped then
            self.stamped = true
            s = stamp_header(s)
        end
        local ok, err = self.f:write(s, ...)
        if not ok then return ok, err end
        return self
    end
    function File:flush() return self.f:flush() end
    function File:close()
        open_files[self] = nil
        return self.f:close()
    end
    function File:seek(...) return self.f:seek(...) end
    function File:setvbuf(...) return self.f:setvbuf(...) end
    io.open = function(path, mode)
        local f, err = real_open(path, mode)
        if f and type(mode) == "string" and mode:sub(1, 1) == "w" and type(path) == "string" and
            path:sub(1, #prefix) == prefix and path:sub(-6) == ".jsonl" then
            local wrapped = setmetatable({f = f}, File)
            open_files[wrapped] = true
            return wrapped
        end
        return f, err
    end
end

--- Close trajectory files left open (a run that never ended). The bridge keeps them open until the run
--- ends; the host calls this before dropping the engine so the files are complete and deletable.
function H.close()
    for f in pairs(open_files) do pcall(f.close, f) end
end

function H.boot(c, host)
    cfg = c
    local lua_dir = cfg.lua_dir

    love = dofile(lua_dir .. "/love_stub.lua")(cfg, host)
    _G.love = love
    package.loaded.love = love
    for k, v in pairs(love) do
        if type(v) == "table" then package.loaded["love." .. k] = v end
    end
    socket = dofile(lua_dir .. "/socket_stub.lua")
    package.loaded.socket = socket
    package.preload.luasteam = steam_stub
    package.preload.lovely = function() return {version = H.LOADER_VERSION} end

    -- Bridge configuration comes only from the host (never from this process's environment).
    local env = cfg.env or {}
    local real_getenv = os.getenv
    os.getenv = function(k)
        if type(k) == "string" and k:sub(1, 11) == "BALATRO_RL_" then return env[k] end
        return real_getenv(k)
    end
    if env.BALATRO_RL_DATA_DIR then wrap_io_open(env.BALATRO_RL_DATA_DIR) end

    if cfg.quiet then
        _G.print = function() end
    end

    package.path = cfg.source_dir .. "/?.lua;" .. package.path
    package.preload.balatro_rl_bridge = function()
        return assert(loadstring(read_file(cfg.bridge_dir .. "/main.lua"), "@balatro_rl_bridge"))()
    end

    -- LOVE boot order: conf.lua (love.conf), main.lua, love.load
    assert(loadstring(read_file(cfg.source_dir .. "/conf.lua"), "@conf.lua"))()
    if love.conf then
        local t = {window = {}, modules = {}, audio = {}}
        love.conf(t)
    end
    assert(loadstring(patch_main(read_file(cfg.source_dir .. "/main.lua")), "@main.lua"))()
    love.load({}, {})
    if love.timer then love.timer.step() end
end

local function frame()
    frame_count = frame_count + 1
    love.update(cfg.dt)
end

function H.frames(n)
    for _ = 1, n do frame() end
    return frame_count
end

local function bridge_fns()
    if settle_status then return end
    bridge = package.loaded.balatro_rl_bridge
    assert(type(bridge) == "table", "bridge not loaded yet")
    settle_status = find_upvalue({bridge.update}, "settle_status")
    get_phase = find_upvalue({bridge.update}, "get_phase")
end

--- Settled per the bridge: returns settled, phase, reason (no frame is run).
function H.status()
    bridge_fns()
    local phase = get_phase()
    local ok, reason = settle_status(phase)
    return ok, phase, reason
end

--- Run frames until settled (checked after each frame), then `extra` more frames while it stays settled.
--- At least one frame always runs: on a live instance every request is served after a full G:update, so
--- per-frame derived state (Card:update tallies, Blueprint compat, ...) is current even when an action
--- queued no events (REORDER). Returns frames_run, settled, phase, reason.
function H.settle(max_frames, extra)
    local start = frame_count
    frame()
    bridge_fns()
    local ok, phase, reason = H.status()
    while not ok and frame_count - start < max_frames do
        frame()
        ok, phase, reason = H.status()
    end
    if ok and extra and extra > 0 then
        for _ = 1, extra do
            frame()
            ok, phase, reason = H.status()
            if not ok then return H.settle(max_frames - (frame_count - start), extra) end
        end
    end
    return frame_count - start, ok, phase, reason
end

--- One request through the bridge's own server loop. Returns the response body (string).
function H.request(method, path, body)
    body = body or ""
    local raw = method .. " " .. path .. " HTTP/1.1\r\nHost: headless\r\nContent-Type: application/json\r\n" ..
        "Content-Length: " .. #body .. "\r\n\r\n" .. body
    local client = socket._inject(raw)
    if not package.loaded.balatro_rl_bridge then frame() end
    bridge = bridge or package.loaded.balatro_rl_bridge
    bridge.update(cfg.dt)
    assert(client.closed, "bridge did not answer the request")
    local resp = table.concat(client.out)
    local sep = resp:find("\r\n\r\n", 1, true)
    local status = tonumber(resp:match("^HTTP/1%.1 (%d+)"))
    return status, sep and resp:sub(sep + 4) or ""
end

function H.frame_count() return frame_count end

return H
