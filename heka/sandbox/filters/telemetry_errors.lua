-- This Source Code Form is subject to the terms of the Mozilla Public
-- License, v. 2.0. If a copy of the MPL was not distributed with this
-- file, You can obtain one at http://mozilla.org/MPL/2.0/.

--[[
Telemetry Errors

*Example Heka Configuration*

.. code-block:: ini

    [TelemetryErrors]
    type = "SandboxFilter"
    filename = "lua_filters/telemetry_errors.lua"
    message_matcher = "Type == 'telemetry.error'"
    ticker_interval = 60
    preserve_data = true
--]]

require "cjson"

_PRESERVATION_VERSION = 2 -- Bump if hash algorithm changes.

local err = {
    err_type = nil,
    err_msg = nil
}

function err.hash(self)
    return self.err_type .. "|" .. self.err_msg
end

local hash, channel, build_id, ts

by_build_id = {}
by_channel = {}

function process_message()
    err.err_type = read_message("Fields[DecodeErrorType]") or "MISSING"
    err.err_msg = read_message("Fields[DecodeError]") or "MISSING"
    hash = err:hash()
    ts = read_message("Timestamp")

    build_id = read_message("Fields[appBuildId]") or "MISSING"
    build_errors = by_build_id[build_id]
    if not build_errors then
        by_build_id[build_id] = {[hash] = {ts}}
    else
        err_times = build_errors[hash]
        if not err_times then
            build_errors[hash] = {ts}
        else
            err_times[#err_times+1] = ts
        end
    end

    channel = read_message("Fields[appUpdateChannel]") or "MISSING"
    channel_errors = by_channel[channel]
    if not channel_errors then
        by_channel[channel] = {[hash] = {ts}}
    else
        err_times = channel_errors[hash]
        if not err_times then
            channel_errors[hash] = {ts}
        else
            err_times[#err_times+1] = ts
        end
    end

    return 0
end

function timer_event(ns)
    local ok, build_error_json = pcall(cjson.encode, by_build_id)
    if ok then
        inject_payload("text", "Errors by Build ID", build_error_json)
    end

    local ok, channel_error_json = pcall(cjson.encode, by_channel)
    if ok then
        inject_payload("text", "Errors by Channel", channel_error_json)
    end
end
