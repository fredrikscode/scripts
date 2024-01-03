import sys
import os
import xmlrpc.client
from deluge_client import DelugeRPCClient
from urllib.parse import urlparse
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

deluge_host = config.get('deluge', 'host')
deluge_port = config.getint('deluge', 'port')
deluge_username = config.get('deluge', 'username')
deluge_password = config.get('deluge', 'password')
deluge_state_dir = config.get('deluge', 'state_path')

rtorrent_url = config.get('rtorrent', 'url')

tracker_seed_requirements = {
    'Torrentleech': {'base_urls': ['https://tracker.torrentleech.org', 'https://tracker.tleechreload.org'], 'seeding_time': int(config.get('torrentleech', 'seeding_time'))},
    'Superbits': {'base_urls': ['https://superbits.org', 'https://sptracker.cc'], 'seeding_time': int(config.get('superbits', 'seeding_time'))},
}

def test_connection_to_deluge():
    try:
        deluge_client.connect()
        print("Successfully connected to Deluge.")
        deluge_client.disconnect()
    except Exception as e:
        print(f"Failed to connect to Deluge: {e}")

def test_connection_to_rtorrent():
    try:
        rtorrent_client.system.listMethods()
        print("Successfully connected to rTorrent.")
    except Exception as e:
        print(f"Failed to connect to rTorrent: {e}")

def get_base_url(url):
    parsed_url = urlparse(url)
    return f"{parsed_url.scheme}://{parsed_url.hostname}"

def identify_matching_torrents():
    try:
        deluge_client.connect()

        torrent_statuses = deluge_client.call('core.get_torrents_status', {}, ['seeding_time', 'trackers'])
        matching_torrents = []
        added_torrent_ids = set()  # Keep track of torrents already added

        for torrent_id, status in torrent_statuses.items():
            seeding_time = status.get(b'seeding_time')
            trackers = status.get(b'trackers')

            for tracker in trackers:
                tracker_url = tracker.get(b'url', b'').decode('utf-8')
                tracker_base_url = get_base_url(tracker_url)

                for tracker_name, tracker_info in tracker_seed_requirements.items():
                    if tracker_base_url in tracker_info['base_urls'] and seeding_time and seeding_time >= tracker_info['seeding_time'] * 3600:
                        if torrent_id.decode('utf-8') not in added_torrent_ids:
                            matching_torrents.append((torrent_id.decode('utf-8'), tracker_name, tracker_url))
                            added_torrent_ids.add(torrent_id.decode('utf-8'))
                        break  # Break if matched

        return matching_torrents

    except Exception as e:
        print(f"Failed to identify matching torrents: {e}")
        return []

    finally:
        deluge_client.disconnect()

def add_torrent_to_rtorrent(torrent_file_path):
    try:
        with open(torrent_file_path, 'rb') as f:
            torrent_content = xmlrpc.client.Binary(f.read())

        rtorrent_client = xmlrpc.client.ServerProxy(rtorrent_url)
        rtorrent_client.load.raw_start('', torrent_content)
        print(f"Torrent added and started in rTorrent: {os.path.basename(torrent_file_path)}")
        return True

    except Exception as e:
        print(f"Failed to add torrent to rTorrent: {e}")
        return False

def move_matching_torrents_to_rtorrent(matching_torrents):
    for torrent_id, _, _ in matching_torrents:
        torrent_file_path = os.path.join(deluge_state_dir, f"{torrent_id}.torrent")
        if os.path.isfile(torrent_file_path):
            if add_torrent_to_rtorrent(torrent_file_path):
                try:
                    # Reinitialize and connect the deluge client
                    deluge_client = DelugeRPCClient(deluge_host, deluge_port, deluge_username, deluge_password)
                    deluge_client.connect()
                    deluge_client.call('core.remove_torrent', torrent_id, False)  # True to remove data
                    print(f"Torrent {torrent_id} removed from Deluge.")
                    deluge_client.disconnect()
                except Exception as e:
                    print(f"Failed to remove torrent {torrent_id} from Deluge: {e}")
                    if deluge_client.connected:
                        deluge_client.disconnect()

deluge_client = DelugeRPCClient(deluge_host, deluge_port, deluge_username, deluge_password)
rtorrent_client = xmlrpc.client.ServerProxy(rtorrent_url)

if len(sys.argv) > 1 and sys.argv[1] == 'test':
    print("Running in test mode...")
    test_connection_to_deluge()
    test_connection_to_rtorrent()
else:
    matching_torrents = identify_matching_torrents()
    if matching_torrents:
        print("Matching torrents that would be moved to rTorrent:")
        for torrent_id, tracker_name, tracker_url in matching_torrents:
            print(f"Torrent ID: {torrent_id}, Tracker: {tracker_name}, URL: {tracker_url}")

        move_matching_torrents_to_rtorrent(matching_torrents)
    else:
        print("No matching torrents found.")
