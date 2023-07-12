import subprocess


def main(urls: list[str]):
    for url in urls:
        subprocess.Popen(["twitch-dl", "download", url, "-q", "source"])


if __name__ == "__main__":
    main(["1863051677"])
