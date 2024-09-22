from flask import Flask, jsonify
from bs4 import BeautifulSoup
import requests

app = Flask(__name__)

# Function to fetch and normalize prices from Alfabeta
def get_concerta_prices_alfabeta():
    url = "https://www.alfabeta.net/precio/concerta.html"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "lxml")
    
    prices = []
    table_rows = soup.find_all("tr", class_="lproducto")
    
    for row in table_rows:
        next_rows = row.find_next_siblings("tr")
        for next_row in next_rows:
            description_cell = next_row.find("td", class_="tddesc")
            price_cell = next_row.find("td", class_="tdprecio")
            if description_cell and price_cell:
                description = description_cell.get_text(strip=True)
                price = price_cell.get_text(strip=True).replace("$", "").replace(",", "")  # Remove currency symbol and commas
                price = float(price) * 1000  # Fix price scaling for Alfabeta
                
                # Standardize presentation format (remove "LP")
                description = description.replace("LP", "").strip()
                
                prices.append({
                    "product": "Concerta",
                    "presentation": description,
                    "price": price,
                    "source": "Alfabeta"
                })

    return prices

# Function to fetch and normalize prices from Kairos
def get_concerta_prices_kairos():
    url = "https://ar.kairosweb.com/precio/producto-concerta-14697/"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "lxml")

    prices = []
    presentaciones = soup.find_all("div", class_="row presentacion")

    for presentacion in presentaciones:
        description = presentacion.find("h5", class_="ttl-pres").text.strip()
        price = presentacion.find("div", class_="precio").text.strip().replace("$", "").replace(",", "")  # Remove currency symbol and commas
        price = float(price)
        
        # Standardize presentation format (remove "LP")
        description = description.replace("LP", "").strip()
        
        prices.append({
            "product": "Concerta",
            "presentation": description,
            "price": price,
            "source": "Kairos"
        })

    return prices

# Function to fetch and normalize prices from Precios de Remedios
def get_concerta_prices_preciosderemedios():
    url = "https://www.preciosderemedios.com.ar/precios/?pattern=concerta"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "lxml")

    prices = []
    rows = soup.select("#resultadoConsulta tbody tr")

    for row in rows:
        product = "Concerta"  # Product is fixed for this query
        presentation = row.find_all("td")[1].text.strip()
        price = row.find_all("td")[2].text.strip().replace("$", "").replace(",", "")  # Remove currency symbol and commas
        price = float(price)
        
        # Standardize presentation format (remove "LP")
        presentation = presentation.replace("LP", "").strip()
        
        prices.append({
            "product": product,
            "presentation": presentation,
            "price": price,
            "source": "Precios de Remedios"
        })

    return prices

# API endpoint to get normalized Concerta prices from all sources
@app.route("/concerta-prices", methods=["GET"])
def concerta_prices():
    try:
        alfabeta_prices = get_concerta_prices_alfabeta()
        kairos_prices = get_concerta_prices_kairos()
        preciosderemedios_prices = get_concerta_prices_preciosderemedios()

        # Combine and return all prices
        combined_prices = alfabeta_prices + kairos_prices + preciosderemedios_prices
        return jsonify(combined_prices)
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(debug=True)
