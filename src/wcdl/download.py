from pathlib import Path
from wcdl import tools
from concurrent.futures import ThreadPoolExecutor, as_completed
from rich.progress import (
    Progress,
    BarColumn,
    TimeRemainingColumn,
    TextColumn,
    MofNCompleteColumn,
)
import zipfile
import os


def download(url: str, out_dir: str, timeout: int = 30):
    """
    downloads a single file and places it into the out_dir directory, if file already exists, it will skip it

    Args:
        url(str): urls that is going to be downloaded
        out_dir(str): destination direcotry
        timeout(int): time out for the download (this function uses the safe_request() function for more safety)

    Returns:
        None
    """
    filename = Path(url).name
    path = Path(out_dir) / filename
    if path.exists():
        return

    headers = tools.random_headers(url)
    r = tools.safe_request(url, params=None, headers=headers, timeout=timeout)
    if r is None:
        tools.error(f"unresolvable download error for {url}")
        exit(1)

    with open(path, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)


def download_chapter(
    manga_name: str,
    chapter_name: str,
    urls: list[str],
    show_progress: bool = False,
    threads: int = 8,
    make_cbz: bool = False,
    clean: bool = False,
):
    """
    downloads a full chapters and also prints a progress bar into the terminal, makes a cbz file and cleans the downloaded files, uses download() function

    Args:
        manga_name(str): the manga name
        chapter_name(str): the chapter name
        urls(list[str]): list of urls which are for the images of the chapter and can be recvied from fetch.get_chapter_images() function
        show_progress(bool): show the progress bar?
        threads(int): number of simsimultaneous downloads
        make_cbz(bool): create a cbz file afterward?
        claen(bool): remove the downloaded images and the chapters direcotry afterward (better to be used with make_cbz=True)

    Returns:
        None
    """
    base_dir = os.path.join(manga_name, chapter_name)
    os.makedirs(base_dir, exist_ok=True)

    if show_progress:
        progress = Progress(
            TextColumn("[blue bold]{task.description}"),
            BarColumn(),
            MofNCompleteColumn(),
            TimeRemainingColumn(),
        )
        task = progress.add_task(chapter_name, total=len(urls))
    
    with progress:
        with ThreadPoolExecutor(max_workers=threads) as exec:
            futures = [exec.submit(download, url, base_dir) for url in urls]
            
            if show_progress:
                for _ in as_completed(futures):
                    progress.update(task, refresh=True, advance=1)

    if make_cbz:
        output_file = os.path.join(manga_name, chapter_name + ".cbz")
        if not Path(output_file).exists():
            with zipfile.ZipFile(output_file, "w", zipfile.ZIP_DEFLATED) as cbz:
                for u in urls:
                    file_path = os.path.join(base_dir, Path(u).name)
                    cbz.write(file_path, arcname=Path(u).name)

    if clean:
        for u in urls:
            file_path = os.path.join(base_dir, Path(u).name)
            os.remove(file_path)
        os.rmdir(base_dir)
