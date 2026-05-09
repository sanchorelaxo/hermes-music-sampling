# Bastl Kastle 2 — Hardware Reference

> Hardware platform reference for all Kastle 2 firmware variants (FX Wizard, Wave Bard, Alchemist, etc.).
> Derived from schematic analysis of `Kastle_2_1.2_schematic.pdf` cross-referenced with firmware source at `github.com/bastl-instruments/kastle2`.

**Schematic:** `https://github.com/bastl-instruments/kastle2/blob/main/schematics/Kastle_2_1.2_schematic.pdf`
**Firmware:** `https://github.com/bastl-instruments/kastle2`
**Local schematic copy:** `/tmp/kastle2/schematics/Kastle_2_1.2_schematic.pdf` (git clone)

---

## Platform Overview

The Kastle 2 is a digital synth platform built around the **Raspberry Pi RP2040** microcontroller (dual-core ARM Cortex-M0+, 176MHz) with a stereo audio codec, extensive CV/Gate/Sync I/O, and a patchbay. Multiple firmware apps share the same hardware.

| Subsystem | Component | Notes |
|-----------|-----------|-------|
| MCU | RP2040 (IC1) | 176MHz (overclocked from 133MHz), 0.5MB flash |
| Flash | W25Q128JVSIQ (IC2) | 128Mbit QSPI; 0.5MB for firmware, 7.5MB user data |
| Codec | NAU88C22YG (IC5) | Stereo 24-bit I2S; WM8731 pin-compatible |
| EEPROM | 24C02 (IC11) | 2Kb I2C; stores pitch calibration |
| MUX | SN74LV4051APWR (IC8, IC9) | 8-ch analog muxes; read 8 pots via 3 address lines |
| Logic | SN74HCT14 (IC10) | Hex inverting Schmitt trigger; cleans gate outputs |
| OpAmps | MCP6004-I/ST (IC4, IC13) | Quad op-amp; audio buffering, CV scaling, VREF |
| OpAmps | MCP6002 (IC12) | Dual op-amp; CV input conditioning |
| LEDs | WS2812B-2020 (LD1-3) | Addressable RGB; GPIO 16 via PIO state machine |

---

## Power Domain

```
USB-C (J1)  or  Battery (BAT+)
    │
    ▼
Q1  LGE2305  (P-Channel MOSFET, reverse-protection / power-path select)
    │
    ├─► D17 (10V Zener, overvoltage clamp)
    │
    ▼
XC2  ME6211C33M5G-N  (3.3V LDO, primary)
    or
XC3  TPS7A2033PDBVR  (3.3V LDO, alternate)
    │
    ▼
+3.3V rails:  VCC (logic),  VDDA (analog)
    │
    ├─► C4-C7 (10µF) and C1-C3,C8,C10 (100nF) bypass caps
    │
    └─► D1-D4  PESD5V0L2BT  (ESD TVS on USB data lines)
```

- **Q1** selects between USB and battery automatically.
- **USB does NOT charge batteries.**
- Battery: 3× AA (~15–18 hours, 100–150mA). Low battery → backlight turns red.
- **Firmware note:** Power management is pure hardware; the RP2040 just runs.

---

## MCU Pin Mapping (RP2040 GPIO)

Source: `code/src/common/core/Hardware.hpp`

| GPIO | Pin Name | Function | Notes |
|------|----------|----------|-------|
| 0 | PIN_TX | Debug UART TX | |
| 1 | PIN_RX | Debug UART RX | |
| 2 | PIN_PULSE_OUT | Pulse output | |
| 3 | PIN_GATE_OUT | Gate output | |
| 4 | PIN_LFO_OUT | LFO triangle (PWM analog out) | 10-bit PWM → RC filter |
| 5 | PIN_ENV_OUT | Envelope (PWM analog out) | 10-bit PWM → RC filter |
| 6 | PIN_CV_OUT | CV (PWM analog out) | 10-bit PWM → RC filter |
| 7 | PIN_SYNC_OUT | Sync output | |
| 8 | PIN_MCLK | I2S master clock | → codec MCLK |
| 9 | PIN_DIN | Spare / diagnostic | |
| 10 | PIN_BCLK | I2S bit clock | → codec BCLK |
| 11 | PIN_LRCLK | I2S LR clock | → codec LRCIN/LRCOUT |
| 12 | PIN_DOUT | I2S DAC data out | → codec DACDAT |
| 13 | PIN_MUX_C | Analog mux address C | IC8/IC9 select |
| 14 | PIN_MUX_B | Analog mux address B | |
| 15 | PIN_MUX_A | Analog mux address A | |
| 16 | PIN_LEDS | WS2812B data | PIO state machine (800kHz) |
| 17 | PIN_BUTTON_SHIFT | Shift button | |
| 18 | PIN_BUTTON_MODE | Mode button | |
| 19 | PIN_TRIG_IN | Trigger input | Digital or analog read |
| 20 | PIN_SDA | I2C SDA | EEPROM + codec config |
| 21 | PIN_SCL | I2C SCL | |
| 22 | PIN_RESET_IN | Reset / sync input | |
| 23 | PIN_AUDIO_IN_DETECT | Audio jack plug detect | |
| 24 | PIN_SYNC_IN_DETECT | Sync jack plug detect | |
| 25 | PIN_SYNC_IN | Sync input (direct) | |

---

## Clock and System

```cpp
// code/src/common/config.hpp
static constexpr float   SAMPLE_RATE      = 44000.0f;   // intentionally nonstandard (was ~44100)
static constexpr uint32_t SYSTEM_CLOCK_KHZ = 176000;    // slightly overclocked (base 133MHz)
static constexpr float   AUDIO_LOOP_RATE  = SAMPLE_RATE / 48.0f;  // ~916 Hz
```

- **X1**: 12MHz crystal with C24/C25 (18pF) load caps.
- I2S runs at 44kHz (not 44.1kHz) because the RP2040 PLL only produces clean multiples at certain input frequencies.
- The `user_data` section starts at `0x10080000` (512KB offset), giving 7.5MB for sample storage.

---

## Audio Codec (NAU88C22YG)

- **IC5**: NAU88C22YG (stereo 24-bit codec)
- Configured over **I2C0** (SDA=GPIO20, SCL=GPIO21) at initialization.
- **IC4** (MCP6004): Input buffering + VREF (virtual ground = 2.5V for single-ended I/O).
- Audio I/O: 3.5mm stereo jack (J2) — shared LINE IN and LINE OUT.

### I2S Signal Routing

| RP2040 Pin | Signal | Codec Pin |
|-----------|--------|-----------|
| GPIO 8  | MCLK | MCLK |
| GPIO 10 | BCLK | BCLK |
| GPIO 11 | LRCLK | LRCIN / LRCOUT |
| GPIO 12 | DOUT | DACDAT |
| (ADC) | ADCDAT | from codec |

### Audio Path

```
LINE IN (J2)
  → C27/C28 (1µF) AC-couple
  → R4/R5 (47k)
  → IC4 buffer (MCP6004)
  → IC5 ADC → I2S → RP2040 DSP → I2S → IC5 DAC
  → R16 (1k) + R20 (1k) attenuator
  → C12/C13 (10µF)
  → LINE OUT (J2)
```

### ADC Reference (12-bit, 0–4095 on 3.3V ref)

```cpp
// code/src/common/config.hpp
static constexpr int32_t ADC_0V  =    0;
static constexpr int32_t ADC_1V  =  819;   // 4095 / 5
static constexpr int32_t ADC_2V  = 1638;
static constexpr int32_t ADC_3V  = 2457;
static constexpr int32_t ADC_4V  = 3276;
static constexpr int32_t ADC_5V  = 4095;
static constexpr int32_t ADC_N1V = -819;   // Citadel (bipolar ±5V inputs)
static constexpr int32_t ADC_N5V = -4095;
```

---

## Analog Multiplexing (Pot Reading)

Two **SN74LV4051APWR** 8-channel analog multiplexers read 8 pots (6 rotary + 2 slide) using only 3 address GPIO pins + 1 ADC input:

```
GPIO 13 (MUX_C), GPIO 14 (MUX_B), GPIO 15 (MUX_A) → address lines (binary)
POT_SIG → RP2040 ADC
```

| Mux | Channels read |
|-----|--------------|
| IC8 | PITCH_1, PITCH_2, RESET, PARAM_3, PARAM_1, MODE, FEED_1, FEED_2 |
| IC9 | FEED_3, PARAM_2, POT_5, POT_1, POT_4, POT_6, TRIG_IN, POT_7 |

**Pot values** are 12-bit (0–4095), averaged. A "freeze" mechanism stops pot updates when a layer changes.

---

## CV / Gate I/O Conditioning

### CV Inputs (2 channels)
- R28/R29 resistor divider scales input voltage.
- **IC12** (MCP6002 dual op-amp) buffers and shifts level to 0–3.3V for the RP2040 ADC.
- Accepts ±5V (Citadel) or 0–5V (Kastle 2) depending on firmware mode.

### Trigger Inputs
- **Q2, Q3, Q4** (MMBT3904 NPN) act as level-shifters / buffers for Eurorack-style trigger gates.

### Gate / CV Outputs
- **IC10** (SN74HCT14 hex inverting Schmitt trigger) cleans and buffers digital gate/pulse signals.
- **IC13** (MCP6004) filters PWM outputs (GPIO 4/5/6) into smooth analog CV.

### PWM DAC (10-bit, 0–1023)

```cpp
static constexpr int32_t DAC_MAX = 1023;
static constexpr int32_t DAC_0V =    0;
static constexpr int32_t DAC_1V =  220;   // rough (USB-powered)
static constexpr int32_t DAC_2V =  440;
static constexpr int32_t DAC_3V =  660;
static constexpr int32_t DAC_4V =  878;
```

PWM on GPIO pins → RC low-pass filter → smooth CV OUT at patchbay and rear jack.

---

## LED Driver (WS2812B)

- **LD1, LD2, LD3**: WS2812B-2020 addressable RGB LEDs.
- Driven by GPIO 16 via **RP2040 PIO** (`WS2812.pio` state machine).
- 800kHz single-wire protocol, PIO shifts bits out autonomously.
- Used for panel indicators and app-specific feedback.

---

## EEPROM (24C02)

- **IC11**: 24C02 2Kb I2C EEPROM.
- Sits on I2C0 (SDA=20, SCL=21).
- Stores calibration data for pitch inputs:

```cpp
enum class Calibration {
    PITCH1_0V, PITCH1_1V, PITCH1_2V, PITCH1_3V, PITCH1_4V,
    PITCH2_0V, PITCH2_1V, PITCH2_2V, PITCH2_3V, PITCH2_4V,
};
```

At startup, the firmware reads these values to linearize the two pitch CV inputs.

---

## Patchbay Signal Summary

All patchbay signals map to the `Hardware::DigitalOutput`, `Hardware::AnalogOutput`, and `Hardware::AnalogInput` enums in firmware.

| Patchbay Signal | Type | Firmware Mapping |
|----------------|-------|-----------------|
| PULSE OUT | Digital | `DigitalOutput::PULSE_OUT` |
| GATE OUT | Digital | `DigitalOutput::GATE_OUT` |
| SYNC OUT | Digital | `DigitalOutput::SYNC_OUT` |
| LFO TRI | Analog (PWM) | `AnalogOutput::TRI_OUT` |
| ENV | Analog (PWM) | `AnalogOutput::ENV_OUT` |
| CV OUT | Analog (PWM) | `AnalogOutput::CV_OUT` |
| TRIG IN | Digital/Analog | `DigitalInput::TRIG_IN` / `AnalogInput::TRIG_IN` |
| RESET IN | Digital | `DigitalInput::RESET_IN` |
| SYNC IN | Digital | `DigitalInput::SYNC_IN` |
| PITCH 1/2 | Analog (ADC) | `HwAnalogInput::ADC2_PITCH1`, `ADC3_PITCH2` |
| FEED 1/2/3 | Tri-state | `AnalogInput::FEED_1`, `FEED_2`, `FEED_3` |
| POT_1–7 | Analog (MUX) | `Hardware::Pot::POT_1` … `POT_7` |

All patchbay inputs are protected by **ESD diodes** (D5–D11, PESD5V0L2BT).

---
