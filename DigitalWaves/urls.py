from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from DigitalWaves.views import index
from DigitalWaves import views
from .views import confirmation_commande, create_paypal_payment, execute_paypal_payment, passer_commande
from django.views.generic.base import RedirectView

urlpatterns = [
            
       path('inscription/', views.inscription, name='inscription'),
       path('connexion/', views.connexion, name='connexion'),
       path('deconnexion/', views.deconnexion, name='deconnexion'),
       path('index/', views.index, name="index"),
       path('apropos/', views.apropos, name='apropos'),
       path('detail_produit/<slug:slug>/', views.detail_produit, name='detail_produit'),
       path('produit/<slug:slug>/', views.detail_produit, name='produit'),
       path('detail_commande/<int:commande_id>/', views.detail_commande, name='detail_commande'),
       path('produits/', views.produits, name='produits'),
       path('confirmation/', views.confirmation, name='confirmation'),
       path('ajouter-au-panier/<int:produit_id>/', views.ajouter_au_panier, name='ajouter_au_panier'),
       path('voir-panier/', views.voir_panier, name='voir_panier'),
       path('passer-commande/', passer_commande, name='passer_commande'),
       path('confirmation-commande/', confirmation_commande, name='confirmation_commande'),
       path('contact/', views.contact, name='contact'),
       path('paiement/', views.paiement, name='paiement'),
       path('create_paypal_payment/', create_paypal_payment, name='create_paypal_payment'),
       path('execute/', execute_paypal_payment, name='execute_paypal_payment'),
       path('process_paypal_payment/', views.process_paypal_payment, name='process_paypal_payment'),
       path('payment_success/', views.payment_success, name='payment_success'),
   ] + static(settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT)