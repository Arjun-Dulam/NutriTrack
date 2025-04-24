from django.shortcuts import render, redirect
from groq import Groq
from django.conf import settings

client = Groq(
    api_key=settings.GROQ_API_KEY,
)


# Create your views here.


def index(request):
    return render(request,'home/index.html', {'joke': llm_call()})

    # return render(request,'home/index.html' )

def about(request):
    return render(request, 'home/about.html')

def contact(request):
    return render(request, 'home/contact.html')

def services(request):
    return render(request, 'home/services.html')


def llm_call():
    chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": "tell me a joke",
        }
    ],
    model="llama-3.3-70b-versatile",
    stream=False,
    )

    return chat_completion.choices[0].message.content
