# dev_ia_certification_bloc_1

## Concernant l'extraction de données par scraping

- placez-vous dans le dossier web_scraping (le 1er dossier)

```bash
cd web_scraping
```

```
web_scraping/
├── scrapy.cfg
└── web_scraping/
    └── spiders/
        └── videogames_spider.py
```
- lancez l'extraction de données avec la commande suivante. Un fichier json comprenant les données collectées sera créé dans le dossier scripts_python : `dev_ia_certification_bloc_1/scripts_python/videogames_dataset.json`
```bash
scrapy crawl videogames_spider -O ../scripts_python/videogames_dataset.json
```

- lancez le script python de nettoyage des données. Un fichier json avec les données nettoyées sera générée dans le dossier scripts_python : `dev_ia_certification_bloc_1/scripts_python/videogames_dataset_clean.json`