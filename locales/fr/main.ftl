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
menu-about-help = À propos de l'application

# Messages d'enregistrement
save-success = L'agenda a été sauvegardé.
save-title = Enregistrer
save-error = Erreur lors de l'enregistrement de l'agenda : { $error }
save-error-title = Erreur d'enregistrement
save-error-exit = Erreur lors de l'enregistrement de l'agenda : { $error }

    Voulez-vous fermer l'application sans sauvegarder ?

# Dialogue À propos
about-name = Le Sablenda
about-version = 1.0
about-description = Une application de calendrier accessible construite avec wxPython
about-developer = Vincent Le Goff, créé avec Claude Code

# Grille du calendrier - noms de jours abrégés
day-mon = Lun
day-tue = Mar
day-wed = Mer
day-thu = Jeu
day-fri = Ven
day-sat = Sam
day-sun = Dim

# Comptage des entrées
entry-count = {$count ->
    [one] { $count } entrée
    *[other] { $count } entrées
}

# Dialogue des entrées
entries-for-date = Entrées pour le { $date }
entries-label = Entrées :
title-label = Titre :
description-label = Description :
start-time-label = Heure de début (HH:MM) :
end-time-label = Heure de fin (HH:MM) :
time-hint = (Utilisez les flèches haut et bas pour ajuster de 15 minutes)
recurrence-label = Récurrence :

# Boutons
btn-add-fullday = Ajouter une entrée s'étendant sur toute la journée
btn-add-timed = Ajouter un événement
btn-edit = Modifier
btn-delete = Supprimer
btn-close = Fermer
btn-ok = OK
btn-cancel = Annuler

# Titres de dialogue
dialog-new-entry = Nouvelle entrée
dialog-edit-entry = Modifier l'entrée

# Types de récurrence
recurrence-none = Seulement cette fois
recurrence-daily = Tous les jours
recurrence-weekly = Toutes les semaines
recurrence-monthly = Tous les mois
recurrence-yearly = Tous les ans

# Messages
confirm-delete = Voulez-vous supprimer l'entrée { $title } ?
confirm-delete-title = Confirmer la suppression
invalid-time = Veuillez entrer des heures valides au format HH:MM (par ex., 09:00)
invalid-time-title = Heure invalide

# Valeurs par défaut
default-title = Sans titre

# Dialogue des préférences
preferences-title = Préférences
preferences-language-label = Langue :
preferences-language-auto = Automatique (Langue du système)
preferences-language-en = Anglais
preferences-language-fr = Français

# Menu d'icône de plateau
tray-show = Afficher Sablenda
tray-show-help = Afficher la fenêtre de l'application
tray-today-entries = Entrées d'aujourd'hui
tray-today-entries-help = Entrées pour aujourd'hui
tray-no-entries = Pas d'entrées aujourd'hui
