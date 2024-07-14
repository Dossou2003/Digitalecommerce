import json
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Produit, Panier, ProduitCommande, ProduitPanier, Categorie, Commande, Facture, Paiement
from .forms import InscriptionForm, ConnexionForm, ContactForm, PaiementForm
from django.core.paginator import Paginator
from django.urls import reverse_lazy
from django.views import generic
from .forms import CustomUserCreationForm
import paypalrestsdk
from django.conf import settings
from django.core.mail import send_mail
from paypal.standard.forms import PayPalPaymentsForm
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

class SignUpView(generic.CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('connexion')
    template_name = 'DigitalWaves/inscription.html'


def index(request):
    produits = Produit.objects.all()
    paginator = Paginator(produits, 10)

    page_number = request.GET.get('page')
    produits = paginator.get_page(page_number)
    
    categories = Categorie.objects.all()
    return render(request, 'DigitalWaves/index.html', {'produits': produits, 'categories': categories})

def inscription(request):
    if request.method == 'POST':
        form = InscriptionForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Inscription réussie. Bienvenue!')
            return redirect('index')
        else:
            messages.error(request, 'Erreur lors de l\'inscription. Veuillez vérifier les informations fournies.')
    else:
        form = InscriptionForm()
    return render(request, 'DigitalWaves/inscription.html', {'form': form})

def connexion(request):
    if request.method == 'POST':
        form = ConnexionForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('index')
            else:
                messages.error(request, 'Nom d\'utilisateur ou mot de passe incorrect.')
    else:
        form = ConnexionForm()
    return render(request, 'DigitalWaves/connexion.html')

def deconnexion(request):
    logout(request)
    return redirect('index')


def apropos(request):
    return render(request, 'DigitalWaves/apropos.html')


def detail_produit(request, slug):
    produit = get_object_or_404(Produit, slug=slug)
    return render(request, 'DigitalWaves/detail_produit.html', {'produit': produit})

def detail_commande(request, commande_id):
    commande = get_object_or_404(Commande, pk=commande_id)
    facture = Facture.objects.get(commande=commande) 
    
    context = {
        'commande': commande,
        'facture': facture,
    }
    return render(request, 'DigitalWaves/detail_commande.html', context)

def produits(request):
    produits = Produit.objects.all()
    return render(request, 'DigitalWaves/produit.html', {'produit': produits})

def confirmation(request):
    info= Commande.objects.all()[:1]
    for user in info:
        nom=user.nom
    return render(request, 'DigitalWaves/commande_complete.html')




@login_required
def voir_panier(request):
    panier_items = Panier.objects.filter(utilisateur=request.user)
    total = sum(item.produit.prix * item.quantite for item in panier_items)
    return render(request, 'DigitalWaves/voir_panier.html', {'panier_items': panier_items, 'total': total})


@login_required
def ajouter_au_panier(request, produit_id):
    produit = get_object_or_404(Produit, id=produit_id)
    panier, created = Panier.objects.get_or_create(utilisateur=request.user, produit=produit)
    if not created:
        panier.quantite += 1
        panier.save()
    return redirect('voir_panier')

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Votre message a été envoyé.')
            return redirect('contact')
    else:
        form = ContactForm()
    return render(request, 'DigitalWaves/contact.html', {'form': form})


paypalrestsdk.configure({
    "mode": settings.PAYPAL_MODE,
    "client_id": settings.PAYPAL_CLIENT_ID,
    "client_secret": settings.PAYPAL_CLIENT_SECRET
})

@login_required
def paiement(request):
    panier = get_object_or_404(Panier, utilisateur=request.user)
    produits_panier = ProduitPanier.objects.filter(panier=panier)

    if request.method == 'POST':
        form = PaiementForm(request.POST)
        if form.is_valid():
            montant_total = sum(item.produit.prix * item.quantite for item in produits_panier)

            commande = Commande.objects.create(
                utilisateur=request.user,
                nom=request.user.nom,
                email=request.user.email,
                adresse=form.cleaned_data['adresse'],
                ville=form.cleaned_data['ville'],
                pays=form.cleaned_data['pays'],
                quantite_totale=sum(item.quantite for item in produits_panier)
            )

            for item in produits_panier:
                ProduitCommande.objects.create(
                    commande=commande,
                    produit=item.produit,
                    quantite=item.quantite,
                    prix_unitaire=item.produit.prix
                )

            facture = Facture.objects.create(
                commande=commande,
                montant_total=montant_total
            )

            paiement = Paiement.objects.create(
                facture=facture,
                type_paiement=form.cleaned_data['type_paiement'],
                montant=montant_total,
                statut='En attente'
            )

            panier.delete()
            messages.success(request, 'Paiement effectué avec succès.')
            return redirect('payment_success')
        else:
            messages.error(request, 'Le formulaire de paiement est invalide. Veuillez vérifier vos informations.')
            return redirect('confirmation')
    else:
        form = PaiementForm()

    return render(request, 'DigitalWaves/paiement.html', {'form': form, 'produits_panier': produits_panier})

@login_required
def execute_paypal_payment(request):
    payment_id = request.GET.get('paymentId')
    payer_id = request.GET.get('PayerID')

    payment = paypalrestsdk.Payment.find(payment_id)

    if payment.execute({"payer_id": payer_id}):
        panier = get_object_or_404(Panier, utilisateur=request.user)
        produits_panier = ProduitPanier.objects.filter(panier=panier)

        commande = Commande.objects.create(
            utilisateur=request.user,
            nom=request.user.nom,
            email=request.user.email,
            adresse=request.GET.get('address', 'adresse'),
            ville=request.GET.get('city', 'ville'),
            pays=request.GET.get('country', 'pays'),
            quantite_totale=sum(item.quantite for item in produits_panier)
        )

        for item in produits_panier:
            ProduitCommande.objects.create(
                commande=commande,
                produit=item.produit,
                quantite=item.quantite,
                prix_unitaire=item.produit.prix
            )

        total_amount = sum(item.produit.prix * item.quantite for item in produits_panier)

        facture = Facture.objects.create(
            commande=commande,
            montant_total=total_amount
        )

        paiement = Paiement.objects.create(
            facture=facture,
            type_paiement='PayPal',
            montant=facture.montant_total
        )

        panier.delete()

        send_mail(
            'Confirmation de commande',
            f'Votre commande {commande.id} a été effectuée avec succès.',
            'from@example.com',
            [request.user.email],
            fail_silently=False,
        )

        messages.success(request, 'Paiement PayPal effectué avec succès.')
        return redirect('payment_success')
    else:
        messages.error(request, 'Le paiement PayPal a échoué.')
        return redirect('paiement')

@csrf_exempt
def process_paypal_payment(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        order_id = data.get('orderID')

        payment = paypalrestsdk.Payment.find(order_id)
        if payment.execute({"payer_id": payment.payer.payer_info.payer_id}):
     
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'error'})

    return JsonResponse({'status': 'error'})

@login_required
def create_paypal_payment(request):
    panier = get_object_or_404(Panier, utilisateur=request.user)
    produits_panier = ProduitPanier.objects.filter(panier=panier)
    total_panier = sum(item.produit.prix * item.quantite for item in produits_panier)

    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal"
        },
        "redirect_urls": {
            "return_url": request.build_absolute_uri(reverse('execute_paypal_payment')),
            "cancel_url": request.build_absolute_uri(reverse('paiement'))
        },
        "transactions": [{
            "item_list": {
                "items": [{
                    "name": "Total Panier",
                    "sku": "item",
                    "price": str(total_panier),
                    "currency": "EUR",
                    "quantity": 1
                }]
            },
            "amount": {
                "total": str(total_panier),
                "currency": "EUR"
            },
            "description": "Achat sur DigitalWaves"
        }]
    })

    if payment.create():
        for link in payment.links:
            if link.rel == "approval_url":
                approval_url = str(link.href)
                return redirect(approval_url)
    else:
        messages.error(request, 'Erreur lors de la création du paiement PayPal')
        return redirect('paiement')

@login_required
def payment_success(request):
    return render(request, 'DigitalWaves/payment_success.html')


def passer_commande(request):
    if request.method == 'POST':
        produits_panier = ProduitPanier.objects.filter(panier__utilisateur=request.user)
        montant_total = sum(item.produit.prix * item.quantite for item in produits_panier)

        commande = Commande.objects.create(
            utilisateur=request.user,
            nom=request.user.nom,
            email=request.user.email,
            adresse=request.POST.get('adresse'),
            ville=request.POST.get('ville'),
            pays=request.POST.get('pays'),
            quantite_totale=sum(item.quantite for item in produits_panier)
        )

        paiement = Paiement.objects.create(
            commande=commande,
            montant=montant_total,
            type_paiement=request.POST.get('type_paiement'),
            statut='En attente'
        )
        produits_panier.delete()

        return redirect('confirmation_commande')

    return redirect('index')

@login_required
def confirmation_commande(request):
    info = Commande.objects.filter(utilisateur=request.user).order_by('-date_commande')[:1]
    for user in info:
        nom = user.nom
    return render(request, 'DigitalWaves/confirmation_commande.html', {'nom': nom})