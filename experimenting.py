import json

with open('data.json', 'r') as f:
    json_obj = json.load(f)
    #json_obj['data']['pairs']['url4'] = 'helloWorld'
    
pairs = json_obj['data']['pairs']
print(json_obj['data']['pairs']['https://www.google.com/maps/place/%D0%A0%D0%B5%D1%81%D1%82%D0%BE%D1%80%D0%B0%D0%BD%D1%82+%D0%9A%D0%B0%D1%81%D1%82%D0%B5%D0%BB%D0%BE/data=!4m7!3m6!1s0x14abae9c2a4f1f21:0xe39f524f6e3f8f94!8m2!3d41.8275234!4d23.4827003!16s%2Fg%2F11clwl9b0z!19sChIJIR9PKpyuqxQRlI8_bk9Sn-M?authuser=0&hl=bg&rclk=1'])
for pair in pairs:
    json_obj['data']['pairs'][pair][:]

'''
BG_WORDS = [
'педал', 'путка', 
'наебан', 'насран', 'грозен', 'малоумен', 'глупав'
]

ENG_WORDS = ['maika', 'pedal', 'kuche', 'putka',
'naeban', 'nasran', 'grozen', 'maloumen', 'glupav',]

with open('reviews.txt', 'r', encoding='utf-8') as f:
    lines = [line.strip() for line in f.readlines()]

with open('filtered  reviews.txt', 'a', encoding='utf-8') as f:
    for line in lines:
        for word in ENG_WORDS:
            if word in line.lower():
                f.write(line + '\n')
                break   
'''