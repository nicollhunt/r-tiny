from engine_draw import Color

def RGB888to565(c) -> int:
    return ((c[0]>>3)<<11) | ((c[1]>>2)<<5) | c[2]>>3

palette_bright = [
  RGB888to565([0x00,0x00,0x00]),
  RGB888to565([0x01,0x00,0xCE]),
  RGB888to565([0xCF,0x01,0x00]),
  RGB888to565([0xCF,0x01,0xCE]),
  RGB888to565([0x00,0xCF,0x15]),
  RGB888to565([0x01,0xCF,0xCF]),
  RGB888to565([0xCF,0xCF,0x15]),
  RGB888to565([0xCF,0xCF,0xCF]),
]

def get_colour_from_data(data: dict, key: str, fallback: Color = Color(255, 255, 255)) -> Color:
    if key not in data:
        return fallback
        
    value = data[key]
    return RGB888to565(value)