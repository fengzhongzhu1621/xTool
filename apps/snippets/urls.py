from django.urls import path

from apps.snippets import views
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    path('snippets1/', views.snippet_list_1, name='snippet-list-1'),
    path('snippets1/<int:pk>/', views.snippet_detail_1, name='snippet-detail-1'),

    path('snippets2/', views.snippet_list_2, name='snippet-list-2'),
    path('snippets2/<int:pk>/', views.snippet_detail_2, name='snippet-detail-2'),

    path('snippets3/', views.SnippetList3.as_view(), name='snippet-list-3'),
    path('snippets3/<int:pk>/', views.SnippetDetail3.as_view(), name='snippet-detail-3'),

    path('snippets4/', views.SnippetList4.as_view(), name='snippet-list-4'),
    path('snippets4/<int:pk>/', views.SnippetDetail4.as_view(), name='snippet-detail-4'),

    path('snippets5/', views.SnippetList5.as_view(), name='snippet-list-5'),
    path('snippets5/<int:pk>/', views.SnippetDetail5.as_view(), name='snippet-detail-5'),

    path('snippets/<int:pk>/highlight/', views.SnippetHighlight.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
