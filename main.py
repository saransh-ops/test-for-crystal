import os
import json
import hashlib
import requests
from datetime import datetime
from colorama import init, Fore, Back, Style
init(autoreset=True)

CONFIG_FILE = "config.json"
DEFAULT_CONFIG = {
    "server_name": "Crystalfbft",
    "google_script_url": "",
    "discord_webhook_url": "",
    "staff_password_hash": "",
    "version": "1.0.0"
}

REASONS = ["Hacking", "Griefing", "Harassment", "Bug Abuse", "Chat Abuse", "Other"]
STATUSES = ["Open", "Investigating", "Resolved", "Rejected"]
STATUS_COLORS = {
    "Open": Fore.YELLOW,
    "Investigating": Fore.CYAN,
    "Resolved": Fore.GREEN,
    "Rejected": Fore.RED
}
REASON_PRIORITY = {
    "Hacking": "🔴 HIGH",
    "Bug Abuse": "🔴 HIGH",
    "Griefing": "🟡 MEDIUM",
    "Harassment": "🟡 MEDIUM",
    "Chat Abuse": "🟢 LOW",
    "Other": "🟢 LOW"
}

def clear(): os.system('cls' if os.name == 'nt' else 'clear')

def load_config():
    if not os.path.exists(CONFIG_FILE):
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG
    with open(CONFIG_FILE) as f:
        return json.load(f)

def save_config(cfg):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(cfg, f, indent=2)

def hash_password(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def banner():
    clear()
    print(Fore.CYAN + r"""
  ██████╗ ██████╗ ███╗   ███╗
  ██╔══██╗██╔══██╗████╗ ████║
  ██████╔╝██████╔╝██╔████╔██║
  ██╔═══╝ ██╔══██╗██║╚██╔╝██║
  ██║     ██║  ██║██║ ╚═╝ ██║
  ╚═╝     ╚═╝  ╚═╝╚═╝     ╚═╝""")
    print(Fore.WHITE + Style.BRIGHT + "  PlayerReportManager" + Fore.CYAN + " v1.0" + Fore.WHITE + " — " + Fore.MAGENTA + "Crystalfbft\n")
    print(Fore.WHITE + "  " + "─" * 40)

def api_get(cfg, params={}):
    try:
        params['_cb'] = str(datetime.now().timestamp())
        r = requests.get(cfg['google_script_url'], params=params, timeout=10)
        return r.json()
    except Exception as e:
        print(Fore.RED + f"  ✗ Connection error: {e}")
        return None

def api_post(cfg, data={}):
    try:
        r = requests.post(cfg['google_script_url'], data=data, timeout=10)
        return r.json()
    except Exception as e:
        print(Fore.RED + f"  ✗ Connection error: {e}")
        return None

def send_discord(cfg, title, description, color=3447003):
    webhook = cfg.get("discord_webhook_url")

    if not webhook:
        return

    payload = {
        "embeds": [{
            "title": title,
            "description": description,
            "color": color,
            "footer": {
                "text": f"{cfg.get('server_name', 'Server')} Report System"
            }
        }]
    }

    try:
        requests.post(webhook, json=payload, timeout=5)
    except:
        pass

def print_report_card(r, index=None):
    sid = f"[{index}] " if index is not None else ""
    status = r.get('status', 'Open')
    sc = STATUS_COLORS.get(status, Fore.WHITE)
    priority = REASON_PRIORITY.get(r.get('reason', ''), '🟢 LOW')
    print(Fore.WHITE + "  " + "─" * 50)
    print(f"  {Fore.CYAN}{sid}{Style.BRIGHT}{r.get('reportId', 'N/A')}" +
          f"  {sc}[{status}]" +
          f"  {Fore.WHITE}{priority}")
    print(f"  {Fore.WHITE}Accused : {Fore.RED + Style.BRIGHT}{r.get('accused', 'N/A')}")
    print(f"  {Fore.WHITE}Reporter: {Fore.YELLOW}{r.get('reporter', 'N/A')}")
    print(f"  {Fore.WHITE}Reason  : {Fore.MAGENTA}{r.get('reason', 'N/A')}")
    print(f"  {Fore.WHITE}Date    : {Fore.WHITE + Style.DIM}{r.get('timestamp', 'N/A')}")
    if r.get('description'):
        desc = r['description'][:80] + ('...' if len(r['description']) > 80 else '')
        print(f"  {Fore.WHITE}Desc    : {Fore.WHITE + Style.DIM}{desc}")

def view_report_full(cfg, report_id):
    banner()
    print(Fore.CYAN + f"  Fetching report {report_id}...\n")
    data = api_get(cfg, {'action': 'get_report', 'reportId': report_id})
    if not data or data.get('result') == 'error':
        print(Fore.RED + f"  ✗ {data.get('message') if data else 'Not found'}")
        input(Fore.WHITE + "\n  Press Enter to go back...")
        return

    r = data
    status = r.get('status', 'Open')
    sc = STATUS_COLORS.get(status, Fore.WHITE)
    priority = REASON_PRIORITY.get(r.get('reason', ''), '🟢 LOW')

    print(Fore.WHITE + "  " + "═" * 50)
    print(f"  {Fore.CYAN + Style.BRIGHT}REPORT {r.get('reportId', 'N/A')}")
    print(Fore.WHITE + "  " + "═" * 50)
    print(f"  Status   : {sc + Style.BRIGHT}{status}")
    print(f"  Priority : {priority}")
    print(f"  Accused  : {Fore.RED + Style.BRIGHT}{r.get('accused', 'N/A')}")
    print(f"  Reporter : {Fore.YELLOW}{r.get('reporter', 'N/A')}")
    print(f"  Reason   : {Fore.MAGENTA}{r.get('reason', 'N/A')}")
    print(f"  Date     : {r.get('timestamp', 'N/A')}")
    if r.get('evidence'):
        print(f"  Evidence : {Fore.CYAN}{r.get('evidence')}")
    print(f"\n  {Fore.WHITE + Style.BRIGHT}Description:")
    print(f"  {Fore.WHITE + Style.DIM}{r.get('description', 'N/A')}")
    if r.get('staffNotes'):
        print(f"\n  {Fore.YELLOW + Style.BRIGHT}Staff Notes:")
        print(f"  {Fore.YELLOW + Style.DIM}{r.get('staffNotes')}")
    if r.get('resolvedBy'):
        print(f"\n  {Fore.GREEN}Handled by: {r.get('resolvedBy')}")

    print(Fore.WHITE + "\n  " + "─" * 50)
    print(f"  {Fore.CYAN}[1]{Fore.WHITE} Change Status   "
          f"{Fore.CYAN}[2]{Fore.WHITE} Reply   "
          f"{Fore.CYAN}[3]{Fore.WHITE} Back")
    choice = input(Fore.CYAN + "\n  › ").strip()

    if choice == '1':
        print(Fore.WHITE + "\n  New status:")
        for i, s in enumerate(STATUSES, 1):
            print(f"  {Fore.CYAN}[{i}]{Fore.WHITE} {s}")
        si = input(Fore.CYAN + "\n  › ").strip()
        if si.isdigit() and 1 <= int(si) <= len(STATUSES):
            new_status = STATUSES[int(si)-1]
            staff = input(Fore.WHITE + "  Your staff name: ").strip()
            result = api_post(cfg, {
                'action': 'update_status',
                'reportId': report_id,
                'status': new_status,
                'resolvedBy': staff
            })
            if result and result.get('result') == 'success':

                send_discord(
                    cfg,
                    f"📌 Report {report_id} Updated",
                    f"**Status:** {new_status}\n**Staff:** {staff}",
                    5763719
                )
                
                print(Fore.GREEN + f"\n  ✓ Status updated to {new_status}")
            else:
                print(Fore.RED + "  ✗ Failed to update")
            input(Fore.WHITE + "  Press Enter to continue...")

    elif choice == '2':
        note = input(Fore.WHITE + "\n  Staff note: ").strip()
        staff = input(Fore.WHITE + "  Your staff name: ").strip()
        result = api_post(cfg, {
            'action': 'add_note',
            'reportId': report_id,
            'note': note,
            'staffName': staff
        })
        if result and result.get('result') == 'success':

            send_discord(
                cfg,
                f"💬 Staff Reply — {report_id}",
                f"**Staff:** {staff}\n\n{note}",
                15844367
            )
            
            print(Fore.GREEN + "\n  ✓ Note added")
        else:
            print(Fore.RED + "  ✗ Failed")
        input(Fore.WHITE + "  Press Enter to continue...")

def list_reports(cfg, filter_status=None, search_accused=None):
    while True:
        banner()
        params = {'action': 'list_reports'}
        if filter_status:
            params['status'] = filter_status
        if search_accused:
            params['accused'] = search_accused

        label = f"Fetching {filter_status or 'all'} reports" + (f" for '{search_accused}'" if search_accused else "") + "..."
        print(Fore.CYAN + f"  {label}\n")
        data = api_get(cfg, params)

        if not data or data.get('result') == 'error':
            print(Fore.RED + "  ✗ Failed to fetch reports")
            input(Fore.WHITE + "\n  Press Enter to go back...")
            return

        reports = data.get('reports', [])
        if not reports:
            print(Fore.YELLOW + "  No reports found.")
            input(Fore.WHITE + "\n  Press Enter to go back...")
            return

        for i, r in enumerate(reports, 1):
            print_report_card(r, i)
        print(Fore.WHITE + "  " + "─" * 50)
        print(f"\n  {Fore.WHITE}Enter report number to view details, or {Fore.CYAN}[0]{Fore.WHITE} to go back:")
        choice = input(Fore.CYAN + "\n  › ").strip()
        if choice == '0' or choice == '':
            return
        if choice.isdigit() and 1 <= int(choice) <= len(reports):
            view_report_full(cfg, reports[int(choice)-1]['reportId'])

def staff_menu(cfg):
    while True:
        banner()
        print(Fore.WHITE + Style.BRIGHT + "  STAFF PANEL\n")
        print(f"  {Fore.CYAN}[1]{Fore.WHITE} View All Open Reports")
        print(f"  {Fore.CYAN}[2]{Fore.WHITE} View All Reports (Any Status)")
        print(f"  {Fore.CYAN}[3]{Fore.WHITE} Filter by Status")
        print(f"  {Fore.CYAN}[4]{Fore.WHITE} Search by Accused Player")
        print(f"  {Fore.CYAN}[5]{Fore.WHITE} View Report by ID")
        print(f"  {Fore.CYAN}[6]{Fore.WHITE} Settings")
        print(f"  {Fore.CYAN}[0]{Fore.WHITE} Logout\n")
        choice = input(Fore.CYAN + "  › ").strip()

        if choice == '1':
            list_reports(cfg, filter_status='Open')
        elif choice == '2':
            list_reports(cfg)
        elif choice == '3':
            banner()
            print(Fore.WHITE + "  Filter by status:\n")
            for i, s in enumerate(STATUSES, 1):
                print(f"  {Fore.CYAN}[{i}]{Fore.WHITE} {s}")
            si = input(Fore.CYAN + "\n  › ").strip()
            if si.isdigit() and 1 <= int(si) <= len(STATUSES):
                list_reports(cfg, filter_status=STATUSES[int(si)-1])
        elif choice == '4':
            accused = input(Fore.WHITE + "\n  Accused username: ").strip()
            if accused:
                list_reports(cfg, search_accused=accused)
        elif choice == '5':
            rid = input(Fore.WHITE + "\n  Report ID: ").strip()
            if rid:
                view_report_full(cfg, rid)
        elif choice == '6':
            settings_menu(cfg)
        elif choice == '0':
            return

def settings_menu(cfg):
    while True:
        banner()
        print(Fore.WHITE + Style.BRIGHT + "  SETTINGS\n")
        print(f"  {Fore.CYAN}[1]{Fore.WHITE} Set Google Script URL")
        print(f"    {Fore.WHITE + Style.DIM}Current: {cfg.get('google_script_url') or 'Not set'}")
        print(f"  {Fore.CYAN}[2]{Fore.WHITE} Set Discord Webhook URL")
        print(f"    {Fore.WHITE + Style.DIM}Current: {'Set ✓' if cfg.get('discord_webhook_url') else 'Not set'}")
        print(f"  {Fore.CYAN}[3]{Fore.WHITE} Change Staff Password")
        print(f"  {Fore.CYAN}[0]{Fore.WHITE} Back\n")
        choice = input(Fore.CYAN + "  › ").strip()

        if choice == '1':
            url = input(Fore.WHITE + "\n  Google Script URL: ").strip()
            cfg['google_script_url'] = url
            save_config(cfg)
            print(Fore.GREEN + "  ✓ Saved")
            input()
        elif choice == '2':
            url = input(Fore.WHITE + "\n  Discord Webhook URL: ").strip()
            cfg['discord_webhook_url'] = url
            save_config(cfg)
            print(Fore.GREEN + "  ✓ Saved")
            input()
        elif choice == '3':
            pw = pwinput(prompt=Fore.WHITE + "\n  New password: ", mask="*")
            cfg['staff_password_hash'] = hash_password(pw)
            save_config(cfg)
            print(Fore.GREEN + "  ✓ Password updated")
            input()
        elif choice == '0':
            return

def login(cfg):
    if not cfg.get('staff_password_hash'):
        banner()
        print(Fore.YELLOW + "  No password set. Setting up for first time...\n")
        pw = input(Fore.WHITE + "  Set a staff password: ").strip()
        cfg['staff_password_hash'] = hash_password(pw)
        save_config(cfg)
        print(Fore.GREEN + "  ✓ Password set!")
        input(Fore.WHITE + "  Press Enter to continue...")
        return True

    banner()
    print(Fore.WHITE + Style.BRIGHT + "  STAFF LOGIN\n")
    from pwinput import pwinput
    pw = pwinput(prompt=Fore.WHITE + "  Password: ", mask="*")
    if hash_password(pw) == cfg['staff_password_hash']:
        print(Fore.GREEN + "\n  ✓ Access granted")
        import time; time.sleep(0.8)
        return True
    else:
        print(Fore.RED + "\n  ✗ Wrong password")
        input(Fore.WHITE + "  Press Enter to exit...")
        return False

def first_time_setup(cfg):
    if cfg.get('google_script_url'):
        return cfg
    banner()
    print(Fore.YELLOW + "  First time setup!\n")
    print(Fore.WHITE + "  You need a Google Apps Script URL to store reports.")
    print(Fore.WHITE + "  See README.md for setup instructions.\n")
    url = input(Fore.WHITE + "  Google Script URL (or press Enter to skip): ").strip()
    if url:
        cfg['google_script_url'] = url
    webhook = input(Fore.WHITE + "  Discord Webhook URL (or press Enter to skip): ").strip()
    if webhook:
        cfg['discord_webhook_url'] = webhook
    save_config(cfg)
    return cfg

def main():
    cfg = load_config()
    cfg = first_time_setup(cfg)
    if not cfg.get('google_script_url'):
        banner()
        print(Fore.RED + "  ✗ No Google Script URL set. Run again and complete setup.")
        return
    if login(cfg):
        staff_menu(cfg)

if __name__ == '__main__':
    main()
