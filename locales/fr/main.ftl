# Fenêtre principale
app-title = Le Sablenda

# Éléments du menu
menu-file = &Fichier
menu-help = &Aide
menu-save = &Enregistrer
menu-save-accelerator = Ctrl+S
menu-save-help = Enregistrer l'agenda
menu-preferences = &Préférences...
menu-preferences-help = Configurer les paramètres de l'application
menu-exit = &Quitter
menu-exit-accelerator = Ctrl+Q
menu-exit-help = Quitter l'application
menu-about = &À propos
menu-about-help = À propos de l'agenda

# Messages d'enregistrement
save-success = Agenda enregistré avec succès !
save-title = Enregistrer
save-error = Erreur lors de l'enregistrement de l'agenda : {$error}
save-error-title = Erreur d'enregistrement
save-error-exit = Erreur lors de l'enregistrement de l'agenda : {$error}

    Quitter quand même ?

# Dialogue À propos
about-name = Le Sablenda
about-version = 1.0
about-description = Une application de calendrier accessible construite avec wxPython
about-developer = Créé avec Claude Code

# Grille du calendrier - noms de jours abrégés
day-mon = Lun
day-tue = Mar
day-wed = Mer
day-thu = Jeu
day-fri = Ven
day-sat = Sam
day-sun = Dim

# Formatage des dates
# Format : « Lundi 1 novembre 2025 » (pas de virgules, pas d'ordinaux en français)
date-full = {$weekday} {$day} {$month} {$year}
# Format : « Novembre 2025 »
date-month-year = {$month} {$year}
# Format : « Lundi 1 novembre 2025 » (pour les titres de dialogue)
date-dialog-title = {$weekday} {$day} {$month} {$year}

# Pas d'ordinaux en français (1er, 2, 3, 4...)
# Le code n'ajoutera pas de suffixe pour le français
ordinal-1 =
ordinal-2 =
ordinal-3 =
ordinal-other =

# Noms complets des jours
day-name-0 = Lundi
day-name-1 = Mardi
day-name-2 = Mercredi
day-name-3 = Jeudi
day-name-4 = Vendredi
day-name-5 = Samedi
day-name-6 = Dimanche

# Noms des mois
month-name-1 = janvier
month-name-2 = février
month-name-3 = mars
month-name-4 = avril
month-name-5 = mai
month-name-6 = juin
month-name-7 = juillet
month-name-8 = août
month-name-9 = septembre
month-name-10 = octobre
month-name-11 = novembre
month-name-12 = décembre

# Comptage des entrées
entry-count = {$count ->
    [one] {$count} entrée
    *[other] {$count} entrées
}

# Dialogue des entrées
entries-for-date = Entrées pour le {$date}
entries-label = Entrées :
title-label = Titre :
description-label = Description :
start-time-label = Heure de début (HH:MM) :
end-time-label = Heure de fin (HH:MM) :
time-hint = (Utilisez les flèches ↑↓ pour ajuster de 15 min)
recurrence-label = Récurrence :

# Boutons
btn-add-fullday = Ajouter une entrée journée complète
btn-add-timed = Ajouter un événement programmé
btn-edit = Modifier
btn-delete = Supprimer
btn-close = Fermer
btn-ok = OK
btn-cancel = Annuler

# Titres de dialogue
dialog-new-entry = Nouvelle entrée
dialog-edit-entry = Modifier l'entrée

# Types de récurrence
recurrence-none = Aucune
recurrence-daily = Quotidienne
recurrence-weekly = Hebdomadaire
recurrence-monthly = Mensuelle
recurrence-yearly = Annuelle

# Messages
confirm-delete = Supprimer l'entrée « {$title} » ?
confirm-delete-title = Confirmer la suppression
invalid-time = Veuillez entrer des heures valides au format HH:MM (par ex., 09:00)
invalid-time-title = Heure invalide

# Valeurs par défaut
default-title = Sans titre

# Dialogue des préférences
preferences-title = Préférences
preferences-language-label = Langue :
preferences-language-auto = Automatique (système par défaut)
preferences-language-en = Anglais
preferences-language-fr = Français
