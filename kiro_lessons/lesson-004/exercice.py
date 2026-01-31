"""
Cours 004: Sécurité Web - XSS innerHTML
=======================================
EXERCICE - Code à corriger

Niveau: Intermédiaire
Durée: 45-60 minutes

INSTRUCTIONS:
-------------
1. Ce fichier contient une VULNÉRABILITÉ XSS
2. Lance le script pour voir la démonstration
3. Corrige la vulnérabilité
4. Valide que l'attaque ne fonctionne plus

PROBLÈME À TROUVER:
-------------------
- Utilisation dangereuse d'innerHTML
- Contenu utilisateur non sanitisé
- Injection de scripts possible

Pour lancer la démonstration:
    python exercice.py
"""

def simulate_web_vulnerability():
    """Simulation d'une vulnérabilité XSS innerHTML"""
    
    print("🌐 Simulation Vulnérabilité XSS - innerHTML")
    print("=" * 50)
    
    # Simulation du contenu utilisateur malveillant
    user_inputs = [
        "Contenu normal",
        "<script>alert('XSS Attack!')</script>",
        "<img src=x onerror=alert('XSS')>",
        "<div onclick=alert('Clicked!')>Click me</div>"
    ]
    
    print("\n📋 Test des entrées utilisateur:")
    
    for i, user_input in enumerate(user_inputs, 1):
        print(f"\n{i}. Input: {user_input}")
        
        # VULNÉRABILITÉ: Simulation d'innerHTML dangereux
        if "<script>" in user_input or "onerror=" in user_input or "onclick=" in user_input:
            print("   ⚠️  VULNÉRABILITÉ DÉTECTÉE: Code JavaScript injecté!")
            print("   💀 Attaque XSS réussie - Script exécuté")
        else:
            print("   ✅ Contenu sûr affiché")
    
    print("\n" + "=" * 50)
    print("🎯 MISSION: Corriger la vulnérabilité XSS")
    print("💡 INDICE: Remplacer innerHTML par textContent")
    print("🔒 OBJECTIF: Empêcher l'exécution de scripts")

def secure_display_content(user_input):
    """Version sécurisée - À implémenter"""
    # TODO: Implémenter la version sécurisée
    # Utiliser textContent au lieu d'innerHTML
    # Ou sanitiser le contenu HTML
    pass

if __name__ == "__main__":
    simulate_web_vulnerability()
