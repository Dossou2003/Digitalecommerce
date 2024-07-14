from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    ROLES = (
        ('client', 'Client'),
        ('gerant', 'Gérant'),
        ('administrateur', 'Administrateur'),
    )
    
    role = models.CharField(max_length=20, choices=ROLES)
    nom = models.CharField(max_length=150, verbose_name='Nom')
    prenom = models.CharField(max_length=150, verbose_name='Prénom')
    telephone = models.CharField(max_length=15, unique=True, verbose_name='Téléphone')
    adresse = models.TextField(verbose_name='Adresse', blank=True, null=True) 
    email = models.EmailField(unique=True, verbose_name='Email') 

    REQUIRED_FIELDS = ['nom', 'prenom', 'telephone', 'email']

    def __str__(self):
        return self.username
    
    
class Categorie(models.Model):
    nom = models.CharField(max_length=100)

    def __str__(self):
        return self.nom
    
class Produit(models.Model):
    nom = models.CharField(max_length=150)
    slug = models.SlugField(max_length=128, unique=True)
    description = models.TextField(blank=True)
    prix = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    categorie = models.ForeignKey(Categorie, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='imagesprod')
    actif = models.BooleanField(default=True)
    date_à_jour = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date_à_jour']

    def __str__(self):
        return self.nom

class Panier(models.Model):
    utilisateur = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    quantite = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f'{self.quantite} de {self.produit.nom} pour {self.utilisateur.username}'
    
class ProduitPanier(models.Model):
    panier = models.ForeignKey(Panier, on_delete=models.CASCADE)
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    quantite = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.produit.nom} dans {self.panier}"

        
class Commande(models.Model):
    utilisateur = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    nom = models.CharField(max_length=150)
    email = models.EmailField()
    adresse = models.CharField(max_length=100)
    ville = models.CharField(max_length=200)
    pays = models.CharField(max_length=300)
    quantite_totale = models.IntegerField(default=1)
    date_commande = models.DateTimeField(auto_now=True)
    statut = models.CharField(max_length=50, default='En attente')

    class Meta:
        ordering = ['-date_commande']

    def __str__(self):
        return f"Commande de {self.utilisateur.username} le {self.date_commande}"

class ProduitCommande(models.Model):
    commande = models.ForeignKey(Commande, on_delete=models.CASCADE)
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    quantite = models.PositiveIntegerField()
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.produit.nom} dans {self.commande}"

class Facture(models.Model):
     commande = models.OneToOneField(Commande, on_delete=models.CASCADE)
     montant_total = models.DecimalField(max_digits=10, decimal_places=2)
     
     def __str__(self):
        return f"Facture pour {self.commande}"

class Paiement(models.Model):
    commande = models.ForeignKey(Commande, on_delete=models.CASCADE)
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    type_paiement = models.CharField(max_length=50)  

    def __str__(self):
        return f"Paiement {self.id} pour la commande {self.commande.id}"



class Contact(models.Model):
    nom = models.CharField(max_length=150)
    email = models.EmailField()
    message = models.TextField()
    date_envoye = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message de {self.nom} le {self.date_envoye}"
     

      
   




