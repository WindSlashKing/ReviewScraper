import json
    
BG_WORDS = [
    'педал', 'путка', 'наебан', 'насран',
    'грозен', 'малоумен', 'глупав', 'да еба',
    'шибан', 'копеле', 'боклук', 'чукундур',
    'пача', 'майна'
    ]

ENG_WORDS = [
    'maika', 'pedal', 'kuche', 'putka',
    'naeban', 'nasran', 'grozen', 'maloumen',
    'glupav', 'da eba', 'shiban', 'kopele',
    'bokluk', 'chukundur', 'pacha', 'maina'
    ] 

with open('data.json', 'r') as f:
    json_obj = json.load(f)
url_dict = json_obj['data']['pairs']

with open('filtered reviews.txt', 'r', encoding='utf-8') as f:
    saved_reviews = f.read()

with open('filtered reviews.txt', 'a', encoding='utf-8') as f:
    for url, reviews in url_dict.items():
        for review in reviews:
            for word in ENG_WORDS:
                if word in review.lower() and review not in saved_reviews:
                    #print(f'########{word}#########', review)
                    f.write(f'{review} - {url}\n')
                    break  
            # for word in BG_WORDS:
            #     if word in review.lower() and review not in saved_reviews:
            #         f.write(f'{review} - {url}\n')
            #         break     

