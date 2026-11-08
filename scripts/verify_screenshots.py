import http.server
import socketserver
import threading
import subprocess
import time
import os

PORT = 8924
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
ARTIFACTS_DIR = r"C:\Users\Asus\.gemini\antigravity\brain\41f7a2ff-7132-41c3-a901-fbeb3db96c9f"

class DualDirectoryHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'docs'), **kwargs)
    def log_message(self, format, *args):
        pass

def take_screenshot(url, out_path, window_size="1440,900"):
    cmd = [
        CHROME_PATH,
        "--headless=new",
        "--disable-gpu",
        f"--window-size={window_size}",
        f"--screenshot={out_path}",
        "--virtual-time-budget=4000",
        url
    ]
    subprocess.run(cmd, check=True)
    print(f"Captured: {out_path} ({window_size})")

def main():
    with socketserver.TCPServer(("", PORT), DualDirectoryHandler) as httpd:
        server_thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        server_thread.start()
        print(f"Server serving docs at port {PORT}")
        time.sleep(1)

        targets = [
            (f"http://localhost:{PORT}/games/index.html", os.path.join(ARTIFACTS_DIR, "arcade_portal_desktop.png"), "1440,900"),
            (f"http://localhost:{PORT}/games/index.html", os.path.join(ARTIFACTS_DIR, "arcade_portal_mobile.png"), "390,844"),
            (f"http://localhost:{PORT}/games/packet-breaker/index.html", os.path.join(ARTIFACTS_DIR, "game_01_packet_breaker.png"), "1280,800"),
            (f"http://localhost:{PORT}/games/circuit-pinball/index.html", os.path.join(ARTIFACTS_DIR, "game_02_circuit_pinball.png"), "1280,800"),
            (f"http://localhost:{PORT}/games/runtime-rush/index.html", os.path.join(ARTIFACTS_DIR, "game_03_runtime_rush.png"), "1280,800"),
            (f"http://localhost:{PORT}/games/firewall-defense/index.html", os.path.join(ARTIFACTS_DIR, "game_04_firewall_defense.png"), "1280,800"),
            (f"http://localhost:{PORT}/games/stack-overflow/index.html", os.path.join(ARTIFACTS_DIR, "game_05_stack_overflow.png"), "1280,800"),
        ]

        for url, out_path, size in targets:
            try:
                take_screenshot(url, out_path, size)
            except Exception as e:
                print(f"Failed {url}: {e}")
        
        httpd.shutdown()

if __name__ == '__main__':
    main()
