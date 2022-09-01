from django.urls import path, include

from apps.snippets import views
from rest_framework import renderers
from rest_framework.routers import DefaultRouter
from rest_framework.urlpatterns import format_suffix_patterns

snippet_list = views.SnippetViewSet.as_view({
    'get': 'list',
    'post': 'create'
})
snippet_detail = views.SnippetViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})
snippet_highlight = views.SnippetViewSet.as_view({
    'get': 'highlight'
}, renderer_classes=[renderers.StaticHTMLRenderer])

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
    path('snippets5/<int:pk>/highlight/', views.SnippetHighlight.as_view()),

    path('snippets6/', snippet_list, name='snippet-list'),
    path('snippets6/<int:pk>/', snippet_detail, name='snippet-detail'),
    path('snippets6/<int:pk>/highlight/', snippet_highlight, name='snippet-highlight'),
]

urlpatterns = format_suffix_patterns(urlpatterns)

# Create a router and register our viewsets with it.
# router = DefaultRouter()
# router.register('snippets7', views.SnippetViewSet, basename="snippets7")
# urlpatterns += [
#     path('', include(router.urls)),
# ]

resource_router = DefaultRouter()
resource_router.register('snippets8', views.SnippetRouterViewSet, basename="resource_router_snippets8")
urlpatterns += [
    path('', include(resource_router.urls)),
]
