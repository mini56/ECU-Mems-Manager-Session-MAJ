# Base documentaire — Français

**Langue :** `fr` — une base autonome regroupant plusieurs documents constructeur originaux.

## État réel au 13 novembre 2026

| Source constructeur | Édition | Données préparées | Sur le site MAJ |
| --- | --- | --- | --- |
| Manuel français Mini | RCL0193FRE, 371 pages | SQLite locale relue : 5 958 entrées et 325 fac-similés | **Non publiée** |
| Chapitre MEMS SPi | AKM7169FRE, 20 pages | Relecture du chapitre terminée : 20 opérations, 267 étapes, 22 valeurs, 19 descriptions, 20 images | **Non publiée** |
| Manuel AKM7169FRE complet | Autres chapitres | Source complète non retrouvée | Non disponible |

Les bases privées sont constituées. La SQLite française réunit désormais **391 pages, 6 387 entrées et 345 images**. Aucune base constructeur n'est encore téléchargeable depuis ce site public : le manifeste indique donc toujours `available: false`.

La branche de développement [`rave-fr-source-sqlite-20261112`](https://github.com/mini56/ECU-Mems-Manager-Session/tree/rave-fr-source-sqlite-20261112) contient le lecteur C++ des bases par langue et l'installation hors ligne d'un ZIP avec mot de passe. Le [Setup SESSION 140 de test](https://github.com/mini56/ECU-Mems-Manager-Session-MAJ/releases/tag/mems-session-140-admin-encrypted-documentary-TEST) est disponible, sans base constructeur embarquée. Il refuse les ZIP non chiffrés et demande exclusivement le mot de passe fixé par l'administrateur.

## AKM7169FRE SPi : chantier documentaire achevé

[Voir le résultat de la relecture, la provenance, les comptes et les contrôles](AKM7169FRE-SPI-PRIORITE.md). Le manuscrit original de 20 pages est intégralement conservé avec les pages et les illustrations ; les 267 étapes de réparation ont été structurées. Aucun statut `review_required` ne reste dans la nouvelle SQLite privée.

## Avant une publication publique

Le dépôt MAJ est **public**. Les manuels, leurs illustrations et des transcriptions restent soumis aux droits de leur éditeur. Ne pas mettre les fichiers Rover sur une Release publique sans autorisation de redistribution confirmée, même chiffrés.

Le manifeste deviendra `available: true` seulement après publication d'un pack autorisé et après validation de son intégrité, de sa langue, de son chiffrement, de sa provenance et de son installation par le programme. Les données ECU, personnelles et expertes restent totalement indépendantes.
