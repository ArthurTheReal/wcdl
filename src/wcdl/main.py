"""
WCDL - Weeb Central Manga Downloader CLI

A command-line interface for searching and downloading manga from WeebCentral.
"""

import click
import os
import sys
from pathlib import Path
from typing import Optional, List, Tuple
from rich.table import Table
from rich.console import Console
from rich.prompt import Prompt, IntPrompt
from rich import box

from wcdl import fetch, download, tools

console = Console()


def display_search_results(results: List[dict]) -> Table:
    """
    Display search results in a rich table format.
    
    Args:
        results: List of search result dictionaries from fetch.search()
    
    Returns:
        Rich Table object
    """
    table = Table(
        title="[bold blue]Search Results[/bold blue]",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold magenta"
    )
    
    table.add_column("ID", style="cyan", width=3)
    table.add_column("Title", style="green", width=30)
    table.add_column("Year", justify="center", width=6)
    table.add_column("Status", justify="center", width=10)
    table.add_column("Type", justify="center", width=10)
    
    for idx, result in enumerate(results, 1):
        table.add_row(
            str(idx),
            result.get("title", "N/A")[:30],
            str(result.get("year", "N/A")),
            result.get("status", "N/A"),
            result.get("type", "N/A")
        )
    
    return table


def display_manga_info(manga: dict, chapters: List[dict], downloaded_chapters: List[str]) -> None:
    """
    Display detailed manga information.
    
    Args:
        manga: Manga dictionary from search results
        chapters: List of chapters from fetch.get_chapters()
        downloaded_chapters: List of already downloaded chapter IDs
    """
    console.print()
    console.print("[bold cyan]═══════════════════════════════════════[/bold cyan]")
    console.print(f"[bold yellow]Title:[/bold yellow] {manga.get('title', 'N/A')}")
    console.print(f"[bold yellow]Authors:[/bold yellow] {', '.join(manga.get('authors', []))}")
    console.print(f"[bold yellow]Status:[/bold yellow] {manga.get('status', 'N/A')}")
    console.print(f"[bold yellow]Type:[/bold yellow] {manga.get('type', 'N/A')}")
    console.print(f"[bold yellow]Year:[/bold yellow] {manga.get('year', 'N/A')}")
    console.print(f"[bold yellow]Tags:[/bold yellow] {', '.join(manga.get('tags', []))}")
    console.print()
    
    if chapters:
        console.print(f"[bold green]Total Chapters:[/bold green] {len(chapters)}")
        console.print(f"[bold blue]Latest Chapter:[/bold blue] {chapters[-1].get('title', 'N/A')} ({chapters[-1].get('date_added', 'N/A')})")
        console.print(f"[bold magenta]Downloaded:[/bold magenta] {len(downloaded_chapters)}/{len(chapters)}")
    
    console.print("[bold cyan]═══════════════════════════════════════[/bold cyan]")
    console.print()


def select_from_results(results: List[dict]) -> Optional[dict]:
    """
    Display results table and let user select one.
    
    Args:
        results: List of search results
    
    Returns:
        Selected manga dictionary or None if user cancels
    """
    table = display_search_results(results)
    console.print(table)
    
    while True:
        try:
            choice = IntPrompt.ask(
                "[bold cyan]Select a manga by ID[/bold cyan]",
                default=1
            )
            
            if 1 <= choice <= len(results):
                return results[choice - 1]
            else:
                tools.error(f"Please enter a number between 1 and {len(results)}")
        except (ValueError, KeyboardInterrupt):
            return None


def get_downloaded_chapters(manga_name: str) -> List[str]:
    """
    Get list of already downloaded chapter IDs for a manga.
    
    Args:
        manga_name: Name of the manga directory
    
    Returns:
        List of chapter IDs (directory names) that have been downloaded
    """
    manga_dir = Path(manga_name)
    
    if not manga_dir.exists():
        return []
    
    downloaded = []
    for item in manga_dir.iterdir():
        if item.suffix == ".cbz":
            downloaded.append(item.stem)
        elif item.is_dir():
            downloaded.append(item.name)

    return list(set(downloaded))

@click.group()
def cli():
    """WCDL - Weeb Central Manga Downloader"""
    pass


@cli.command()
@click.argument("query")
@click.option(
    "--cbz",
    is_flag=True,
    default=False,
    help="Create CBZ files from downloaded chapters"
)
@click.option(
    "--keep-files",
    is_flag=True,
    default=False,
    help="Keep image files after CBZ creation (use with --cbz)"
)
@click.option(
    "--connections",
    "-c",
    type=int,
    default=4,
    help="Number of simultaneous download connections (default: 4)"
)
@click.option(
    "--range",
    "-r",
    type=str,
    default=None,
    help="Chapter range to download (e.g., '1-5', '1,3,5', or '2')"
)
def download_cmd(query: str, cbz: bool, keep_files: bool, connections: int, range: Optional[str]):
    """
    Search for manga and download chapters.
    
    Usage:
        wcdl download "manga name" --cbz --range 1-10, 12, 25-60
    """
    
    try:
        # Search for the manga
        tools.notic(f"Searching for '{query}'...")
        results = fetch.search(query)
        
        if not results:
            tools.error("No results found")
            return
        
        # Let user select a manga
        selected_manga = select_from_results(results)
        
        if not selected_manga:
            tools.warn("No selection made")
            return
        
        manga_id = selected_manga.get("manga_id")
        manga_title = selected_manga.get("title")
        
        # Get chapters
        tools.notic(f"Fetching chapters for '{manga_title}'...")
        chapters = fetch.get_chapters(manga_id)
        
        if not chapters:
            tools.error("No chapters found")
            return
        
        # Determine which chapters to download
        if range:
            try:
                chapter_indices = tools.parse_range_args(range)
                # Convert indices to actual chapters (1-indexed to 0-indexed)
                chapters_to_download = [
                    chapters[i - 1] for i in chapter_indices
                    if 1 <= i <= len(chapters)
                ]
                
                if not chapters_to_download:
                    tools.error("No valid chapters in specified range")
                    return
                
                # Validate that indices are within bounds
                invalid_indices = [i for i in chapter_indices if i < 1 or i > len(chapters)]
                if invalid_indices:
                    tools.warn(f"Chapters {invalid_indices} are out of range (total: {len(chapters)})")
            
            except click.BadParameter as e:
                tools.error(str(e))
                return
        else:
            # Let user choose which chapters to download
            console.print()
            console.print("[bold yellow]Chapters available:[/bold yellow]")
            
            chapter_table = Table(box=box.ROUNDED, show_header=True, header_style="bold magenta")
            chapter_table.add_column("ID", style="cyan", width=4)
            chapter_table.add_column("Title", style="green", width=40)
            chapter_table.add_column("Date", justify="center", width=12)
            
            for idx, ch in enumerate(chapters, 1):
                chapter_table.add_row(
                    str(idx),
                    ch.get("title", "N/A")[:40],
                    ch.get("date_added", "N/A")
                )
            
            console.print(chapter_table)
            
            range_input = Prompt.ask(
                "[bold cyan]Enter chapter range[/bold cyan] (e.g., '1-5' or '1,3,5')"
            )
            
            try:
                chapter_indices = tools.parse_range_args(range_input)
                chapters_to_download = [
                    chapters[i - 1] for i in chapter_indices
                    if 1 <= i <= len(chapters)
                ]
                
                if not chapters_to_download:
                    tools.error("No valid chapters selected")
                    return
            except click.BadParameter as e:
                tools.error(str(e))
                return
        
        # Download chapters
        console.print()
        tools.notic(f"Starting download of {len(chapters_to_download)} chapter(s)...")
        
        for chapter in chapters_to_download:
            chapter_title = chapter.get("title", "Unknown")
            chapter_id = chapter.get("chapter_id")
            
            try:
                tools.notic(f"Fetching images for {chapter_title}...")
                image_urls = fetch.get_chapter_images(chapter_id)
                
                if not image_urls:
                    tools.error(f"No images found for {chapter_title}")
                    continue
                
                download.download_chapter(
                    manga_name=manga_title,
                    chapter_name=chapter_title,
                    urls=image_urls,
                    show_progress=True,
                    threads=connections,
                    make_cbz=cbz,
                    clean=not keep_files  # If keep_files is True, don't clean
                )
                
                tools.success(f"Downloaded {chapter_title}")
            
            except Exception as e:
                tools.error(f"Failed to download {chapter_title}: {str(e)}")
                continue
        
        tools.success(f"All downloads completed!")
    
    except KeyboardInterrupt:
        console.print("\n[yellow bold][!] Download cancelled by user[/yellow bold]")
        sys.exit(0)
    except Exception as e:
        tools.error(f"An error occurred: {str(e)}")
        sys.exit(1)


@cli.command()
@click.argument("query")
def search_cmd(query: str):
    """
    Search for manga and display detailed information.
    
    Usage:
        wcdl search "manga name"
    """
    
    try:
        # Search for the manga
        tools.notic(f"Searching for '{query}'...")
        results = fetch.search(query)
        
        if not results:
            tools.error("No results found")
            return
        
        # Let user select a manga
        selected_manga = select_from_results(results)
        
        if not selected_manga:
            tools.warn("No selection made")
            return
        
        manga_id = selected_manga.get("manga_id")
        manga_title = selected_manga.get("title")
        
        # Get chapters
        tools.notic(f"Fetching chapters for '{manga_title}'...")
        chapters = fetch.get_chapters(manga_id)
        
        # Get downloaded chapters
        downloaded = get_downloaded_chapters(manga_title)
        
        # Display detailed info
        display_manga_info(selected_manga, chapters, downloaded)
    
    except KeyboardInterrupt:
        console.print("\n[yellow bold][!] Search cancelled by user[/yellow bold]")
        sys.exit(0)
    except Exception as e:
        tools.error(f"An error occurred: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    cli()
