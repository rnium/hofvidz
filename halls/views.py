from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Hall, Video
from .forms import VideoForm, SearchForm
from django.http import Http404, HttpResponse, JsonResponse
from urllib.parse import urlparse, parse_qs
import requests

YOUTUBE_API_KEY = "AIzaSyC0ThBo8v6DKUSu_rBy8K0WHiC4h_cXKTM"

def home(request):
    halls = Hall.objects.order_by('-id')[:3]
    return render(request, "halls/home.html", {"halls":halls})

@login_required
def dashboard(request):
    halls = Hall.objects.filter(user=request.user)
    return render(request, "halls/dashboard.html", {'halls':halls})


@login_required
def add_video(request, pk):
    form = VideoForm()
    search_form = SearchForm()
    hall = get_object_or_404(Hall, id=pk)
    if not hall.user == request.user:
        raise Http404
    if request.method == "POST":
        submitted_form = VideoForm(request.POST)
        if submitted_form.is_valid():
            video = Video()
            video.url = submitted_form.cleaned_data['url']
            parse_result = urlparse(video.url)
            video_id = parse_qs(parse_result.query).get('v')[0] 
            print(video_id)
            res = requests.get(f'https://youtube.googleapis.com/youtube/v3/videos?part=snippet&id={ video_id }&key={ YOUTUBE_API_KEY }')
            json_res = res.json()
            try:
                video_title = json_res['items'][0]['snippet']['title']
            except IndexError:
                return render(request, "halls/add_video.html", {'form': form, 'search_form':search_form, 'error': 'Invalid Video Id', 'hall':hall})
            video.youtube_id = video_id
            video.title = video_title
            video.hall = hall
            video.save()
            return redirect('detail_hof', pk)
        else:
            return render(request, "halls/add_video.html", {'form': form, 'search_form':search_form, 'error': submitted_form.errors, 'hall':hall})
    return render(request, "halls/add_video.html", {'form': form, 'search_form':search_form, 'hall':hall})


@login_required
def video_search(request):
    search_form = SearchForm(request.GET)
    if search_form.is_valid():
            search_term = search_form.cleaned_data['search_term']
            url = f"https://youtube.googleapis.com/youtube/v3/search?part=snippet&maxResults=6&q={search_term}&key={YOUTUBE_API_KEY}"
            res = requests.get(url)
            return JsonResponse(res.json())
    return JsonResponse({"data": f"invalid search"})


class Signup(generic.CreateView):
    template_name = 'registration/signup.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        print("working...")
        rv = super(Signup, self).form_valid(form)
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password1')
        user = authenticate(username=username, password=password)
        print(username)
        print(password)
        login(self.request, user)
        return rv


class CreateHall(LoginRequiredMixin, generic.CreateView):
    model = Hall
    fields = ['title']
    template_name = 'halls/create_hall.html'
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        form.instance.user = self.request.user
        rv = super(CreateHall, self).form_valid(form)
        return rv
    


class DetailHall(LoginRequiredMixin, generic.DetailView):
    model = Hall
    template_name = "halls\detail_hall.html"


class UpdateHall(LoginRequiredMixin, generic.UpdateView):
    model = Hall
    fields = ['title']
    template_name = "halls/update_hall.html"
    success_url = reverse_lazy("dashboard")

    def get_object(self):
        hall = super(UpdateHall, self).get_object()
        if hall.user != self.request.user:
            raise Http404
        return hall


class DeleteHall(LoginRequiredMixin, generic.DeleteView):
    model = Hall
    template_name = "halls/delete_hall.html"
    success_url = reverse_lazy("dashboard")

    def get_object(self):
        hall = super(DeleteHall, self).get_object()
        if hall.user != self.request.user:
            raise Http404
        return hall


class DeleteVideo(LoginRequiredMixin, generic.DeleteView):
    model = Video
    template_name = "halls/delete_video.html"
    success_url = reverse_lazy('dashboard')
    def get_object(self):
        video = super(DeleteVideo, self).get_object()
        if video.hall.user != self.request.user:
            raise Http404
        return video
    
    def delete(self, request, *args, **kwargs) -> HttpResponse:
        video = self.get_object()
        hall_id = video.hall.id
        super().delete(request, *args, **kwargs)
        return redirect("detail_hof", hall_id)