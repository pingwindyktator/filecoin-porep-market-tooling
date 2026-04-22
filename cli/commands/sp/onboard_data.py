import json
import subprocess
import tempfile
from pathlib import Path
from urllib.parse import urlparse

import click

from cli import utils
from cli.commands import utils as commands_utils
from cli.services.contracts.porep_market import PoRepMarket, PoRepMarketDealState


@click.command()
@click.argument("deal_id", type=click.IntRange(min=0))
@click.option("--output-dir", type=click.Path(), required=True, help="Directory to save downloaded pieces")
@click.option("--jobs", default=1, type=click.IntRange(min=1), show_default=True, help="Number of parallel downloads")
# TODO add commP files verification after download
def onboard_data(deal_id: int, output_dir: str, jobs: int):
    """
    Onboard (download) data for a given deal using aria2 downloader.

    DEAL_ID - ID of the deal to download pieces for.

    \b
    See https://aria2.github.io/ and https://github.com/aria2/aria2 for more information about aria2 and installation instructions.
    """

    aria2c_path = utils.get_env_required("ARIA2C_PATH", default="aria2c")

    try:
        subprocess.run([aria2c_path, "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    except Exception:
        raise Exception("aria2c is not installed or not found in PATH. Please install aria2c to use this command.")

    deal = PoRepMarket().get_deal_proposal(deal_id)

    if deal.state != PoRepMarketDealState.COMPLETED:
        raise Exception(f"Deal id {deal_id} is not in COMPLETED state")

    _output_dir = Path(output_dir).resolve()
    _output_dir.mkdir(parents=True, exist_ok=True)
    manifest_file = _output_dir / f"manifest_{deal.deal_id}.json"
    manifest = commands_utils.fetch_manifest(deal.manifest_location, show_manifest=False, retries=10)

    if manifest_file.exists():
        with open(manifest_file, "r", encoding="utf-8") as f:
            existing_manifest = json.load(f)

        if utils.json_pretty(existing_manifest, True) != utils.json_pretty(manifest, True):
            if not utils.ask_user_confirm(f"A different manifest already exists in the output directory: {manifest_file}\n"
                                          "Do you want to overwrite it?", default_answer=False):
                #
                click.echo("Canceled!")
                return

    host = urlparse(deal.manifest_location)
    download_host = f"{host.scheme or 'http'}://{host.hostname}:7777"
    pieces = manifest[0]["pieces"]

    with tempfile.NamedTemporaryFile(delete=False) as f:
        aria2_file = Path(f.name)

    try:
        with open(aria2_file, "w", encoding="utf-8") as f:
            click.echo("\n")

            for piece in pieces:
                storage_path = piece["storagePath"]
                piece_name = storage_path.removesuffix(".car")

                output_file = _output_dir / storage_path
                output_file.parent.mkdir(parents=True, exist_ok=True)

                if _output_dir not in output_file.parents:
                    raise Exception(f"Invalid manifest piece storagePath: {storage_path}")

                download_url = f"{download_host}/piece/{piece_name}"

                f.write(f"{download_url}\n")
                f.write(f"  out={output_file.name}\n")
                f.write(f"  dir={output_file.parent}\n")

                click.echo(f"Download {download_url} -> {output_file}")

            if not utils.ask_user_confirm("\n\nContinue?", default_answer=True):
                click.echo("Canceled!")
                return

        with open(manifest_file, "w", encoding="utf-8") as f:
            f.write(utils.json_pretty(manifest))

        click.echo("\n")
        try:
            subprocess.run(
                [
                    aria2c_path,
                    "-i", str(aria2_file),
                    "-j", str(jobs),
                    "-x", "4",
                    "-s", "4",
                    "--continue=true",
                    "--auto-file-renaming=false",
                    "--summary-interval=30",
                    "--console-log-level=warn",
                ],
                check=True,
            )
            #
        except subprocess.CalledProcessError as e:
            raise Exception(f"aria2c failed with exit code {e.returncode}")
    finally:
        aria2_file.unlink(missing_ok=True)
