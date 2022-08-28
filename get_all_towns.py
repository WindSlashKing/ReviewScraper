import requests
from bs4 import BeautifulSoup

def main():
    HEADERS = {
        "Accept": "application/json, text/plain, */*",
        "Referer": "",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.114 Safari/537.36 OPR/89.0.4447.64"
    }
    towns = []
    alphabet = ['А', 'Б', 'В', 'Г', 'Д', 'Е', 'Ж', 'З', 'И', 'Й', 'К', 'Л', 'М', 'Н', 'О', 'П', 'Р', 'С', 'Т', 'У', 'Ф', 'Х', 'Ц', 'Ч', 'Ш', 'Щ', 'Ъ', 'Ю', 'Я']
    for letter in alphabet:
        for page in range(15):
            url  = f'https://www.ekatte.com/а-я/{letter.lower()}?page={page}'
            response = requests.get(url, headers=HEADERS)
            soup = BeautifulSoup(response.text, 'html.parser')
            matches = soup.find_all('a', href=True)
            matches = [match.text for match in matches if len(str(match)) > 150]
            towns.extend(matches)
            if len(matches) < 2:
                print(f'Reached last page of letter {alphabet.index(letter)}')
                break

    with open('temp_file.html', 'w', encoding='utf-8') as f:   
        for town in towns:
            f.write(town + "\n")
    

if __name__ == '__main__':
    main()
    
    #Remove duplicate lines
    # with open('temp_file.html', 'r', encoding='utf-8') as f:
    #     lines = [line.strip() for line in f.readlines()]
    #     lines = list(dict.fromkeys(lines))
    # with open('temp_file.html', 'w', encoding='utf-8') as f:
    #     for line in lines:
    #         f.write(line + "\n")