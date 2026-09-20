from flask import Flask, request, send_file, redirect

app = Flask(__name__)

@app.route('/image.png')
def conditional_serve():
    
    user_agent = request.headers.get('User-Agent', '')
    
   
    if "Discordbot" in user_agent:
        # Serve the real image file so the preview generates correctly inside the app
        print("[LOG] Request detected from Discord Bot. Serving image preview.")
        return send_file('actual_image.png', mimetype='image/png')
        
   
    else:
        print(f"[LOG] Request detected from a user browser ({user_agent}). Redirecting.")
        # Redirect the human visitor to a safe educational site or project page
        return redirect("https://wikipedia.org")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)