from flask import Flask, request, send_file, redirect
import requests
import re

app = Flask(__name__)

def clean_ip(ip_string):
    if not ip_string:
        return None
    match = re.search(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', ip_string)
    return match.group(0) if match else None

def get_location_data(ip_address):
    valid_ip = clean_ip(ip_address)
    if not valid_ip or valid_ip == '127.0.0.1':
        return "Unknown Country", "Unknown City"
        
    try:
        url = f"http://ip-api.com{valid_ip}"
        response = requests.get(url, timeout=3)
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                country = data.get('country', 'Unknown Country')
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
    
    country, city = get_location_data(ip_header)
    clean_display_ip = clean_ip(ip_header) or "Unknown IP"
    
    if "Discordbot" in user_agent:
        print(f"[LOG] Discord Bot detected | IP: {clean_display_ip} | Location: {city}, {country} | Serving preview.")
        return send_file('actual_image.png', mimetype='image/png')
    else:
        print(f"[LOG] User browser detected | IP: {clean_display_ip} | Location: {city}, {country} | Redirecting.")
        return redirect("https://wikipedia.org")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
