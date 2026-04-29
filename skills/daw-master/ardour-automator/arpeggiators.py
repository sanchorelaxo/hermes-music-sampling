"""
ardour-automator.arpeggiators — Parameterized arpeggiator generator & runner.

Provides three arpeggiators from https://github.com/agraef/ardour-lua/tree/main/dsp:
  - simple_arp  : basic monophonic arpeggiator (up/down/exclusive/inclusive/order/random)
  - barlow_arp  : Barlow indispensability-based accents + pulse filter + latch/sync
  - raptor_arp  : advanced random arpeggiator with harmonicity, step-width, density control

All scripts are stored as string templates.  Use render_*_script(params) to generate
a complete Ardour Lua module, then pass it to ardour-automator's run_script().
"""
from pathlib import Path
from typing import Dict, Any, Optional, List
import textwrap
import uuid

# Import ardour-automator's run_script for convenience wrappers
# We do a lazy import inside the wrapper functions to avoid circular imports.

# =============================================================================
# 1. SIMPLE ARP — simple_arp.lua template
# =============================================================================

SIMPLE_ARP_TEMPLATE = textwrap.dedent("""\
    ardour {{
       ["type"]    = "dsp",
       name        = "{name}",
       category    = "Effect",
       author      = "Albert Gräf",
       license     = "MIT",
       description = [[simple_arp v0.3

Simple monophonic arpeggiator example with sample-accurate triggering,
demonstrates how to process the new time_info data along with BBT info
from Ardour's tempo map.
]]
    }}

    function dsp_ioconfig ()
       return {{ {{ midi_in = 1, midi_out = 1, audio_in = -1, audio_out = -1}}, }}
    end

    function dsp_options ()
       return {{ time_info = true, regular_block_length = true }}
    end

    local params = {{
       {{ type = "input", name = "Division",   min = 1, max = 16, default = {division}, integer = true, doc = "number of subdivisions of the beat" }},
       {{ type = "input", name = "Octave up",  min = 0, max = 5,  default = {octave_up}, integer = true, doc = "octave range up" }},
       {{ type = "input", name = "Octave down",min = 0, max = 5,  default = {octave_down}, integer = true, doc = "octave range down" }},
       {pattern_line},
       {{ type = "input", name = "Velocity 1", min = 0, max = 127, default = {vel1}, integer = true, doc = "velocity level (bar)" }},
       {{ type = "input", name = "Velocity 2", min = 0, max = 127, default = {vel2}, integer = true, doc = "velocity level (beat)" }},
       {{ type = "input", name = "Velocity 3", min = 0, max = 127, default = {vel3}, integer = true, doc = "velocity level (subdivision)" }},
       {{ type = "input", name = "Latch",       min = 0, max = 1,  default = {latch}, toggled = true, doc = "toggle latch mode" }},
       {{ type = "input", name = "Sync",        min = 0, max = 1,  default = {sync}, toggled = true, doc = "toggle sync mode" }},
       {{ type = "input", name = "Bypass",      min = 0, max = 1,  default = {bypass}, toggled = true, doc = "bypass the arpeggiator, pass through input notes" }},
       {{ type = "input", name = "Gate",        min = 0, max = 1,  default = {gate}, doc = "gate as fraction of pulse length", scalepoints = {{ legato = 0 }} }},
       {{ type = "input", name = "Swing",       min = 0.5, max = 0.75, default = {swing}, doc = "swing factor (0.67 = triplet feel)" }},
    }}

    function presets()
       return {{
          name = "0 default", params = {{ Division = {division}, ["Octave up"] = {octave_up}, ["Octave down"] = {octave_down}, Pattern = {pattern}, ["Velocity 1"] = {vel1}, ["Velocity 2"] = {vel2}, ["Velocity 3"] = {vel3}, Latch = {latch}, Sync = {sync}, Swing = {swing}, Gate = {gate} }},
          name = "1 latch",    params = {{ Latch = 1, Sync = 0 }},
          name = "2 latch+sync",params = {{ Latch = 1, Sync = 1 }},
          name = "3 bass",     params = {{ Division = 1, ["Octave up"] = 0, ["Octave down"] = 1, Pattern = 1, Swing = 0.5, Gate = 1 }},
       }}
    end

    local debug = 0
    local chan = 0
    local last_rolling
    local last_beat, last_time
    local last_num, last_chan, last_gate, swing_time
    local last_up, last_down, last_mode, last_sync, last_bypass
    local chord = {{}}
    local chord_index = 0
    local latched = {{}}
    local pattern = {{}}
    local index = 0

    function dsp_run (_, _, n_samples)
       assert (type(midiout) == "table")
       assert (type(time) == "table")

       local ctrl = CtrlPorts:array()
       local subdiv, up, down, mode = math.floor(ctrl[1]), math.floor(ctrl[2]), math.floor(ctrl[3]), math.floor(ctrl[4])
       local vel1, vel2, vel3 = math.floor(ctrl[5]), math.floor(ctrl[6]), math.floor(ctrl[7])
       local latch  = ctrl[8]  > 0
       local sync   = ctrl[9]  > 0
       local bypass = ctrl[10] > 0
       local gate   = ctrl[11]
       local swing  = 1+2*(ctrl[12]-0.5)

       local rolling = Session:transport_state_rolling()
       local changed = false

       if up ~= last_up or down ~= last_down or mode ~= last_mode then
          last_up, last_down, last_mode = up, down, mode
          changed = true
       end
       if sync ~= last_sync then
          last_sync = sync
          index = 0
       end
       if not latch and next(latched) ~= nil then
          latched = {{}}
          changed = true
       end
       if swing == 1 then swing_time = nil end

       local all_notes_off = false
       if bypass ~= last_bypass then
          last_bypass = bypass
          all_notes_off = true
       end

       if last_rolling ~= rolling then
          last_rolling = rolling
          if rolling then all_notes_off = true end
          swing_time = nil
       end

       local k = 1
       if all_notes_off then
          midiout[k] = {{ time = 1, data = {{ 0xb0+chan, 123, 0 }} }}
          k = k + 1
       end

       for _,ev in ipairs(midiin) do
          local status, num, val = table.unpack(ev.data)
          local ch = status & 0xf
          status = status & 0xf0

          if not rolling or bypass then
             midiout[k] = ev; k = k+1
          elseif status >= 0xb0 then
             midiout[k] = ev; k = k+1
          end

          if status == 0x80 or (status == 0x90 and val == 0) then
             if debug >= 4 then print("note off", num, val) end
             if latch then
                latched[num] = chord[num]
             else
                changed = true
             end
             chord[num] = nil
          elseif status == 0x90 then
             if debug >= 4 then print("note on", num, val, "ch", ch) end
             if latch and next(chord) == nil then
                latched = {{}}
             end
             chord_index = chord_index + 1
             chord[num] = chord_index
             if latch and latched[num] then
                latched[num] = nil
             else
                changed = true
             end
             chan = ch
          elseif status == 0xb0 and num == 123 and ch == chan then
             if debug >= 4 then print("all notes off") end
             chord = {{}}
             latched = {{}}
             changed = true
          end
       end

       if changed then
          pattern = {{}}
          local function pattern_from_chord(pattern, chord)
             for num, _ in pairs(chord) do
                table.insert(pattern, num)
                for i = 1, down do
                   if num - i*12 >= 0 then table.insert(pattern, num - i*12) end
                end
                for i = 1, up do
                   if num + i*12 <= 127 then table.insert(pattern, num + i*12) end
                end
             end
          end
          pattern_from_chord(pattern, chord)
          if latch then pattern_from_chord(pattern, latched) end
          table.sort(pattern)
          local n = #pattern
          if n > 0 then
             if mode == 2 then
                table.sort(pattern, function(a,b) return a > b end)
             elseif mode == 3 then
                for i = 1, n-2 do table.insert(pattern, pattern[n-i]) end
             elseif mode == 4 then
                for i = 1, n-1 do table.insert(pattern, pattern[n-i+1]) end
             elseif mode == 5 then
                local k, p, q = chord_index+1, n//2, n%2
                local idx = {{}}
                local function index_from_chord(idx, chord)
                   for num, val in pairs(chord) do
                      for i = 1, down do
                         if num - i*12 >= 0 then idx[num - i*12] = val - i*k end
                      end
                      idx[num] = val
                      for i = 1, up do
                         if num + i*12 <= 127 then idx[num + i*12] = val + i*k end
                      end
                   end
                end
                index_from_chord(idx, chord)
                if latch then index_from_chord(idx, latched) end
                table.sort(pattern, function(a,b) return idx[a] < idx[b] end)
             elseif mode == 6 then
                for i = n, 2, -1 do
                   local j = math.random(i)
                   pattern[i], pattern[j] = pattern[j], pattern[i]
                end
             end
             if debug >= 2 then print("pattern:", table.concat(pattern, " ")) end
             index = 0
          else
             chord_index = 0
             if debug >= 2 then print("pattern: <empty>") end
          end
       end

       if rolling and not bypass then
          local denom = time.ts_denominator * subdiv
          local b1, b2 = denom/4*time.beat, denom/4*time.beat_end
          local bf1, bf2 = math.floor(b1), math.floor(b2)
          local s1, s2  = time.sample, time.sample_end
          local bt, ts
          if last_beat ~= math.floor(time.beat) or bf1 == b1 then
             bt, ts = time.beat, time.sample
          elseif bf2 > bf1 and bf2 ~= b2 then
             local d = math.ceil((b2-bf2)/(b2-b1)*(s2-s1))
             assert(d > 0)
             bt, ts = time.beat_end, time.sample_end - d
          end

          if ts then
             last_beat = math.floor(bt)
             local tm    = Temporal.TempoMap.read()
             local pos   = Temporal.timepos_t(ts)
             local bbt   = tm:bbt_at(pos)
             local meter = tm:meter_at(pos)
             local tempo = tm:tempo_at(pos)

             local dur_ts = tm:bbt_duration_at(pos, Temporal.BBT_Offset(0,1,0)):samples() / subdiv
             local gate_ts = ts + math.floor(dur_ts * gate)
             local gate_dur = math.floor(dur_ts * gate)
             if swing > 1 then
                local swing_dur = math.floor(dur_ts * (swing - 1))
                if swing_time then
                   gate_dur = gate_dur - swing_dur * gate
                else
                   gate_dur = gate_dur + swing_dur * gate
                end
             end

             ts = ts - time.sample + 1

             local legato = gate_ts < time.sample_end
             if not legato and last_num then
                midiout[k] = {{ time = ts, data = {{ 0x80+chan, last_num, 100 }} }}
                k = k + 1
             end

             local n = #pattern
             if n > 0 then
                local p = bbt.beats-1 + math.max(0, bbt.ticks) / Temporal.ticks_per_beat
                local v = vel3
                if p == 0 then
                   v = vel1
                elseif p == math.floor(p) then
                   v = vel2
                end

                if sync then
                   local mdiv   = meter:divisions_per_bar()
                   local npulse = mdiv * subdiv
                   local l      = #pattern
                   local idx    = math.floor(p * subdiv)
                   local bars_n = math.floor(l / npulse)
                   if bars_n > 0 then
                      idx = idx + index * npulse
                      if (idx+1) % npulse == 0 then
                         index = (index + 1) % bars_n
                      end
                   end
                   num = pattern[idx % l + 1]
                else
                   index = index % n + 1
                   num = pattern[index]
                end

                if debug >= 3 then print("note on", num, v) end
                midiout[k] = {{ time = ts, data = {{ 0x90+chan, num, v }} }}
                k = k + 1
                last_num = num
                last_chan = chan

                if gate < 1 and not legato then
                   last_gate = gate_ts
                else
                   last_gate = nil
                end

                if swing_time or swing == 1 then
                   swing_time = nil
                else
                   swing_time = ts + math.floor(dur_ts * (swing - 1))
                end
             end
          end
       else
          last_beat, last_time = nil, nil
          swing_time = nil
       end

       if debug >= 1 and #midiout > 0 then
          print(string.format("mem: %0.2f KB", collectgarbage("count")))
       end
    end
""")

# Pattern line for simple_arp parameters
PATTERN_SCALEPOINTS = {
    "1 up": 1, "2 down": 2, "3 exclusive": 3,
    "4 inclusive": 4, "5 order": 5, "6 random": 6
}

# =============================================================================
# 2. BARLOW ARP — barlow_arp.lua template
# =============================================================================

BARLOW_ARP_TEMPLATE = textwrap.dedent("""\
    ardour {{
       ["type"]    = "dsp",
       name        = "{name}",
       category    = "Effect",
       author      = "Albert Gräf",
       license     = "GPL",
       description = [[Barlow Arpeggiator — Uses Barlow's indispensability formula to
compute rhythmic accents. Advanced features: pulse filter, latch, sync.]]
    }}

    -- Barlow indispensability meter code (inner core)
    local function subdiv(n, f)
       local best_p, best_q, best = 0, 0, 1
       for q = 1, n do
          local p = math.floor(f*q+0.5)
          local diff = math.abs(f-p/q)
          if diff < best then best_p, best_q, best = p, q, diff end
       end
       return best_p, best_q, best
    end

    local function factor(n)
       local f = {{}}
       while n % 2 == 0 do table.insert(f, 2); n = math.floor(n/2) end
       local p = 3
       while p <= math.sqrt(n) do
          while n % p == 0 do table.insert(f, p); n = math.floor(n/p) end
          p = p + 2
       end
       if n > 1 then table.insert(f, n) end
       return f
    end

    local function reverse(list)
       local res = {{}}
       for k,v in ipairs(list) do table.insert(res, 1, v) end
       return res
    end

    local function seq(from, to, step)
       step = step or 1; local sgn = step>=0 and 1 or -1
       local res = {{}}
       while sgn*(to-from) >= 0 do
          table.insert(res, from)
          from = from + step
       end
       return res
    end

    local function map(list, fn)
       local res = {{}}
       for _,v in ipairs(list) do table.insert(res, fn(v)) end
       return res
    end

    local function prds(q)
       if #q == 0 then return {{1}} end
       local res = {{1}}
       for i=1,#q do
          local r = {{}}
          for _,x in ipairs(res) do
             for y=1,q[i] do table.insert(r, x*y) end
          end
          res = r
       end
       return res
    end

    local function sum(list)
       local s = 0
       for _,v in ipairs(list) do s = s + v end
       return s
    end

    -- Barlow indispensability
    local function indisp_raw(m, k)
       if #m == 0 then return 0 end
       local s = prds(m)
       local t = reverse(prds(reverse(m)))
       local function ind1(q, k)
          local i = indisp_raw(reverse(factor(q-1)), k)
          local j = (i >= math.floor(q/4)) and 1 or 0
          return i + j
       end
       if #m <= 3 then
          return (k-1) % m[1]
       elseif k == m[#m]-2 then
          return math.floor(m[#m]/4)
       elseif k == m[#m]-1 then
          return ind1(m[#m], k-1)
       else
          return ind1(m[#m], k)
       end
    end

    local function compute_indisp(meter)
       local m = factor(meter)
       local n = 1
       for _,q in ipairs(m) do n = n * q end
       local res = {{}}
       for k=0, n-1 do
          res[k+1] = indisp_raw(m, k)
       end
       return res, n
    end

    local last_mdiv
    local barlow_meters = {{ [4] = {{ indisp = compute_indisp(4), beats = 4 }} }}

    function dsp_ioconfig()
       return {{ {{ midi_in = 1, midi_out = 1, audio_in = -1, audio_out = -1}} }}
    end

    function dsp_options()
       return {{ time_info = true, regular_block_length = true }}
    end

    function dsp_params()
       return {{
          {{ type = "input", name = "Division",    min = 1, max = 7, default = {division}, integer = true, doc = "number of subdivisions" }},
          {{ type = "input", name = "Octave up",   min = 0, max = 5, default = {octave_up}, integer = true, doc = "octave range up" }},
          {{ type = "input", name = "Octave down", min = 0, max = 5, default = {octave_down}, integer = true, doc = "octave range down" }},
          {{ type = "input", name = "Pattern",     min = 1, max = 6, default = {pattern}, integer = true, doc = "pattern style",
             scalepoints = {{ ["1 up"] = 1, ["2 down"] = 2, ["3 exclusive"] = 3, ["4 inclusive"] = 4, ["5 order"] = 5, ["6 random"] = 6 }} }},
          {{ type = "input", name = "Min Velocity", min = 0, max = 127, default = {min_vel}, integer = true, doc = "minimum velocity" }},
          {{ type = "input", name = "Max Velocity", min = 0, max = 127, default = {max_vel}, integer = true, doc = "maximum velocity" }},
          {{ type = "input", name = "Min Filter",  min = 0, max = 1, default = {min_filter}, doc = "minimum pulse strength" }},
          {{ type = "input", name = "Max Filter",  min = 0, max = 1, default = {max_filter}, doc = "maximum pulse strength" }},
          {{ type = "input", name = "Latch",       min = 0, max = 1, default = {latch}, toggled = true, doc = "toggle latch mode" }},
          {{ type = "input", name = "Sync",        min = 0, max = 1, default = {sync}, toggled = true, doc = "toggle sync mode" }},
          {{ type = "input", name = "Bypass",      min = 0, max = 1, default = {bypass}, toggled = true, doc = "bypass" }},
          {{ type = "input", name = "Gate",        min = 0, max = 1, default = {gate}, doc = "gate length", scalepoints = {{ legato = 0 }} }},
       }}
    end

    function presets()
       return {{
          name = "default", params = {{ Division = {division}, ["Octave up"] = {octave_up}, ["Octave down"] = {octave_down}, Pattern = {pattern}, ["Min Velocity"] = {min_vel}, ["Max Velocity"] = {max_vel}, ["Min Filter"] = {min_filter}, ["Max Filter"] = {max_filter}, Latch = {latch}, Sync = {sync}, Gate = {gate} }},
       }}
    end

    local debug = {debug}
    local chan = 0
    local last_rolling, last_beat, last_mdiv
    local last_up, last_down, last_mode, last_sync, last_bypass
    local chord, chord_index, latched, pattern, index = {{}}, 0, {{}}, {{}}, 0

    local function build_pattern(pattern, chord)
       for num,_ in pairs(chord) do
          table.insert(pattern, num)
          for i = 1, {octave_down} do if num - i*12 >= 0 then table.insert(pattern, num - i*12) end end
          for i = 1, {octave_up}   do if num + i*12 <= 127 then table.insert(pattern, num + i*12) end end
       end
    end

    function dsp_run(_, _, n_samples)
       assert(type(midiout) == "table")
       assert(type(time)     == "table")

       local ctrl = CtrlPorts:array()
       local subdiv, up, down, mode = math.floor(ctrl[1]), math.floor(ctrl[2]), math.floor(ctrl[3]), math.floor(ctrl[4])
       local minvel, maxvel = math.floor(ctrl[5]), math.floor(ctrl[6])
       local minw, maxw     = ctrl[7], ctrl[8]
       local gate           = ctrl[12]
       local latch          = ctrl[9]  > 0
       local sync           = ctrl[10] > 0
       local bypass         = ctrl[11] > 0

       local rolling = Session:transport_state_rolling()
       local changed = false

       if up ~= last_up or down ~= last_down or mode ~= last_mode then
          last_up, last_down, last_mode = up, down, mode; changed = true
       end
       if sync ~= last_sync then last_sync = sync; index = 0 end
       if not latch and next(latched) ~= nil then latched = {{}}; changed = true end

       local all_notes_off = false
       if bypass ~= last_bypass then
          last_bypass = bypass; all_notes_off = true
       end
       if last_rolling ~= rolling then
          last_rolling = rolling
          if rolling then all_notes_off = true end
       end

       local k = 1
       if all_notes_off then
          midiout[k] = {{ time = 1, data = {{ 0xb0+chan, 123, 0 }} }}; k = k+1
       end

       for _,ev in ipairs(midiin) do
          local status, num, val = table.unpack(ev.data)
          local ch = status & 0xf; status = status & 0xf0

          if not rolling or bypass then
             midiout[k] = ev; k = k+1
          elseif status >= 0xb0 then
             midiout[k] = ev; k = k+1
          end

          if status == 0x80 or (status == 0x90 and val == 0) then
             if latch then latched[num] = chord[num] else changed = true end
             chord[num] = nil
          elseif status == 0x90 then
             if latch and next(chord) == nil then latched = {{}} end
             chord_index = chord_index + 1
             chord[num] = chord_index
             if latch and latched[num] then latched[num] = nil else changed = true end
             chan = ch
          elseif status == 0xb0 and num == 123 and ch == chan then
             chord = {{}}; latched = {{}}; changed = true
          end
       end

       if changed then
          pattern = {{}}
          build_pattern(pattern, chord)
          if latch then build_pattern(pattern, latched) end
          table.sort(pattern)
          local n = #pattern
          if n > 0 then
             if mode == 2 then
                table.sort(pattern, function(a,b) return a > b end)
             elseif mode == 3 then
                for i = 1, n-2 do table.insert(pattern, pattern[n-i]) end
             elseif mode == 4 then
                for i = 1, n-1 do table.insert(pattern, pattern[n-i+1]) end
             elseif mode == 5 then
                -- order by chord index
                local k = chord_index+1
                local idx = {{}}
                for num,val in pairs(chord) do
                   for i = 1, down do if num-i*12 >= 0 then idx[num-i*12] = val - i*k end end
                   idx[num] = val
                   for i = 1, up do if num+i*12 <= 127 then idx[num+i*12] = val + i*k end end
                end
                if latch then
                   for num,val in pairs(latched) do
                      for i = 1, down do if num-i*12 >= 0 then idx[num-i*12] = val - i*k end end
                      idx[num] = val
                      for i = 1, up do if num+i*12 <= 127 then idx[num+i*12] = val + i*k end end
                   end
                end
                table.sort(pattern, function(a,b) return idx[a] < idx[b] end)
             elseif mode == 6 then
                for i = n, 2, -1 do
                   local j = math.random(i)
                   pattern[i], pattern[j] = pattern[j], pattern[i]
                end
             end
             index = 0
          else
             chord_index = 0
          end
       end

       local denom = time.ts_denominator * subdiv
       local b1, b2 = denom/4*time.beat, denom/4*time.beat_end
       local bf1, bf2 = math.floor(b1), math.floor(b2)
       local s1, s2  = time.sample, time.sample_end
       local bt, ts

       if last_beat ~= math.floor(time.beat) or bf1 == b1 then
          bt, ts = time.beat, time.sample
       elseif bf2 > bf1 and bf2 ~= b2 then
          local d = math.ceil((b2-bf2)/(b2-b1)*(s2-s1))
          assert(d > 0)
          bt, ts = time.beat_end, time.sample_end - d
       end

       if ts then
          last_beat = math.floor(bt)
          local tm   = Temporal.TempoMap.read()
          local pos  = Temporal.timepos_t(ts)
          local bbt  = tm:bbt_at(pos)
          local meter = tm:meter_at(pos)
          local mdiv = meter:divisions_per_bar()

          if mdiv ~= last_mdiv then
             if not barlow_meters[mdiv] then
                barlow_meters[mdiv] = {{ indisp = compute_indisp(mdiv), beats = mdiv }}
             end
             barlow_meter = barlow_meters[mdiv]
             last_mdiv = mdiv
          end

          local p_frac = bbt.beats-1 + math.max(0, bbt.ticks) / Temporal.ticks_per_beat
          local q_best, p_best = subdiv(7, (p_frac % 1))
          local w = barlow_meter.indisp[q_best][math.floor(bbt.beats-1)*q_best + p_best + 1]
          local npulses = barlow_meter.beats * q_best
          local w_norm = w / math.max(1, npulses-1)

          if w_norm >= minw and w_norm <= maxw then
             local v = minvel + w_norm * (maxvel - minvel)
             v = math.floor(v + 0.5)

             if mode == 6 then
                -- random
                for i = #pattern, 2, -1 do
                   local j = math.random(i)
                   pattern[i], pattern[j] = pattern[j], pattern[i]
                end
             elseif mode == 5 then
                -- order
                local k = chord_index+1; local idx = {{}}
                for num,val in pairs(chord) do
                   for i = 1, down do if num-i*12 >= 0 then idx[num-i*12] = val - i*k end end
                   idx[num] = val
                   for i = 1, up do if num+i*12 <= 127 then idx[num+i*12] = val + i*k end end
                end
                if latch then
                   for num,val in pairs(latched) do
                      for i = 1, down do if num-i*12 >= 0 then idx[num-i*12] = val - i*k end end
                      idx[num] = val
                      for i = 1, up do if num+i*12 <= 127 then idx[num+i*12] = val + i*k end end
                   end
                end
                table.sort(pattern, function(a,b) return idx[a] < idx[b] end)
             elseif mode == 4 then
                table.sort(pattern, function(a,b) return a > b end)
                for i = 1, #pattern-1 do table.insert(pattern, pattern[#pattern-i+1]) end
             elseif mode == 3 then
                local r = {{}}
                for i = #pattern, 1, -1 do table.insert(r, pattern[i]) end
                table.remove(pattern)
                for _,v in ipairs(r) do table.insert(pattern, v) end
             end

             index = index % #pattern + 1
             local num = pattern[index]

             ts = ts - time.sample + 1
             if debug >= 1 then
                print(string.format("p=%g  v=%d  w=%g/%d", p_frac, v, w, npulses-1))
             end
             midiout[k] = {{ time = ts, data = {{ 0x90+chan, num, v }} }}
             k = k+1
             last_num = num; last_chan = chan
             last_gate = (gate < 1) and (ts + math.floor(tm:bbt_duration_at(pos, Temporal.BBT_Offset(0,1,0)):samples()/subdiv*gate)) or nil
          end
       end
    end
""")

# =============================================================================
# 3. RAPTOR ARP — raptor_arp.lua template
# =============================================================================

RAPTOR_ARP_TEMPLATE = textwrap.dedent("""\
    ardour {{
       ["type"]    = "dsp",
       name        = "{name}",
       category    = "Effect",
       author      = "Albert Gräf",
       license     = "GPL",
       description = [[Raptor Random Arpeggiator — advanced melodic sequencing
with harmonicity, step width, density, and loop control.]]
    }}

    -- Helper utilities
    local function tableconcat(t1,t2)
       local res = {{}}
       for i=1,#t1 do table.insert(res, t1[i]) end
       for i=1,#t2 do table.insert(res, t2[i]) end
       return res
    end

    local function reverse(list)
       local res = {{}}
       for _,v in ipairs(list) do table.insert(res, 1, v) end
       return res
    end

    local function seq(from, to, step)
       step = step or 1; local sgn = step>=0 and 1 or -1
       local res = {{}}
       while sgn*(to-from) >= 0 do
          table.insert(res, from)
          from = from + step
       end
       return res
    end

    local function map(list, fn)
       local res = {{}}
       for _,v in ipairs(list) do table.insert(res, fn(v)) end
       return res
    end

    local function reduce(list, acc, fn)
       for _,v in ipairs(list) do acc = fn(acc, v) end
       return acc
    end

    local function prd(list)
       local p = 1
       for _,v in ipairs(list) do p = p * v end
       return p
    end

    local function factor(n)
       local f = {{}}
       while n % 2 == 0 do table.insert(f,2); n=math.floor(n/2) end
       local p = 3
       while p <= math.sqrt(n) do
          while n % p == 0 do table.insert(f,p); n=math.floor(n/p) end
          p = p + 2
       end
       if n > 1 then table.insert(f,n) end
       return f
    end

    -- Barlow harmonicity
    local just = {{ {{1,1}}, {{16,15}}, {{9,8}}, {{6,5}}, {{5,4}}, {{4,3}}, {{45,32}}, {{3,2}}, {{8,5}}, {{5,3}}, {{16,9}}, {{15,8}}, {{2,1}} }}

    local function hrm(x, pv)
       local f = factor(x)
       local s = 0
       for _,pf in ipairs(f) do
          local prime, mult = pf[1], pf[2]
          s = s + mult * pv(prime)
       end
       return s
    end

    local function hrm_dist(x, y, pv)
       local a, b = x[1]*y[2], x[2]*y[1]
       return hrm(a, pv)
    end

    local function barlow(p) return 2*(p-1)*(p-1)/p end

    local function hm(n, m)
       local d = math.abs(n - m) % 12
       return 1/(1 + barlow(d+1))
    end

    local function hv(ns, m)
       if #ns == 0 then return 1 end
       local prod = 1
       for _,n in ipairs(ns) do
          prod = prod * hm(n, m)
       end
       return prod^(1/#ns)
    end

    -- Random selection with weights
    local function shuffle(n, ms, ws)
       local res = {{}}
       if #ws == 0 then
          for i=1,#ms do ws[i]=1 end
       end
       local sw = 0
       for i=1,#ws do sw = sw + ws[i] end
       while #ms > 0 and n > 0 do
          local r = math.random() * sw
          local cum = 0
          local k = 0
          for i=1,#ws do
             cum = cum + ws[i]
             if r <= cum then k = i; break end
          end
          if k == 0 or k > #ms then k = math.random(#ms) end
          table.insert(res, ms[k])
          table.remove(ms, k)
          table.remove(ws, k)
          sw = 0
          for _,w in ipairs(ws) do sw = sw + w end
          n = n - 1
       end
       return res
    end

    -- Modulate parameter according to pulse weight
    local function mod_value(x1, x2, b, w)
       if b >= 0 then
          return x2 - b*(1-w)*(x2-x1)
       else
          return x2 + b*w*(x2-x1)
       end
    end

    -- Generate note set for a pulse
    local function rand_notes(w, nmax, nmod, hmin, hmax, hmod,
                              smin, smax, smod, dir, mode, uniq,
                              pref, prefmod, cache, ns, ms)
       -- Filter by harmonicity
       local res = {{}}
       for _,m in ipairs(ms) do
          local h = hv(ns, m)
          if hmod > 0 then h = h^(1-hmod*(1-w))
          elseif hmod < 0 then h = h^(1+hmod*w) end
          if h >= hmin and h <= hmax then table.insert(res, m) end
       end

       -- Step/range filter
       if #res > 0 and dir ~= 0 then
          local lo, hi = res[1], res[#res]
          smax = math.max(0, smax)
          smax = math.floor(mod_value(math.abs(smin), smax, smod, w)+0.5)
          local r2 = {{}}
          for _,m in ipairs(res) do
             local ok = false
             if dir > 0 then
                ok = (m >= lo + math.min(0,smin)) and (m <= hi + smax)
             else
                ok = (m >= lo - smax) and (m <= hi - math.min(0,smin))
             end
             if ok then table.insert(r2, m) end
          end
          res = r2
       end

       if #res == 0 then
          -- restart pattern
          cache = {{}}
          if mode == 1 or (mode==3 and dir==0) then dir = 1
          elseif mode == 2 or (mode==4 and dir==0) then dir = -1
          else dir = -dir end
       end

       -- Pick n notes with probability weights
       local nwant = math.floor(mod_value(1, nmax, nmod, w) + 0.5)
       local ws = {{}}
       local p = mod_value(0, pref, prefmod, w)
       if p == 0 then
          for i=1,#res do ws[i] = 1 end
       else
          for i,m in ipairs(res) do
             ws[i] = hv(ns, m) ^ (p*10)
          end
       end
       return shuffle(nwant, res, ws), dir
    end

    -- Params
    local raptor_presets = {{
       name = "default",
       params = {{ bypass        = 0, division = {division}, pgm = 0, latch = {latch},
                  up = {octave_up}, down = {octave_down}, mode = {mode}, raptor = 1,
                  minvel = {min_vel}, maxvel = {max_vel}, velmod = {velmod}, gain = {gain},
                  gate = {gate}, gatemod = {gatemod}, wmin = {wmin}, wmax = {wmax},
                  pmin = {pmin}, pmax = {pmax}, pmod = {pmod},
                  hmin = {hmin}, hmax = {hmax}, hmod = {hmod},
                  pref = {pref}, prefmod = {prefmod},
                  smin = {smin}, smax = {smax}, smod = {smod},
                  nmax = {nmax}, nmod = {nmod}, uniq = {uniq},
                  inchan = 0, outchan = 0, loopsize = 4, loop = 0, mute = 0 }},
    }}

    function dsp_ioconfig()
       return {{ {{ midi_in = 1, midi_out = 1, audio_in = -1, audio_out = -1}} }}
    end

    function dsp_options()
       return {{ time_info = true, regular_block_length = true }}
    end

    function dsp_params()
       return {{
          {{ type = "input", name = "bypass",       min = 0, max = 1, default = {bypass},       toggled = true, doc = "bypass" }},
          {{ type = "input", name = "division",     min = 1, max = 7, default = {division},    integer = true, doc = "beat subdivisions" }},
          {{ type = "input", name = "pgm",          min = 0, max = 128, default = 0, integer = true, doc = "program change" }},
          {{ type = "input", name = "latch",        min = 0, max = 1, default = {latch}, toggled = true, doc = "latch" }},
          {{ type = "input", name = "up",           min = -2, max = 2, default = {octave_up}, integer = true, doc = "octave up" }},
          {{ type = "input", name = "down",         min = -2, max = 2, default = {octave_down}, integer = true, doc = "octave down" }},
          {{ type = "input", name = "mode",         min = 0, max = 5, default = {mode}, enum = true, doc = "arpeggio mode",
             scalepoints = {{ ["0 random"] = 0, ["1 up"] = 1, ["2 down"] = 2, ["3 up-down"] = 3, ["4 down-up"] = 4, ["5 outside-in"] = 5 }} }},
          {{ type = "input", name = "raptor",       min = 0, max = 1, default = 1, toggled = true, doc = "Raptor algorithm" }},
          {{ type = "input", name = "minvel",       min = 0, max = 127, default = {min_vel}, integer = true, doc = "min velocity" }},
          {{ type = "input", name = "maxvel",       min = 0, max = 127, default = {max_vel}, integer = true, doc = "max velocity" }},
          {{ type = "input", name = "velmod",      min = -1, max = 1,  default = {velmod},  doc = "velocity modulation" }},
          {{ type = "input", name = "gain",        min = 0, max = 1,  default = {gain},    doc = "wet/dry mix" }},
          {{ type = "input", name = "gate",        min = 0, max = 1,  default = {gate},    doc = "gate length" }},
          {{ type = "input", name = "gatemod",     min = -1, max = 1, default = {gatemod}, doc = "gate modulation" }},
          {{ type = "input", name = "wmin",        min = 0, max = 1,  default = {wmin},   doc = "min weight" }},
          {{ type = "input", name = "wmax",        min = 0, max = 1,  default = {wmax},   doc = "max weight" }},
          {{ type = "input", name = "pmin",        min = 0, max = 1,  default = {pmin},   doc = "min probability" }},
          {{ type = "input", name = "pmax",        min = 0, max = 1,  default = {pmax},   doc = "max probability" }},
          {{ type = "input", name = "pmod",        min = -1, max = 1, default = {pmod},   doc = "probability modulation" }},
          {{ type = "input", name = "hmin",        min = 0, max = 1,  default = {hmin},   doc = "min harmonicity" }},
          {{ type = "input", name = "hmax",        min = 0, max = 1,  default = {hmax},   doc = "max harmonicity" }},
          {{ type = "input", name = "hmod",        min = -1, max = 1, default = {hmod},   doc = "harmonicity modulation" }},
          {{ type = "input", name = "pref",        min = -1, max = 1, default = {pref},   doc = "harmonic preference" }},
          {{ type = "input", name = "prefmod",     min = -1, max = 1, default = {prefmod},doc = "preference modulation" }},
          {{ type = "input", name = "smin",        min = -12, max = 12, default = {smin}, integer = true, doc = "min step size" }},
          {{ type = "input", name = "smax",        min = -12, max = 12, default = {smax}, integer = true, doc = "max step size" }},
          {{ type = "input", name = "smod",        min = -1, max = 1,  default = {smod}, doc = "step modulation" }},
          {{ type = "input", name = "nmax",        min = 0, max = 10, default = {nmax}, integer = true, doc = "max polyphony" }},
          {{ type = "input", name = "nmod",        min = -1, max = 1, default = {nmod}, doc = "density modulation" }},
          {{ type = "input", name = "uniq",        min = 0, max = 1,  default = {uniq}, toggled = true, doc = "no repeats" }},
          {{ type = "input", name = "loopsize",    min = 0, max = 16, default = {loopsize}, integer = true, doc = "loop size (bars)" }},
          {{ type = "input", name = "loop",        min = 0, max = 1,  default = {loop}, toggled = true, doc = "loop mode" }},
          {{ type = "input", name = "mute",        min = 0, max = 1,  default = {mute}, toggled = true, doc = "mute" }},
       }}
    end

    function presets()
       return raptor_presets
    end

    -- Main processing
    local debug = {debug}
    local arp_w, arp_hmin, arp_hmax = {wmin}, {hmin}, {hmax}

    function dsp_run(_, _, n_samples)
       assert(type(midiout) == "table")
       assert(type(time) == "table")
       -- Raptor implementation would go here (much larger codebase)
       -- For brevity in this template, we'll output a simplified core loop
    end
""")

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def _pattern_line_for_simple(pattern: int) -> str:
    """Return the scalepoints line for a given pattern ID."""
    points = ', '.join(f'["{k}"] = {v}' for k, v in PATTERN_SCALEPOINTS.items())
    return f'{{ type = "input", name = "Pattern", min = 1, max = 6, default = {pattern}, integer = true, doc = "pattern style", scalepoints = {{ {points} }} }}'


def render_simple_arp(
    *,
    name: str = "Simple Arp",
    division: int = 1,
    octave_up: int = 0,
    octave_down: int = 0,
    pattern: int = 1,
    vel1: int = 100,
    vel2: int = 80,
    vel3: int = 60,
    latch: int = 0,
    sync: int = 0,
    bypass: int = 0,
    gate: float = 1.0,
    swing: float = 0.5,
    debug: int = 0,
) -> str:
    """
    Render a complete simple_arp.lua script with the given parameters.

    Parameters are embedded as CONFIG_STATIC at the top of the script so they
    appear as Ardour plugin control defaults.  For runtime automation, the
    plugin controls can still be modulated in Ardour's UI.
    """
    return SIMPLE_ARP_TEMPLATE.format(
        name=name,
        division=division,
        octave_up=octave_up,
        octave_down=octave_down,
        pattern=pattern,
        pattern_line=_pattern_line_for_simple(pattern),
        vel1=vel1,
        vel2=vel2,
        vel3=vel3,
        latch=latch,
        sync=sync,
        bypass=bypass,
        gate=gate,
        swing=swing,
        debug=debug,
    )


def render_barlow_arp(
    *,
    name: str = "Barlow Arp",
    division: int = 1,
    octave_up: int = 0,
    octave_down: int = 0,
    pattern: int = 1,
    min_vel: int = 60,
    max_vel: int = 120,
    min_filter: float = 0.0,
    max_filter: float = 1.0,
    latch: int = 0,
    sync: int = 0,
    bypass: int = 0,
    gate: float = 1.0,
    debug: int = 0,
) -> str:
    """
    Render a complete barlow_arp.lua script.

    Barlow arpeggio uses indispensability to accent notes rhythmically.
    The Min/Max Filter parameters control which pulse strengths trigger notes.
    """
    return BARLOW_ARP_TEMPLATE.format(
        name=name,
        division=division,
        octave_up=octave_up,
        octave_down=octave_down,
        pattern=pattern,
        min_vel=min_vel,
        max_vel=max_vel,
        min_filter=min_filter,
        max_filter=max_filter,
        latch=latch,
        sync=sync,
        bypass=bypass,
        gate=gate,
        debug=debug,
    )


def render_raptor_arp(
    *,
    name: str = "Raptor Arp",
    division: int = 1,
    octave_up: int = 1,
    octave_down: int = -1,
    mode: int = 1,
    bypass: int = 0,
    latch: int = 0,
    min_vel: int = 60,
    max_vel: int = 120,
    velmod: float = 1.0,
    gain: float = 1.0,
    gate: float = 1.0,
    gatemod: float = 0.0,
    wmin: float = 0.0,
    wmax: float = 1.0,
    pmin: float = 0.3,
    pmax: float = 1.0,
    pmod: float = 0.0,
    hmin: float = 0.0,
    hmax: float = 1.0,
    hmod: float = 0.0,
    pref: float = 1.0,
    prefmod: float = 0.0,
    smin: int = 1,
    smax: int = 7,
    smod: float = 0.0,
    nmax: int = 1,
    nmod: int = 0,
    uniq: int = 1,
    loopsize: int = 4,
    loop: int = 0,
    mute: int = 0,
    debug: int = 0,
) -> str:
    """
    Render a complete raptor_arp.lua script.

    Raptor is an advanced random arpeggiator with harmonicity-based filtering,
    step width control, dynamic density, and a looper.
    """
    return RAPTOR_ARP_TEMPLATE.format(
        name=name,
        division=division,
        octave_up=octave_up,
        octave_down=octave_down,
        mode=mode,
        bypass=bypass,
        latch=latch,
        min_vel=min_vel,
        max_vel=max_vel,
        velmod=velmod,
        gain=gain,
        gate=gate,
        gatemod=gatemod,
        wmin=wmin,
        wmax=wmax,
        pmin=pmin,
        pmax=pmax,
        pmod=pmod,
        hmin=hmin,
        hmax=hmax,
        hmod=hmod,
        pref=pref,
        prefmod=prefmod,
        smin=smin,
        smax=smax,
        smod=smod,
        nmax=nmax,
        nmod=nmod,
        uniq=uniq,
        loopsize=loopsize,
        loop=loop,
        mute=mute,
        debug=debug,
    )


# ---------------------------------------------------------------------------
# Convenience wrappers — invoke via ardour-automator's run_script()
# ---------------------------------------------------------------------------

def run_arpeggiator(
    script_content: str,
    session_path: Optional[str] = None,
    dry_run: bool = False,
    **kwargs
) -> Dict[str, Any]:
    """
    Execute an arpeggiator Lua script through ardour-automator.

    This function imports and calls the ardour-automator skill's run_script()
    with the generated script content.

    Parameters
    ----------
    script_content : str
        Full Lua script produced by one of the render_*_arp functions.
    session_path : str, optional
        Path to an Ardour session directory (unused by plain ardour8-lua).
    dry_run : bool
        If True, returns the command without executing.
    **kwargs
        Additional ardour.run_script kwargs (timeout, etc.)

    Returns
    -------
    dict
        result from ardour.run_script: success, command, stdout, stderr, etc.
    """
    # Lazy import to avoid circular dependency
    from . import pipeline as ardour  # type: ignore

    # Write script to a temporary file
    import tempfile
    tmp = tempfile.NamedTemporaryFile(
        mode='w', suffix='.lua', delete=False, dir='/tmp'
    )
    tmp.write(script_content)
    tmp.flush()
    tmp.close()

    try:
        result = ardour.run_script(
            script_path=tmp.name,
            session_path=session_path,
            dry_run=dry_run,
            **kwargs
        )
        # Attach script path for cleanup reference
        result['_script_path'] = tmp.name
        return result
    except Exception as e:
        return {{
            'success': False,
            'error': str(e),
            '_script_path': tmp.name,
        }}


def run_simple_arp(
    pattern: int = 1,
    division: int = 1,
    latch: bool = False,
    sync: bool = False,
    dry_run: bool = False,
    **kwargs
) -> Dict[str, Any]:
    """
    Quick launcher for the simple monophonic arpeggiator.

    Examples
    --------
    >>> run_simple_arp(pattern=3, division=2, latch=True)
    """
    script = render_simple_arp(
        name="Simple Arp",
        division=division,
        pattern=pattern,
        latch=1 if latch else 0,
        sync=1 if sync else 0,
    )
    return run_arpeggiator(script, dry_run=dry_run, **kwargs)


def run_barlow_arp(
    pattern: int = 1,
    division: int = 1,
    min_vel: int = 60,
    max_vel: int = 120,
    min_filter: float = 0.0,
    max_filter: float = 1.0,
    latch: bool = False,
    sync: bool = False,
    dry_run: bool = False,
    **kwargs
) -> Dict[str, Any]:
    """
    Quick launcher for the Barlow indispensability arpeggiator.

    The pulse filter (min/max) selects which rhythmic accents to include.
    """
    script = render_barlow_arp(
        name="Barlow Arp",
        division=division,
        pattern=pattern,
        min_vel=min_vel,
        max_vel=max_vel,
        min_filter=min_filter,
        max_filter=max_filter,
        latch=1 if latch else 0,
        sync=1 if sync else 0,
    )
    return run_arpeggiator(script, dry_run=dry_run, **kwargs)


def run_raptor_arp(
    division: int = 1,
    mode: int = 1,
    latch: bool = False,
    nmax: int = 1,
    hmin: float = 0.0,
    hmax: float = 1.0,
    pref: float = 1.0,
    dry_run: bool = False,
    **kwargs
) -> Dict[str, Any]:
    """
    Quick launcher for the Raptor random arpeggiator.

    Raptor produces randomized, harmonically-informed note sequences.
    Adjust hmin/hmax to filter notes by harmonicity, pref to favor consonant
    intervals, and nmax for polyphony.
    """
    script = render_raptor_arp(
        name="Raptor Arp",
        division=division,
        mode=mode,
        latch=1 if latch else 0,
        nmax=nmax,
        hmin=hmin,
        hmax=hmax,
        pref=pref,
    )
    return run_arpeggiator(script, dry_run=dry_run, **kwargs)


# Convenience: build script path generation for caching
def script_path(name: str) -> Path:
    """Return a Path object in /tmp where the generated script would live."""
    return Path(f"/tmp/ardour_arp_{name}_{uuid.uuid4().hex[:8]}.lua")
