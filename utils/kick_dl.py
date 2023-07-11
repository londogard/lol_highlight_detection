import os


def download(self, url: str, output_path: str) -> None:
    source_url = self._get_source_url(url)

    if not source_url:
        raise Exception("could not find a source url for given broadcast")

    command = f"ffmpeg -i {source_url} -vcodec copy -acodec copy {output_path}"
    os.system(command)
