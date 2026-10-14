--- Headless LOVE 11 replacement: just enough of the `love` API for Balatro's game logic.
---
--- Rendering, audio, input and windowing are inert; love.filesystem serves the game source from the
--- extracted cache directory (read-only) plus an in-memory save directory; love.timer is a virtual clock.
--- `host` supplies the few primitives Lua cannot do alone (sha256, gzip, raw deflate); `cfg` the paths.

return function(cfg, host)
    local love = {}

    ---------------------------------------------------------------------------
    -- Inert objects: any method call is a no-op; getters answer with plausible numbers.
    ---------------------------------------------------------------------------
    local function noop() end
    local inert_mt = {}
    inert_mt.__index = function(t, k)
        local f
        if k == "getWidth" or k == "getPixelWidth" then
            f = function(self) return rawget(self, "_w") or 1 end
        elseif k == "getHeight" or k == "getPixelHeight" then
            f = function(self) return rawget(self, "_h") or 1 end
        elseif k == "getDimensions" or k == "getPixelDimensions" then
            f = function(self) return rawget(self, "_w") or 1, rawget(self, "_h") or 1 end
        elseif k == "isPlaying" or k == "hasGlyphs" then
            f = function() return false end
        else
            f = noop
        end
        rawset(t, k, f)
        return f
    end
    local function inert(w, h) return setmetatable({_w = w, _h = h}, inert_mt) end

    -- Fonts: width = chars * size/2, height = size. Only UI layout reads these.
    local function new_font(size)
        size = tonumber(size) or 12
        local f = inert(size, size)
        f.getWidth = function(_, s) return #tostring(s or "") * size * 0.5 end
        f.getHeight = function() return size end
        f.getLineHeight = function() return 1 end
        f.getAscent = function() return size * 0.8 end
        f.getDescent = function() return size * 0.2 end
        f.getBaseline = function() return size * 0.8 end
        f.hasGlyphs = function() return true end
        f.getWrap = function(_, s) return #tostring(s or "") * size * 0.5, {tostring(s or "")} end
        return f
    end

    ---------------------------------------------------------------------------
    -- love.graphics (inert)
    ---------------------------------------------------------------------------
    local win = {w = cfg.window_w or 1280, h = cfg.window_h or 720}
    local graphics = {}
    graphics.getWidth = function() return win.w end
    graphics.getHeight = function() return win.h end
    graphics.getDimensions = function() return win.w, win.h end
    graphics.getPixelWidth = graphics.getWidth
    graphics.getPixelHeight = graphics.getHeight
    graphics.getDPIScale = function() return 1 end
    graphics.isActive = function() return false end
    graphics.isCreated = function() return true end
    graphics.newImage = function() return inert(1024, 1024) end
    graphics.newCanvas = function(w, h) return inert(w or win.w, h or win.h) end
    graphics.newShader = function() return inert() end
    graphics.newQuad = function() return inert() end
    graphics.newText = function(font) return inert(1, 1) end
    graphics.newVideo = function() return inert() end
    graphics.newSpriteBatch = function() return inert() end
    graphics.newMesh = function() return inert() end
    graphics.newFont = function(a, b) return new_font(type(a) == "number" and a or b) end
    graphics.setNewFont = graphics.newFont
    graphics.getFont = function() return new_font(12) end
    graphics.getColor = function() return 1, 1, 1, 1 end
    graphics.getCanvas = function() return nil end
    graphics.getShader = function() return nil end
    graphics.getLineWidth = function() return 1 end
    graphics.getStats = function() return {} end
    setmetatable(graphics, {__index = function(t, k)
        rawset(t, k, noop)
        return noop
    end})
    love.graphics = graphics

    ---------------------------------------------------------------------------
    -- love.window
    ---------------------------------------------------------------------------
    local window = {}
    window.getMode = function() return win.w, win.h, {fullscreen = false, vsync = 1, display = 1} end
    window.setMode = function(w, h) win.w, win.h = w or win.w, h or win.h; return true end
    window.updateMode = function(w, h) win.w, win.h = w or win.w, h or win.h; return true end
    window.getDisplayCount = function() return 1 end
    window.getDesktopDimensions = function() return 1920, 1080 end
    window.getFullscreenModes = function() return {{width = 1920, height = 1080}, {width = 1280, height = 720}} end
    window.isOpen = function() return true end
    window.getTitle = function() return "Balatro" end
    window.toPixels = function(v) return v end
    window.fromPixels = function(v) return v end
    window.getDPIScale = function() return 1 end
    window.showMessageBox = function() return 1 end
    setmetatable(window, {__index = function(t, k) rawset(t, k, noop); return noop end})
    love.window = window

    ---------------------------------------------------------------------------
    -- love.audio / love.sound / input devices (inert)
    ---------------------------------------------------------------------------
    local function inert_module()
        return setmetatable({}, {__index = function(t, k) rawset(t, k, noop); return noop end})
    end
    love.audio = inert_module()
    love.audio.newSource = function() return inert() end
    love.sound = inert_module()
    love.mouse = inert_module()
    love.mouse.getPosition = function() return 0, 0 end
    love.mouse.isVisible = function() return false end
    love.mouse.isDown = function() return false end
    love.keyboard = inert_module()
    love.keyboard.isDown = function() return false end
    love.joystick = inert_module()
    love.joystick.getJoysticks = function() return {} end
    love.touch = inert_module()
    love.touch.getTouches = function() return {} end
    love.event = inert_module()
    love.event.poll = function() return function() return nil end end
    love.handlers = {}

    ---------------------------------------------------------------------------
    -- love.system
    ---------------------------------------------------------------------------
    love.system = inert_module()
    -- The live harness runs the Windows build; OS-dependent flags (globals.lua) must match it.
    love.system.getOS = function() return cfg.os_name or "Windows" end
    love.system.getProcessorCount = function() return 1 end
    love.system.getClipboardText = function() return "" end

    ---------------------------------------------------------------------------
    -- love.thread: channels drop everything (save/sound/http threads do not exist)
    ---------------------------------------------------------------------------
    local channel = setmetatable({}, {__index = function(t, k) rawset(t, k, noop); return noop end})
    channel.pop = function() return nil end
    channel.peek = function() return nil end
    channel.demand = function() return nil end
    channel.supply = function() return true end
    channel.getCount = function() return 0 end
    love.thread = {
        newThread = function() return inert() end,
        getChannel = function() return channel end,
        newChannel = function() return channel end,
    }

    ---------------------------------------------------------------------------
    -- love.timer: virtual clock. The game reads it only for perf checkpoints and for nuGC's per-frame
    -- GC time budget (3e-4 s of collectgarbage("step") calls); each read advances it by `timer_tick`, so
    -- nuGC does a fixed, small amount of GC work per frame instead of burning 0.3 ms of wall time.
    -- GC timing has no effect on game state (no weak tables or finalizers in the game source).
    ---------------------------------------------------------------------------
    local vclock, tick = 0, cfg.timer_tick or 1e-4
    love.timer = {
        getTime = function()
            vclock = vclock + tick
            return vclock
        end,
        step = function() return 0 end,
        sleep = noop,
        getFPS = function() return 60 end,
        getDelta = function() return 1 / 60 end,
        getAverageDelta = function() return 1 / 60 end,
    }

    ---------------------------------------------------------------------------
    -- love.data
    ---------------------------------------------------------------------------
    love.data = {
        compress = function(container, format, data, level)
            if format == "gzip" then return host.gzip(data, level or -1) end
            return host.deflate(data, level or -1, format)
        end,
        decompress = function(container, format, data)
            return host.inflate(data, format)
        end,
        hash = function(alg, data) return host.hash(alg, data) end,
        encode = function(container, format, data)
            assert(format == "hex", "love.data.encode: only hex is supported headless")
            return (data:gsub(".", function(c) return string.format("%02x", c:byte()) end))
        end,
    }

    ---------------------------------------------------------------------------
    -- love.filesystem: game source (read-only, from the cache dir) + in-memory save dir
    ---------------------------------------------------------------------------
    local root = cfg.source_dir
    local files, dirs = {}, {[""] = {}}
    for line in io.lines(root .. "/.manifest") do
        files[line] = true
        local parent, name = line:match("^(.*)/([^/]+)$")
        if not parent then parent, name = "", line end
        -- register every ancestor directory
        local p, child = parent, name
        while true do
            dirs[p] = dirs[p] or {}
            if not dirs[p][child] then
                dirs[p][child] = true
            end
            if p == "" then break end
            local pp, pn = p:match("^(.*)/([^/]+)$")
            if not pp then pp, pn = "", p end
            child, p = pn, pp
        end
    end

    local save = {} -- path -> contents (string) or true for a directory
    for k, v in pairs(cfg.save_files or {}) do save[k] = v end

    local function norm(p)
        p = tostring(p):gsub("\\", "/"):gsub("/+", "/"):gsub("^%./", ""):gsub("^/", ""):gsub("/$", "")
        return p
    end

    local function read_source(p)
        if not files[p] then return nil end
        local f = io.open(root .. "/" .. p, "rb")
        if not f then return nil end
        local s = f:read("*a")
        f:close()
        return s
    end

    local fs = {}
    fs.getInfo = function(p)
        p = norm(p)
        local s = save[p]
        if s == true then return {type = "directory"} end
        if s then return {type = "file", size = #s} end
        if files[p] then return {type = "file"} end
        if dirs[p] then return {type = "directory"} end
        return nil
    end
    fs.read = function(a, b)
        -- read(name [, size]) or read(container, name [, size])
        local p = norm((type(b) == "string" and (a == "string" or a == "data")) and b or a)
        local s = save[p]
        if type(s) == "string" then return s, #s end
        s = read_source(p)
        if s then return s, #s end
        return nil, "Could not open file " .. p .. ". Does not exist."
    end
    fs.write = function(p, data) save[norm(p)] = tostring(data); return true end
    fs.append = function(p, data)
        p = norm(p)
        save[p] = (type(save[p]) == "string" and save[p] or "") .. tostring(data)
        return true
    end
    fs.remove = function(p) p = norm(p); local had = save[p] ~= nil; save[p] = nil; return had end
    fs.createDirectory = function(p) save[norm(p)] = true; return true end
    fs.getDirectoryItems = function(p)
        p = norm(p)
        local out = {}
        for name in pairs(dirs[p] or {}) do out[#out + 1] = name end
        table.sort(out)
        return out
    end
    fs.load = function(p)
        local s, err = fs.read(p)
        if not s then return nil, err end
        return loadstring(s, "@" .. norm(p))
    end
    fs.getSourceBaseDirectory = function() return root end
    fs.getSaveDirectory = function() return "headless-save" end
    fs.getIdentity = function() return "Balatro" end
    fs.setIdentity = noop
    fs.isFused = function() return true end
    fs.lines = function(p)
        local s = fs.read(p) or ""
        return s:gmatch("([^\n]*)\n?")
    end
    love.filesystem = fs
    love._save = save

    love.arg = {parseGameArguments = function(a) return a or {} end}
    love.getVersion = function() return 11, 5, 0, "Mysterious Mysteries" end
    return love
end
