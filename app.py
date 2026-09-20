from flask import Flask, request, send_file, redirect

app = Flask(__name__)

@app.route('/image.png')
def conditional_serve():
    user_agent = request.headers.get('User-Agent', '')
    
    if "UptimeRobot" in user_agent:
        return "OK", 200

    client_ip = request.headers.get('True-Client-IP')
    if not client_ip:
        ip_header = request.headers.get('X-Forwarded-For', request.remote_addr)
        client_ip = ip_header.split(',')[0].strip() if ip_header else 'Unknown IP'
    
    if "Discordbot" in user_agent:
        print(f"[LOG] Discord Bot detected | IP: {client_ip} | Serving preview.")
        return send_file('actual_image.png', mimetype='image/png')
    else:
        print(f"[LOG] User browser detected | IP: {client_ip} | Redirecting.")
        return redirect("https://wikipedia.org")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
