import json
import logging
import os
import re
import uuid
import feedparser
from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from django.template.defaultfilters import slugify
from django.utils import timezone

from blog.models import Blog, category
from blog.ai_service import get_client, get_gemini_api_key, _call_gemini_with_fallback

logger = logging.getLogger(__name__)

DEFAULT_FEEDS = [
    "https://feeds.arstechnica.com/arstechnica/index",
    "https://www.theverge.com/rss/index.xml",
    "https://techcrunch.com/feed/",
    "https://venturebeat.com/category/ai/feed/",
]


class Command(BaseCommand):
    help = "Generates a daily AI-assisted blog draft from recent technology and AI RSS feeds."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Generate a draft even if one has already been created today.",
        )
        parser.add_argument(
            "--feed-url",
            type=str,
            default=None,
            help="Specify a custom RSS feed URL to fetch headlines from.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Simulate generation without committing changes to the database.",
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Starting daily AI blog draft generator..."))

        today = timezone.now().date()

        # 1. Date-based duplicate prevention
        if not options["force"]:
            existing_today = Blog.objects.filter(is_ai_generated=True, generation_date=today).first()
            if existing_today:
                self.stdout.write(
                    self.style.WARNING(
                        f"An AI draft has already been generated today ({today}): '{existing_today.title}'. "
                        "Skipping generation to prevent duplicates. Pass --force to override."
                    )
                )
                return

        # 2. Check Gemini API credentials
        api_key = get_gemini_api_key()
        if not api_key:
            err_msg = "Gemini API key is missing. Configure GEMINI_API_KEY environment variable."
            self.stderr.write(self.style.ERROR(err_msg))
            raise CommandError(err_msg)

        # 3. Fetch RSS headlines
        feeds_to_check = [options["feed_url"]] if options["feed_url"] else DEFAULT_FEEDS
        entries = self.fetch_rss_entries(feeds_to_check)
        if not entries:
            err_msg = "No articles could be retrieved from configured RSS feeds."
            self.stderr.write(self.style.ERROR(err_msg))
            raise CommandError(err_msg)

        # 4. Select a fresh topic avoiding recent drafts
        selected_entry = self.select_fresh_entry(entries)
        if not selected_entry:
            self.stdout.write(self.style.WARNING("All fetched topics have already been covered in recent drafts."))
            # Fall back to top entry if all seem recent
            selected_entry = entries[0]

        self.stdout.write(
            self.style.SUCCESS(f"Selected headline: '{selected_entry['title']}' from {selected_entry['link']}")
        )

        # 5. Call Gemini to create an original explanatory article
        article_data = self.generate_article_with_gemini(api_key, selected_entry)

        # 6. Validate the structured response
        self.validate_article_data(article_data)

        if options["dry_run"]:
            self.stdout.write(self.style.SUCCESS("[DRY RUN] Generated draft validated successfully. Not saved."))
            self.stdout.write(f"Title: {article_data['title']}")
            self.stdout.write(f"Excerpt: {article_data['short_description']}")
            return

        # 7. Map fields and save to Django database strictly as Draft
        draft_post = self.save_draft(article_data, selected_entry, today)

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully created draft post (ID: {draft_post.pk}): '{draft_post.title}'\n"
                f"Status: {draft_post.status} | Author: {draft_post.author.username} | "
                f"Category: {draft_post.category.category_name}"
            )
        )

    def fetch_rss_entries(self, feed_urls):
        """Fetches and aggregates entries across supplied RSS feeds."""
        aggregated = []
        for url in feed_urls:
            try:
                self.stdout.write(f"Fetching RSS feed: {url}...")
                parsed = feedparser.parse(url)
                if parsed.bozo and not parsed.entries:
                    self.stdout.write(self.style.WARNING(f"Warning: Could not parse feed {url}"))
                    continue
                for item in parsed.entries[:10]:
                    title = getattr(item, "title", "").strip()
                    link = getattr(item, "link", "").strip()
                    summary = getattr(item, "summary", "") or getattr(item, "description", "")
                    if title and link:
                        aggregated.append({
                            "title": title,
                            "link": link,
                            "summary": summary,
                        })
            except Exception as e:
                logger.warning(f"Error fetching RSS feed {url}: {e}")
                self.stdout.write(self.style.WARNING(f"Failed to fetch {url}: {e}"))
        return aggregated

    def select_fresh_entry(self, entries):
        """Selects an entry whose title has not been used in recent posts."""
        recent_posts = list(
            Blog.objects.all().order_by("-created_at")[:25].values_list("title", flat=True)
        )
        recent_titles_lower = [t.lower() for t in recent_posts]

        for item in entries:
            item_title_lower = item["title"].lower()
            # Simple word overlap check
            words = set(re.findall(r"\w+", item_title_lower))
            is_duplicate = False
            for prev in recent_titles_lower:
                prev_words = set(re.findall(r"\w+", prev))
                overlap = words.intersection(prev_words)
                if len(overlap) >= 4:
                    is_duplicate = True
                    break
            if not is_duplicate:
                return item
        return None

    def generate_article_with_gemini(self, api_key: str, entry: dict) -> dict:
        """Asks Gemini to create an original structured article in JSON format."""
        from google.genai import types

        client = get_client(api_key=api_key)

        prompt = (
            "You are an expert technology journalist and explanatory writer.\n"
            "Write an original, informative, and engaging blog article explaining the following news topic and its broader implications.\n\n"
            "EDITORIAL RULES:\n"
            "1. Do NOT copy full sentences or verbatim phrases from the source. Write an original analysis.\n"
            "2. Explain what happened, why it matters, and what readers should know next.\n"
            "3. Do not invent facts, fabricate quotations, or make unverified claims.\n"
            "4. Return strictly a JSON object with this exact structure:\n"
            "{\n"
            '  "title": "Engaging original headline under 95 characters",\n'
            '  "short_description": "Clear 2-3 sentence summary under 300 characters",\n'
            '  "category": "Technology",\n'
            '  "blog_body": "Full article text with clear explanatory paragraphs (approx 350-600 words)",\n'
            f'  "source_urls": ["{entry["link"]}"]\n'
            "}\n\n"
            f"SOURCE MATERIAL:\n"
            f"Headline: {entry['title']}\n"
            f"Link: {entry['link']}\n"
            f"Summary: {entry.get('summary', '')[:1000]}\n"
        )

        system_instruction = (
            "You are an editorial assistant writing factual, original technology blog posts for a publication. "
            "Output valid JSON only."
        )

        try:
            # Request JSON output
            config = types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type="application/json",
            )
        except Exception:
            config = None

        text, _ = _call_gemini_with_fallback(client, contents=prompt, system_instruction=system_instruction)

        # Clean JSON fences if any
        clean_text = text.strip()
        if clean_text.startswith("```"):
            clean_text = re.sub(r"^```(?:json)?\s*", "", clean_text)
            clean_text = re.sub(r"\s*```$", "", clean_text)

        try:
            parsed = json.loads(clean_text)
            return parsed
        except json.JSONDecodeError as err:
            logger.error(f"Failed to decode Gemini JSON response: {clean_text}")
            raise CommandError(f"Model returned invalid JSON: {err}")

    def validate_article_data(self, data: dict):
        """Validates that all required fields are present, non-empty, and compliant."""
        required = ["title", "short_description", "blog_body"]
        for field in required:
            if not data.get(field) or not str(data[field]).strip():
                raise CommandError(f"Generated article is missing required field: '{field}'")

        if len(data["title"]) > 255:
            data["title"] = data["title"][:252] + "..."

        if len(data.get("short_description", "")) > 1000:
            data["short_description"] = data["short_description"][:997] + "..."

        if len(data["blog_body"].split()) < 50:
            raise CommandError("Generated article body is suspiciously short.")

    def save_draft(self, data: dict, entry: dict, date_today) -> Blog:
        """Maps fields and saves the blog post with Draft status."""
        # 1. Author resolution
        author_id = os.environ.get("BLOG_GENERATOR_AUTHOR_ID") or getattr(settings, "BLOG_GENERATOR_AUTHOR_ID", None)
        author = None
        if author_id:
            author = User.objects.filter(pk=author_id).first()
        if not author:
            author = User.objects.filter(is_superuser=True).first()
        if not author:
            author = User.objects.first()
        if not author:
            author = User.objects.create_user(username="ai_editor", password=uuid.uuid4().hex)

        # 2. Category resolution
        cat_name = data.get("category", "Technology").strip() or "Technology"
        cat_obj, _ = category.objects.get_or_create(category_name=cat_name)

        # 3. Slug creation
        title = data["title"].strip()
        base_slug = slugify(title)[:100]
        if not base_slug:
            base_slug = "ai-daily-post"
        unique_slug = f"{base_slug}-{uuid.uuid4().hex[:6]}"
        while Blog.objects.filter(slug=unique_slug).exists():
            unique_slug = f"{base_slug}-{uuid.uuid4().hex[:6]}"

        # 4. Source URLs
        raw_sources = data.get("source_urls", [entry["link"]])
        if isinstance(raw_sources, list):
            source_urls_str = "\n".join(raw_sources)
        else:
            source_urls_str = str(raw_sources)

        # 5. Create Draft (Publication Rule: Never set status='Published')
        draft_post = Blog.objects.create(
            title=title,
            slug=unique_slug,
            category=cat_obj,
            author=author,
            short_description=data["short_description"].strip(),
            blog_body=data["blog_body"].strip(),
            status="Draft",  # STRICTLY Draft
            is_featured=False,
            is_ai_generated=True,
            source_urls=source_urls_str,
            generation_date=date_today,
        )

        return draft_post
