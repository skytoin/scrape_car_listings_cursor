# 🚗 Car Listings Scraper A Python project that **scrapes car listings and images** from [Cars.com](https://www.cars.com/), using filters like car model and production year. Each listing includes: - 📸 Car images - 📄 Description - 🏷️ Model name - 📅 Year produced This project is built using **vanilla Python** and follows clean, modular coding practices with the help of **Cursor** (AI-powered code editor). --- ## ✅ Features (Current) - Scrape listings based on car model and year - Extract and download listing images - Parse model name, production year, and description - Store data in a clean, organized format --- ## 🛠️ Setup Instructions 1. **Clone the repository**
bash
git clone https://github.com/skytoin/scrape_car_listings_cursor.git
cd your-repo
(Already done) Create and activate the virtual environment

bash
Copy code
python -m venv venv
venv\Scripts\activate  # Windows
Install required packages

bash
Copy code
pip install -r requirements.txt
Run the scraper

bash
Copy code
python scraper.py
📁 Project Structure
graphql
Copy code
.
├── scraper.py         # Main scraping logic
├── images/            # Downloaded images
├── tests/             # Unit tests
├── requirements.txt   # Python dependencies
├── README.md          # Project info and usage
└── CURSOR.md          # Development guidelines and code standards
🧭 Roadmap
Planned future features:

Filter by price, mileage, location

Multi-page scraping

Save results to CSV or JSON

Scrape other car listing websites

📘 Development Guidelines
For full dev practices, code style, structure, and Git workflow, see CURSOR.md