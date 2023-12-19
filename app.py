from flask import Flask, request, jsonify, render_template
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
import qrcode
url = ""
app = Flask(__name__)

titles = []
descriptions = []
# prices = []
ratings = []
review_counts = []

def generate_qr_code(text, file_name='static/qrcode.png'):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(text)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img.save(file_name)

def get_description(soup):
    bullet_list = soup.find('ul', class_='a-unordered-list a-vertical a-spacing-mini').find_all('li')
    items = [item.get_text(strip=True) for item in bullet_list]

    description = ""
    for i in items:
        description += i + "\n"
    
    return description
def get_title(soup):
	
	try:
		# Outer Tag Object
		title = soup.find("span", attrs={"id":'productTitle'})

		# Inner NavigableString Object
		title_value = title.string

		# Title as a string value
		title_string = title_value.strip()

	except AttributeError:
		title_string = ""	

	return title_string

# Function to extract Product Rating
def get_rating(soup):

	try:
		rating = soup.find("i", attrs={'class':'a-icon a-icon-star a-star-4-5'}).string.strip()
		
	except AttributeError:
		
		try:
			rating = soup.find("span", attrs={'class':'a-icon-alt'}).string.strip()
		except:
			rating = ""	

	return rating

# Function to extract Number of User Reviews
def get_review_count(soup):
	try:
		review_count = soup.find("span", attrs={'id':'acrCustomerReviewText'}).string.strip()
		
	except AttributeError:
		review_count = ""	

	return review_count



@app.route('/', methods=['GET', 'POST'])
def index():
	# global prices

	if request.method == 'POST':
		global url
		user_details = request.form
		url = user_details['url']

	if url != "":
		global titles, descriptions, ratings, review_counts

		webpage = requests.get(url)

		# Soup Object containing all data
		soup = BeautifulSoup(webpage.content, "lxml")
		
		print(f"\nURL Entered: {url}\n")
		title = get_title(soup)
		rating = get_rating(soup)
		review_count = get_review_count(soup)
		# price = get_price(soup)
		description = get_description(soup)
		
		# Appends all the values to the global lists
		titles.append(title)
		ratings.append(rating)
		review_counts.append(review_count)
		# prices.append(price)
		descriptions.append(description)

	data = zip(titles, ratings, review_counts, descriptions)
	
	return render_template('index.html', data=data)

@app.route('/qr-code', methods=['GET', 'POST'])
def qr_code():
		text_to_encode = ""
		for i in titles:
			text_to_encode += i + "\n\n"

		generate_qr_code(text_to_encode)

		return render_template('qrcode.html')

@app.route('/clear', methods=['GET', 'POST'])
def clear_items():
	global titles, descriptions, ratings, review_counts, url
	titles = []
	descriptions = []
	ratings = []
	review_counts = []
	url = ""
	return render_template('index.html')
	
if __name__ == '__main__':
    app.run(debug=True)
