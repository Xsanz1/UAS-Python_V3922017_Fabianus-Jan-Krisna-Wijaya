#!/usr/bin/env python
# coding: utf-8

# In[3]:


from bs4 import BeautifulSoup as bs
import requests as req
import glob, json, os, csv, time

# Base URL and API URL for Bukalapak
baseurl = 'https://www.bukalapak.com/u/'
apiurl = 'https://api.bukalapak.com/stores/'

class Bukalapak:
    def __init__(self, username):
        self.username = username
        self.urltoko = baseurl + username
        self.headerbrowser = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:74.0) Gecko/20100101 Firefox/74.0'}
        
        # Send a GET request to the seller's page
        pg_data = req.get(self.urltoko, headers=self.headerbrowser, timeout=3000)
        try:
            if pg_data.status_code == 200:
                soup = bs(pg_data.text, 'html.parser')
                
                # Get the seller's ID
                print("[+] Mengambil id penjual ...")
                self.idseller = soup.find('a', attrs={'data-user-id': True}).get('data-user-id')
                print("[+] Id penjual: " + self.idseller)
                
                # Get the access token for the API
                print("[+] Mengambil access token ...")
                stoken = soup.find_all('script')
                gtoken = str(stoken[4]).replace("<script>localStorage.setItem('bl_token', '", "").replace(
                    "');</script>", "")
                gtoken = json.loads(str(gtoken))
                self.token = gtoken['access_token']
                print("[+] Access token: " + self.token)
                
                # Start grabbing the products
                self.grabproduk()
            else:
                print("[!] Username tidak ditemukan!")
        except Exception as e:
            print(e)
            print("[!] Website down!")
            exit()

    def grabproduk(self):
        print("=== GRABBING PRODUK ===")
        print("[+] Memulai download halaman produk ...")
        print("\x1B[3m" + "(delay 3 detik untuk menghindari anti-spam!)" + "\x1B[0m")
        
        # Get the total number of products from the API
        api = apiurl + str(self.idseller) + '/products?offset=0&limit=50&access_token=' + self.token
        total_product = req.get(api, headers=self.headerbrowser, timeout=3000).json()
        print("[+] Total produk: " + str(total_product['meta']['total']))
        
        # Remove old files
        print("[+] Hapus file lama ...")
        if not os.path.exists("data"):
            os.makedirs("data")
        for filename in glob.glob("data/" + str(self.idseller) + "_bukalapak*.json"):
            os.remove(filename)
        for filename in glob.glob(str(self.idseller) + "_bukalapak.csv"):
            os.remove(filename)
        
        # Grab each page of products
        a = 0
        b = 0
        while True:
            print("-> download halaman ke-" + str(b + 1))
            api = apiurl + str(self.idseller) + '/products?offset=' + str(a) + '&limit=50&access_token=' + self.token
            pg_data = req.get(api, headers=self.headerbrowser, timeout=3000).json()
            
            # If there are no more products, break the loop
            if len(pg_data['data']) == 0:
                break
            
            # Save the product data to a JSON file
            with open("data/" + str(self.idseller) + "_bukalapak" + str(b) + ".json", 'w') as json_file:
                json.dump(pg_data['data'], json_file)
            
            # Increment offsets and wait for 3 seconds to avoid anti-spam measures
            a += 50
            b += 1
            time.sleep(3)
        
        # Merge all JSON files into one
        print("[+] Merging data produk ...")
        data = []
        for f in glob.glob("data/" + str(self.idseller) + "_bukalapak*.json"):
            with open(f) as infile:
                data.extend(json.load(infile))
        with open("data/" + str(self.idseller) + "_bukalapak_all.json", 'w') as outfile:
            json.dump(data, outfile)
        
        # Create a CSV file with the product data
        print("[+] Membuat csv data produk ...")
        f_data = []
        for i in data:
            f_data.append([
                self.idseller,
                self.username,
                i['store']['name'],
                i['store']['level']['name'],
                i['store']['premium_level'],
                i['id'],
                i['name'],
                i['category']['name'],
                i['condition'],
                i['rating']['average_rate'],
                i['rating']['user_count'],
                i['stock'],
                i['stats']['interest_count'],
                i['stats']['sold_count'],
                i['stats']['view_count'],
                i['price'],
                i['original_price'],
                i['discount_percentage'],
                i['description']
            ])
        
        f_header = [
            'id_seller', 'username', 'nama_toko', 'level_toko', 'premium_toko', 'id_produk', 'nama_produk',
            'kategori', 'kondisi', 'rating', 'jumlah_rating', 'stok', 'jumlah_interest', 'jumlah_sold',
            'jumlah_view', 'harga', 'harga_asli', 'diskon', 'deskripsi'
        ]
        
        with open(str(self.idseller) + '_bukalapak.csv', 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(f_header)
            writer.writerows(f_data)
        
        print('done! ' + str(self.idseller) + '_bukalapak.csv')


print("[+] https://github.com/heryandp/bukalapak-product-scrap")
sname = input("[+] Masukkan username seller: https://www.bukalapak.com/u/")
act = Bukalapak(sname)


# In[4]:


import pandas as pd

# reading the database
data = pd.read_csv("230413328_bukalapak.csv")

# printing the top 10 rows
display(data.head(10))


# In[8]:


import pandas as pd
import matplotlib.pyplot as plt

# Reading the database
data = pd.read_csv("230413328_bukalapak.csv")

# Selecting the first 50 data points
data_subset = data.head(50)

# Scatter plot with 'rating' against 'jumlah_rating'
plt.scatter(data_subset['jumlah_rating'], data_subset['stok'])

# Adding title to the plot
plt.title("Bukalapak - Scatter Plot")

# Setting the x and y labels
plt.xlabel('jumlah_rating')
plt.ylabel('stok')

# Save the plot as a PNG file
plt.savefig('scatter_plot.png', dpi=300, bbox_inches='tight')

# Display the plot
plt.show()


# In[1]:


import pandas as pd
import matplotlib.pyplot as plt

# reading the database
data = pd.read_csv("230413328_bukalapak.csv")

# Scatter plot w day against tip
plt.plot(data['jumlah_rating'])
plt.plot(data['stok'])


# Adding Title to the plot
plt.title("Test")

# Setting the X and Y labels
plt.xlabel('jumlah_rating')
plt.ylabel('stok')

# Save the plot as a PNG file
plt.savefig('line.png', dpi=300, bbox_inches='tight')

plt.show()


# In[ ]:




