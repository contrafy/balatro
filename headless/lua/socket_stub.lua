--- In-memory replacement for LuaSocket, enough for the bridge's non-blocking HTTP server loop.
---
--- socket.tcp() returns a fake listening server whose accept() hands out clients queued by the host
--- (`socket._inject(raw_http_request)`); whatever the bridge sends to a client is collected in
--- `client.out`. The bridge code runs unchanged: same parse, routing, handlers and JSON encoding.

local ffi = require("ffi")

local socket = {}

-- Wall clock in seconds (epoch based); the bridge only uses differences and anchors them to os.time().
if ffi.os == "Windows" then
    pcall(ffi.cdef, "void GetSystemTimeAsFileTime(uint64_t *ft);")
    local ft = ffi.new("uint64_t[1]")
    socket.gettime = function()
        ffi.C.GetSystemTimeAsFileTime(ft)
        return tonumber(ft[0]) / 1e7 - 11644473600
    end
else
    pcall(ffi.cdef, [[
        typedef struct { long tv_sec; long tv_usec; } hl_timeval;
        int gettimeofday(hl_timeval *tv, void *tz);
    ]])
    local tv = ffi.new("hl_timeval")
    socket.gettime = function()
        ffi.C.gettimeofday(tv, nil)
        return tonumber(tv.tv_sec) + tonumber(tv.tv_usec) * 1e-6
    end
end

local incoming = {}

local Client = {}
Client.__index = Client
function Client:settimeout() return 1 end
function Client:receive()
    local data = self.inbuf
    self.inbuf = ""
    -- Non-blocking LuaSocket semantics: fewer bytes than requested -> nil, "timeout", partial
    return nil, "timeout", data
end
function Client:send(data, i, j)
    i = i or 1
    local piece = data:sub(i, j)
    self.out[#self.out + 1] = piece
    return (i - 1) + #piece
end
function Client:close() self.closed = true; return 1 end
function Client:setoption() return 1 end
function Client:getpeername() return "127.0.0.1", 0 end

local Server = {}
Server.__index = Server
function Server:setoption() return 1 end
function Server:bind() return 1 end
function Server:listen() return 1 end
function Server:settimeout() return 1 end
function Server:close() return 1 end
function Server:getsockname() return "127.0.0.1", 0 end
function Server:accept()
    local c = table.remove(incoming, 1)
    if c then return c end
    return nil, "timeout"
end

socket.tcp = function() return setmetatable({}, Server) end
socket.bind = function() return setmetatable({}, Server) end
socket.sleep = function() end
socket._VERSION = "LuaSocket 3.0 (headless stub)"

--- Host side: queue a raw HTTP request; returns the client whose `out` collects the response.
socket._inject = function(raw)
    local c = setmetatable({inbuf = raw, out = {}, closed = false}, Client)
    incoming[#incoming + 1] = c
    return c
end

return socket
