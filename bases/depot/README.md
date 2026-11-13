# Dépôt des bases chiffrées — MEMS Manager SESSION

**Dossier de réception :** `bases/depot/`

Une base chiffrée de plus de 25 Mo peut être déposée depuis le navigateur
GitHub en **deux morceaux de moins de 24 Mio chacun**, sans Git LFS.

Exemple, avec la base française actuelle :

- `MEMS-DOC-FR-RCL0193FRE-AKM7169FRE-SPI-20261113-MAJ.encrypted.part1`
- `MEMS-DOC-FR-RCL0193FRE-AKM7169FRE-SPI-20261113-MAJ.encrypted.part2`

La base anglaise, plus petite, est déposée en un fichier :

- `MEMS-DOC-EN-AKM7169ENG-20261113-MAJ.encrypted`

Le dépôt utilise les boutons GitHub **Add file > Upload files**.
Les morceaux doivent être dans ce même dossier et conserver exactement
leurs noms et leur ordre d'origine. La somme des octets reconstitue
le pack chiffré de départ : aucun nouveau mot de passe n'est créé.

## Vérification automatique

Le workflow `audit-deposited-documentary-packs.yml` a réellement
reconstruit les fichiers FR et EN déposés le 13 novembre 2026.
Résultat vert : run GitHub `43434712725`.

- FR : RCL0193FRE (371 pages) + AKM7169FRE (20 pages),
  SHA-256 `1686e3f7a8432751695d000897ad6b2412293444444ae983e44d84b083aeda04`.
- EN : AKM7169ENG (482 pages),
  SHA-256 `10164258b6f8780d7e2249ef5ffa00cb9784f99cab1991cdb640e7833e9954ab`.

Les packs ont été déchiffrés avec le secret MAJ stocké dans
GitHub Actions, puis leurs schémas, pages, images, index et relations
SQLite ont été contrôlés. Aucune base utilisateur n'a été modifiée.

## Publication des mises à jour

Le workflow `publish-documentary-depot.yml` peut maintenant être relancé
**manuellement sur les fichiers déjà présents**, sans devoir les déposer
une deuxième fois. Il vérifie et publie les nouvelles versions dans une
Release, puis met à jour `manifest.json`.

**Le dépôt MAJ est public.** La publication des pages et illustrations
constructeur doit rester bloquée sans preuve de droits de redistribution.
Les variables administrateur requises sont :

- `MEMS_DOCUMENTARY_REDISTRIBUTION_AUTHORIZED` = `true`
- `MEMS_DOCUMENTARY_RIGHTS_REFERENCE` = référence réelle de l'autorisation.

Le fait de posséder les documents ou de les chiffrer n'établit pas à lui
seul ces droits. Ne pas remplir ces variables avec une attestation inventée.

## Mises à jour suivantes

Ajouter un nouveau pack complet d'une langue avec un nouveau nom de version.
Le valideur doit retrouver les documents déjà présents et les nouveaux,
sans perdre les anciens. Un fichier incomplet, corrompu, non authentifié
ou mal indexé est refusé. Le mécanisme ne modifie pas les bases ECU,
personnelles ou expertes.

**Etat réel :** les deux packs sont présents et vérifiés ; leur publication
dans le manifeste public reste conditionnée à la validation des droits.
