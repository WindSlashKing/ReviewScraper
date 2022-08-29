import os
path = 'C:\\Users\\babag\\Documents\\GitHub\\AscendBot-v3.0\\message-spammer\\Spam Messages'
files = os.listdir(path=path)
for file in files:
    with open(os.path.join(path, file), 'r', encoding='utf-8') as f:
        content = f.read()
        content = content.replace('https://ascend.ezyro.com', 'https://discord.gg/gxMrfkTEPW')
    with open(os.path.join(path, file), 'w', encoding='utf-8') as f:
        f.write(content)    
        
