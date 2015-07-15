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
require "os"
require "string"

_PRESERVATION_VERSION = 5

local err = {
    err_type = nil,
    err_msg = nil
}

local key, channel, build_id, ts, size

errors = {}
size_high_values = {}

function process_message()
    err.err_type = read_message("Fields[DecodeErrorType]") or "MISSING"
    err.err_msg = read_message("Fields[DecodeError]") or "MISSING"
    ts = read_message("Timestamp")
    ts = os.date("%Y.%m.%dT%H:%M:%S", ts/1e9)

    build_id = read_message("Fields[appBuildId]") or "MISSING"
    channel = read_message("Fields[appUpdateChannel]") or "MISSING"

    key = channel .. "-" .. build_id
    errors_for_key = errors[key]
    if not errors_for_key then
        errors[key] = {[err.err_type] = {{ts, err.err_msg}}}
    else
        errors_of_type_for_key = errors_for_key[err.err_type]
        if not errors_of_type_for_key then
            errors_for_key[err.err_type] = {{ts, err.err_msg},}
        else
            errors_of_type_for_key[#errors_of_type_for_key+1] = {ts, err.err_msg}
        end
    end

    if err.err_type == "size" then
        size = tonumber(string.match(err.err_msg, '%d+$'))
        if not size then
            size = 0
        end
        high_value = size_high_values[key]
        if not high_value then
            size_high_values[key] = size
        elseif size > high_value then
            size_high_values[key] = size
        end
    end

    return 0
end

function timer_event(ns)
    local ok, errors_json = pcall(cjson.encode, errors)
    if ok then
        inject_payload("text", "Errors by Channel-BuildID", errors_json)
    end

    local ok, sizes_json = pcall(cjson.encode, size_high_values)
    if ok then
        inject_payload("text", "Highest Size Values by Channel-BuildID", sizes_json)
    end
end
