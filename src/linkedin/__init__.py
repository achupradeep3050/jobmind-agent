"""LinkedIn integration — package marker."""
from .client import LinkedInClient
from .scrape_utils import extract_jd_with_scrapegraph, batch_extract_jds

__all__ = ["LinkedInClient", "extract_jd_with_scrapegraph", "batch_extract_jds"]