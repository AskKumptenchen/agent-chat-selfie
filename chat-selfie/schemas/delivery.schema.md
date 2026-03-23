# Delivery Schema

## Core fields

- mode: every_reply | occasional | heartbeat
- image_source: generate | mood_asset
- target destination
- trigger conditions
- cooldown rules
- caption policy
- fallback_to_generation when image_source = mood_asset

## Heartbeat-specific fields

- enabled
- interval
- allowed hours
- target destination
