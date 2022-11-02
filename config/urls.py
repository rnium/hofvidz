from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path
from halls import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls, name='adm1n'),
    path('', views.home, name="home"),
    path('dashboard', views.dashboard, name="dashboard"),
    #AUTH
    path('signup/', views.Signup.as_view(), name='signupUser'),
    path('login/', LoginView.as_view(), name='loginUser'),
    path("logout/", LogoutView.as_view(next_page="home"), name='logoutUser'),
    # Halls
    path("halloffame/create", views.CreateHall.as_view(), name='create_hof'),
    path("halloffame/<int:pk>", views.DetailHall.as_view(), name='detail_hof'),
    path("halloffame/<int:pk>/update", views.UpdateHall.as_view(), name='update_hof'),
    path("halloffame/<int:pk>/delete", views.DeleteHall.as_view(), name='delete_hof'),
    #Video
    path('halloffame/<int:pk>/addvideo/', views.add_video, name="add_video"),
    path('video/<int:pk>/delete/', views.DeleteVideo.as_view(), name="delete_video"),
    path('search/', views.video_search, name="video_search"),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
