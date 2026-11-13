# Mise en ligne des bases documentaires — FR et EN

**État au 13 novembre 2026 :** la Release `mems-documentary-fr-en-20261113` existe sous forme de **brouillon**, sans pièces jointes. La configuration du manifeste est désactivée (`available: false`). Ne pas annoncer les bases disponibles tant que les fichiers et contrôles ne sont pas réellement terminés.

## Deux fichiers précis à déposer dans le brouillon

| Langue | Fichier | Taille (octets) | SHA-256 |
| --- | --- | ---: | --- |
| Français (RCL0193FRE + AKM7169FRE SPi) | `MEMS-DOC-FR-RCL0193FRE-AKM7169FRE-SPI-20261113-MAJ.encrypted` | 28098898 | `1686e3f7a8432751695d000897ad6b2412293444444ae983e44d84b083aeda04` |
| Anglais (AKM7169ENG) | `MEMS-DOC-EN-AKM7169ENG-20261113-MAJ.encrypted` | 6731477 | `10164258b6f8780d7e2249ef5ffa00cb9784f99cab1991cdb640e7833e9954ab` |

Les fichiers sont disponibles dans les livrables privés du propriétaire, pas dans ce dépôt. **Ne pas uploader l'archive ZIP globale en guise de pack** ; les fichiers doivent être attachés séparément, avec les noms et les tailles exactes du tableau.

Ces deux enveloppes sont chiffrées au format `MEMSDOC1` / AES-256-GCM avec le secret administrateur configuré dans GitHub MAJ. La vérification du déchiffrement a réussi hors ligne. Aucune information de mot de passe ne doit figurer dans les Releases, le code ou les logs.

## Opérations GitHub (administrateur du dépôt)

1. Confirmer au préalable que le projet dispose du droit de distribuer les données techniques et les illustrations Rover incluses dans les packs. La possession d'un PDF et son chiffrement ne prouvent pas cette autorisation.
2. Ouvrir le dépôt `mini56/ECU-Mems-Manager-Session-MAJ` → **Releases** → brouillon `mems-documentary-fr-en-20261113` → **Edit**.
3. Ajouter les **deux fichiers `.encrypted`** comme pièces jointes, puis vérifier leurs noms et tailles. Ne pas les placer dans le code source ni les fichiers README du dépôt.
4. Si la diffusion est autorisée, **Publish release**. La simple existence du brouillon n'active aucune mise à jour dans le programme.
5. Ouvrir **Actions** → `Activer les bases documentaires vérifiées sur le site MAJ` → **Run workflow**. Choisir `both` et fournir la référence de l'autorisation écrite. Ne cocher l'attestation de droit de redistribution que si elle est exacte.
6. Le workflow télécharge chaque pack depuis la Release et vérifie **SHA-256 exact**, **mot de passe administrateur**, **authentification AES-GCM**, **langue**, **pages constructeur**, **SQLite**, **procédures**, **index FTS** et **images**. Il ne modifie `manifest.json` qu'après réussite totale.
7. Vérifier sur `manifest.json` que `documentary_bases.fr.available` et `documentary_bases.en.available` valent `true`, puis tester depuis **SESSION 140** : Vérifier → Télécharger → saisir le mot de passe administrateur → contrôle et installation → consulter la base FR/EN. Ne pas annoncer une installation sur le poste utilisateur sans ce test.

## Récupération

Une installation refusée (mauvais secret, pack altéré, base incomplète) doit laisser le système précédent intact. Ne pas modifier les bases ECU, les sessions ni les données expertes. Les anciennes bases documentaires sont conservées comme sauvegarde lors de l'installation d'un nouveau pack valide.

Si le contenu n'est pas publiable, **laisser la Release en brouillon** et `available: false`. L'importation et l'utilisation privées ne donnent pas automatiquement le droit de publier les pages constructeur dans une Release GitHub publique.

## Automatisations validées

- [Contrôle du format double source et chiffrement](https://github.com/mini56/ECU-Mems-Manager-Session/actions/runs/43400776387)
- [Installation native sur base française synthétique à deux documents](https://github.com/mini56/ECU-Mems-Manager-Session/actions/runs/43401165876)
- [Test du manifeste, de l'authentification et de l'activation FR/EN](https://github.com/mini56/ECU-Mems-Manager-Session-MAJ/actions/runs/43403956332)

Les tests utilisent des données synthétiques lorsqu'il s'agit de publier des résultats CI. Les deux fichiers réels ont été chiffrés et vérifiés séparément, mais ne sont **pas hébergés sur GitHub MAJ** à ce stade.
