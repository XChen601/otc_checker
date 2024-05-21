import os

import requests
import json
import datetime
import schedule
import time

from dotenv import load_dotenv
load_dotenv()
class OtcChecker:
    def __init__(self):
        self.saved_events = []
        self.discord_token = os.getenv('DISCORD_TOKEN')

    def get_finra_data(self, date=None):
        if not date:
            current_date = datetime.datetime.now()
            date = current_date.strftime('%Y-%m-%d')
            print(date)

        url = "https://api.finra.org/data/group/otcMarket/name/otcDailyList"
        payload = json.dumps({
            "quoteValues": False,
            "delimiter": "|",
            "limit": 5000,
            "sortFields": [
                "-dailyListDatetime",
                "+oldSymbolCode"
            ],
            "dateRangeFilters": [
                {
                    "fieldName": "dailyListDatetime",
                    "startDate": f"{date} 00:00:00",
                    "endDate": f"{date} 23:59:59"
                }
            ]
        })
        headers = {
            'accept': 'application/json',
            'accept-language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
            'content-type': 'application/json',
            'cookie': '_cfuvid=gOZwp_WFer1QDujyW5Bqsv54wi7Ph.d2QOedtR.9D4A-1715375198995-0.0.1.1-604800000; _ga=GA1.1.24254548.1715375197; __cf_bm=Ph6WZm0FgYSzgB1ddYp8PS3QqwV0hVi00oao6u5hebg-1715378983-1.0.1.1-uzihfFfIVlkpJiIaZlPaCVsv4O6y9dp322zEFPy45AqhtH1Vdhqe3ENGvgGCEfvJxI7pp0b7WhGxiEbdafVbVw; _ga_2BPYJP2DGG=GS1.1.1715378981.2.0.1715379099.0.0.0',
            'origin': 'https://otce.finra.org',
            'priority': 'u=1, i',
            'referer': 'https://otce.finra.org/',
            'sec-ch-ua': '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
        }

        try:
            response = requests.request("POST", url, headers=headers, data=payload)
            events = response.json()
            print(events)

        except Exception as e:
            events = []
            print(e)

        return events

    def filter_events(self, events):
        filtered_events = []
        for event in events:
            if 'Reverse Split' in event['dailyListReasonDescription']:
                filtered_events.append(event)

        return filtered_events

    def send_filtered_list(self, filtered_events):
        if not filtered_events:
            return
        message = "@everyone \n"
        for event in filtered_events:
            message += self.create_event_message(event)
        print(message)
        print(self.send_discord_message(message))

    def create_event_message(self, event):
        symbol = event['oldSymbolCode']
        exDate = event['exDate']
        ratio = event['reverseSplitRate']

        return f"Symbol: {symbol} | Ex Date: {exDate} | Ratio : {ratio}\n"

    def send_discord_message(self, message):
        url = "https://discord.com/api/v9/channels/1080693441303953468/messages"
        payload = json.dumps({
            "mobile_network_type": "unknown",
            "content": message,
            "tts": False,
            "flags": 0
        })
        headers = {
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
            'authorization': self.discord_token,
            'content-type': 'application/json',
            'cookie': 'ph_foZTeM1AW8dh5WkaofxTYiInBhS4XzTzRqLs50kVziw_posthog=%7B%22distinct_id%22%3A%221891b891d85d49-055b9903f2b93d-26031d51-384000-1891b891d86169c%22%2C%22%24device_id%22%3A%221891b891d85d49-055b9903f2b93d-26031d51-384000-1891b891d86169c%22%2C%22%24user_state%22%3A%22anonymous%22%2C%22extension_version%22%3A%221.5.5%22%2C%22%24session_recording_enabled_server_side%22%3Afalse%2C%22%24autocapture_disabled_server_side%22%3Afalse%2C%22%24active_feature_flags%22%3A%5B%5D%2C%22%24enabled_feature_flags%22%3A%7B%22enable-session-recording%22%3Afalse%2C%22sourcing%22%3Afalse%2C%22only-company-edit%22%3Afalse%2C%22job-lists%22%3Afalse%7D%2C%22%24feature_flag_payloads%22%3A%7B%7D%7D; _ga_YL03HBJY7E=GS1.1.1712279950.5.0.1712280013.0.0.0; __dcfduid=fdb5c85401e711ef8bc7d23a7f93f105; __sdcfduid=fdb5c85401e711ef8bc7d23a7f93f10514289ef4e1abba4b2a48702d1c466e243532079c38ec887ef0cb3ea2158e27c1; __cfruid=c512e05c5e4ea7c4af489f4e882ce7a1162c47a4-1713928137; cf_clearance=CdKLkTwrRBfnqP5sYK84JcDlFYB.p94GkuKJ6dJF4WE-1714420575-1.0.1.1-Dz0ZCa.DlxgTLu27fQNOanrIk4CEwEho.0wCbB55.X9LtSftoL82tUvhULMPGZkoG7k1hPh452xu.t.vwx428g; _cfuvid=z5MGYN25mxiVNGiTGEmii9HjalVHIIRNg_HvqDjMVj4-1715380906191-0.0.1.1-604800000; locale=en-US; _gcl_au=1.1.2083692572.1715380905; cf_clearance=kWFy4c2MSDri4akEwt5TreC8NhtRKbXJKKITyLIX8vg-1715380907-1.0.1.1-WYH7qPTCwR4tDT_FQ.AQA930Y4VwbPkTDESHxQhFdyt5vkhMs.JfTYViYWOQxYkYxG3L.W53GR1NoJQMgMvMMw; _ga=GA1.1.1007521200.1647663730; OptanonConsent=isIABGlobal=false&datestamp=Fri+May+10+2024+18%3A41%3A45+GMT-0400+(Eastern+Daylight+Time)&version=6.33.0&hosts=&landingPath=NotLandingPage&groups=C0001%3A1%2CC0002%3A1%2CC0003%3A1&AwaitingReconsent=false; _ga_Q149DFWHT7=GS1.1.1715380904.64.0.1715380906.0.0.0; __dcfduid=22b1a24cb80311ee946d2ebcf1c675b4; __sdcfduid=22b1a24cb80311ee946d2ebcf1c675b4de8834b3e5fa4ec420a743b5ffa6d5cf4e1e0c79bd540f15310b038fb2ccd807',
            'origin': 'https://discord.com',
            'priority': 'u=1, i',
            'referer': 'https://discord.com/channels/@me/1080693441303953468',
            'sec-ch-ua': '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            'x-debug-options': 'bugReporterEnabled',
            'x-discord-locale': 'en-US',
            'x-discord-timezone': 'America/New_York',
            'x-super-properties': 'eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiQ2hyb21lIiwiZGV2aWNlIjoiIiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzEyNC4wLjAuMCBTYWZhcmkvNTM3LjM2IiwiYnJvd3Nlcl92ZXJzaW9uIjoiMTI0LjAuMC4wIiwib3NfdmVyc2lvbiI6IjEwIiwicmVmZXJyZXIiOiJodHRwczovL3dob3AuY29tLyIsInJlZmVycmluZ19kb21haW4iOiJ3aG9wLmNvbSIsInJlZmVycmVyX2N1cnJlbnQiOiIiLCJyZWZlcnJpbmdfZG9tYWluX2N1cnJlbnQiOiIiLCJyZWxlYXNlX2NoYW5uZWwiOiJzdGFibGUiLCJjbGllbnRfYnVpbGRfbnVtYmVyIjoyOTE5NjMsImNsaWVudF9ldmVudF9zb3VyY2UiOm51bGwsImRlc2lnbl9pZCI6MH0='
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        if response.status_code == 200:
            return True
        return False

    def check_daily(self):
        while True:
            all_events = self.get_finra_data()
            rs_events = self.filter_events(all_events)
            rs_events_set = {tuple(sorted(event.items())) for event in rs_events}
            saved_events_set = {tuple(sorted(event.items())) for event in self.saved_events}
            new_events_set = rs_events_set - saved_events_set
            new_events = [dict(event) for event in new_events_set]
            print("new events:", new_events)
            self.saved_events.extend(new_events)
            self.send_filtered_list(new_events)
            time.sleep(900)

if __name__ == '__main__':
    otc_checker = OtcChecker()
    otc_checker.check_daily()
