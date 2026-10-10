from unittest.mock import MagicMock, patch
from django.contrib.auth.models import User
from django.core.cache import cache
from django.test import TestCase, Client
from django.urls import reverse
from blog.models import Blog, category
from blog.ai_service import summarize_blog_post, answer_blog_chat, check_rate_limit


class AIBlogFeatureTests(TestCase):
    def setUp(self):
        cache.clear()
        self.client = Client()
        self.user = User.objects.create_user(username='testauthor', password='password123')
        self.cat = category.objects.create(category_name='Technology')

        self.published_blog = Blog.objects.create(
            title='Django and AI Future',
            slug='django-and-ai-future',
            category=self.cat,
            author=self.user,
            short_description='How Django powers modern AI applications.',
            blog_body='Django is a powerful Python web framework. Integrating Gemini allows intelligent summarization and retrieval.',
            status='Published',
            is_featured=True,
        )

        self.draft_blog = Blog.objects.create(
            title='Secret Unreleased Project',
            slug='secret-unreleased-project',
            category=self.cat,
            author=self.user,
            short_description='Confidential draft article.',
            blog_body='This is proprietary internal company data about unreleased products.',
            status='Draft',
        )

        self.empty_blog = Blog.objects.create(
            title='Empty Blog Post',
            slug='empty-blog-post',
            category=self.cat,
            author=self.user,
            short_description='No content',
            blog_body='',
            status='Published',
        )

    def test_summarize_published_post_success(self):
        """A published post with text can be summarized successfully and saved."""
        fake_summary = "• Point 1\n• Point 2\n• Point 3\n• Point 4\n• Point 5"

        with patch('blog.ai_service.get_gemini_api_key', return_value='test-gemini-key'):
            with patch('blog.ai_service._call_gemini_with_fallback', return_value=(fake_summary, 'gemini-2.5-flash')):
                success, result, is_cached = summarize_blog_post(self.published_blog)
                self.assertTrue(success)
                self.assertEqual(result, fake_summary)
                self.assertFalse(is_cached)

                # Check persistence in database
                self.published_blog.refresh_from_db()
                self.assertEqual(self.published_blog.ai_summary, fake_summary)

    def test_summarize_cached_summary_reused(self):
        """The generated summary is saved and reused on subsequent requests without calling API."""
        self.published_blog.ai_summary = "Cached summary points."
        self.published_blog.save(update_fields=['ai_summary'])

        with patch('blog.ai_service.get_client') as mock_client:
            success, result, is_cached = summarize_blog_post(self.published_blog)
            self.assertTrue(success)
            self.assertEqual(result, "Cached summary points.")
            self.assertTrue(is_cached)
            # Ensure API client was never called
            mock_client.assert_not_called()

    def test_editing_post_invalidates_cached_summary(self):
        """Editing a post's body invalidates or clears its cached summary."""
        self.published_blog.ai_summary = "Old cached summary."
        self.published_blog.save()

        # Update body
        self.published_blog.blog_body = "Completely updated new content about AI."
        self.published_blog.save()

        self.published_blog.refresh_from_db()
        self.assertEqual(self.published_blog.ai_summary, "", "Summary must be cleared when body changes")

    def test_empty_post_produces_helpful_error(self):
        """An empty post produces a helpful error message."""
        with patch('blog.ai_service.get_gemini_api_key', return_value='test-gemini-key'):
            success, error, is_cached = summarize_blog_post(self.empty_blog)
            self.assertFalse(success)
            self.assertIn("empty", error.lower())

    def test_missing_api_key_produces_helpful_error(self):
        """Missing API key produces a helpful error without throwing unhandled exceptions."""
        with patch('blog.ai_service.get_gemini_api_key', return_value=''):
            success, error, is_cached = summarize_blog_post(self.published_blog)
            self.assertFalse(success)
            self.assertIn("GEMINI_API_KEY", error)

    def test_draft_post_cannot_be_summarized_publicly(self):
        """Draft posts cannot be summarized publicly (Security rule)."""
        response = self.client.post(reverse('summarize_blog', args=[self.draft_blog.pk]))
        self.assertIn(response.status_code, [302, 403])
        self.draft_blog.refresh_from_db()
        self.assertEqual(self.draft_blog.ai_summary, "")

    def test_chatbot_answers_matching_published_articles(self):
        """Chatbot answers reader queries using matching published articles and returns source links."""
        fake_answer = "Django integrates with Gemini to provide automated summaries as described in our articles."

        with patch('blog.ai_service.get_gemini_api_key', return_value='test-gemini-key'):
            with patch('blog.ai_service._call_gemini_with_fallback', return_value=(fake_answer, 'gemini-2.5-flash')):
                result = answer_blog_chat("Tell me about Django and AI framework")
                self.assertTrue(result['success'])
                self.assertEqual(result['answer'], fake_answer)
                self.assertEqual(len(result['sources']), 1)
                self.assertEqual(result['sources'][0].id, self.published_blog.id)

    def test_chatbot_never_leaks_drafts(self):
        """Drafts and private posts never appear in public chatbot context (Security rule)."""
        with patch('blog.ai_service.get_gemini_api_key', return_value='test-gemini-key'):
            with patch('blog.ai_service._call_gemini_with_fallback') as mock_ai:
                result = answer_blog_chat("What is the Secret Unreleased Project?")
                # Should not match draft article
                for source in result['sources']:
                    self.assertNotEqual(source.status, 'Draft')
                    self.assertNotEqual(source.id, self.draft_blog.id)

    def test_chatbot_no_matching_content_fallback(self):
        """A question with no matching content receives an honest fallback without calling API."""
        with patch('blog.ai_service.get_client') as mock_client:
            result = answer_blog_chat("Quantum astrophysics teleportation warp drive")
            self.assertTrue(result['success'])
            self.assertIn("could not find enough information", result['answer'])
            self.assertEqual(len(result['sources']), 0)
            mock_client.assert_not_called()

    def test_chatbot_invalid_input(self):
        """Invalid questions (empty or too long) return an appropriate error."""
        # Empty question
        res_empty = answer_blog_chat("   ")
        self.assertFalse(res_empty['success'])
        self.assertIn("valid question", res_empty['error'].lower())

        # Too long question (> 500 characters)
        long_q = "what is " + "ai " * 300
        res_long = answer_blog_chat(long_q)
        self.assertFalse(res_long['success'])
        self.assertIn("500", res_long['error'])

    def test_rate_limiting(self):
        """Rate limiting correctly blocks excessive requests."""
        key = "test_rate_ip"
        for i in range(5):
            allowed = check_rate_limit(key, limit=5, window=60)
            self.assertTrue(allowed)

        # 6th request within window must be blocked
        blocked = check_rate_limit(key, limit=5, window=60)
        self.assertFalse(blocked)

    def test_api_key_never_leaks_in_html_views(self):
        """The API key never appears in HTML responses, templates, or views."""
        secret_key = "AIzaSySecretTestKey123456789"
        with patch('blog.ai_service.get_gemini_api_key', return_value=secret_key):
            # Test blog detail page
            resp_blog = self.client.get(reverse('blog', args=[self.published_blog.slug]))
            self.assertNotIn(secret_key, resp_blog.content.decode('utf-8'))

            # Test AI Chatbot page
            resp_chat = self.client.get(reverse('ai_chat'))
            self.assertNotIn(secret_key, resp_chat.content.decode('utf-8'))

    def test_summarize_view_ajax_endpoint(self):
        """Summarize endpoint handles AJAX requests and returns JSON."""
        fake_summary = "• Bullet point summary"
        with patch('blog.ai_service.get_gemini_api_key', return_value='test-key'):
            with patch('blog.ai_service._call_gemini_with_fallback', return_value=(fake_summary, 'gemini-2.5-flash')):
                response = self.client.post(
                    reverse('summarize_blog', args=[self.published_blog.pk]),
                    data={'ajax': '1'},
                    HTTP_X_REQUESTED_WITH='XMLHttpRequest'
                )
                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertTrue(data['success'])
                self.assertEqual(data['summary'], fake_summary)

    def test_ai_chat_view_ajax_endpoint(self):
        """AI Chat endpoint handles AJAX POST and returns JSON with answer and source links."""
        fake_answer = "Django is a web framework."
        with patch('blog.ai_service.get_gemini_api_key', return_value='test-key'):
            with patch('blog.ai_service._call_gemini_with_fallback', return_value=(fake_answer, 'gemini-2.5-flash')):
                response = self.client.post(
                    reverse('ai_chat'),
                    data={'question': 'Django framework', 'ajax': '1'},
                    HTTP_X_REQUESTED_WITH='XMLHttpRequest'
                )
                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertTrue(data['success'])
                self.assertEqual(data['answer'], fake_answer)
                self.assertTrue(len(data['sources']) > 0)
