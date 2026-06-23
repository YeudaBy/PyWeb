from pyweb_client import main as pyweb_client

if __name__ == "__main__":
    try:
        pyweb_client.run()
    except KeyboardInterrupt:
        exit(0)
