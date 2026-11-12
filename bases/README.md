# Bases documentaires par langue

Un seul dossier par langue : `fr`, `en`, `pt`, `es`, `it`, `de`.

Chaque base est indépendante et utilise le **même schéma de consultation**, afin que MEMS Manager SESSION puisse changer de langue en changeant de pack plutôt qu'en traduisant les pages à l'affichage.

**Chaque base accumule plusieurs documents** : RAVE en premier, puis d'autres sources. Les références et étapes sont identifiées par **document + révision + identifiant interne**, pas uniquement par leur numéro constructeur. La mise à jour par langue remplace un snapshot validé qui contient aussi tous les documents déjà publiés. Voir [ARCHITECTURE-MULTIDOCUMENTS.md](ARCHITECTURE-MULTIDOCUMENTS.md).

- Pas de mélange de langues.
- Pas de traduction automatique à la consultation.
- Pas de base incomplète publiée comme base complète.
- Identification du PDF constructeur et contrôle SHA-256 obligatoires.
- Le français est traité en premier.
- Les PC sans Internet doivent pouvoir importer un pack téléchargé ailleurs.

Les dossiers sont des emplacements de préparation et de documentation, **pas** des preuves de disponibilité des bases. Le fichier `../manifest.json` fait foi pour les publications validées.
