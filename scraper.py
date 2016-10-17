import json, csv, requests, requests_cache, sqlite3, dateutil.parser

DB_FILE = 'data.sqlite'
conn = sqlite3.connect(DB_FILE)
c = conn.cursor()

c.execute("DROP TABLE IF EXISTS data")
c.execute("CREATE TABLE IF NOT EXISTS data (album,year,artist,rating_avg,count,item_id UNIQUE)")

req = requests.Session()
requests_cache.install_cache('allmusic')

headers = {'referer':'http://www.allmusic.com/advanced-search','user-agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.59 Safari/537.36'}
payload = {'filters[]': 'editorialrating:9', 'sort': ''}

link = 'http://www.allmusic.com/advanced-search/results/{0}'
rating_link = 'http://www.allmusic.com/rating/average/{0}'

page_no = 0
while True: #uhh
    print('page no',page_no)
    site = req.post(link.format(str(page_no) if page_no>0 else ''),data=payload,headers=headers).text

    #with open('test.html','w') as file:
    #    file.write(site)
    
    if 'desktop-results' not in site:
        print('nothing for page number',page_no)
        break
    if 'http://www.allmusic.com/album/' not in site:
        print('nothing for page number',page_no)
        break
    page_no += 1

    table = site.split('<tbody>')[1].split('</tbody>')[0]
    
    for row in table.split('<tr>')[1:]:
        album = row.split('"title">',1)[1].split('">',1)[1].split('</a',1)[0]
        
        year = row.split('class="year">')[1].split('</td',1)[0].strip()
        
        artist = row.split('artist">')[1].split('</td',1)[0].strip()
        if 'href=' in artist:
            artist = artist.split('">',1)[1].split('</a',1)[0]
        
        item_id = row.split('/album/',1)[1].split('"',1)[0].split('-')[-1]

        rating_data = json.loads(req.get(rating_link.format(item_id.upper()),headers=headers).text)
        rating_avg = rating_data[0]['average']

        count = rating_data[0]['count']
        item_id = rating_data[0]['itemId']
        #print(album,item_id,rating_data)
        #album,year,artist,rating_avg,count,item_id)
        c.execute('INSERT OR REPLACE INTO data VALUES(?,?,?,?,?,?)',[album,year,artist,rating_avg,count,item_id])
        
    print('Done')
    conn.commit()
c.close()
