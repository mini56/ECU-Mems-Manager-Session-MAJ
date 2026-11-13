# Mises à jour documentaires : mécanisme évolutif

## État réel au 13 novembre 2026

Les anciennes valeurs figées (deux manuels FR, un manuel EN, tailles,
empreintes et Release fixes) ont été supprimées du mécanisme de publication.

Une nouvelle Release peut maintenant fournir une nouvelle version complète
de la base documentaire de chaque langue, contenant les anciens manuels et
de nouvelles sources. Le système vérifie le mot de passe administrateur,
AES-GCM, l'intégrité SQLite, la couverture des pages, la provenance,
les index de recherche, le statut des données et chaque image.

La publication actuelle reste désactivée : les champs FR et EN du
manifeste indiquent toujours available=false. Les deux anciens packs chiffrés
ne sont pas hébergés sur cette Release.

## Ajouter une nouvelle version autorisée

1. Préparer un snapshot SQLite contrôlé, avec les anciens et nouveaux documents.
2. Former le ZIP du snapshot et des images, puis le chiffrer en MEMSDOC1
   avec le secret administrateur MAJ.
3. Dans Actions, lancer « Préparer un dépôt de pack documentaire (brouillon privé) »
   avec un nouveau tag, par exemple mems-doc-20261114-v2.
4. Joindre le ou les fichiers MEMS-DOC-FR-*.encrypted,
   MEMS-DOC-EN-*.encrypted, etc. à la Release brouillon.
5. Ne rendre la Release publique qu'avec une autorisation de redistribution
   écrite couvrant tous les documents, textes et images présents.
6. Dans Actions, lancer « Activer les bases documentaires vérifiées sur le site MAJ »,
   choisir la ou les langues et le nouveau tag, renseigner la référence
   de l'autorisation et valider les contrôles.
7. Après réussite, le manifeste est mis à jour et SESSION peut télécharger
   et installer la nouvelle version avec sauvegarde de la précédente.

## Tests réellement passés

- Site MAJ : run 43423084644, tests FR et EN, deux versions successives.
- Site MAJ : run 43421683563, ajout de troisième manuel synthétique,
  corruption refusée et conservation des documents existants.
- SESSION : run 43422993264, compilation Linux et installation de deux
  documents puis mise à jour vers trois documents avec sauvegarde.
- Aucun nouveau Setup Windows contenant ces changements n'est publié.

## Limite encore ouverte

MEMS Forge possède déjà un dossier depot/ et une chaîne d'extraction/OCR PDF,
mais il produit des packs candidats qui ne sont PAS des bases natives validées
de SESSION. Le pont « nouveau PDF -> validation -> snapshot SQLite par langue
-> pack chiffré » n'est pas encore automatisé de bout en bout.

Il reste également à transférer réellement les packs binaires sur le site MAJ
et à démontrer le téléchargement depuis un Setup Windows mis à jour.

Le dépôt MAJ et MEMS Forge sont publics. Ne pas y déposer de manuels
constructeur soumis à droits sans autorisation de redistribution.

Ne pas annoncer la fonction complète comme terminée avant un test réel
avec un nouveau document sur Windows.
