from django.urls import path, re_path

from . import views


urlpatterns = [
    path("", views.index, name="index"),
    path("hot/", views.hot, name="hot"),
    path("tag/<str:tag_name>/", views.tag, name="tag"),
    path("question/<int:question_id>/", views.question, name="question"),
    path("tags/", views.tags, name="tags"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.signup, name="signup"),
    path("ask/", views.ask, name="ask"),
    path("settings/", views.settings, name="settings"),
    path("profile/<int:user_id>/", views.profile, name="profile"),
    # Catch-all для всех несуществующих URL (исключаем /media/ и /static/)
    re_path(r"^(?!media/|static/).*$", views.custom_404_view),
]
