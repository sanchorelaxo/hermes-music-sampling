# Wave Bard — Web App Editor Reference

Access: Chrome/Edge/Firefox desktop (not Safari). PWA-installable.

## Features

- Load WAV, MP3, OGG, AAC, M4A, AIFF
- Organize samples into banks (3–32 per bank)
- Edit scales (3–32 custom scales)
- Edit rhythms (3–32 patterns)
- Set number of sequencer steps (polyrhythms/polymeters)
- Preview samples
- Generate .uf2 firmware file

## To Upload

1. Go to [apps.bastl-instruments.com/wave-bard-sample-loader](https://apps.bastl-instruments.com/wave-bard-sample-loader/)
2. Add/organize samples
3. Click **GENERATE FIRMWARE FILE**
4. Power off → hold SHIFT → power on (connected to USB)
5. Copy .uf2 to RPI-RP2 disk
6. Wait 2–5 minutes

## Tips

- Samples should be tuned to C for scale accuracy
- Remove silence from samples to save memory
- All banks must have same number of samples
- Draft saves allow re-editing before generating .uf2

## Resources

- [Wave Bard Sample Loader Web App](https://apps.bastl-instruments.com/wave-bard-sample-loader/)
- [GitHub (open-source)](https://github.com/bastl-instruments/kastle2)