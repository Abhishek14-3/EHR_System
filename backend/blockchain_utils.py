import requests


def upload_to_ipfs(file_path):
    """Upload a file to IPFS and return its content hash (CID)."""
    with open(file_path, 'rb') as f:
        files = {'file': f}
        response = requests.post('http://127.0.0.1:5001/api/v0/add', files=files)
        response.raise_for_status()
    return response.json()['Hash']


def get_from_ipfs(cid):
    """Return the IPFS gateway URL for viewing a file by CID."""
    return f"https://ipfs.io/ipfs/{cid}"