import json
from django.contrib import messages
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from django.db.models import Q

from .models import Blog, category, Comment
from .ai_service import summarize_blog_post, answer_blog_chat, check_rate_limit


def post_by_category(request, category_id):
    selected_category = get_object_or_404(category, pk=category_id)
    posts = Blog.objects.filter(status='Published', category=selected_category)
    
    context = {
        'posts': posts,
        'selected_category': selected_category,
    }
    return render(request, 'post_by_category.html', context)


def blog(request, slug):
    single_blog = get_object_or_404(Blog, slug=slug, status='Published')
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, "Please log in to submit a comment.")
            return redirect('login')
        comment_text = request.POST.get('comment', '').strip()
        if comment_text:
            comment = Comment()
            comment.user = request.user
            comment.blog = single_blog
            comment.comment = comment_text
            comment.save()
            messages.success(request, "Your comment has been posted.")
        return HttpResponseRedirect(request.path_info)

    comments = Comment.objects.filter(blog=single_blog)
    comment_count = comments.count()
    context = {
        'single_blog': single_blog,
        'blog': single_blog,
        'comments': comments,
        'comment_count': comment_count,
    }
    return render(request, 'blog.html', context)


def search(request):
    keyword = request.GET.get('keyword', '').strip()
    if keyword:
        blog = Blog.objects.filter(
            Q(title__icontains=keyword) |
            Q(short_description__icontains=keyword) |
            Q(blog_body__icontains=keyword),
            status='Published'
        )
    else:
        blog = Blog.objects.none()

    context = {
        'blog': blog,
        'keyword': keyword,
    }
    return render(request, 'search.html', context)


@require_POST
@csrf_protect
def summarize_blog(request, pk):
    """
    POST endpoint to summarize a published blog post.
    Validates post status and content, and reuses cached summary if available.
    """
    client_ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', '127.0.0.1')).split(',')[0].strip()
    is_ajax = (
        request.headers.get('x-requested-with') == 'XMLHttpRequest' or
        request.headers.get('accept') == 'application/json' or
        request.POST.get('ajax') == '1'
    )

    # Rate limiting (10 requests per minute per IP)
    if not check_rate_limit(f"summarize_{client_ip}", limit=10, window=60):
        err_msg = "Rate limit exceeded. Please wait a moment before requesting another summary."
        if is_ajax:
            return JsonResponse({'success': False, 'error': err_msg}, status=429)
        messages.error(request, err_msg)
        single_blog = get_object_or_404(Blog, pk=pk)
        return redirect('blog', slug=single_blog.slug)

    single_blog = get_object_or_404(Blog, pk=pk)

    # Security check: only published posts
    if single_blog.status != 'Published':
        err_msg = "Only published blog posts can be summarized."
        if is_ajax:
            return JsonResponse({'success': False, 'error': err_msg}, status=403)
        messages.error(request, err_msg)
        return redirect('home')

    force_refresh = request.POST.get('refresh') == 'true'
    success, result, is_cached = summarize_blog_post(single_blog, force_refresh=force_refresh)

    if is_ajax:
        if success:
            return JsonResponse({
                'success': True,
                'summary': result,
                'is_cached': is_cached,
            })
        else:
            return JsonResponse({
                'success': False,
                'error': result,
            }, status=400)

    if success:
        messages.success(request, "AI summary loaded successfully.")
    else:
        messages.error(request, result)

    return redirect('blog', slug=single_blog.slug)


@csrf_protect
def ai_chat(request):
    """
    Chatbot endpoint grounded strictly in published blog articles.
    GET: Renders the chatbot interface.
    POST: Processes question and returns grounded response with source links.
    """
    if request.method == 'GET':
        return render(request, 'ai_chatbot.html', {
            'question': '',
            'answer': '',
            'sources': [],
            'error': None,
        })

    # POST handling
    client_ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', '127.0.0.1')).split(',')[0].strip()
    is_ajax = (
        request.headers.get('x-requested-with') == 'XMLHttpRequest' or
        request.headers.get('accept') == 'application/json' or
        request.POST.get('ajax') == '1'
    )

    # Rate limiting (15 chat queries per minute per IP)
    if not check_rate_limit(f"chat_{client_ip}", limit=15, window=60):
        err_msg = "Rate limit reached. Please wait a moment before sending another message."
        if is_ajax:
            return JsonResponse({'success': False, 'error': err_msg}, status=429)
        return render(request, 'ai_chatbot.html', {'error': err_msg, 'question': request.POST.get('question', '')})

    question = request.POST.get('question', '').strip()

    # Validation
    if not question:
        err_msg = "Enter a question under 500 characters."
        if is_ajax:
            return JsonResponse({'success': False, 'error': err_msg}, status=400)
        return render(request, 'ai_chatbot.html', {'error': err_msg})

    if len(question) > 500:
        err_msg = "Enter a question under 500 characters."
        if is_ajax:
            return JsonResponse({'success': False, 'error': err_msg}, status=400)
        return render(request, 'ai_chatbot.html', {'error': err_msg, 'question': question})

    result = answer_blog_chat(question)

    if is_ajax:
        return JsonResponse({
            'success': result['success'],
            'question': question,
            'answer': result['answer'],
            'sources': [
                {
                    'title': post.title,
                    'slug': post.slug,
                    'short_description': post.short_description,
                }
                for post in result['sources']
            ],
            'error': result['error']
        }, status=200 if (result['success'] or not result['error']) else 400)

    return render(request, 'ai_chatbot.html', {
        'question': question,
        'answer': result['answer'],
        'sources': result['sources'],
        'error': result['error']
    })