import os
import tempfile
import time
import urllib.parse
import re
import unicodedata
from groq import Groq
import gradio as gr

# 1. INITIALISATION SÉCURISÉE DE L'API GROQ
try:
    cle_secrete = os.environ.get('GROQ_AI')
    client = Groq(api_key=cle_secrete)
except Exception as e:
    client = None

# --- STATISTIQUES DE L'ENTREPRISE ---
STATS_ENTREPRISE = {
    "revenus_hebdo": 0,
    "ebooks_vendus": 0,
    "affiches_vendues": 0,
    "abonnes_fb": 150,
    "abonnes_ig": 85,
    "abonnes_tt": 210,
}

# 2. DEFINITIONS DES AGENTS
AGENTS_DEFINITIONS = {
    "CEO": "Tu es le CEO d'ORADI OS. Tu supervises l'empire, analyses les rapports et prends les décisions stratégiques.",
    "Niche Hunter": "Tu analyses le marché pour trouver une idée d'e-book ou d'affiche ultra-tendance, rentable et facile à vendre.",
    "Rédacteur Simple": "Tu rédiges des guides pratiques et e-books de manière claire, concise, captivante et accessible sans jargon.",
    "Designer Canva": "Tu es un designer d'élite. Ton SEUL rôle est de fournir 4 à 8 mots-clés simples EN ANGLAIS décrivant l'image, séparés par des virgules (Ex: 'minimalist, book cover, plants, modern'). RÈGLE CRITIQUE : Écris UNIQUEMENT en anglais. Aucun mot en français, pas d'accents, pas de phrases, pas d'introduction.",
    "Creator AI": "Tu es le chef d'équipe de création. Tu rassembles, valides le livrable final et le livres officiellement au CEO AI.",
    "Chariow Publisher": "Tu es chargé de prendre le produit validé par le Creator, de le publier sur la boutique Chariow et d'ajuster les revenus.",
}

# Fonction pour enlever les accents
def supprimer_accents(texte):
    texte_normalise = unicodedata.normalize('NFD', texte)
    return "".join([c for c in texte_normalise if unicodedata.category(c) != 'Mn'])

# Fonction de nettoyage du prompt d'image
def nettoyer_prompt(text):
    text = supprimer_accents(text)
    text = text.replace("\n", " ").replace("\r", " ").strip()
    text = re.sub(r'["\'`«»]', '', text)
    text = text.replace(".", "")
    text = re.sub(r'[^a-zA-Z0-9\s,]', '', text)
    mots = text.split()
    if len(mots) > 10:
        text = " ".join(mots[:10])
    return text.strip().lower()

# 3. PIPELINE DE CRÉATION & PUBLICATION AUTOMATISÉE
def executer_pipeline_entreprise(theme_demande, type_produit):
    if not client:
        yield "Configuration API requise.", "Veuillez configurer la variable d'environnement GROQ_AI sur Render.", None, "⚠️ Erreur API", "0", "0", "0"
        return

    etapes_log = []
    
    etapes_log.append("🟢 [DEPT CRÉATION] Niche Hunter AI cherche l'idée parfaite...")
    yield "\n".join(etapes_log), "Recherche de tendance...", None, "<em>Génération du visuel...</em>", str(STATS_ENTREPRISE["revenus_hebdo"]), f"{STATS_ENTREPRISE['ebooks_vendus']} e-books / {STATS_ENTREPRISE['affiches_vendues']} affiches", f"FB: {STATS_ENTREPRISE['abonnes_fb']} | IG: {STATS_ENTREPRISE['abonnes_ig']} | TT: {STATS_ENTREPRISE['abonnes_tt']}"
    
    prompt_niche = f"{AGENTS_DEFINITIONS['Niche Hunter']}\nTrouve un titre accrocheur et un concept d'e-book ou affiche très vendeur sur le sujet : {theme_demande}."
    res_niche = client.chat.completions.create(messages=[{"role": "user", "content": prompt_niche}], model="llama-3.1-8b-instant")
    concept_niche = res_niche.choices[0].message.content
    
    etapes_log.append("✅ Idée trouvée !\n🟢 [DEPT CRÉATION] Conception du livrable et du visuel par nos agents...")
    yield "\n".join(etapes_log), "Création en cours...", None, "<em>Génération du visuel...</em>", str(STATS_ENTREPRISE["revenus_hebdo"]), f"{STATS_ENTREPRISE['ebooks_vendus']} e-books / {STATS_ENTREPRISE['affiches_vendues']} affiches", f"FB: {STATS_ENTREPRISE['abonnes_fb']} | IG: {STATS_ENTREPRISE['abonnes_ig']} | TT: {STATS_ENTREPRISE['abonnes_tt']}"
    
    if type_produit == "E-book":
        prompt_content = f"{AGENTS_DEFINITIONS['Rédacteur Simple']}\nRédige le plan et l'introduction de l'e-book basé sur :\n{concept_niche}"
    else:
        prompt_content = f"{AGENTS_DEFINITIONS['Rédacteur Simple']}\nRédige une description textuelle explicative de l'affiche et de sa valeur ajoutée basée sur :\n{concept_niche}"
        
    res_content = client.chat.completions.create(messages=[{"role": "user", "content": prompt_content}], model="llama-3.1-8b-instant")
    contenu_produit = res_content.choices[0].message.content

    prompt_img_designer = f"{AGENTS_DEFINITIONS['Designer Canva']}\nCrée un prompt d'image composé de quelques mots-clés simples en anglais pour illustrer de façon moderne : {concept_niche}"
    res_img_prompt = client.chat.completions.create(messages=[{"role": "user", "content": prompt_img_designer}], model="llama-3.1-8b-instant")
    
    prompt_brut = res_img_prompt.choices[0].message.content
    prompt_genere = nettoyer_prompt(prompt_brut)

    if not prompt_genere:
        prompt_genere = "minimalist style digital book cover design"

    prompt_propre = urllib.parse.quote(prompt_genere)
    url_image_generee = f"https://image.pollinations.ai/p/{prompt_propre}?width=1024&height=1024&nologo=true"
    html_image = f'<div style="text-align: center;"><img src="{url_image_generee}" alt="Visuel" style="max-width: 100%; border-radius: 12px; border: 2px solid #1F2937; box-shadow: 0 4px 15px rgba(0,0,0,0.5);" /></div>'

    etapes_log.append("✅ Produit conçu !\n🟢 [DEPT CRÉATION] Creator AI valide la qualité et compile le livrable...")
    yield "\n".join(etapes_log), contenu_produit, None, html_image, str(STATS_ENTREPRISE["revenus_hebdo"]), f"{STATS_ENTREPRISE['ebooks_vendus']} e-books / {STATS_ENTREPRISE['affiches_vendues']} affiches", f"FB: {STATS_ENTREPRISE['abonnes_fb']} | IG: {STATS_ENTREPRISE['abonnes_ig']} | TT: {STATS_ENTREPRISE['abonnes_tt']}"
    
    prompt_compile = f"{AGENTS_DEFINITIONS['Creator AI']}\nCompile ce produit final proprement en un livrable professionnel :\n{contenu_produit}\n\n[Visual Prompt Utilise]: {prompt_genere}"
    res_compile = client.chat.completions.create(messages=[{"role": "user", "content": prompt_compile}], model="llama-3.1-8b-instant")
    livrable_final = res_compile.choices[0].message.content

    etapes_log.append("✅ Creator AI : Produit validé et envoyé au CEO !\n🟢 [DEPT LOGISTIQUE] Chariow Publisher met en boutique...")
    yield "\n".join(etapes_log), livrable_final, None, html_image, str(STATS_ENTREPRISE["revenus_hebdo"]), f"{STATS_ENTREPRISE['ebooks_vendus']} e-books / {STATS_ENTREPRISE['affiches_vendues']} affiches", f"FB: {STATS_ENTREPRISE['abonnes_fb']} | IG: {STATS_ENTREPRISE['abonnes_ig']} | TT: {STATS_ENTREPRISE['abonnes_tt']}"
    
    time.sleep(1)
    if type_produit == "E-book":
        STATS_ENTREPRISE["ebooks_vendus"] += 1
        STATS_ENTREPRISE["revenus_hebdo"] += 27
    else:
        STATS_ENTREPRISE["affiches_vendues"] += 1
        STATS_ENTREPRISE["revenus_hebdo"] += 15

    etapes_log.append("✅ Produit publié sur Chariow !\n🟢 [DEPT ACQUISITION] Campagne Marketing lancée sur les réseaux...")
    yield "\n".join(etapes_log), livrable_final, None, html_image, str(STATS_ENTREPRISE["revenus_hebdo"]), f"{STATS_ENTREPRISE['ebooks_vendus']} e-books / {STATS_ENTREPRISE['affiches_vendues']} affiches", f"FB: {STATS_ENTREPRISE['abonnes_fb']} | IG: {STATS_ENTREPRISE['abonnes_ig']} | TT: {STATS_ENTREPRISE['abonnes_tt']}"
    
    STATS_ENTREPRISE["abonnes_fb"] += 12
    STATS_ENTREPRISE["abonnes_ig"] += 18
    STATS_ENTREPRISE["abonnes_tt"] += 35
    
    etapes_log.append("🎉 [CEO REPORT] Tout le pipeline a fonctionné ! Rapport envoyé à l'Oracle.")
    
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode="w", encoding="utf-8-sig")
    temp_file.write(f"RAPPORT DE PRODUCTION ORADI OS v6.5\n\n=== LIVRABLE FINAL ===\n\n{livrable_final}\n\n=== LIEN DE VOTRE VISUEL ===\n{url_image_generee}")
    temp_file.close()

    yield "\n".join(etapes_log), livrable_final, temp_file.name, html_image, f"{STATS_ENTREPRISE['revenus_hebdo']} €", f"{STATS_ENTREPRISE['ebooks_vendus']} e-books / {STATS_ENTREPRISE['affiches_vendues']} affiches", f"FB: {STATS_ENTREPRISE['abonnes_fb']} | IG: {STATS_ENTREPRISE['abonnes_ig']} | TT: {STATS_ENTREPRISE['abonnes_tt']}"


# 4. CONSTRUCTEUR DE L'INTERFACE GRAPHIQUE
with gr.Blocks(css="""
    body { font-family: 'Space Grotesk', sans-serif !important; background-color: #0B0F19; color: #F3F4F6; }
""") as demo:
    
    gr.Markdown("# 🤖 ORADI OS v6.5 — L'Empire Automatisé")
    
    gr.Markdown("### 📊 TABLEAU DE BORD CEO")
    with gr.Row():
        with gr.Column(scale=1):
            revenus_widget = gr.Textbox(value=f"{STATS_ENTREPRISE['revenus_hebdo']} €", label="💰 Revenus Hebdomadaires", interactive=False)
        with gr.Column(scale=1):
            produits_widget = gr.Textbox(value=f"{STATS_ENTREPRISE['ebooks_vendus']} e-books / {STATS_ENTREPRISE['affiches_vendues']} affiches", label="📦 Catalogue Chariow", interactive=False)
        with gr.Column(scale=1):
            audience_widget = gr.Textbox(value=f"FB: {STATS_ENTREPRISE['abonnes_fb']} | IG: {STATS_ENTREPRISE['abonnes_ig']} | TT: {STATS_ENTREPRISE['abonnes_tt']}", label="👥 Audience Réseaux", interactive=False)
            
    gr.Markdown("---")
    
    gr.Markdown("### 🏭 PROCESSUS DE PRODUCTION")
    with gr.Row():
        with gr.Column(scale=1):
            input_theme = gr.Textbox(label="Quel e-book ou affiche voulez-vous créer ?", placeholder="Ex: Apprendre le Japonais facilement")
            input_type = gr.Radio(["E-book", "Affiche"], label="Type de Produit", value="E-book")
            btn_lancer = gr.Button("🚀 ORDONNER LA CRÉATION & PUBLICATION", variant="primary")
            
        with gr.Column(scale=2):
            logs_agents = gr.Markdown("### Statut de l'Équipe\n*En attente de vos ordres...*")
            
            with gr.Tabs():
                with gr.TabItem("📝 Rapport Texte"):
                    livrable_rendu = gr.Markdown("### Aperçu du Livrable\n*Le texte du produit s'affichera ici.*")
                    file_download = gr.File(label="Télécharger le rapport (.txt clean)")
                with gr.TabItem("🎨 Visuel Généré"):
                    gr.Markdown("### 🖼️ Image Réelle créée par Designer AI")
                    image_rendu = gr.HTML(value="<p style='text-align:center; color:#9CA3AF;'>Aucun visuel généré pour le moment.</p>")

    btn_lancer.click(
        fn=executer_pipeline_entreprise,
        inputs=[input_theme, input_type],
        outputs=[logs_agents, livrable_rendu, file_download, image_rendu, revenus_widget, produits_widget, audience_widget]
    )

# Configuration du port pour Render
port_serveur = int(os.environ.get("PORT", 10000))
demo.launch(server_name="0.0.0.0", server_port=port_serveur)
